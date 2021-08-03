"""Graphs."""

__all__ = [
    "breakdown_multiple_clicks_by_level",
    "click_rate_based_deception_indicators",
    "clicking_user_timeline",
    "count_unique_clickes_by_office_per_level",
    "count_unique_clicks_by_level_per_office",
    "graph_builder",
    "perc_total_unique_clicks_belong_office_by_level",
    "percentage_office_clicked_by_level",
    "time_first_click_report",
    "time_ticks",
    "timeline_unique_user_clicks_all_levels",
    "unique_total_click_report_results_by_level",
    "unique_user_click_rate_vs_report_rate_per_level_deception",
]

# Standard Python Libraries
from datetime import timedelta
import json
import os
import textwrap

# Third-Party Libraries
from adjustText import adjust_text
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Set Colors
BLUE = "#3C679D"
DARK_RED = "#A03D3B"
GREEN = "#7E9B45"
PURPLE = "#664E84"
LIGHT_BLUE = "#398DA6"
ORANGE = "#D67836"


def graph_builder(assessment_id, labels):
    """Build the graphs."""
    success = True
    data_file = "reportData_" + assessment_id + ".json"

    if not os.path.exists("figures"):
        try:
            os.mkdir("figures")
        except OSError:
            print("\tERROR- Creation of the directory figures failed")
            success = False

    if success:
        print("\tGenerating Graphs for " + assessment_id + " Report...")
        # Loads report data into a dictionary from json file.
        with open(data_file) as out_file:
            report_data = json.load(out_file)
        report_data["figures"] = list()

        COLOR = "#101010"
        mpl.rcParams["text.color"] = COLOR
        mpl.rcParams["axes.labelcolor"] = COLOR
        mpl.rcParams["xtick.color"] = COLOR
        mpl.rcParams["ytick.color"] = COLOR

        unique_user_click_rate_vs_report_rate_per_level_deception(report_data)
        timeline_unique_user_clicks_all_levels(report_data)
        time_first_click_report(report_data)
        click_rate_based_deception_indicators(report_data)
        unique_total_click_report_results_by_level(report_data)
        breakdown_multiple_clicks_by_level(report_data)
        clicking_user_timeline(report_data)

        if labels:
            count_unique_clickes_by_office_per_level(report_data)
            percentage_office_clicked_by_level(report_data)
            count_unique_clicks_by_level_per_office(report_data)
            perc_total_unique_clicks_belong_office_by_level(report_data)

        with open("reportData_" + report_data["RVA_Number"] + ".json", "w") as fp:
            json.dump(report_data, fp, indent=4)

    return success


def time_ticks(in_val, _):
    """Time tick interval logic to return string."""
    return str(timedelta(seconds=int(in_val))).split(".")[0]


