import sys
import os
import versioneer
import distutils.command.clean
import shutil

have_cython = False

try:
    import Cython
    if Cython.__version__ < '0.25':
        raise Exception('cython is too old or not installed '
                        '(at least 0.25 required)')
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    # for devel version
    raise

    def cythonize(args):
        for arg in args:
            arg.sources = [(s[:-3] + 'c' if s.endswith('.pyx') else s) for s in arg.sources]

# clang gives an error if passed -mno-fused-madd
# (and I don't even understand why it's passed in the first place)
if sys.platform == 'darwin':
    from distutils import sysconfig, ccompiler

    sysconfig_customize_compiler = sysconfig.customize_compiler

    def customize_compiler(compiler):
        sysconfig_customize_compiler(compiler)
        if sys.platform == 'darwin':
            while '-mno-fused-madd' in compiler.compiler:
                compiler.compiler.remove('-mno-fused-madd')
            while '-mno-fused-madd' in compiler.compiler_so:
                compiler.compiler_so.remove('-mno-fused-madd')
            while '-mno-fused-madd' in compiler.linker_so:
                compiler.linker_so.remove('-mno-fused-madd')
    sysconfig.customize_compiler = customize_compiler
    ccompiler.customize_compiler = customize_compiler

try:
    from setuptools import setup, Extension as _Extension

    # setuptools is stupid and rewrites "sources" to change '.pyx' to '.c'
    # if it can't find Pyrex (and in recent versions, Cython).
    #
    # This is a really stupid thing to do behind the users's back (since
    # it breaks development builds) especially with no way of disabling it
    # short of the hack below.
    class Extension(_Extension):
        def __init__(self, *args, **kwargs):
            save_sources = kwargs.get('sources', None)
            _Extension.__init__(self, *args, **kwargs)
            self.sources = save_sources
except ImportError:
    from distutils.core import setup, Extension

import numpy as np

to_del = []

for i, a in enumerate(sys.argv):
    if a == '--disable-cython':
        to_del.append(i)
        have_cython = False

for i in reversed(to_del):
    del sys.argv[i]

del to_del

include_dirs = [np.get_include()]
library_dirs = []
if not os.getenv('CONDA_BUILD'):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    include_dirs += [os.path.join(current_dir, 'src')]

    if sys.platform == 'win32':
        default_bin_dir = os.path.join(current_dir, 'lib{}Release'.format(os.path.sep))
    else:
        default_bin_dir = os.path.join(current_dir, 'lib')
    if not os.path.isdir(default_bin_dir):
        raise RuntimeError('default binary dir {} does not exist, you may need to build the C library in release mode'.format(default_bin_dir))
    library_dirs += [default_bin_dir]

class cmd_clean(distutils.command.clean.clean):
    def run(self):
        import glob
        with open('.clean', 'r') as f:
            ignores = f.read()
            for wildcard in filter(bool, ignores.split('\n')):
                for filename in glob.glob(wildcard):
                    try:
                        os.remove(filename)
                    except OSError:
                        shutil.rmtree(filename, ignore_errors=True)

        # It's an old-style class in Python 2.7...
        distutils.command.clean.clean.run(self)


ea = []
if sys.platform in ('darwin', 'linux'):
    # Silence unused stuff warnings
    ea = ["-Wno-unused-variable", "-Wno-unused-function"]

exts = [Extension('pygpu.gpuarray',
                  sources=['pygpu/gpuarray.pyx'],
                  include_dirs=include_dirs,
                  libraries=['gpuarray'],
                  library_dirs=library_dirs,
                  extra_compile_args=ea,
                  define_macros=[('GPUARRAY_SHARED', None)]
                  ),
        Extension('pygpu.blas',
                  sources=['pygpu/blas.pyx'],
                  include_dirs=include_dirs,
                  libraries=['gpuarray'],
                  library_dirs=library_dirs,
                  extra_compile_args=ea,
                  define_macros=[('GPUARRAY_SHARED', None)]
                  ),
        Extension('pygpu._elemwise',
                  sources=['pygpu/_elemwise.pyx'],
                  include_dirs=include_dirs,
                  libraries=['gpuarray'],
                  library_dirs=library_dirs,
                  extra_compile_args=ea,
                  define_macros=[('GPUARRAY_SHARED', None)]
                  ),
        Extension('pygpu.collectives',
                  sources=['pygpu/collectives.pyx'],
                  include_dirs=include_dirs,
                  libraries=['gpuarray'],
                  library_dirs=library_dirs,
                  extra_compile_args=ea,
                  define_macros=[('GPUARRAY_SHARED', None)]
                  )]

cmds = versioneer.get_cmdclass()
cmds["clean"] = cmd_clean

version_data = versioneer.get_versions()

if version_data['error'] is not None:
    raise ValueError("Can't determine version for build: %s\n  Please make sure that your git checkout includes tags." % (version_data['error'],))

setup(name='pygpu',
      version=version_data['version'],
      cmdclass=cmds,
      description='numpy-like wrapper on libgpuarray for GPU computations',
      packages=['pygpu', 'pygpu/tests'],
      include_package_data=True,
      package_data={'pygpu': ['gpuarray.h', 'gpuarray_api.h',
                              'blas_api.h', 'numpy_compat.h',
                              'collectives.h', 'collectives_api.h']},
      ext_modules=cythonize(exts),
      install_requires=['mako>=0.7', 'six'],
      )
