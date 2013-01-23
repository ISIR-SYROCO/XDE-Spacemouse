import dsimi.rtt
import rtt_interface
import deploy.deployer as ddeployer

import lgsm

sm = None

class SpaceMouse(dsimi.rtt.Task):
	def __init__(self, name, time_step, phy, graph, body_name, P1, P2, D1, D2):
		super(SpaceMouse, self).__init__(rtt_interface.PyTaskFactory.CreateTask(name))

		self.s.setPeriod(time_step)
		self.smf = dsimi.rtt.Task(ddeployer.load("smf", "dio::SpaceMouseFactory", "dio-hw-spacemouse", "dio/factory/"))
		self.smf.s.setPeriod(time_step)
		self.device = self.smf.s.scan()
		self.sm = dsimi.rtt.Task(self.smf.s.build(self.device[0], 'smf'))
		self.sm.s.setPeriod(time_step)
		self.phy = phy
		self.camera_interface = graph.s.Interface.CameraInterface("mainScene")

		self.sm_in_port = self.addCreateInputPort("sm_in", "Twistd", True)
		self.sm_in_port.connectTo(self.sm.getPort("out_vel"))
		self.sm_obs_in_port = self.sm.getPort("obs_frame")
		self.vel_out = self.addCreateOutputPort("vel_out", "Twistd")

		self.P1 = P1
		self.P2 = P2
		self.D1 = D1
		self.D2 = D2

		self.body = None
		self.createConnector(body_name)

		self.camera = lgsm.Displacement()

	def setPDCGain(self, P1, P2, D1, D2):
		self.pdc.setGainsP(P1, P2)
		self.pdc.setGainsD(D1, D2)

	def setBody(self, body_name):
		if self.body is not None:
			self.body.enableWeight()

		self.pdc.disable()
		ms = self.phy.s.GVM.Scene("main")
		ms.removeCartesianPDCoupling("pdc")
		self.phy.s.Connectors.delete("icis")
		self.phy.s.deleteComponent("pdc")

		self.createConnector(body_name)

	def createConnector(self, body_name):
		self.pdc = self.phy.s.GVM.CartesianPDCoupling.new("pdc")
		self.pdc.setCoupledRigidBody(body_name)
		ms = self.phy.s.GVM.Scene("main")
		ms.addCartesianPDCoupling(self.pdc)

		#1 is for Twist port creation
		self.phy.s.Connectors.IConnectorPDCoupling.new("icis", "sm_vel", "pdc", 1)
		self.pdc.setMaxAngularVelocity(0.31415)
		self.pdc.setMaxLinearVelocity(0.5)
		self.setPDCGain(self.P1, self.P2, self.D1, self.D2)

		self.phy.getPort("sm_vel").connectTo(self.vel_out)

		self.body = self.phy.s.GVM.RigidBody(body_name)
		self.body.disableWeight()

	def cleanConnector():
		self.phy.s.Connectors.delete("icis")

	def startHook(self):
		self.smf.s.start()
		self.sm.s.start()

	def stopHook(self):
		pass

	def updateHook(self):

 	 	sm_vel, sm_vel_ok = self.sm_in_port.read()

		#Hack
		self.camera = self.camera_interface.getCameraDisplacementInPhysicSpace("mainViewportBaseCamera")

		if sm_vel_ok :
			H_0_c = self.camera
			H_0_b = self.body.getPosition()
			H_b_0 = H_0_b.inverse()

			H_b_c = H_b_0 * H_0_c
			H_b_c.setTranslation(lgsm.vector([0,0,0]))

			sm_vel = H_b_c.adjoint() * sm_vel
			#sm_vel.setAngularVelocity(lgsm.vector([0,0,0]))
			#self.vel_out.write(sm_vel)
			self.body.setVelocity(sm_vel)
		else:
			#self.vel_out.write(lgsm.Twist())
			self.body.setVelocity(lgsm.Twist())


def createTask(name, time_step, phy, graph, body_name, P1=0, P2=0, D1=1, D2=2):
	sm = SpaceMouse(name, time_step, phy, graph, body_name, P1, P2, D1, D2)
	setProxy(sm)
	return sm

def setProxy(_sm):
	global sm
	sm = _sm