# Unique User Click Rate vs. Report Rate per Level of Deception
def unique_user_click_rate_vs_report_rate_per_level_deception(report_data):
    """Handle unique user click rate vs report rate logic."""
    # data to plot
    n_groups = 6
    click_rate = list()
    report_rate = list()
    ratio = list()
    user_report_provided = report_data["User_Report_Provided"]

    # Pulls the Click Rate from the Report Data
    for numlevel, value1 in report_data["Level"].items():
        click_rate.append(report_data["Level"][numlevel]["Click_Rate"])

    if user_report_provided:

        # Calculates the Report Rate from the Report Data
        for numlevel, value1 in report_data["Level"].items():
            report_rate.append(
                round(
                    report_data["Level"][numlevel]["User_Reports"]
                    / report_data["Level"][numlevel]["Emails_Sent_Attempted"]
                    * 100,
                    2,
                )
            )

        # Builds the report vs click ratio
        for numlevel, value1 in report_data["Level"].items():
            if report_data["Level"][numlevel]["User_Clicks"] == 0:
                ratio.append(report_data["Level"][numlevel]["User_Reports"])
            else:
                ratio.append(
                    round(
                        report_data["Level"][numlevel]["User_Reports"]
                        / report_data["Level"][numlevel]["User_Clicks"],
                        1,
                    )
                )

    else:
        # Sets the Report Rate to 0 when user reports are not provided.
        for numlevel, value1 in report_data["Level"].items():
            report_rate.append(0)

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.4

    # Sets x and y labels.
    plt.xlabel("Deception Level")
    plt.xticks(index + bar_width / 2, ("1", "2", " 3", "4", "5", "6"))

    # Establishes the unique click rate bars
    rects1 = plt.bar(
        index, click_rate, bar_width, color=BLUE, label="Unique Click Rate"  # blue
    )
    rects1_lable_buffer = plt.bar(
        index, 3, bar_width, bottom=click_rate, edgecolor="none", color="none"
    )

    # Establishes the User Report Rate bars
    rects2 = plt.bar(
        index + bar_width,
        report_rate,
        bar_width,
        color=DARK_RED,  # dark red
        label="User Report Rate",
    )
    rects2_label_buffer = plt.bar(
        index + bar_width,
        3,
        bar_width,
        bottom=report_rate,
        edgecolor="none",
        color="none",
    )

    # Lines xtick labels to center
    for tick in ax_val.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("Rate Percentages")
    ax_val.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    if user_report_provided:
        if max(click_rate) > max(report_rate):
            percent_lim = max(click_rate) + 10
        else:
            percent_lim = max(report_rate) + 10
    else:
        percent_lim = max(click_rate) + 10

    if percent_lim > 100:
        ax_val.set_ylim(0, 100)
    else:
        ax_val.set_ylim(0, percent_lim)

        # Add counts above the two bar graphs
    if user_report_provided:
        for rect in rects1 + rects2:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "%.2f" % height + "%",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    else:
        for rect in rects1:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "%.2f" % height + "%",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        for rect in rects2:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "N/A",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    if user_report_provided and max(ratio) <= 2.0:
        plt.legend(
            loc="upper center", bbox_to_anchor=(0.30, -0.2), frameon=False, ncol=2
        )

        ratio_x = np.arange(n_groups)

        # Plots the ratio
        axes2 = plt.twinx()
        axes2.plot(ratio_x, ratio, color="#8DB04A", label="Reporting Ratio")
        axes2.set_ylim(-2.2, 2.2)
        axes2.get_yaxis().set_visible(False)

        ratio_text = [
            axes2.text(
                x_val, ratio_val + 0.05, ratio_val, ha="center", va="bottom", fontsize=8
            )
            for x_val, ratio_val in zip(ratio_x, ratio)
        ]

        to_avoid = rects1_lable_buffer + rects2_label_buffer
        adjust_text(
            ratio_text,
            add_objects=to_avoid,
            only_move={"points": "y", "text": "y", "objects": "y"},
            va="top",
            autoalign="y",
        )

        # Adjusts the legend location
        plt.legend(
            loc="upper center", bbox_to_anchor=(0.78, -0.2), frameon=False, ncol=3
        )

        # Hide the right and top spines
        axes2.spines["right"].set_visible(False)
        axes2.spines["top"].set_visible(False)

    else:
        plt.legend(
            loc="upper center", bbox_to_anchor=(0.50, -0.2), frameon=False, ncol=2
        )

    ax_val._val.spines["right"].set_visible(False)
    ax_val._val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        "figures/UniqueUserClickRateVsReportRatePerLevelDeception.png",
        bbox_inches="tight",
    )
    report_data["figures"].append(1)


# Time line of Unique User Clicks Across All Levels
def timeline_unique_user_clicks_all_levels(report_data):
    """Timeline unique clicks logic."""
    # data to Plot
    time_frame = list(report_data["Unique_Click_Timeline"].keys())[: 10 or None]

    n_groups = len(time_frame)

    if bool(report_data["Unique_Click_Timeline"]):
        intervalpercent = list(report_data["Unique_Click_Timeline"].values())[
            : 10 or None
        ]
    else:
        intervalpercent = [0] * n_groups

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.7

    # Sets x and y labels.
    plt.xticks(index, time_frame, rotation=45, fontsize=8, ha="right")

    # Establishes the interval bars
    rects1 = plt.bar(
        index, intervalpercent, bar_width, color=BLUE, label="Time Intervals"  # blue
    )

    # Lines xtick labels to center
    for tick in ax_val.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("%" + " of Unique User Clicks")
    ax_val.set_ylim(0, 110)
    ax_val.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    plt.xlabel("Time Intervals")

    # Add counts above the bar graphs
    for rect in rects1:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            "%.0f" % height + "%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig("figures/TimelineUniqueUserClicksAllLevels.png", bbox_inches="tight")
    report_data["figures"].append(2)


# Time to First Click (HH:MM:SS)
def time_first_click_report(report_data):
    """Time to first click logic."""
    # data to plot
    n_groups = 6
    first_clicks = list()
    first_report = list()
    user_report_provided = report_data["User_Report_Provided"]

    # Pulls the first clicks from the Report Data
    for numlevel, _ in report_data["Level"].items():
        first_clicks.append(report_data["Level"][numlevel]["Time_To_First_Click_TD"])
        if user_report_provided:
            first_report.append(
                report_data["Level"][numlevel]["Time_To_First_Report_TD"]
            )
        else:
            first_report.append(0)

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.45

    # Sets x and y labels.
    plt.xlabel("Campaign Week")
    plt.xticks(index + bar_width / 2, ("1", "2", "3", "4", "5", "6"))

    # Establishes the interval bars
    rects1 = plt.bar(
        index, first_clicks, bar_width, color=BLUE, label="Time to First Click"  # blue
    )

    rects2 = plt.bar(
        index + bar_width,
        first_report,
        bar_width,
        color=DARK_RED,  # Dark Red
        label="Time to First Report",
    )

    # Lines xtick labels to center
    for tick in ax_val.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    # Sets max y lim to 1.08 times the longest time
    all_time = first_clicks + first_report
    time_spread = max(all_time) - min(all_time)
    if time_spread > 86400:
        ax_val.set_ylim(-1000, max(all_time) * 1.08)
    else:
        ax_val.set_ylim(0, max(all_time) * 1.08)

    # Hide y-axis value but show label.
    ax_val.set_yticklabels([])
    plt.ylabel("Elapsed Time")

    # Add counts above the bar graphs
    for rect in rects1 + rects2:
        height = np.float64(rect.get_height())
        if height != 0:
            hours = height // 3600
            minutes = (height % 3600) // 60
            seconds = height % 60

            str_val = "{:02d}:{:02d}:{:02d}".format(
                int(hours), int(minutes), int(seconds)
            )
        else:
            str_val = "N/A"

        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            str_val,
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=45,
        )

    # Hide the right and top spines
    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.legend(loc="upper center", bbox_to_anchor=(0.50, -0.2), frameon=False, ncol=2)

    plt.tight_layout()
    plt.savefig("figures/TimeFirstClickReport.png", bbox_inches="tight")
    report_data["figures"].append(3)


