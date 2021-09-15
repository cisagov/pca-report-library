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

__all__ = [
    "latex_template",
    "main",
    "manualData_template",
]

# Standard Python Libraries
import os
import shutil
import tempfile
from typing import Dict

# Third-Party Libraries
from docopt import docopt
import pkg_resources

from .._version import __version__

MANUAL_DATA_TEMPLATE = "template-manualData_RVXXXX.json"
ASSETS_DIR = pkg_resources.resource_filename("pca_report_library", "assets")
MUSTACHE_FILE = "report.mustache"


def manualData_template(work_dir):
    """Move manual data template to working dir."""
    file_src = os.path.join(ASSETS_DIR, MANUAL_DATA_TEMPLATE)
    file_dst = os.path.join(work_dir, MANUAL_DATA_TEMPLATE)
    shutil.copyfile(file_src, file_dst)


def latex_template(work_dir):
    """Move latex template to working dir."""
    file_src = os.path.join(ASSETS_DIR, MUSTACHE_FILE)
    file_dst = os.path.join(work_dir, MUSTACHE_FILE)
    shutil.copyfile(file_src, file_dst)


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

    for temp_entry in os.listdir(temp_working_dir):
        temp_path = os.path.join(temp_working_dir, temp_entry)
        work_dir_path = os.path.join(original_working_dir, temp_entry)
        if os.path.exists(temp_path) and not os.path.exists(work_dir_path):
            shutil.move(temp_path, original_working_dir)

    os.chdir(original_working_dir)
    shutil.rmtree(temp_working_dir)
