import dsimi.rtt
import rtt_interface
import deploy.deployer as ddeployer

import lgsm

sm = None

class SpaceMouse(dsimi.rtt.Task):
	def __init__(self, name, time_step, phy, graph, cursor_name, pdc_enabled, body_name, PR, PT, DR, DT):
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
		self.vel_out = self.addCreateOutputPort("vel_out", "Twistd")

		self.cursor = None
		self.cursor = self.phy.s.GVM.RigidBody(cursor_name)
		self.cursor.disableWeight()
		self.pdc_enabled = pdc_enabled

		self.PR = PR
		self.PT = PT
		self.DR = DR
		self.DT = DT

		if self.pdc_enabled == True:
			if body_name is not None:
				self.createPDC(body_name)

		self.camera = lgsm.Displacement()


	def setPDCGain(self, PR, PT, DR, DT):
		"""
		Set the gain for the PDCoupling
		"""
		self.pdc.setGainsP(PR, PT)
		self.pdc.setGainsD(DR, DT)

	def setBody(self, body_name):
		"""
		Set the body named to be attached to the PDC
		"""
		if self.pdc_enabled == True:
			self.cleanPDC()
			self.createPDC(body_name)

	def createPDC(self, body_name):
		"""
		Create the PDC, attach the body 'body_name' to the origin of the virtual spring
		and enable PDC Control mode
		"""
		self.pdc = self.phy.s.GVM.CartesianPDCoupling.new("sm_pdc")
		self.pdc.setCoupledRigidBody(body_name)
		ms = self.phy.s.GVM.Scene("main")
		ms.addCartesianPDCoupling(self.pdc)

		self.pdc.setMaxAngularVelocity(2*3.1415)
		self.pdc.setMaxLinearVelocity(2.0)
		self.setPDCGain(self.PR, self.PT, self.DR, self.DT)
		self.pdc_enabled = True

	def cleanPDC(self):
		"""
		Remove properly the PDC (for example when changing body)
		"""
		self.pdc_enabled = False
		self.pdc.disable()
		ms = self.phy.s.GVM.Scene("main")
		ms.removeCartesianPDCoupling("sm_pdc")
		self.phy.s.deleteComponent("sm_pdc")

	def startHook(self):
		self.smf.s.start()
		self.sm.s.start()

	def stopHook(self):
		pass

	def updateHook(self):

 	 	sm_vel, sm_vel_ok = self.sm_in_port.read()

		#Hack
		self.camera = self.camera_interface.getCameraDisplacementInPhysicSpace("mainViewportBaseCamera")

		H_0_c = self.camera
		H_0_b = self.cursor.getPosition()
		H_b_0 = H_0_b.inverse()

		H_b_c = H_b_0 * H_0_c
		H_b_c.setTranslation(lgsm.vector([0,0,0]))


		if self.pdc_enabled:
			if "sm_pdc" in self.phy.s.getComponents():
				self.pdc.setDesiredPosition(H_0_b, H_0_b)

		if sm_vel_ok :
			sm_vel = H_b_c.adjoint() * sm_vel

			self.cursor.setVelocity(sm_vel)

		else:
			self.cursor.setVelocity(lgsm.Twist())


def createTask(name, time_step, phy, graph, cursor_name, pdc_enabled=False, body_name=None, PR=30, PT=30, DR=30, DT=30):
	sm = SpaceMouse(name, time_step, phy, graph, cursor_name, pdc_enabled, body_name, PR, PT, DR, DT)
	setProxy(sm)
	return sm

def setProxy(_sm):
	global sm
	sm = _sm