# Click Rates Based on Deception Indicators
def click_rate_based_deception_indicators(report_data):
    """Click rate indicator logic."""
    indicators = dict()
    click_rate = list()
    click_rates = list()

    indicators["behavior"] = dict()
    indicators["behavior"]["indicators"] = [
        "Greed",
        "Fear",
        "Curiosity",
        "Duty or Obligation",
    ]
    indicators["behavior"]["click_rates"] = list()

    indicators["relevancy"] = dict()
    indicators["relevancy"]["indicators"] = ["Public News", "Organization"]
    indicators["relevancy"]["click_rates"] = list()

    indicators["sender"] = dict()
    indicators["sender"]["indicators"] = [
        "Authoritative - Federal/High-Level",
        "Authoritative - Local/Mid-Level",
        "Internal - Spoofed Specific",
        "Internal - Spoofed Generic",
        "External - Spoofed/Plausible",
        "External - Unknown",
    ]
    indicators["sender"]["click_rates"] = list()

    indicators["appearance"] = dict()
    indicators["appearance"]["indicators"] = [
        "Graphics - Spoofed or HTML",
        "Link/Domain - Spoofed or Hidden",
        "Link/Domain - Fake",
        "Proper Grammar",
        "Decent Grammar",
        "Poor Grammar",
    ]
    indicators["appearance"]["click_rates"] = list()

    for category, _ in report_data["complexity"].items():
        for indicator_key, _ in report_data["complexity"][category].items():
            indicators[category]["click_rates"].append(
                report_data["complexity"][category][indicator_key]["click_rate"]
            )
            click_rate.append(
                report_data["complexity"][category][indicator_key]["click_rate"]
            )

    percent_max = max(click_rate) + 1

    for _ in range(18):
        click_rates.append(report_data["Click_Rate"])

    plt.figure(figsize=(7, 10))

    gridspec.GridSpec(9, 1)

    plt.xticks([])
    plt.yticks([])

    # Builds out Behavior Plot
    behavior_plot = plt.subplot2grid(
        (9, 1), (0, 0), colspan=1, rowspan=2
    )  # subplot(4,1,1)
    behavior_plot.set_ylabel("Behavior", fontsize=10, labelpad=87, fontweight="bold")
    behavior_plot.set_xlim(0, percent_max)
    behavior_plot.barh(
        np.arange(4),
        indicators["behavior"]["click_rates"],
        align="center",
        color="#755998",
    )
    behavior_plot.set_yticks(np.arange(4))
    behavior_plot.set_yticklabels(indicators["behavior"]["indicators"], fontsize=10)
    behavior_plot.invert_yaxis()
    behavior_plot.spines["right"].set_visible(False)
    behavior_plot.spines["bottom"].set_visible(False)
    behavior_plot.xaxis.set_ticklabels([])
    behavior_plot.xaxis.grid()  # Vertical lines
    behavior_plot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds behavior labels
    for item, val in enumerate(indicators["behavior"]["click_rates"]):
        behavior_plot.text(val + 0.1, item, str(val) + "%", va="center", fontsize=10)

    # Plots the red Click Rate Line
    axes2 = plt.twinx()
    axes2.plot(click_rates, np.arange(18), color="red", label="Click Rate")
    axes2.get_yaxis().set_visible(False)
    axes2.get_xaxis().set_visible(False)
    axes2.spines["right"].set_visible(False)
    axes2.spines["top"].set_visible(False)
    axes2.spines["bottom"].set_visible(False)
    plt.margins(0)

    # Builds out Relevancy Plot
    relevancy_plot = plt.subplot2grid(
        (9, 1), (2, 0), colspan=1, rowspan=1
    )  # subplot(4,1,2)
    relevancy_plot.set_ylabel("Relevancy", fontsize=10, labelpad=114, fontweight="bold")
    relevancy_plot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    relevancy_plot.set_xlim(0, percent_max)
    relevancy_plot.barh(
        np.arange(2),
        indicators["relevancy"]["click_rates"],
        align="center",
        color="#4576B5",
    )
    relevancy_plot.set_yticks(np.arange(2))
    relevancy_plot.set_yticklabels(indicators["relevancy"]["indicators"], fontsize=10)
    relevancy_plot.invert_yaxis()
    relevancy_plot.spines["right"].set_visible(False)
    relevancy_plot.spines["bottom"].set_visible(False)
    relevancy_plot.spines["top"].set_visible(False)
    relevancy_plot.xaxis.set_ticklabels([])
    relevancy_plot.xaxis.grid()  # Vertical lines
    relevancy_plot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds relevancy labels
    for item, val in enumerate(indicators["relevancy"]["click_rates"]):
        relevancy_plot.text(val + 0.1, item, str(val) + "%", va="center", fontsize=10)

    # Plots the red Click Rate Line
    axes2 = plt.twinx()
    axes2.plot(click_rates, np.arange(18), color="red", label="Click Rate")
    axes2.get_yaxis().set_visible(False)
    axes2.get_xaxis().set_visible(False)
    axes2.spines["right"].set_visible(False)
    axes2.spines["top"].set_visible(False)
    axes2.spines["bottom"].set_visible(False)
    plt.margins(0)

    # Builds out Sender Plot
    sender_plot = plt.subplot2grid(
        (9, 1), (3, 0), colspan=1, rowspan=3
    )  # subplot(4,1,3)
    sender_plot.set_ylabel("Sender", fontsize=10, labelpad=10, fontweight="bold")
    sender_plot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    sender_plot.set_xlim(0, percent_max)
    sender_plot.barh(
        np.arange(6),
        indicators["sender"]["click_rates"],
        align="center",
        color="#F68B3E",
    )
    sender_plot.set_yticks(np.arange(6))
    sender_plot.set_yticklabels(indicators["sender"]["indicators"], fontsize=10)
    sender_plot.invert_yaxis()
    sender_plot.spines["right"].set_visible(False)
    sender_plot.spines["bottom"].set_visible(False)
    sender_plot.spines["top"].set_visible(False)
    sender_plot.xaxis.set_ticklabels([])
    sender_plot.xaxis.grid()  # Vertical lines
    sender_plot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds sender labels
    for item, val in enumerate(indicators["sender"]["click_rates"]):
        sender_plot.text(val + 0.1, item, str(val) + "%", va="center", fontsize=10)

    # Plots the red Click Rate Line
    axes2 = plt.twinx()
    axes2.plot(click_rates, np.arange(18), color="red", label="Click Rate")
    axes2.get_yaxis().set_visible(False)
    axes2.get_xaxis().set_visible(False)
    axes2.spines["right"].set_visible(False)
    axes2.spines["top"].set_visible(False)
    axes2.spines["bottom"].set_visible(False)
    axes2.margins(0)

    # Builds out Appearance Plot
    appearance_plot = plt.subplot2grid(
        (9, 1), (6, 0), colspan=1, rowspan=3
    )  # subplot(4,1,4)
    appearance_plot.set_ylabel(
        "Appearance", fontsize=10, labelpad=11, fontweight="bold"
    )
    appearance_plot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    appearance_plot.set_xlim(0, percent_max)
    appearance_plot.barh(
        np.arange(6),
        indicators["appearance"]["click_rates"],
        align="center",
        color="#B7B7B7",
    )
    appearance_plot.set_yticks(np.arange(6))
    appearance_plot.set_yticklabels(indicators["appearance"]["indicators"], fontsize=10)
    appearance_plot.invert_yaxis()
    appearance_plot.spines["right"].set_visible(False)
    appearance_plot.spines["top"].set_visible(False)
    appearance_plot.xaxis.grid()  # Vertical lines

    # adds Appearance labels
    for item, val in enumerate(indicators["appearance"]["click_rates"]):
        appearance_plot.text(val + 0.1, item, str(val) + "%", va="center", fontsize=10)

    # Plots the red Click Rate Line
    axes2 = plt.twinx()
    axes2.plot(click_rates, np.arange(18), color="red", label="Click Rate")

    axes2.get_yaxis().set_visible(False)
    axes2.get_xaxis().set_visible(False)
    axes2.spines["right"].set_visible(False)

    axes2.spines["right"].set_visible(False)
    axes2.spines["top"].set_visible(False)
    axes2.spines["bottom"].set_visible(False)
    axes2.margins(0)

    # ----- Currently does not put the label in the correct spot each time.
    plt.savefig("figures/ClickRateBasedDeceptionIndicators.png", bbox_inches="tight")
    report_data["figures"].append(4)


