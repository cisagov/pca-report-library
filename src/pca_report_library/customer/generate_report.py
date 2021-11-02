"""PCA Report Generator builds PCA Reports with LaTeX template.

Usage:
  ./pca-report-generator [--labels] [--manual | --graph | --Metrics | --editable ] ASSESSMENT_ID
  ./pca-report-generator (-h | --help)
  ./pca-report-generator --version

Options:
  -h --help     Show this screen.
  --version     Show version.

  Supporting Files:
    -l --labels  Indicates the assessment included labels which utilities the labels template.

    Ad-hoc builds:
    -m --manual   Loads the manual data in to the report data JSON. Loads data from manualData_ASSESSMENT_ID.json
    -g --graph    Builds only the graphs for the report.
    -M --Metrics    Creates the Assessments Metrics JSON.
    -e --editable   Exports the needed tex file and supporting documents to allow manual editing.
"""

__all__ = [
    "assessment_metrics",
    "dict_formater",
    "group_text_builder",
    "latex_builder",
    "latex_data_fields",
    "latex_dict_prep",
    "latex_string_prep",
    "main",
    "manualData_processor",
    "setup_work_directory",
    "get_time_gap",
]

# Standard Python Libraries
import codecs
from datetime import datetime
from functools import reduce
import html
import json
import os
import shutil
import subprocess  # nosec See line 627 for explication.
import sys
import tempfile
from typing import Dict

# Third-Party Libraries
from docopt import docopt
import pkg_resources
import pystache
from pytz import timezone

from .._version import __version__
from ..utility.time import format_timedelta_to_HHMMSS, time_to_string
from .closing import closing_builder
from .graphs import graph_builder

utc = timezone("UTC")
localTimeZone = timezone("US/Eastern")  # Holds the desired time zone.

MUSTACHE_FILE = "report.mustache"
ASSETS_DIR = pkg_resources.resource_filename("pca_report_library", "assets")
ASSETS_DIR_DST = "assets"
TO_COPY = ["figures", "screenshots"]
# Fields that should not be Escaped for LaTeX.
LATEX_EXCLUDE_ESCAPE = [
    "Customer_Setup",
    "Hover_Over",
    "Display_Link",
    "User_Report_Provided",
]
LATEX_ESCAPE_MAP = {
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "[": "{[}",
    "]": "{]}",
    # "'":"{'}",
    "<": "\\textless{}",
    ">": "\\textgreater{}",
}
# Use to identify URLs in the Display Link of a campaign
URL_ID = ["http://", "https://", "hxxp://", "hxxps://", "www"]

BEHAVIORS = ["Fear", "Duty_Obligation", "Curiosity", "Greed"]

# Group wording
GROUP_TEMPLATE = (
    "CISA divided the {:,} email addresses that {} provided into {} groups."
)
SUB_GROUP_TEMPLATE = "Group {} had {:,} addresses and received levels {}. "
NUM_WORDS = ["zero", "one", "two", "three", "four", "five", "six"]

CLOSING_REPORTING = (
    "There were {} users who reported the suspicious "
    "level {} email to {}'s IT helpdesk ({} percent "
    "report rate) and {} users who reported the level "
    "{} email. The level {}, and {} "
    "deceptive email by indicator count, with the subject “{}” "
    "had the greatest number of user reports ({}), a reporting "
    "rate of {} percent, and a {} second {} "
    "between first report and first click. The {} "
    "deceptive level {} email with the subject “{}” had the largest "
    "lead time between reporting and clicking ({})."
)


def setup_work_directory(work_dir):
    """Set up a temporary working directory."""
    file_src = os.path.join(ASSETS_DIR, MUSTACHE_FILE)
    file_dst = os.path.join(work_dir, MUSTACHE_FILE)
    shutil.copyfile(file_src, file_dst)
    # copy static assets
    dir_dst = os.path.join(work_dir, ASSETS_DIR_DST)
    shutil.copytree(ASSETS_DIR, dir_dst)


