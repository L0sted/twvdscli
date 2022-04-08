from setuptools import setup


with open("README.md", "r") as long_descr:
    long_description = long_descr.read()

setup(
    name = 'twvdscli',
    version = '1.0',
    author = 'L0sted',
    description = 'Servers and services manage tool for Timeweb Cloud',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/L0sted/twvdscli',
    classifiers = [
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
    py_modules = ['twvdscli'],
    install_requires = [
        'typer==0.4.0',
        'prettytable==3.2.0',
        'wcwidth==0.2.5'
    ],
    entry_points = {
        'console_scripts': [
            'twvdscli = twvdscli'
        ]
    }
)
