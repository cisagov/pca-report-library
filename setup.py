"""
This is the setup module for the example project.

Based on:

- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""

# Standard Python Libraries
import codecs
from glob import glob
from os import walk
from os.path import abspath, basename, dirname, join, splitext

# Third-Party Libraries
from setuptools import find_packages, setup


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()


# Below two methods were pulled from:
# https://packaging.python.org/guides/single-sourcing-package-version/
def read(rel_path):
    """Open a file for reading from a given relative path."""
    here = abspath(dirname(__file__))
    with codecs.open(join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(version_file):
    """Extract a version number from the given file path."""
    for line in read(version_file).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


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
    version=get_version("src/pca_report_library/_version.py"),
    description="PCA Report library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    # Landing page for CISA's cybersecurity mission
    url="https://www.cisa.gov/cybersecurity",
    # Additional URLs for this project per
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls
    project_urls={
        "Source": "https://github.com/cisagov/pca-report-library",
        "Tracker": "https://github.com/cisagov/pca-report-library/issues",
    },
    # Author details
    author="Cybersecurity and Infrastructure Security Agency",
    author_email="github@cisa.dhs.gov",
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
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    # What does your project relate to?
    keywords="pca report automation",
    packages=find_packages(where="src/pca_report_library"),
    package_dir={"": "src/pca_report_library"},
    package_data={
        "": extra_files,
        "customer": ["*.mustache"],
        "templates": ["*.json"],
    },
    py_modules=[
        splitext(basename(path))[0] for path in glob("src/pca_report_library/*.py")
    ],
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
            "coverage",
            # coveralls 1.11.0 added a service number for calls from
            # GitHub Actions. This caused a regression which resulted in a 422
            # response from the coveralls API with the message:
            # Unprocessable Entity for url: https://coveralls.io/api/v1/jobs
            # 1.11.1 fixed this issue, but to ensure expected behavior we'll pin
            # to never grab the regression version.
            "coveralls != 1.11.0",
            "pre-commit",
            "pytest-cov",
            "pytest",
        ]
    },
    # Conveniently allows one to run the CLI tool as `pca-report-compiler`,`pca-report-generator`,and `pca-report-templates`
    entry_points={
        "console_scripts": [
            "pca-report-compiler = pca_report_library.compiler.xelatex:main",
            "pca-report-generator = pca_report_library.customer.generate_report:main",
            "pca-report-templates = pca_report_library.templates.generate_template:main",
        ]
    },
)