# Unique Click, Total Click, and Report Results by Level
def unique_total_click_report_results_by_level(reportData):
    """Handle Unique total click report results logic."""
    # data to plot
    n_groups = 6
    unique_clicks = list()
    total_clicks = list()
    user_reports = list()
    user_report_provided = reportData["User_Report_Provided"]

    # Pulls the Unique Clicks from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        unique_clicks.append(reportData["Level"][numlevel]["User_Clicks"])

    # Pulls the Total Clicks from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        total_clicks.append(reportData["Level"][numlevel]["Total_Clicks"])

    if user_report_provided:
        # Pulls the Report Rate from the Report Data
        for numlevel, value1 in reportData["Level"].items():
            user_reports.append(reportData["Level"][numlevel]["User_Reports"])
    else:
        # Sets the Report Rate to 0
        for numlevel, value1 in reportData["Level"].items():
            user_reports.append(0)

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.3

    # Sets x and y labels.
    plt.xlabel("Deception Level")

    plt.xticks(index + bar_width, ("1", "2", " 3", "4", "5", "6"))

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Establishes the unique clicks bars
    rects1 = plt.bar(
        index,
        unique_clicks,
        bar_width,
        edgecolor="white",
        color=BLUE,  # Blue
        label="Unique Clicks",
        align="edge",
    )

    rects2 = plt.bar(
        index + bar_width,
        total_clicks,
        bar_width,
        edgecolor="white",
        color=DARK_RED,  # Dark Red
        label="Total Clicks",
        align="edge",
    )

    # Establishes the User Reports bars
    rects3 = plt.bar(
        index + (bar_width * 2),
        user_reports,
        bar_width,
        edgecolor="white",
        color=GREEN,  # Green
        label="User Reports",
        align="edge",
    )

    # Lines xtick labels to center
    for tick in ax_val.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("# of Clicks")

    # Add counts above the two bar graphs
    if user_report_provided:
        for rect in rects1 + rects2 + rects3:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                height,
                ha="center",
                va="bottom",
                fontsize=8,
            )
    else:
        for rect in rects1 + rects2:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                height,
                ha="center",
                va="bottom",
                fontsize=8,
            )
        for rect in rects3:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "N/A",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, ncol=3)

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/UniqueTotalClickReportResultsByLevel.png", bbox_inches="tight")
    reportData["figures"].append(5)


