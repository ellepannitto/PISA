from setuptools import setup

setup(
    name='resnikmeasure',
    description='New measure',
    author='Ludovica Pannitto',
    author_email='ellepannitto@gmail.com',
    version='0.1.0',
    license='MIT',
    packages=['resnikmeasure'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'resnikmeasure = resnikmeasure.main:main'
        ],
    },
    install_requires=[],
)