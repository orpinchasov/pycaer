from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pycaer',
      version='1.0',
      description='Python wrapper for libcaer.',
      long_description=readme(),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: GPL-3 License',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Libraries',
                   ],
      keywords='caer DVS128 inilabs',
      url='https://github.com/orpinchasov/pycaer',
      author='Or Pinchasov',
      author_email='or.pinchasov@gmail.com',
      license='GPL-3',
      packages=['pycaer'],
      )