# Breakdown of Multiple Clicks by Level
def breakdown_multiple_clicks_by_level(report_data):
    """Breakdown clicks by level logic."""
    # data to plot
    n_groups = 6
    one_click = list()
    two_3_clicks = list()
    four_5_clicks = list()
    six_10_clicks = list()
    more_10_clicks = list()

    # Pulls the number of clikers that clicked onces from the Report Data
    for num_level, _ in report_data["Level"].items():
        one_click.append(
            report_data["Level"][num_level]["User_Click_Summary"]["1 time"]
        )

    # Pulls the number of clikers that clicked 2 to 3 times from the Report Data
    for num_level, _ in report_data["Level"].items():
        two_3_clicks.append(
            report_data["Level"][num_level]["User_Click_Summary"]["2-3 times"]
        )

    # Pulls the number of clikers that clicked 4 to 5 times from the Report Data
    for num_level, _ in report_data["Level"].items():
        four_5_clicks.append(
            report_data["Level"][num_level]["User_Click_Summary"]["4-5 times"]
        )

    # Pulls the number of clikers that clicked 6 to 10 times from the Report Data
    for num_level, _ in report_data["Level"].items():
        six_10_clicks.append(
            report_data["Level"][num_level]["User_Click_Summary"]["6-10 times"]
        )

    # Pulls the number of clikers that clicked 6 to 10 times from the Report Data
    for num_level, _ in report_data["Level"].items():
        more_10_clicks.append(
            report_data["Level"][num_level]["User_Click_Summary"][">10 times"]
        )

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.17

    # Establishes the unique clicks bars
    rects1 = plt.bar(
        index,
        one_click,
        bar_width,
        edgecolor="white",
        color="#4576B5",  # Blue
        label="1 Click",
        align="edge",
    )

    rects2 = plt.bar(
        index + bar_width,
        two_3_clicks,
        bar_width,
        edgecolor="white",
        color="#B84644",  # Dark Red
        label="2-3 Clicks",
        align="edge",
    )

    rects3 = plt.bar(
        index + bar_width * 2,
        four_5_clicks,
        bar_width,
        edgecolor="white",
        color="#91B24F",  # Green
        label="4-5 Clicks",
        align="edge",
    )

    rects4 = plt.bar(
        index + bar_width * 3,
        six_10_clicks,
        bar_width,
        edgecolor="white",
        color="#755998",  # purple
        label="6-10 Clicks",
        align="edge",
    )

    rects5 = plt.bar(
        index + bar_width * 4,
        more_10_clicks,
        bar_width,
        edgecolor="white",
        color="#42A2BF",  # Light Blue
        label=">10 Clicks",
        align="edge",
    )

    plt.ylabel("# of Unique Users")
    ax_val.set_yticks([])

    # Sets x labels.
    plt.xlabel("Deception Level")
    plt.xticks(index + bar_width * 2, ("1", "2", " 3", "4", "5", "6"))

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Add counts above the two bar graphs
    for rect in rects1 + rects2 + rects3 + rects4 + rects5:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            height,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.2),
        frameon=False,
        ncol=5,
        prop={"size": 8},
    )

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)
    ax_val.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/BreakdownMultipleClicksByLevel.png", bbox_inches="tight")
    report_data["figures"].append(6)


