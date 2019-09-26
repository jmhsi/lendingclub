from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("rem_to_be_paid.pyx"),
    include_dirs=[numpy.get_include()]
)
