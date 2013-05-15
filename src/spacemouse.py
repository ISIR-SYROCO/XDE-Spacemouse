""" This module abstract the instantiation and configuration of the spacemouse.
"""

import dsimi.rtt
import rtt_interface
import deploy.deployer as ddeployer

import lgsm

sm = None

class SpaceMouse(dsimi.rtt.Task):
	""" Orocos task that gathers the components to use the spacemouse: load driver, open device and configure.
	Two control mode are available: Normal and PDC.
	In Normal mode, the spacemouse control a cursor.
	In PDC mode, the user attach a body to the cursor with a PD coupling so that
	the body is attracted to the cursor.
	In both case the cursor is controlled in the camera frame.

	:param name: name of the Orocos task that will be associated to this task
	:param time_step: period of the Orocos task
	:param phy: the main physic agent
	:param graph: the main graphic agent
	:param cursor_name: name of the body that will represent the cursor
	:param pdc_enabled: set to True to enable PDC mode, False to enable Normal mode
	:param body_name: name of the body to be attached to the cursor in PDC mode
	:param PR: P parameter for rotation of the PD Coupling (PDC mode)
	:param PT: P parameter for translation of the PD Coupling (PDC mode)
	:param DR: D parameter for rotation of the PD Coupling (PDC mode)
	:param DT: D parameter for translation of the PD Coupling (PDC mode)
	"""
	def __init__(self, name, time_step, phy, graph, cursor_name, pdc_enabled, body_name, PR, PT, DR, DT):
		"""
		"""
		super(SpaceMouse, self).__init__(rtt_interface.PyTaskFactory.CreateTask(name))

		self.s.setPeriod(time_step)
		self.smf = dsimi.rtt.Task(ddeployer.load("smf", "dio::SpaceMouseFactory", "dio-hw-spacemouse", "dio/factory/"))
		self.smf.s.setPeriod(time_step)
		self.device = self.smf.s.scan()
		self.sm = dsimi.rtt.Task(self.smf.s.build(self.device[0], 'smf'))
		self.sm.s.setPeriod(time_step)
		self.phy = phy
		self.camera_interface = graph.s.Interface.CameraInterface("mainScene")

		self.sm_in_port = self.addCreateInputPort("sm_in", "Twistd" )
		self.sm_in_port.connectTo(self.sm.getPort("out_vel"))
		self.pos_out = self.addCreateOutputPort("pos_out", "Displacementd")

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

		:param PR: P parameter for rotation of the PD Coupling (PDC mode)
		:param PT: P parameter for translation of the PD Coupling (PDC mode)
		:param DR: D parameter for rotation of the PD Coupling (PDC mode)
		:param DT: D parameter for translation of the PD Coupling (PDC mode)
		"""
		self.pdc.setGainsP(PR, PT)
		self.pdc.setGainsD(DR, DT)

	def setBody(self, body_name):
		"""
		Set the body named to be attached to the PDC

		:param body_name: name of the body to be attached to the cursor in PDC mode
		"""
		if self.pdc_enabled == True:
			self.cleanPDC()
			self.createPDC(body_name)

	def createPDC(self, body_name):
		"""
		Create the PDC, attach the body 'body_name' to the origin of the virtual spring
		and enable PDC Control mode

		:param body_name: name of the body to be attached to the cursor in PDC mode
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
		self.sm.s.stop()
		self.smf.s.stop()

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

		self.pos_out.write(self.cursor.getPosition())


def createTask(name, time_step, phy, graph, cursor_name, pdc_enabled=False, body_name=None, PR=30, PT=30, DR=30, DT=30):
	"""
	Instantiate the Orocos task and set a proxy

	:param name: name of the Orocos task that will be associated to this task
	:param time_step: period of the Orocos task
	:param phy: the main physic agent
	:param graph: the main graphic agent
	:param cursor_name: name of the body that will represent the cursor
	:param pdc_enabled: set to True to enable PDC mode, False to enable Normal mode
	:param body_name: name of the body to be attached to the cursor in PDC mode
	:param PR: P parameter for rotation of the PD Coupling (PDC mode)
	:param PT: P parameter for translation of the PD Coupling (PDC mode)
	:param DR: D parameter for rotation of the PD Coupling (PDC mode)
	:param DT: D parameter for translation of the PD Coupling (PDC mode)
	"""
	sm = SpaceMouse(name, time_step, phy, graph, cursor_name, pdc_enabled, body_name, PR, PT, DR, DT)
	setProxy(sm)
	return sm

def setProxy(_sm):
	"""
	Set the proxy
	"""
	global sm
	sm = _sm