def dict_formater(dictionary, labels):
    """Set dictionary formatting for report merging."""
    # Loops through each of the Levels in main dictionary
    for numLevel in dictionary["Level"].keys():

        # Loops through each of the Levels sub dictionary
        for word2, replacement in dictionary["Level"][numLevel].items():
            # Checks if the current field is user click summary to loop through 2nd sub dictionary

            if word2 == "Start_Date":  # Converts Start Date to ET
                replacement = datetime.strptime(replacement, "%m/%d/%Y %H:%M:%S")
                replacement = utc.localize(replacement)
                replacement = replacement.astimezone(localTimeZone)
                dictionary["Level-" + numLevel + "-" + word2] = replacement.strftime(
                    "%m/%d/%Y %H:%M"
                )
            elif word2 != "User_Click_Summary" and word2 != "Complexity":
                dictionary["Level-" + numLevel + "-" + word2] = replacement

            else:
                for word3, replacement3 in dictionary["Level"][numLevel][word2].items():
                    # Sets Behavior to X when present and blank string when not.
                    if word3 in BEHAVIORS:
                        if replacement3 == 1:
                            dictionary[
                                "Level-" + numLevel + "-" + word2 + "-" + word3
                            ] = "X"
                        else:
                            dictionary[
                                "Level-" + numLevel + "-" + word2 + "-" + word3
                            ] = ""
                    else:
                        dictionary[
                            "Level-" + numLevel + "-" + word2 + "-" + word3
                        ] = replacement3

    del dictionary["Level"]

    # flattens the label dicts if the label flag is set when calling.
    if labels:
        for label, replacement in dictionary["Labels"].items():
            for label_key, label_value in dictionary["Labels"][label].items():
                if label_key not in ["1", "2", "3", "4", "5", "6"]:
                    dictionary["Labels-" + label + "-" + label_key] = label_value
                else:
                    for level_key, level_value in dictionary["Labels"][label][
                        label_key
                    ].items():
                        dictionary[
                            "Labels-" + label + "-" + label_key + "-" + level_key
                        ] = level_value

        del dictionary["Labels"]

    for recon_key, recon_value in dictionary["Email_Recon"].items():
        dictionary["Email_Recon-" + recon_key] = recon_value

    del dictionary["Email_Recon"]

    dictionary["complexity-behavior-fear-Click_Rate"] = dictionary["complexity"][
        "behavior"
    ]["fear - True"]["click_rate"]
    dictionary["complexity-sender-internal-Generic-Click_Rate"] = dictionary[
        "complexity"
    ]["sender"]["internal - Generic"]["click_rate"]

    # Remove un-needed dictionaries to prevent mail merge errors.
    if bool(dictionary["Unique_Click_Timeline"]):
        dictionary["Unique_Click_Timeline-60_min"] = round(
            dictionary["Unique_Click_Timeline"]["60 minutes"]
        )
    else:
        dictionary["Unique_Click_Timeline-60_min"] = 0
    del dictionary["Unique_Click_Timeline"]
    del dictionary["complexity"]

    # Converts values to strings.
    for key, value in dictionary.items():
        if key not in ["figures", "User_Report_Provided"]:
            if isinstance(dictionary[key], int) or isinstance(dictionary[key], float):
                dictionary[key] = "{:,}".format(value)
            else:
                dictionary[key] = str(
                    value
                )  # FIXME possible change this to exclude bools?

    return dictionary


def latex_string_prep(temp_string):
    """Clean strings of latex sensitive characters."""
    for latex_key, latex_value in LATEX_ESCAPE_MAP.items():
        temp_string = temp_string.replace(latex_key, latex_value)

    return temp_string


def group_text_builder(reportData):
    """Build group text statement."""
    first_line = GROUP_TEMPLATE.format(
        reportData["Num_Users"], reportData["Acronym"], len(reportData["Groups"])
    )

    second_line = ""

    for group_num in reportData["Groups"].keys():
        # TODO Make change to include "and"s and ","s
        second_line += SUB_GROUP_TEMPLATE.format(
            group_num,
            reportData["Groups"][group_num]["Num_Emails"],
            reportData["Groups"][group_num]["Campaigns"],
        )

    return "{} {}".format(first_line, second_line)


