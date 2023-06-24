from distutils.core import setup
import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='banana_dev',
    packages=['banana_dev'],
    version='5.0.1',
    license='MIT',
    # Give a short description about your library
    description='The banana package is a python client to interact with your machine learning models hosted on Banana',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Erik Dunteman',
    author_email='erik@banana.dev',
    url='https://www.banana.dev',
    keywords=['Banana client', 'API wrapper', 'Banana', 'SDK'],
    setup_requires=['wheel'],
    install_requires=[
        "requests>=2.26.0,<3.0.0",
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