# Time line of Unique Clicks
def clicking_user_timeline(report_data):
    """User timeline logic."""
    # data to plot
    time_frame = list(report_data["Unique_Click_Timeline"].keys())

    n_groups = len(time_frame)

    # create plot
    _, ax_val = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)

    # Sets x labels.
    plt.xticks(index, time_frame, rotation=45, fontsize=8, ha="right")

    # plt.ylabel('Rate Percentages')
    level_one_x = list(report_data["Level"]["1"]["timeIntervalCount"].values())
    level_two_x = list(report_data["Level"]["2"]["timeIntervalCount"].values())
    level_three_x = list(report_data["Level"]["3"]["timeIntervalCount"].values())
    level_four_x = list(report_data["Level"]["4"]["timeIntervalCount"].values())
    level_five_x = list(report_data["Level"]["5"]["timeIntervalCount"].values())
    level_six_x = list(report_data["Level"]["6"]["timeIntervalCount"].values())

    for x_lists in [
        level_one_x,
        level_two_x,
        level_three_x,
        level_four_x,
        level_five_x,
        level_six_x,
    ]:

        if not x_lists:
            while len(x_lists) < n_groups:
                x_lists.append(0)
        else:
            while len(x_lists) < n_groups:
                x_lists.append(100)

    # Plots Level One
    plt.plot(index, level_one_x, color=BLUE, label="Level 1")

    # Plots Level Two
    plt.plot(index, level_two_x, color=DARK_RED, label="Level 2")

    # Plots Level Three
    plt.plot(index, level_three_x, color=GREEN, label="Level 3")

    # Plots Level Four
    plt.plot(index, level_four_x, color=PURPLE, label="Level 4")

    # Plots Level Five
    plt.plot(index, level_five_x, color=LIGHT_BLUE, label="Level 5")

    # Plots Level Six
    plt.plot(index, level_six_x, color=ORANGE, label="Level 6")

    # Adjusts the legend location
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.3),
        frameon=False,
        ncol=6,
        fontsize=8,
    )
    # Hide the right and top spines

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    ax_val.set_ylim(0, 101)
    ax_val.yaxis.set_ticks(np.arange(0, 101, 25))
    ax_val.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    ax_val.yaxis.grid()  # horizontal lines

    plt.tight_layout()
    plt.savefig("figures/ClickingUserTimeline.png", bbox_inches="tight")
    report_data["figures"].append(7)


# Clicks by Level for offices
def count_unique_clickes_by_office_per_level(report_data):
    """Count unique clicks by office per level logic."""
    # data to plot
    label_names = list()
    level_one = list()
    level_two = list()
    level_three = list()
    level_four = list()
    level_five = list()
    level_six = list()

    # pulls all office Names and each levels unique clicks.
    for label, _ in report_data["Labels"].items():
        if label != "Other":
            label_names.append(
                "\n".join(textwrap.wrap(report_data["Labels"][label]["Name"], 15))
            )
            level_one.append(report_data["Labels"][label]["1"]["Unique_Clicks"])
            level_two.append(report_data["Labels"][label]["2"]["Unique_Clicks"])
            level_three.append(report_data["Labels"][label]["3"]["Unique_Clicks"])
            level_four.append(report_data["Labels"][label]["4"]["Unique_Clicks"])
            level_five.append(report_data["Labels"][label]["5"]["Unique_Clicks"])
            level_six.append(report_data["Labels"][label]["6"]["Unique_Clicks"])

    # create plot
    _, ax_val = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    lvl1 = np.arange(len(level_one))
    lvl2 = [x_val + bar_width for x_val in lvl1]
    lvl3 = [x_val + bar_width for x_val in lvl2]
    lvl4 = [x_val + bar_width for x_val in lvl3]
    lvl5 = [x_val + bar_width for x_val in lvl4]
    lvl6 = [x_val + bar_width for x_val in lvl5]

    # Establishes the unique clicks bars
    rects1 = plt.bar(
        lvl1,
        level_one,
        bar_width,
        edgecolor="white",
        color=BLUE,  # Blue
        label="Level 1",
        align="edge",
    )

    rects2 = plt.bar(
        lvl2,
        level_two,
        bar_width,
        edgecolor="white",
        color=DARK_RED,  # Dark Red
        label="Level 2",
        align="edge",
    )

    rects3 = plt.bar(
        lvl3,
        level_three,
        bar_width,
        edgecolor="white",
        color=GREEN,  # Green
        label="Level 3",
        align="edge",
    )

    rects4 = plt.bar(
        lvl4,
        level_four,
        bar_width,
        edgecolor="white",
        color=PURPLE,  # Purple
        label="Level 4",
        align="edge",
    )

    rects5 = plt.bar(
        lvl5,
        level_five,
        bar_width,
        edgecolor="white",
        color=LIGHT_BLUE,  # Light Blue
        label="Level 5",
        align="edge",
    )

    rects6 = plt.bar(
        lvl6,
        level_six,
        bar_width,
        edgecolor="white",
        color=ORANGE,  # Orange
        label="Level 6",
        align="edge",
    )

    plt.ylabel("# of Unique Users")

    # Sets x labels.
    plt.xticks([r_val + bar_width * 3 for r_val in range(len(level_one))], label_names)

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Add counts above the two bar graphs
    for rect in rects1 + rects2 + rects3 + rects4 + rects5 + rects6:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            height,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.2),
        frameon=False,
        ncol=6,
        prop={"size": 8},
    )

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/CountUniqueClickesByOfficePerLevel.png", bbox_inches="tight")
    report_data["figures"].append(8)


