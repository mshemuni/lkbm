from setuptools import setup, find_packages

setup(
    name='pardus',
    version='0.0.1.b',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'pardus = main:main',
        ],
    },
    install_requires=[
    ],
)