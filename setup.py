#!/usb/bin/env python

import os

from setuptools import setup

try:
    from PyQt5.uic import compileUi
except ImportError:
    def compileUi(*args):
        pass

def compile_uis(packageroot):
    if compileUi is None:
        return
    for dirpath, dirnames, filenames in os.walk(packageroot):
        for fn in [fn_ for fn_ in filenames if fn_.endswith('.ui')]:
            fname = os.path.join(dirpath, fn)
            pyfilename = os.path.splitext(fname)[0] + '_ui.py'
            with open(pyfilename, 'wt', encoding='utf-8') as pyfile:
                compileUi(fname, pyfile)
            print('Compiled UI file: {} -> {}.'.format(fname, pyfilename))

compile_uis('src')


setup(name='mdscripts', author='Andras Wacha',
      author_email='awacha@gmail.com', url='http://github.com/awacha/mdscripts',
      description='Various scripts for molecular dynamics simulations',
      package_dir={'': 'src'},
      packages=['mdscripts', 'mdscripts.io', 'mdscripts.rama_analyzer'],
      entry_points={'gui_scripts': ['gmx_extract_energy = mdscripts.extract_energy:run',
                                    'gmx_rama_analyzer = mdscripts.rama_analyzer.__main__:run'],
                    'console_scripts': ['gmx_insert_protein = mdscripts.insertprotein:run',
                                        'gmx_intralayer_solvents = mdscripts.find_intrabilayer_solvent:run'],
                    },
      package_data={'': ['*.ui']},
      install_requires=['numpy>=1.0.0', 'matplotlib',
                        'setuptools_scm'],
      setup_requires=['setuptools_scm'],
      use_scm_version=True,
      license="BSD",
      zip_safe=False,
      )
