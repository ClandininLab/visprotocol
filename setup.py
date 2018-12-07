from setuptools import setup

setup(
    name='visprotocol',
    version='0.1.1',
    description='Visual stimulation protocol and metadata handler for flystim experiments',
    url='https://github.com/ClandininLab/visprotocol',
    author='Max Turner',
    author_email='mhturner@stanford.edu',
    packages=['visprotocol'],
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
