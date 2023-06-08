from setuptools import setup

setup(
    name='visprotocol',
    version='3.0.0',
    description='Visual stimulation protocol and metadata handler for flystim experiments',
    url='https://github.com/ClandininLab/visprotocol',
    author='Max Turner',
    author_email='mhturner@stanford.edu',
    packages=['visprotocol'],
    install_requires=[
        'numpy',
        'nidaqmx',
        'labjack-ljm',
        'h5py',
        'scipy',
        'PyQT5',
        'pyYaml'],
    extras_require={'gui':  ["PyQT6"]},
    include_package_data=True,
    zip_safe=False,
)