def manualData_processor(dataFile, manualFile):
    """Process manual data into data file."""
    success = True
    # total_report_time = (
    #    0  # Hold total number of seconds to find the average report time
    # )

    print("\tLoading Manual Data from " + manualFile + "...")

    with open(dataFile, encoding="utf-8") as f:
        reportData = json.load(f)

    # Tries to open manual data file
    try:
        f = open(manualFile)
    except IOError:
        print("\tERROR- Manual Data File not found: " + manualFile)
        sys.exit(1)
    else:

        manualData = json.load(f)
        f.close()

        # Holds if user reports were provided
        userReportProvided = manualData["User_Report_Provided"]
        reportData["User_Report_Provided"] = manualData["User_Report_Provided"]

        # Adds the group break down string
        reportData["Group_String"] = group_text_builder(reportData)

        reportData["Emails_Per_User"] = NUM_WORDS[int(6 / len(reportData["Groups"]))]

        # creates list of first report times.
        if userReportProvided:
            firstReportTimes = []

        for key, value in manualData.items():
            if key == "Email_Recon":

                reportData["Email_Recon"] = dict()

                for recon_name, recon_value in manualData["Email_Recon"].items():
                    reportData["Email_Recon"][recon_name] = recon_value

                reportData["Email_Recon"]["Match_Rate"] = round(
                    reportData["Email_Recon"]["Email_List_Match"]
                    / reportData["Num_Users"]
                    * 100,
                    2,
                )

            elif key == "Level":
                for numLevel in manualData["Level"].keys():
                    reportData["Level"][numLevel]["Description"] = manualData["Level"][
                        numLevel
                    ]["Description"]

                    reportData["Level"][numLevel]["Key_Characteristics"] = manualData[
                        "Level"
                    ][numLevel]["Key_Characteristics"]

                    if "Url" in manualData["Level"][numLevel].keys():
                        reportData["Level"][numLevel]["Url"] = manualData["Level"][
                            numLevel
                        ]["Url"]

                    if "From_Address" in manualData["Level"][numLevel].keys():
                        reportData["Level"][numLevel]["From_Address"] = manualData[
                            "Level"
                        ][numLevel]["From_Address"]

                    if "Display_Link" in manualData["Level"][numLevel].keys():
                        reportData["Level"][numLevel]["Display_Link"] = '"{}"'.format(
                            manualData["Level"][numLevel]["Display_Link"].replace(
                                ", ", '", "'
                            )
                        )
                    else:
                        reportData["Level"][numLevel]["Display_Link"] = ""

                    if reportData["Level"][numLevel]["Time_To_First_Click_TD"] == 0:
                        reportData["Level"][numLevel]["Time-To-First-Click"] = "N/A"
                    else:
                        reportData["Level"][numLevel][
                            "Time-To-First-Click"
                        ] = format_timedelta_to_HHMMSS(
                            reportData["Level"][numLevel]["Time_To_First_Click_TD"]
                        )

                    if userReportProvided:
                        reportData["Level"][numLevel]["User_Reports"] = manualData[
                            "Level"
                        ][numLevel]["User_Reports"]

                        if (
                            manualData["Level"][numLevel]["Time_Of_First_Report"]
                            != "N/A"
                            and manualData["Level"][numLevel]["Time_Of_First_Report"]
                            != ""
                        ):
                            reportData["Level"][numLevel][
                                "Time_To_First_Report"
                            ] = manualData["Level"][numLevel]["Time_Of_First_Report"]

                            if datetime.strptime(
                                manualData["Level"][numLevel]["Time_Of_First_Report"],
                                "%m/%d/%Y %H:%M",
                            ) < datetime.strptime(
                                reportData["Level"][numLevel]["Start_Date"],
                                "%m/%d/%Y %H:%M:%S",
                            ):
                                raise Exception(
                                    f"Campaign {numLevel}'s Time Of First Report is before Campaign start date."
                                )

                            reportData["Level"][numLevel]["Time_To_First_Report_TD"] = (
                                datetime.strptime(
                                    manualData["Level"][numLevel][
                                        "Time_Of_First_Report"
                                    ],
                                    "%m/%d/%Y %H:%M",
                                )
                                - datetime.strptime(
                                    reportData["Level"][numLevel]["Start_Date"],
                                    "%m/%d/%Y %H:%M:%S",
                                )
                            ).total_seconds()

                            reportData["Level"][numLevel]["Time_To_First_Report"] = (
                                time_to_string(
                                    reportData["Level"][numLevel][
                                        "Time_To_First_Report_TD"
                                    ]
                                )
                                .replace("hour", "hr")
                                .replace("minute", "min")
                                .replace("seconds", "sec")
                            )

                            firstReportTimes.append(
                                reportData["Level"][numLevel]["Time_To_First_Report_TD"]
                            )

                        else:
                            reportData["Level"][numLevel]["Time_To_First_Report"] = None
                            reportData["Level"][numLevel]["Time_To_First_Report_TD"] = 0
                            firstReportTimes.append(
                                reportData["Level"][numLevel]["Time_To_First_Report_TD"]
                            )

                        # Calculates User Report Rate
                        reportData["Level"][numLevel]["Report-Rate"] = round(
                            reportData["Level"][numLevel]["User_Reports"]
                            / reportData["Level"][numLevel]["Emails_Sent_Attempted"]
                            * 100,
                            2,
                        )  # TODO Check here for problems with User Report Rate

                        # Calculates the Report Ratio
                        if reportData["Level"][numLevel]["User_Clicks"] == 0:
                            reportData["Level"][numLevel]["Report_Ratio"] = reportData[
                                "Level"
                            ][numLevel]["User_Reports"]
                        else:
                            reportData["Level"][numLevel]["Report_Ratio"] = round(
                                reportData["Level"][numLevel]["User_Reports"]
                                / reportData["Level"][numLevel]["User_Clicks"],
                                2,
                            )

                        (
                            reportData["Level"][numLevel]["Time_Gap"],
                            reportData["Level"][numLevel]["Time_Gap_TD"],
                            reportData["Level"][numLevel]["Gap_Type"],
                        ) = get_time_gap(
                            reportData["Level"][str(numLevel)][
                                "Time_To_First_Report_TD"
                            ],
                            reportData["Level"][str(numLevel)][
                                "Time_To_First_Click_TD"
                            ],
                        )

                    else:
                        reportData["Level"][str(numLevel)]["User_Reports"] = "N/A"
                        reportData["Level"][str(numLevel)][
                            "Time_To_First_Report"
                        ] = "N/A"
                        reportData["Level"][str(numLevel)][
                            "Time_To_First_Report_TD"
                        ] = 0
                        if reportData["Level"][numLevel]["Time_To_First_Click_TD"]:

                            reportData["Level"][str(numLevel)]["Gap_Type"] = "(LAG)"
                        else:
                            reportData["Level"][str(numLevel)]["Time_Gap"] = "N/A"
                            reportData["Level"][str(numLevel)]["Gap_Type"] = ""

                        # Calculates User Report Rate
                        reportData["Level"][str(numLevel)]["Report-Rate"] = "N/A"
                        reportData["Level"][str(numLevel)]["Report_Ratio"] = "N/A"

                        # Build out the time Gap information
                        reportData["Level"][str(numLevel)][
                            "Time_To_First_Report_TD"
                        ] = 0

            elif key == "Customer_Setup":
                reportData["Customer_Setup"] = ""
                for entry in manualData["Customer_Setup"]:
                    reportData["Customer_Setup"] += "\\item {} ".format(
                        latex_string_prep(entry)
                    )

            else:
                reportData[key] = value

        # Calculations if the user reports are provided.
        if userReportProvided:
            # Calculates the Report Rate
            reportData["User_Report_Rate"] = round(
                reportData["Total_User_Reports"] / reportData["Sum_Emails_Sent"] * 100,
                2,
            )

            # Builds out the Report Ratio
            if reportData["Sum_Unique_Clicks"] == 0:
                reportData["Report_Ratio"] = reportData["Total_User_Reports"]
            else:
                reportData["Report_Ratio"] = round(
                    reportData["Total_User_Reports"] / reportData["Sum_Unique_Clicks"],
                    2,
                )

            # Calculates geomean for Time to First Click then formats it for out put before saving it.
            firstReportTimes = list(filter(lambda a: a != 0, firstReportTimes))

            geomeans = (reduce(lambda x, y: x * y, firstReportTimes)) ** (
                1 / len(firstReportTimes)
            )
            reportData["Ave_Time_First_Report"] = time_to_string(geomeans)

        else:
            reportData["User_Report_Rate"] = "N/A"
            reportData["Report_Ratio"] = "N/A"
            reportData["Ave_Time_First_Report"] = "N/A"

        with open(
            "reportData_" + reportData["RVA_Number"] + ".json", "w", encoding="utf-8"
        ) as fp:
            json.dump(reportData, fp, indent=4)

        print(
            "\tManual Data added to "
            + "reportData_"
            + reportData["RVA_Number"]
            + ".json "
            + "..."
        )

    return success


