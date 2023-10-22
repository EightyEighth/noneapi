from setuptools import find_packages, setup

setup(
    name='zero_connect',
    packages=find_packages(include=['zero_connect']),
    version='0.0.1',
    description=(
        'Small RPC framework based on ZeroMQ that allows you to concentrate '
        'on the business logic of your application and resolve communication '
        'issues between services for you with auto documentation support.'
    ),
    author='Denys Rozlomii',
    license='MIT',
    install_requires=[
        'pyzmq==25.1.1',
        'loguru==0.7.2',
        'gevent==23.9.1',
        'pdoc==14.1.0',
        'pydantic==2.4.2',
        'msgpack==1.0.7'

    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.2.2'],
    test_suite='tests',
)
