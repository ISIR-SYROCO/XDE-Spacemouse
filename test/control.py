import lgsm
import rtt_interface
import dsimi.rtt
import numpy as np
import physicshelper

controller = None

class SimpleController(dsimi.rtt.Task):
	def __init__(self, name, time_step):
		super(SimpleController, self).__init__(rtt_interface.PyTaskFactory.CreateTask(name))

		# Create ports to read the state of the robot from the physical scene
		self.q_port = self.addCreateInputPort("q", "VectorXd", True)
		self.qdot_port = self.addCreateInputPort("qdot", "VectorXd", True)
		self.d_port = self.addCreateInputPort("d", "Displacementd", True)
		self.t_port = self.addCreateInputPort("t", "Twistd", True)
		self.tau_port = self.addCreateOutputPort("tau", "VectorXd")

		# Ref to the dynamic model
		self.model = None

		self.s.setPeriod(time_step)

	def startHook(self):
		pass

	def stopHook(self):
		pass

	def updateHook(self):
		if self.model is None:
			return

		q,qok = self.q_port.read()
		qdot, qdotok = self.qdot_port.read()
		d, dok = self.d_port.read()
		t, tok = self.t_port.read()

		tau = lgsm.vector([0] * self.model.nbInternalDofs())

		if qok and qdotok and dok and tok:
			model = self.model

			# Refresh dynamic and kinematic models
			model.setFreeFlyerPosition(d)
			model.setFreeFlyerVelocity(t)
			model.setJointPositions(q)
			model.setJointVelocities(qdot)

			# Control
			tau = model.getGravityTerms()

			self.tau_port.write(tau)

def createTask(name, time_step):
	controller = SimpleController(name, time_step)
	setProxy(controller)
	return controller

def createDynamicModel(world, robotName):
	controller.model = physicshelper.createDynamicModel(world, robotName)

def setProxy(_controller):
	global controller
	controller=_controller