def get_time_gap(report_td, click_td):
    """Build out the time Gap information.

    If Time to First Report is greater than  Time to first Click
    indicate that Gap is a Lag unless no clicks, then Lead.
    """
    time_gap = ""
    time_gap_td = None
    gap_type = ""

    if report_td > click_td:
        time_gap_td = report_td - click_td

        # If Time to First Click is 0 set Time_Gap to blank string.
        if click_td == 0:
            time_gap = ""
            gap_type = "(LEAD)"
        else:
            time_gap = time_to_string(time_gap_td)
            gap_type = "(LAG)"

    # If time to first click is greater than Time to first Report
    # indicate that Gap is a Lead unless there are no reports, then Lag
    elif click_td > report_td:

        time_gap_td = click_td - report_td

        # If Time to First Report is 0 set Time_Gap to blank string.
        if report_td == 0:
            time_gap = ""
            gap_type = "(LAG)"

        else:
            time_gap = time_to_string(time_gap_td)
            gap_type = "(LEAD)"

    # Last possible option is if times are the same so Gap is None.
    else:
        time_gap = "None"
        gap_type = ""

    time_gap = (
        time_gap.replace("hour", "hr")
        .replace("minute", "min")
        .replace("seconds", "sec")
    )

    return time_gap, time_gap_td, gap_type


