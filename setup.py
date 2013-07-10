from distutils.core import setup, Command

from distutils.sysconfig import get_config_vars
import os, sys, string, shutil, errno
from site import USER_BASE

package_name = 'xde_spacemouse'

def force_symlink(file1, file2):
	try:
		os.symlink(file1, file2)
	except OSError, e:
		if e.errno == errno.EEXIST:
			shutil.rmtree(file2)
			os.symlink(file1, file2)

class develop(Command):
	description = "Create symbolic link instead of installing files"
	user_options = [
			('prefix=', None, "installation prefix"),
			('uninstall', None, "uninstall development files")
			]

	def initialize_options(self):
		self.prefix = None
		self.uninstall = 0

	def finalize_options(self):
		self.py_version = (string.split(sys.version))[0]
		if self.prefix is None:
		    self.prefix = USER_BASE
		self.prefix = os.path.expanduser(self.prefix)

	def run(self):
		out_dir = os.path.join(self.prefix, "lib", "python"+self.py_version[0:3], "site-packages")
		if not os.path.isdir(out_dir):
			os.makedirs(out_dir)

		out_dir = os.path.join(out_dir, package_name)
		src_dir = os.path.join(os.getcwd(), "src" )
		if self.uninstall == 1:
			if os.path.islink(out_dir):
				print "Removing symlink "+out_dir
				os.remove(out_dir)
			else:
				print "Not in dev mode, nothing to do"
		else:
			if os.path.islink(out_dir):
				print "Already in dev mode"
			else:
				print "Creating symlink "+src_dir+" -> "+out_dir
				force_symlink(src_dir, out_dir)

cmdclass={'develop': develop}

try:
	# add a command for building the html doc
	from sphinx.setup_command import BuildDoc
	cmdclass['build_doc'] = BuildDoc
except ImportError:
	pass


if sys.argv[0] == "setup.py":
    script_name=sys.argv[0]
    script_args=sys.argv[1:]
else:
    script_name=sys.argv[1]
    script_args=sys.argv[2:]

setup(name='XDE-Spacemouse',
	  version='0.1',
	  description='Spacemouse util for xde',
	  author='Soseph',
	  author_email='hak@isir.upmc.fr',
	  package_dir={'xde_spacemouse':'src'},
	  packages=[package_name],
	  cmdclass=cmdclass,

	  script_name=script_name,
	  script_args= script_args
	 )
