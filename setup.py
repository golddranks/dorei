import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()
CHANGES = open(os.path.join(here, 'CHANGES.txt'), encoding='utf-8').read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_mako',
    'waitress',
    'httpagentparser',
    'prefixtree',
    ]

setup(name='dorei',
      version='0.59',
      description='dorei',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="dorei",
      entry_points="""\
      [paste.app_factory]
      main = dorei:main
      """,
      )
