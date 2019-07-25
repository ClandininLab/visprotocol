from setuptools import setup

setup(
    name='visprotocol',
    version='2.0.0',
    description='Visual stimulation protocol and metadata handler for flystim experiments',
    url='https://github.com/ClandininLab/visprotocol',
    author='Max Turner',
    author_email='mhturner@stanford.edu',
    packages=['visprotocol'],
    install_requires=[
        'PyQT5',
        'numpy',
        'nidaqmx',
        'h5py',
        'scipy',
        'nptdms',
        'pyYaml'],
    include_package_data=True,
    zip_safe=False,
)
