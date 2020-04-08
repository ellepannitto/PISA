from setuptools import setup

setup(
    name='resnikmeasure',
    description='New measure',
    authors=['Ludovica Pannitto', 'Giulia Cappelli'],
    author_email=['ellepannitto@gmail.com', ''],
    version='0.1.0',
    license='MIT',
    packages=['resnikmeasure'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'resnikmeasure = resnikmeasure.main:main'
        ],
    },
    install_requires=['pyyaml>=4.2b1', 'nltk>=3.2.1', 'scipy>=1.2.1', 'tqdm>=4.19.5', 'numpy>=1.16.3',
                      'pandas>=0.23.4'],
)