def latex_data_fields(labels, reportData):
    """Set latex control and display fields."""
    # Sets Labels true or false
    if labels:
        reportData["Labels_bool"] = "true"
    else:
        reportData["Labels_bool"] = "false"

    if reportData["User_Report_Provided"]:
        reportData["User_Report_bool"] = "true"
    else:
        reportData["User_Report_bool"] = "false"

    for level in range(1, 7):
        link_type = reportData["Level-{}-Complexity-Link_Domain".format(level)]

        if link_type == "0":
            reportData["Level-{}-Link_Type".format(level)] = "Written Out/Hover Over"
            reportData["Level-{}-Hover_Over".format(level)] = ""
            reportData["Level-{}-Display_Link".format(level)] = ""

        else:
            reportData["Level-{}-Link_Type".format(level)] = "Spoofed/Hidden"
            reportData[
                "Level-{}-Hover_Over".format(level)
            ] = "\\newline \\textbf{Hover Over:} \\newline"

            display_link = reportData["Level-{}-Display_Link".format(level)]
            if any(url_item in display_link for url_item in URL_ID):
                display_link = '"\\nolinkurl{' + display_link.replace('"', "") + '}"'
                reportData["Level-{}-Display_Link".format(level)] = "{} {}".format(
                    "\\newline\\indent",
                    display_link.replace("http", "hxxp").replace(":", "[:]"),
                )
            else:
                reportData["Level-{}-Display_Link".format(level)] = "{} {}".format(
                    "\\newline\\indent", display_link
                )

    return reportData


def latex_dict_prep(dictionary):
    """Prepare dictionary for latex."""
    del dictionary["figures"]
    for data_key in dictionary.keys():
        if not any(exclude in data_key for exclude in LATEX_EXCLUDE_ESCAPE):
            for latex_key, latex_value in LATEX_ESCAPE_MAP.items():
                try:
                    dictionary[data_key] = dictionary[data_key].replace(
                        latex_key, latex_value
                    )
                except AttributeError as e:
                    print("Attribute error with {}: {}".format(data_key, e))
                    pass
            if "url" in data_key.lower():
                dictionary[data_key] = (
                    "\\nolinkurl{"
                    + dictionary[data_key].replace("tt", "xx").replace(":", "[:]")
                    + "}"
                )

    return dictionary


def latex_builder(assessment_id, dataFile, labels, template):
    """Compile latex report."""
    with open(dataFile, encoding="utf-8") as f:
        reportData = json.load(f)

    reportData["Report_Date"] = datetime.today().strftime("%B %d, %Y")

    reportData = dict_formater(reportData, labels)

    reportData = latex_data_fields(labels, reportData)

    reportData = latex_dict_prep(reportData)

    template = codecs.open(template, "r", encoding="utf-8").read()

    # renderer = pystache.Renderer(string_encoding="utf-8")

    r = pystache.render(template, reportData)

    r = html.unescape(r)

    with codecs.open(assessment_id + "_report.tex", "w", encoding="utf-8") as output:
        output.write(r)

    for _ in range(1, 3):
        # Bandit complains about the use of subprocess, but this
        # should be safe as this will only run "xelatex". The command
        # is hardcoded, which limits the ease of abuse. It could still be
        # possible that the assessment_id is provided in a way t0 allow
        # execution of unwanted commands. Also used in compiler.xelatex.py
        # FIXME Find a better method than subprocess to run the compiler.
        subprocess.call(["xelatex", assessment_id + "_report.tex"])  # nosec

    if reportData["No_Clicks"] == "true":
        print("**** WARNING! ****")
        print(
            "**** There were 0 clicks in this assessment, adjust closing manually!****"
        )
        print("**** WARNING! ****")


