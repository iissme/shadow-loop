from setuptools import setup
import os

root = os.path.dirname(os.path.abspath(__file__))

about = {}
with open(os.path.join(root, 'shadow_loop', '__version__.py'), 'r') as f:
    exec(f.read(), about)

readme = ''
with open(os.path.join(root, 'README.md')) as f:
    readme = f.read()

setup(name=about['__title__'],
      author=about['__author__'],
      author_email='ishlyakhov@gmail.com',
      url='http://github.com/isanich/shadow-loop',
      version=about['__version__'],
      license=about['__license__'],
      description='Submit _awaitable_ objects to a shadow event loop in a separate thread '
                  'and wait for their execution from synchronous code if needed.',
      long_description=readme,
      packages=['shadow_loop'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True,
      platforms='any',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
