#!/usr/bin/env python3
"""PCA Tex Compiler compiles PCA Reports from Tex File.

Usage:
  ./pca-report-compiler TEX_FILE
  ./pca-report-compiler (-h | --help)
  ./pca-report-compiler --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  TEX_FILE      LaTeX File to come compiled

  Supporting Files:
    -l --labels  Indicates the assessment included labels which utilities the labels template.


"""

# Standard Python Libraries
import os
import shutil
import subprocess  # nosec See line 42 for explication.
import sys
import tempfile
from typing import Dict

# Third-Party Libraries
from docopt import docopt

from .._version import __version__

TO_COPY = ["figures", "screenshots"]
ASSETS_DIR_SRC = "../assets"
ASSETS_DIR_DST = "assets"
TEX_FILE = "/home/pca/"


def compile_tex(tex_file):
    """Run xelatex compiler twice."""
    for x in range(1, 3):
        # Bandit complains about the use of subprocess, but this
        # should be safe as this will only run "xelatex". The command
        # is hardcoded, which limits the ease of abuse. It could still be
        # possible that the assessment_id is provided in a way t0 allow
        # execution of unwanted commands. Also used in customer.generate_report.py
        # FIXME Find a better method than subprocess to run the compiler.
        subprocess.call(["xelatex", tex_file])  # nosec


def setup_work_directory(work_dir, text_file):
    """Set up a temporary working directory."""
    me = os.path.realpath(__file__)
    my_dir = os.path.dirname(me)
    file_src = os.path.join(TEX_FILE, text_file)
    file_dst = os.path.join(work_dir, text_file)
    shutil.copyfile(file_src, file_dst)
    # copy static assets
    dir_src = os.path.join(my_dir, ASSETS_DIR_SRC)
    dir_dst = os.path.join(work_dir, ASSETS_DIR_DST)
    shutil.copytree(dir_src, dir_dst)


def main():
    """Set up logging, connect to API, remove assessment data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)
    success = True

    # Tries to see if report tex file is present.
    try:
        # Checks for report data file
        f = open(args["TEX_FILE"])
        f.close()

    except IOError as e:
        print("ERROR- File not found: " + e.filename)
        success = False
    else:

        # Moves supporting files.

        # create a working directory
        original_working_dir = os.getcwd()

        temp_working_dir = tempfile.mkdtemp()

        os.chdir(temp_working_dir)

        # setup the working directory
        setup_work_directory(temp_working_dir, args["TEX_FILE"])

        for folder in TO_COPY:
            dir_src = os.path.join(original_working_dir, folder)
            dir_dst = os.path.join(temp_working_dir, "{}".format(folder))
            shutil.copytree(dir_src, dir_dst)

        compile_tex(args["TEX_FILE"])

        # revert working directory
        os.chdir(original_working_dir)

        src_report_filename = os.path.join(
            temp_working_dir, args["TEX_FILE"].split(".")[0] + ".pdf"
        )

        dest_report_filename = args["TEX_FILE"].split(".")[0] + ".pdf"

        shutil.move(src_report_filename, dest_report_filename)

        shutil.rmtree(temp_working_dir)

        print("Completed, Please see report: {}".format(dest_report_filename))

    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