def assessment_metrics(dataFile):
    """Build the assessment metric file."""
    with open(dataFile, encoding="utf-8") as f:
        reportData = json.load(f)

    dropped_keys = [
        "Org_Name",
        "Acronym",
        "POC_Name",
        "POC_Email",
        "FED_Name",
        "Target_Domain",
        "figures",
        "FED_Email",
    ]

    reportData["_id"] = reportData.pop("RVA_Number")

    for key in dropped_keys:
        reportData.pop(key, None)

    for level in reportData["Level"]:
        reportData["Level"][level].pop("Url", None)

    with open(
        "assessmentMetrics_" + reportData["_id"] + ".json", "w", encoding="utf-8"
    ) as fp:
        json.dump(reportData, fp, indent=4)

    print(
        "\tAssessment Metrics place in "
        + "assessmentMetrics_"
        + reportData["_id"]
        + ".json "
        + "..."
    )

    return True


def main():
    """Set up logging, connect to API, remove assessment data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    success = True

    # --- Initializes the files ---
    data_file = "reportData_" + args["ASSESSMENT_ID"] + ".json"

    manual_data_file = "manualData_" + args["ASSESSMENT_ID"] + ".json"

    # Tries to see if report data file is present.
    try:
        # Checks for report data file
        f = open(data_file)
        f.close()

        # Checks for template file.
        f = open(manual_data_file)
        f.close()
    except IOError as e:
        print("ERROR- File not found: " + e.filename)
        success = False
    else:
        if args["--manual"]:
            manualData_processor(data_file, manual_data_file)
        elif args["--graph"]:
            manualData_processor(data_file, manual_data_file)
            success = graph_builder(args["ASSESSMENT_ID"], args["--labels"])

        elif args["--Metrics"]:
            manualData_processor(data_file, manual_data_file)
            success = assessment_metrics(data_file)

        else:
            manualData_processor(data_file, manual_data_file)

            graph_builder(args["ASSESSMENT_ID"], args["--labels"])

            closing_builder(args["ASSESSMENT_ID"])

            # Moves supporting files.

            # create a working directory
            original_working_dir = os.getcwd()

            temp_working_dir = tempfile.mkdtemp()

            os.chdir(temp_working_dir)

            # setup the working directory
            setup_work_directory(temp_working_dir)
            org_manual_data_file = os.path.join(original_working_dir, manual_data_file)
            shutil.copy(org_manual_data_file, manual_data_file)

            # Moves supporting files.
            org_data_filename = os.path.join(original_working_dir, data_file)
            shutil.copy(org_data_filename, data_file)

            for folder in TO_COPY:
                dir_src = os.path.join(original_working_dir, folder)
                dir_dst = os.path.join(temp_working_dir, "{}".format(folder))
                shutil.copytree(dir_src, dir_dst)

            latex_builder(
                args["ASSESSMENT_ID"], data_file, args["--labels"], MUSTACHE_FILE
            )

            # revert working directory
            os.chdir(original_working_dir)

            src_report_filename = os.path.join(
                temp_working_dir, args["ASSESSMENT_ID"] + "_report.pdf"
            )
            src_data_filename = os.path.join(temp_working_dir, data_file)
            src_tex_filename = os.path.join(
                temp_working_dir, args["ASSESSMENT_ID"] + "_report.tex"
            )

            dest_report_filename = args["ASSESSMENT_ID"] + "_report.pdf"
            dest_tex_filename = args["ASSESSMENT_ID"] + "_report.tex"

            shutil.move(src_report_filename, dest_report_filename)
            shutil.move(src_data_filename, data_file)
            if args["--editable"]:

                shutil.move(src_tex_filename, dest_tex_filename)

                asset_src = os.path.join(temp_working_dir, "assets")

                if os.path.exists("assets") and os.path.isdir("assets"):
                    shutil.rmtree("assets")

                shutil.copytree(asset_src, "assets")

            shutil.rmtree(temp_working_dir)

            print(
                "Completed, Please see report: {}_report.pdf".format(
                    args["ASSESSMENT_ID"]
                )
            )

    if success:
        return 0

    return 1