# Click percent by Level for offices
def percentage_office_clicked_by_level(report_data):
    """Percentage office click by level logic."""
    # data to plot
    label_names = list()
    level_one = list()
    level_two = list()
    level_three = list()
    level_four = list()
    level_five = list()
    level_six = list()

    # pulls all office Names and each levels unique clicks.
    for label, _ in report_data["Labels"].items():
        if label != "Other":
            label_names.append(
                "\n".join(textwrap.wrap(report_data["Labels"][label]["Name"], 15))
            )
            level_one.append(report_data["Labels"][label]["1"]["Click_Rate"])
            level_two.append(report_data["Labels"][label]["2"]["Click_Rate"])
            level_three.append(report_data["Labels"][label]["3"]["Click_Rate"])
            level_four.append(report_data["Labels"][label]["4"]["Click_Rate"])
            level_five.append(report_data["Labels"][label]["5"]["Click_Rate"])
            level_six.append(report_data["Labels"][label]["6"]["Click_Rate"])

    # create plot
    _, ax_val = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    lvl1 = np.arange(len(level_one))
    lvl2 = [x_val + bar_width for x_val in lvl1]
    lvl3 = [x_val + bar_width for x_val in lvl2]
    lvl4 = [x_val + bar_width for x_val in lvl3]
    lvl5 = [x_val + bar_width for x_val in lvl4]
    lvl6 = [x_val + bar_width for x_val in lvl5]

    # Establishes the unique clicks bars
    rects1 = plt.bar(
        lvl1,
        level_one,
        bar_width,
        edgecolor="white",
        color=BLUE,  # Blue
        label="Level 1",
        align="edge",
    )

    rects2 = plt.bar(
        lvl2,
        level_two,
        bar_width,
        edgecolor="white",
        color=DARK_RED,  # Dark Red
        label="Level 2",
        align="edge",
    )

    rects3 = plt.bar(
        lvl3,
        level_three,
        bar_width,
        edgecolor="white",
        color=GREEN,  # Green
        label="Level 3",
        align="edge",
    )

    rects4 = plt.bar(
        lvl4,
        level_four,
        bar_width,
        edgecolor="white",
        color=PURPLE,  # Purple
        label="Level 4",
        align="edge",
    )

    rects5 = plt.bar(
        lvl5,
        level_five,
        bar_width,
        edgecolor="white",
        color=LIGHT_BLUE,  # Light Blue
        label="Level 5",
        align="edge",
    )

    rects6 = plt.bar(
        lvl6,
        level_six,
        bar_width,
        edgecolor="white",
        color=ORANGE,  # Orange
        label="Level 6",
        align="edge",
    )

    # plt.ylabel('Rate Percentages')
    ax_val.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    # Sets x labels.
    # plt.xlabel('Office Name')
    plt.xticks([r + bar_width * 3 for r in range(len(level_one))], label_names)

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Add counts above the two bar graphs
    for rect in rects1 + rects2 + rects3 + rects4 + rects5 + rects6:
        height = rect.get_height()
        if height > 0:
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "%.1f" % height + "%",
                ha="center",
                va="bottom",
                fontsize=6,
            )
        else:
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                1.01 * height,
                "%.f" % height + "%",
                ha="center",
                va="bottom",
                fontsize=6,
            )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.2),
        frameon=False,
        ncol=6,
        prop={"size": 8},
    )

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/PercentageOfficeClickedByLevel.png", bbox_inches="tight")
    report_data["figures"].append(9)


