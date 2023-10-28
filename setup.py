from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zero-connect',
    packages=find_packages(include=['zero_connect']),
    version='0.0.1',
    description=(
        'Small RPC framework based on ZeroMQ that allows you to concentrate '
        'on the business logic of your application and resolve communication '
        'issues between services for you with auto documentation support.'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Denys Rozlomii',
    license='MIT',
    install_requires=[
        'pyzmq==25.1.1',
        'loguru==0.7.2',
        'gevent==23.9.1',
        'pdoc==14.1.0',
        'pydantic==2.4.2',
        'orjson==3.9.10'

    ],
    extras_require={
        'dev': [
            'pytest', 'flake8', 'black', 'mypy', 'isort', 'pytest-cov',
            'requests'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    url='https://github.com/yourusername/zero-connect',
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.2.2'],
    test_suite='tests',
)
