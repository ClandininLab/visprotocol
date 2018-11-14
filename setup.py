from setuptools import setup

setup(
    name='vis-protocol',
    version='0.1.0',
    description='Visual stimulation protocol and metadata handler for flystim experiments',
    url='https://github.com/ClandininLab/vis-protocol',
    author='Max Turner',
    author_email='mhturner@stanford.edu',
    packages=['vis-protocol'],
    install_requires=[
        'PyQT5',
        'numpy',
        'flystim',
        'nidaqmx',
        'h5py',
        'scipy',
        'flyrpc'],
    include_package_data=True,
    zip_safe=False,
)