# Click by Office for level
def count_unique_clicks_by_level_per_office(report_data):
    """Count unique clicks by level per office."""
    # data to plot
    label_names = list()
    label_data = dict()
    label_data[1] = list()
    label_data[2] = list()
    label_data[3] = list()
    label_data[4] = list()
    label_data[5] = list()
    label_data[6] = list()

    count = 1
    # pulls all office Names and each levels unique clicks.
    for label, _ in report_data["Labels"].items():
        label_names.append(
            "\n".join(textwrap.wrap(report_data["Labels"][label]["Name"], 15))
        )
        label_data[count].append(report_data["Labels"][label]["1"]["Unique_Clicks"])
        label_data[count].append(report_data["Labels"][label]["2"]["Unique_Clicks"])
        label_data[count].append(report_data["Labels"][label]["3"]["Unique_Clicks"])
        label_data[count].append(report_data["Labels"][label]["4"]["Unique_Clicks"])
        label_data[count].append(report_data["Labels"][label]["5"]["Unique_Clicks"])
        label_data[count].append(report_data["Labels"][label]["6"]["Unique_Clicks"])
        count += 1

    # create plot
    _, ax_val = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    num_labels = len(label_names)
    label = [None] * num_labels
    color_list = [BLUE, DARK_RED, GREEN, PURPLE, LIGHT_BLUE, ORANGE]

    for num in range(num_labels):
        if num == 0:
            label[num] = np.arange(len(label_data[1]))
        else:
            label[num] = [x_val + bar_width for x_val in label[num - 1]]

    # Establishes the unique clicks bars
    rects = list()
    for num in range(num_labels):
        rect = plt.bar(
            label[num],
            label_data[num + 1],
            bar_width,
            edgecolor="white",
            color=color_list[num],
            label=label_names[num],
            align="edge",
        )
        rects.append(rect)

    # Sets x labels.
    plt.xticks(
        [r_val + bar_width * 2.5 for r_val in range(len(label_data[1]))],
        ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"],
    )

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Add counts above the two bar graphs
    first = True

    for rect in rects:

        if first:
            all_rects = rect
            first = False
        else:
            all_rects = all_rects + rect

    for rect in all_rects:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            height,
            ha="center",
            va="bottom",
            fontsize=6,
        )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        frameon=False,
        ncol=3,
        prop={"size": 8},
    )

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/CountUniqueClicksByLevelPerOffice.png", bbox_inches="tight")
    report_data["figures"].append(10)


# Percent of All clicks by Office for level
def perc_total_unique_clicks_belong_office_by_level(report_data):
    """Percentage of total unique clicks by office by level logic."""
    # data to plot
    label_names = list()
    label_data = dict()
    label_data[1] = list()
    label_data[2] = list()
    label_data[3] = list()
    label_data[4] = list()
    label_data[5] = list()
    label_data[6] = list()

    count = 1
    # pulls all office Names and each levels unique clicks.
    for label, _ in report_data["Labels"].items():
        label_names.append(
            "\n".join(textwrap.wrap(report_data["Labels"][label]["Name"], 15))
        )
        label_data[count].append(
            report_data["Labels"][label]["1"]["Percent_Of_All_Clicks"]
        )
        label_data[count].append(
            report_data["Labels"][label]["2"]["Percent_Of_All_Clicks"]
        )
        label_data[count].append(
            report_data["Labels"][label]["3"]["Percent_Of_All_Clicks"]
        )
        label_data[count].append(
            report_data["Labels"][label]["4"]["Percent_Of_All_Clicks"]
        )
        label_data[count].append(
            report_data["Labels"][label]["5"]["Percent_Of_All_Clicks"]
        )
        label_data[count].append(
            report_data["Labels"][label]["6"]["Percent_Of_All_Clicks"]
        )
        count += 1

    # create plot
    _, ax_val = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    num_labels = len(label_names)
    label = [None] * num_labels
    color_list = [BLUE, DARK_RED, GREEN, PURPLE, LIGHT_BLUE, ORANGE]

    for num in range(num_labels):
        if num == 0:
            label[num] = np.arange(len(label_data[1]))
        else:
            label[num] = [x_val + bar_width for x_val in label[num - 1]]

    # Establishes the unique clicks bars
    rects = list()
    for num in range(num_labels):
        rect = plt.bar(
            label[num],
            label_data[num + 1],
            bar_width,
            edgecolor="white",
            color=color_list[num],
            label=label_names[num],
            align="edge",
        )
        rects.append(rect)

    ax_val.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    # Sets x labels.
    plt.xticks(
        [r + bar_width * 2.5 for r in range(len(label_data[1]))],
        ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"],
    )

    # Sets X Axis margin.
    ax_val.margins(0.01, 0)

    # Add counts above the bars
    first = True

    for rect in rects:

        if first:
            all_rects = rect
            first = False
        else:
            all_rects = all_rects + rect

    for rect in all_rects:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            "%.f" % height + "%",
            ha="center",
            va="bottom",
            fontsize=6,
        )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        frameon=False,
        ncol=3,
        prop={"size": 8},
    )

    ax_val.spines["right"].set_visible(False)
    ax_val.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        "figures/PercTotalUniqueClicksBelongOfficeByLevel.png", bbox_inches="tight"
    )
    report_data["figures"].append(11)
