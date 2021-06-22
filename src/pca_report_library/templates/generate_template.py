#!/usr/bin/env python3
"""PCA Report Template provides template files for PCA Reports.

Usage:
  ./pca-report-templates --manualData | --LaTeX
  ./pca-report-templates (-h | --help)
  ./pca-report-templates --version

Options:
  -h --help     Show this screen.
  --version     Show version.

  Supporting Files:
    -m --manualData    Creates a template manualData json file.
    -L --LaTeX    Creates a LaTeX file that the reports a built from.
"""

# Standard Python Libraries
import os
import shutil
import sys
import tempfile
from typing import Dict

# Third-Party Libraries
from docopt import docopt

from ._version import __version__

MANUAL_DATA_TEMPLATE = "template-manualData_RVXXXX.json"
MUSTACHE_DIR = "../customer/"
MUSTACHE_FILE = "report.mustache"

ASSETS_DIR_SRC = "../assets"
ASSETS_DIR_DST = "assets"


def manualData_template(work_dir):
    """Move manual data template to working dir."""
    me = os.path.realpath(__file__)
    my_dir = os.path.dirname(me)
    file_src = os.path.join(my_dir, MANUAL_DATA_TEMPLATE)
    file_dst = os.path.join(work_dir, MANUAL_DATA_TEMPLATE)
    shutil.copyfile(file_src, file_dst)


def latex_template(work_dir):
    """Move latex template to working dir."""
    me = os.path.realpath(__file__)
    my_dir = os.path.dirname(me)

    file_src = os.path.join(my_dir, MUSTACHE_DIR + MUSTACHE_FILE)
    file_dst = os.path.join(work_dir, MUSTACHE_FILE)
    shutil.copyfile(file_src, file_dst)
    # copy static assets
    dir_src = os.path.join(my_dir, ASSETS_DIR_SRC)
    dir_dst = os.path.join(work_dir, ASSETS_DIR_DST)
    shutil.copytree(dir_src, dir_dst)


def main():
    """Set up logging, connect to API, remove assessment data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    original_working_dir = os.getcwd()

    temp_working_dir = tempfile.mkdtemp()

    os.chdir(temp_working_dir)

    if args["--manualData"]:
        manualData_template(temp_working_dir)
        print("Copying {} to current dir....".format(MANUAL_DATA_TEMPLATE))

    if args["--LaTeX"]:
        latex_template(temp_working_dir)
        print("Copying {} to current dir....".format(MUSTACHE_FILE))
        print("Copying Asset Folder for LaTeX report to current dir....")

    for i in os.listdir(temp_working_dir):
        shutil.move(os.path.join(temp_working_dir, i), original_working_dir)

    os.chdir(original_working_dir)
    shutil.rmtree(temp_working_dir)


if __name__ == "__main__":
    sys.exit(main())
