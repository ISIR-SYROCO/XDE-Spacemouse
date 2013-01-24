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
controller.connectToRobot(phy, kukaWorld, "k1g")

import numpy as np
kuka = phy.s.GVM.Robot("k1g")
kuka.enableGravity(True)
kuka.setJointPositions(np.array([.4]*7).reshape(7,1))
kuka.setJointVelocities(np.array([0.0]*7).reshape(7,1))
kuka.enableContactWithBody("spheresphere", True)


controller.s.start()

sm = spacemouse.createTask("smi", TIME_STEP, phy, graph, "spheresphere", pdc_enabled=False)

sm.s.start()

phy.s.startSimulation()

shell()


