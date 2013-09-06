#!/usr/bin/env python

####################################
#                                  #
# Import all modules: configure... #
#                                  #
####################################
import xde_world_manager as xwm

import xdefw.interactive
shell = xdefw.interactive.shell_console()

import rtt_interface
rtt_interface.Logger_Instance().setLogLevel(rtt_interface.Logger.Error)

###################
#                 #
# Begin of Script #
#                 #
###################
print "BEGIN OF SCRIPT..."

TIME_STEP = .01

import xde_resources as xr

import xde_robot_loader as xrl
wm = xwm.WorldManager()
wm.createAllAgents(TIME_STEP)


import xde_spacemouse as spacemouse


#######################################################################################################
print "START ALL..."

sphereWorld = xrl.createWorldFromUrdfFile(xr.sphere, "sphere", [0,0.6,1.2, 1, 0, 0, 0], False, 0.2, 0.005)# , "material.concrete")
kukaWorld = xrl.createWorldFromUrdfFile(xr.kuka, "k1g", [0,0,0.4, 1, 0, 0, 0], True, 1, 0.005) #, "material.concrete")

wm.addMarkers(sphereWorld, ["sphere.sphere"], thin_markers=False)
wm.addWorld(sphereWorld )
wm.addWorld(kukaWorld)


# Create simple gravity compensator controller
import control
controller = control.createTask("controlK1G", TIME_STEP)
controller.connectToRobot(wm.phy, kukaWorld, "k1g")

# Configure the robot
import lgsm
kuka = wm.phy.s.GVM.Robot("k1g")
kuka.enableGravity(True)
kuka.setJointPositions(lgsm.vector([0.4]*7))
kuka.setJointVelocities(lgsm.vector([0.0]*7))
#kuka.enableContactWithBody("sphere.sphere", True)


controller.s.start()

#PDC Control mode
sm = spacemouse.createTask("smi", TIME_STEP, wm.phy, wm.graph, "sphere.sphere", pdc_enabled=True, body_name="k1g.07")

# Normal mode
#sm = spacemouse.createTask("smi", TIME_STEP, wm.phy, wm.graph, "sphere.sphere", pdc_enabled=False)

sm.s.start()

wm.startAgents()

shell()


