XDE-Spacemouse
===============

Module to interface with a spacemouse

If `prefix` is not defined, install in python USER_BASE directory (`~/.local` by default)

Install:
---------
Install module:

`python setup.py install [--prefix=PREFIX]`

Dev-mode:
----------------
Create a symlink to `./XDE-Spacemouse/src` in `prefix` directory:

`python setup.py develop [--prefix=PREFIX] [--uninstall]`

Control modes:
--------------
This module provides two control modes:
 - Normal Mode: the spacemouse control a cursor
 - PDC Mode: a body is attached to the cursor with a PD Coupling

Documentation:
--------------
To build documentation:

`runxde.sh setup.py build_doc [--build-dir=BUILD_DIR] [-b TARGET_BUILD]`

