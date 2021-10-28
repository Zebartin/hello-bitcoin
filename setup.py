from setuptools import setup

setup(
    name='hello-bitcoin',
    version='1.0',
    py_modules=['main'],
    install_requires=[
        'Click',
        'ecdsa',
        'base58'
    ],
    entry_points={
        'console_scripts': [
            'hello-bitcoin = main:cli',
        ],
    },
)
