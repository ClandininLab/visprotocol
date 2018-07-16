from setuptools import setup

setup(
    name='ClandininLab-flystim',
    version='0.0.1',
    description='Clandinin-lab protocol and metadata handler for flystim experiments',
    url='https://github.com/ClandininLab/ClandininLab-flystim',
    author='Max Turner',
    author_email='mhturner@stanford.edu',
    packages=['ClandininLab-flystim'],
    install_requires=[
        'PyQT5',
        'numpy',
        'flystim'],
    include_package_data=True,
    zip_safe=False,
)