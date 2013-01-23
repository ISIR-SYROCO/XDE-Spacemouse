#!/usr/bin/env python

####################################
#                                  #
# Import all modules: configure... #
#                                  #
####################################
import xde_world_manager as xwm

import dsimi.interactive
shell = dsimi.interactive.shell()

import deploy.deployer as ddeployer

###################
#                 #
# Begin of Script #
#                 #
###################
print "BEGIN OF SCRIPT..."

TIME_STEP = .01


import xde_robot_loader as xrl
clock, phy, graph = xwm.createAllAgents(TIME_STEP)


import xde_spacemouse as spacemouse


#######################################################################################################
print "START ALL..."
import lgsm


sphereWorld = xrl.createWorldFromUrdfFile("resources/urdf/sphere.xml", "sphere", [0,0,-0.4, 1, 0, 0, 0], False, 0.1, 0.05) #, "material.concrete")
kukaWorld = xrl.createWorldFromUrdfFile("resources/urdf/kuka.xml", "k1g", [0,0,0.4, 1, 0, 0, 0], True, 1, 0.05) #, "material.concrete")

xwm.addWorld(sphereWorld, True)
xwm.addWorld(kukaWorld, True)

import control
controller = control.createTask("controlK1G", TIME_STEP)
control.createDynamicModel(kukaWorld, "k1g")
#create connectors to get robot k1g state 'k1g_q', 'k1g_qdot', 'k1g_Hroot', 'k1g_Troot', 'k1g_H'
phy.s.Connectors.OConnectorRobotState.new("ocpos", "k1g_", "k1g")
phy.s.Connectors.IConnectorRobotJointTorque.new("ict", "k1g_", "k1g")

phy.getPort("k1g_q").connectTo(controller.getPort("q"))
phy.getPort("k1g_qdot").connectTo(controller.getPort("qdot"))
phy.getPort("k1g_Troot").connectTo(controller.getPort("t"))
phy.getPort("k1g_Hroot").connectTo(controller.getPort("d"))
controller.getPort("tau").connectTo(phy.getPort("k1g_tau"))


import numpy as np
kuka = phy.s.GVM.Robot("k1g")
kuka.enableGravity(True)
kuka.setJointPositions(np.array([.4]*7).reshape(7,1))
kuka.setJointVelocities(np.array([0.0]*7).reshape(7,1))
kuka.enableContactWithBody("spheresphere", True)


controller.s.start()

sm = spacemouse.createTask("smi", TIME_STEP, phy, graph, "spheresphere")

sm.s.start()

phy.s.startSimulation()

shell()


