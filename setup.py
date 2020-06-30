"""
This is the setup module for the example project.

Based on:

- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""

# Standard Python Libraries
from glob import glob
from os import walk
from os.path import basename, join, splitext

# Third-Party Libraries
from setuptools import find_packages, setup


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()


def package_vars(version_file):
    """Read in and return the variables defined by the version_file."""
    pkg_vars = {}
    with open(version_file) as f:
        exec(f.read(), pkg_vars)  # nosec
    return pkg_vars


def package_files(directory):
    """Read in and return package files from directory."""
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append("../" + join(path, filename))
    return paths


extra_files = package_files("pca_report/assets")


setup(
    name="pca-report-library",
    # Versions should comply with PEP440
    version=package_vars("src/_version.py")["__version__"],
    description="PCA Report generation library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # NCATS "homepage"
    url="https://www.us-cert.gov/resources/ncats",
    # The project's main homepage
    download_url="https://github.com/bjb28/pca-report-library",
    # Author details
    author="Cyber and Infrastructure Security Agency",
    author_email="ncats@hq.dhs.gov",
    license="License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.6",
    # What does your project relate to?
    keywords="pca report automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": extra_files,
        "pca_report.customer": ["*.mustache"],
        "pca_report.templates": ["*.json"],
    },
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=[
        "adjustText >= 0.7.3",
        "docopt",
        "matplotlib >= 3.1.1",
        "numpy >= 1.17.2",
        "pystache >= 0.5.4",
        "pytz >= 2019.2",
        "pytimeparse >= 1.1.8",
        "setuptools >= 24.2.0",
        "schema",
    ],
    extras_require={
        "test": [
            "pre-commit",
            # coveralls 1.11.0 added a service number for calls from
            # GitHub Actions. This caused a regression which resulted in a 422
            # response from the coveralls API with the message:
            # Unprocessable Entity for url: https://coveralls.io/api/v1/jobs
            # 1.11.1 fixed this issue, but to ensure expected behavior we'll pin
            # to never grab the regression version.
            "coveralls != 1.11.0",
            "coverage",
            "pytest-cov",
            "pytest",
        ]
    },
    # Conveniently allows one to run the CLI tool as `example`
    entry_points={
        "console_scripts": [
            "pca-report-compiler = compiler.xelatex:main",
            "pca-report-generator = customer.generate_report:main",
            "pca-report-templates = templates.generate_template:main",
        ]
    },
)
