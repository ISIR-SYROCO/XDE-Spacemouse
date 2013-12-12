from IsirPythonTools import *

package_name = 'xde_spacemouse'

setup(name='XDE-Spacemouse',
	  version='0.1',
	  description='Spacemouse util for xde',
	  author='Soseph',
	  author_email='hak@isir.upmc.fr',
	  package_dir={package_name:'src'},
	  packages=[package_name],
	  cmdclass=cmdclass,

	  script_name=script_name,
	  script_args= script_args
	 )
