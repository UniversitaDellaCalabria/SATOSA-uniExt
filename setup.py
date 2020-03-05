from setuptools import setup, Extension

def readme():
    with open('README.md') as f:
        return f.read()

DESC = "SATOSA extensions components for the Unical context "

setup(name='SATOSA-uniExt',
      version='0.2.2',
      description=DESC,
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=['Development Status :: 5 - Production/Stable',
                  'License :: OSI Approved :: BSD License',
                  'Programming Language :: Python :: 3'],
      url='https://github.com/UniversitaDellaCalabria/SATOSA-uniExt',
      author='Giuseppe De Marco',
      author_email='giuseppe.demarco@unical.it',
      license='GPL',
      #scripts=[''],
      packages=['satosa_uniext/processors'],
      install_requires=[
                      'satosa>=6.1.0',
                  ],
     )
