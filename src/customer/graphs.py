"""Graphs."""

__all__ = ["graph_builder"]

# Standard Python Libraries
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
import timedelta

# Set Colors
BLUE = "#3C679D"
DARK_RED = "#A03D3B"
GREEN = "#7E9B45"
PURPLE = "#664E84"
LIGHT_BLUE = "#398DA6"
ORANGE = "#D67836"


def graph_builder(assessment_ID, labels):
    """Build the graphs."""
    success = True
    dataFile = "reportData_" + assessment_ID + ".json"

    if not os.path.exists("figures"):
        try:
            os.mkdir("figures")
        except OSError:
            print("\tERROR- Creation of the directory figures failed")
            success = False

    if success:
        print("\tGenerating Graphs for " + assessment_ID + " Report...")
        # Loads report data into a dictionary from json file.
        with open(dataFile) as f:
            reportData = json.load(f)
        reportData["figures"] = list()

        COLOR = "#101010"
        mpl.rcParams["text.color"] = COLOR
        mpl.rcParams["axes.labelcolor"] = COLOR
        mpl.rcParams["xtick.color"] = COLOR
        mpl.rcParams["ytick.color"] = COLOR

        unique_user_click_rate_vs_report_rate_per_level_deception(reportData)
        timeline_unique_user_clicks_all_levels(reportData)
        time_first_click_report(reportData)
        click_rate_based_deception_indicators(reportData)
        unique_total_click_report_results_by_level(reportData)
        breakdown_multiple_clicks_by_level(reportData)
        clicking_user_timeline(reportData)

        if labels:
            count_unique_clickes_by_office_per_level(reportData)
            percentage_office_clicked_by_level(reportData)
            count_unique_clicks_by_level_per_office(reportData)
            perc_total_unique_clicks_belong_office_by_level(reportData)

        with open("reportData_" + reportData["RVA_Number"] + ".json", "w") as fp:
            json.dump(reportData, fp, indent=4)

    return success


def time_ticks(x, pos):
    return str(timedelta(seconds=int(x))).split(".")[0]


# Unique User Click Rate vs. Report Rate per Level of Deception
def unique_user_click_rate_vs_report_rate_per_level_deception(reportData):
    # data to plot
    n_groups = 6
    click_rate = list()
    report_rate = list()
    ratio = list()
    userReportProvided = reportData["User_Report_Provided"]

    # Pulls the Click Rate from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        click_rate.append(reportData["Level"][numlevel]["Click_Rate"])

    if userReportProvided:

        # Calculates the Report Rate from the Report Data
        for numlevel, value1 in reportData["Level"].items():
            report_rate.append(
                round(
                    reportData["Level"][numlevel]["User_Reports"]
                    / reportData["Level"][numlevel]["Emails_Sent_Attempted"]
                    * 100,
                    2,
                )
            )

        # Builds the report vs click ratio
        for numlevel, value1 in reportData["Level"].items():
            if reportData["Level"][numlevel]["User_Clicks"] == 0:
                ratio.append(reportData["Level"][numlevel]["User_Reports"])
            else:
                ratio.append(
                    round(
                        reportData["Level"][numlevel]["User_Reports"]
                        / reportData["Level"][numlevel]["User_Clicks"],
                        1,
                    )
                )

    else:
        # Sets the Report Rate to 0 when user reports are not provided.
        for numlevel, value1 in reportData["Level"].items():
            report_rate.append(0)

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
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
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("Rate Percentages")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    if userReportProvided:
        if max(click_rate) > max(report_rate):
            percent_Lim = max(click_rate) + 10
        else:
            percent_Lim = max(report_rate) + 10
    else:
        percent_Lim = max(click_rate) + 10

    if percent_Lim > 100:
        ax.set_ylim(0, 100)
    else:
        ax.set_ylim(0, percent_Lim)

        # Add counts above the two bar graphs
    if userReportProvided:
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

    if userReportProvided and max(ratio) <= 2.0:
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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        "figures/UniqueUserClickRateVsReportRatePerLevelDeception.png",
        bbox_inches="tight",
    )
    reportData["figures"].append(1)


# Time line of Unique User Clicks Across All Levels
def timeline_unique_user_clicks_all_levels(reportData):
    # data to Plot
    timeFrame = list(reportData["Unique_Click_Timeline"].keys())[: 10 or None]

    n_groups = len(timeFrame)

    if bool(reportData["Unique_Click_Timeline"]):
        intervalpercent = list(reportData["Unique_Click_Timeline"].values())[
            : 10 or None
        ]
    else:
        intervalpercent = [0] * n_groups

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.7

    # Sets x and y labels.
    plt.xticks(index, timeFrame, rotation=45, fontsize=8, ha="right")

    # Establishes the interval bars
    rects1 = plt.bar(
        index, intervalpercent, bar_width, color=BLUE, label="Time Intervals"  # blue
    )

    # Lines xtick labels to center
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("%" + " of Unique User Clicks")
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

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
    reportData["figures"].append(2)


# Time to First Click (HH:MM:SS)
def time_first_click_report(reportData):
    # data to plot
    n_groups = 6
    firstClicks = list()
    firstReport = list()
    userReportProvided = reportData["User_Report_Provided"]

    # Pulls the first clicks from the Report Data
    for numlevel, value in reportData["Level"].items():
        firstClicks.append(reportData["Level"][numlevel]["Time_To_First_Click_TD"])
        if userReportProvided:
            firstReport.append(reportData["Level"][numlevel]["Time_To_First_Report_TD"])
        else:
            firstReport.append(0)

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.45

    # Sets x and y labels.
    plt.xlabel("Campaign Week")
    plt.xticks(index + bar_width / 2, ("1", "2", "3", "4", "5", "6"))

    # Establishes the interval bars
    rects1 = plt.bar(
        index, firstClicks, bar_width, color=BLUE, label="Time to First Click"  # blue
    )

    rects2 = plt.bar(
        index + bar_width,
        firstReport,
        bar_width,
        color=DARK_RED,  # Dark Red
        label="Time to First Report",
    )

    # Lines xtick labels to center
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    # Sets max y lim to 1.08 times the longest time
    allTime = firstClicks + firstReport
    timeSpread = max(allTime) - min(allTime)
    if timeSpread > 86400:
        ax.set_ylim(-1000, max(allTime) * 1.08)
    else:
        ax.set_ylim(0, max(allTime) * 1.08)

    # Hide y-axis value but show label.
    ax.set_yticklabels([])
    plt.ylabel("Elapsed Time")

    # Add counts above the bar graphs
    for rect in rects1 + rects2:
        height = np.float64(rect.get_height())
        if height != 0:
            hours = height // 3600
            minutes = (height % 3600) // 60
            seconds = height % 60

            str = "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
        else:
            str = "N/A"

        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            1.01 * height,
            str,
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=45,
        )

    # Hide the right and top spines
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.legend(loc="upper center", bbox_to_anchor=(0.50, -0.2), frameon=False, ncol=2)

    plt.tight_layout()
    plt.savefig("figures/TimeFirstClickReport.png", bbox_inches="tight")
    reportData["figures"].append(3)


# Click Rates Based on Deception Indicators
def click_rate_based_deception_indicators(reportData):
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

    for category, categoryValue in reportData["complexity"].items():
        for indicator_key, indicator_value in reportData["complexity"][
            category
        ].items():
            indicators[category]["click_rates"].append(
                reportData["complexity"][category][indicator_key]["click_rate"]
            )
            click_rate.append(
                reportData["complexity"][category][indicator_key]["click_rate"]
            )

    percent_max = max(click_rate) + 1

    for x in range(18):
        click_rates.append(reportData["Click_Rate"])

    plt.figure(figsize=(7, 10))

    gridspec.GridSpec(9, 1)

    plt.xticks([])
    plt.yticks([])

    # Builds out Behavior Plot
    behaviorPlot = plt.subplot2grid(
        (9, 1), (0, 0), colspan=1, rowspan=2
    )  # subplot(4,1,1)
    behaviorPlot.set_ylabel("Behavior", fontsize=10, labelpad=87, fontweight="bold")
    behaviorPlot.set_xlim(0, percent_max)
    behaviorPlot.barh(
        np.arange(4),
        indicators["behavior"]["click_rates"],
        align="center",
        color="#755998",
    )
    behaviorPlot.set_yticks(np.arange(4))
    behaviorPlot.set_yticklabels(indicators["behavior"]["indicators"], fontsize=10)
    behaviorPlot.invert_yaxis()
    behaviorPlot.spines["right"].set_visible(False)
    behaviorPlot.spines["bottom"].set_visible(False)
    behaviorPlot.xaxis.set_ticklabels([])
    behaviorPlot.xaxis.grid()  # Vertical lines
    behaviorPlot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds behavior labels
    for i, v in enumerate(indicators["behavior"]["click_rates"]):
        behaviorPlot.text(v + 0.1, i, str(v) + "%", va="center", fontsize=10)

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
    relevancyPlot = plt.subplot2grid(
        (9, 1), (2, 0), colspan=1, rowspan=1
    )  # subplot(4,1,2)
    relevancyPlot.set_ylabel("Relevancy", fontsize=10, labelpad=114, fontweight="bold")
    relevancyPlot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    relevancyPlot.set_xlim(0, percent_max)
    relevancyPlot.barh(
        np.arange(2),
        indicators["relevancy"]["click_rates"],
        align="center",
        color="#4576B5",
    )
    relevancyPlot.set_yticks(np.arange(2))
    relevancyPlot.set_yticklabels(indicators["relevancy"]["indicators"], fontsize=10)
    relevancyPlot.invert_yaxis()
    relevancyPlot.spines["right"].set_visible(False)
    relevancyPlot.spines["bottom"].set_visible(False)
    relevancyPlot.spines["top"].set_visible(False)
    relevancyPlot.xaxis.set_ticklabels([])
    relevancyPlot.xaxis.grid()  # Vertical lines
    relevancyPlot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds relevancy labels
    for i, v in enumerate(indicators["relevancy"]["click_rates"]):
        relevancyPlot.text(v + 0.1, i, str(v) + "%", va="center", fontsize=10)

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
    senderPlot = plt.subplot2grid(
        (9, 1), (3, 0), colspan=1, rowspan=3
    )  # subplot(4,1,3)
    senderPlot.set_ylabel("Sender", fontsize=10, labelpad=10, fontweight="bold")
    senderPlot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    senderPlot.set_xlim(0, percent_max)
    senderPlot.barh(
        np.arange(6),
        indicators["sender"]["click_rates"],
        align="center",
        color="#F68B3E",
    )
    senderPlot.set_yticks(np.arange(6))
    senderPlot.set_yticklabels(indicators["sender"]["indicators"], fontsize=10)
    senderPlot.invert_yaxis()
    senderPlot.spines["right"].set_visible(False)
    senderPlot.spines["bottom"].set_visible(False)
    senderPlot.spines["top"].set_visible(False)
    senderPlot.xaxis.set_ticklabels([])
    senderPlot.xaxis.grid()  # Vertical lines
    senderPlot.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # adds sender labels
    for i, v in enumerate(indicators["sender"]["click_rates"]):
        senderPlot.text(v + 0.1, i, str(v) + "%", va="center", fontsize=10)

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
    appearancePlot = plt.subplot2grid(
        (9, 1), (6, 0), colspan=1, rowspan=3
    )  # subplot(4,1,4)
    appearancePlot.set_ylabel("Appearance", fontsize=10, labelpad=11, fontweight="bold")
    appearancePlot.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    appearancePlot.set_xlim(0, percent_max)
    appearancePlot.barh(
        np.arange(6),
        indicators["appearance"]["click_rates"],
        align="center",
        color="#B7B7B7",
    )
    appearancePlot.set_yticks(np.arange(6))
    appearancePlot.set_yticklabels(indicators["appearance"]["indicators"], fontsize=10)
    appearancePlot.invert_yaxis()
    appearancePlot.spines["right"].set_visible(False)
    appearancePlot.spines["top"].set_visible(False)
    appearancePlot.xaxis.grid()  # Vertical lines

    # adds Appearance labels
    for i, v in enumerate(indicators["appearance"]["click_rates"]):
        appearancePlot.text(v + 0.1, i, str(v) + "%", va="center", fontsize=10)

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
    reportData["figures"].append(4)


# Unique Click, Total Click, and Report Results by Level
def unique_total_click_report_results_by_level(reportData):
    # data to plot
    n_groups = 6
    unique_clicks = list()
    total_clicks = list()
    user_reports = list()
    userReportProvided = reportData["User_Report_Provided"]

    # Pulls the Unique Clicks from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        unique_clicks.append(reportData["Level"][numlevel]["User_Clicks"])

    # Pulls the Total Clicks from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        total_clicks.append(reportData["Level"][numlevel]["Total_Clicks"])

    if userReportProvided:
        # Pulls the Report Rate from the Report Data
        for numlevel, value1 in reportData["Level"].items():
            user_reports.append(reportData["Level"][numlevel]["User_Reports"])
    else:
        # Sets the Report Rate to 0
        for numlevel, value1 in reportData["Level"].items():
            user_reports.append(0)

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)
    bar_width = 0.3

    # Sets x and y labels.
    plt.xlabel("Deception Level")

    plt.xticks(index + bar_width, ("1", "2", " 3", "4", "5", "6"))

    # Sets X Axis margin.
    ax.margins(0.01, 0)

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
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(5)
        tick.tick2line.set_markersize(5)
        tick.label1.set_horizontalalignment("center")

    plt.ylabel("# of Clicks")

    # Add counts above the two bar graphs
    if userReportProvided:
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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/UniqueTotalClickReportResultsByLevel.png", bbox_inches="tight")
    reportData["figures"].append(5)


# Breakdown of Multiple Clicks by Level
def breakdown_multiple_clicks_by_level(reportData):
    # data to plot
    n_groups = 6
    one_click = list()
    two_3_clicks = list()
    four_5_clicks = list()
    six_10_clicks = list()
    more_10_clicks = list()

    # Pulls the number of clikers that clicked onces from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        one_click.append(reportData["Level"][numlevel]["User_Click_Summary"]["1 time"])

    # Pulls the number of clikers that clicked 2 to 3 times from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        two_3_clicks.append(
            reportData["Level"][numlevel]["User_Click_Summary"]["2-3 times"]
        )

    # Pulls the number of clikers that clicked 4 to 5 times from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        four_5_clicks.append(
            reportData["Level"][numlevel]["User_Click_Summary"]["4-5 times"]
        )

    # Pulls the number of clikers that clicked 6 to 10 times from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        six_10_clicks.append(
            reportData["Level"][numlevel]["User_Click_Summary"]["6-10 times"]
        )

    # Pulls the number of clikers that clicked 6 to 10 times from the Report Data
    for numlevel, value1 in reportData["Level"].items():
        more_10_clicks.append(
            reportData["Level"][numlevel]["User_Click_Summary"][">10 times"]
        )

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
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
    ax.set_yticks([])

    # Sets x labels.
    plt.xlabel("Deception Level")
    plt.xticks(index + bar_width * 2, ("1", "2", " 3", "4", "5", "6"))

    # Sets X Axis margin.
    ax.margins(0.01, 0)

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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/BreakdownMultipleClicksByLevel.png", bbox_inches="tight")
    reportData["figures"].append(6)


# Time line of Unique Clicks
def clicking_user_timeline(reportData):
    # data to plot

    timeFrame = list(reportData["Unique_Click_Timeline"].keys())

    n_groups = len(timeFrame)

    # create plot
    fig, ax = plt.subplots(figsize=(7, 3.5))
    index = np.arange(n_groups)

    # Sets x labels.
    plt.xticks(index, timeFrame, rotation=45, fontsize=8, ha="right")

    # plt.ylabel('Rate Percentages')
    levelOne_x = list(reportData["Level"]["1"]["timeIntervalCount"].values())
    levelTwo_x = list(reportData["Level"]["2"]["timeIntervalCount"].values())
    levelThree_x = list(reportData["Level"]["3"]["timeIntervalCount"].values())
    levelFour_x = list(reportData["Level"]["4"]["timeIntervalCount"].values())
    levelFive_x = list(reportData["Level"]["5"]["timeIntervalCount"].values())
    levelSix_x = list(reportData["Level"]["6"]["timeIntervalCount"].values())

    for xLists in [
        levelOne_x,
        levelTwo_x,
        levelThree_x,
        levelFour_x,
        levelFive_x,
        levelSix_x,
    ]:

        if not xLists:
            while len(xLists) < n_groups:
                xLists.append(0)
        else:
            while len(xLists) < n_groups:
                xLists.append(100)

    # Plots Level One
    plt.plot(index, levelOne_x, color=BLUE, label="Level 1")

    # Plots Level Two
    plt.plot(index, levelTwo_x, color=DARK_RED, label="Level 2")

    # Plots Level Three
    plt.plot(index, levelThree_x, color=GREEN, label="Level 3")

    # Plots Level Four
    plt.plot(index, levelFour_x, color=PURPLE, label="Level 4")

    # Plots Level Five
    plt.plot(index, levelFive_x, color=LIGHT_BLUE, label="Level 5")

    # Plots Level Six
    plt.plot(index, levelSix_x, color=ORANGE, label="Level 6")

    # Adjusts the legend location
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.3),
        frameon=False,
        ncol=6,
        fontsize=8,
    )
    # Hide the right and top spines

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    ax.set_ylim(0, 101)
    ax.yaxis.set_ticks(np.arange(0, 101, 25))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))
    ax.yaxis.grid()  # horizontal lines

    plt.tight_layout()
    plt.savefig("figures/ClickingUserTimeline.png", bbox_inches="tight")
    reportData["figures"].append(7)


# Clicks by Level for offices
def count_unique_clickes_by_office_per_level(reportData):
    # data to plot
    label_names = list()
    level_one = list()
    level_two = list()
    level_three = list()
    level_four = list()
    level_five = list()
    level_six = list()

    # pulls all office Names and each levels unique clicks.
    for label, data in reportData["Labels"].items():
        if label != "Other":
            label_names.append(
                "\n".join(textwrap.wrap(reportData["Labels"][label]["Name"], 15))
            )
            level_one.append(reportData["Labels"][label]["1"]["Unique_Clicks"])
            level_two.append(reportData["Labels"][label]["2"]["Unique_Clicks"])
            level_three.append(reportData["Labels"][label]["3"]["Unique_Clicks"])
            level_four.append(reportData["Labels"][label]["4"]["Unique_Clicks"])
            level_five.append(reportData["Labels"][label]["5"]["Unique_Clicks"])
            level_six.append(reportData["Labels"][label]["6"]["Unique_Clicks"])

    # create plot
    fig, ax = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    lvl1 = np.arange(len(level_one))
    lvl2 = [x + bar_width for x in lvl1]
    lvl3 = [x + bar_width for x in lvl2]
    lvl4 = [x + bar_width for x in lvl3]
    lvl5 = [x + bar_width for x in lvl4]
    lvl6 = [x + bar_width for x in lvl5]

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
    plt.xticks([r + bar_width * 3 for r in range(len(level_one))], label_names)

    # Sets X Axis margin.
    ax.margins(0.01, 0)

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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/CountUniqueClickesByOfficePerLevel.png", bbox_inches="tight")
    reportData["figures"].append(8)


# Click percent by Level for offices
def percentage_office_clicked_by_level(reportData):
    # data to plot
    label_names = list()
    level_one = list()
    level_two = list()
    level_three = list()
    level_four = list()
    level_five = list()
    level_six = list()

    # pulls all office Names and each levels unique clicks.
    for label, data in reportData["Labels"].items():
        if label != "Other":
            label_names.append(
                "\n".join(textwrap.wrap(reportData["Labels"][label]["Name"], 15))
            )
            level_one.append(reportData["Labels"][label]["1"]["Click_Rate"])
            level_two.append(reportData["Labels"][label]["2"]["Click_Rate"])
            level_three.append(reportData["Labels"][label]["3"]["Click_Rate"])
            level_four.append(reportData["Labels"][label]["4"]["Click_Rate"])
            level_five.append(reportData["Labels"][label]["5"]["Click_Rate"])
            level_six.append(reportData["Labels"][label]["6"]["Click_Rate"])

    # create plot
    fig, ax = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    lvl1 = np.arange(len(level_one))
    lvl2 = [x + bar_width for x in lvl1]
    lvl3 = [x + bar_width for x in lvl2]
    lvl4 = [x + bar_width for x in lvl3]
    lvl5 = [x + bar_width for x in lvl4]
    lvl6 = [x + bar_width for x in lvl5]

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
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    # Sets x labels.
    # plt.xlabel('Office Name')
    plt.xticks([r + bar_width * 3 for r in range(len(level_one))], label_names)

    # Sets X Axis margin.
    ax.margins(0.01, 0)

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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/PercentageOfficeClickedByLevel.png", bbox_inches="tight")
    reportData["figures"].append(9)


# Click by Office for level
def count_unique_clicks_by_level_per_office(reportData):
    # data to plot
    label_names = list()
    labelData = dict()
    labelData[1] = list()
    labelData[2] = list()
    labelData[3] = list()
    labelData[4] = list()
    labelData[5] = list()
    labelData[6] = list()

    count = 1
    # pulls all office Names and each levels unique clicks.
    for label, data in reportData["Labels"].items():
        label_names.append(
            "\n".join(textwrap.wrap(reportData["Labels"][label]["Name"], 15))
        )
        labelData[count].append(reportData["Labels"][label]["1"]["Unique_Clicks"])
        labelData[count].append(reportData["Labels"][label]["2"]["Unique_Clicks"])
        labelData[count].append(reportData["Labels"][label]["3"]["Unique_Clicks"])
        labelData[count].append(reportData["Labels"][label]["4"]["Unique_Clicks"])
        labelData[count].append(reportData["Labels"][label]["5"]["Unique_Clicks"])
        labelData[count].append(reportData["Labels"][label]["6"]["Unique_Clicks"])
        count += 1

    # create plot
    fig, ax = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    numLabels = len(label_names)
    label = [None] * numLabels
    colorList = [BLUE, DARK_RED, GREEN, PURPLE, LIGHT_BLUE, ORANGE]

    for num in range(numLabels):
        if num == 0:
            label[num] = np.arange(len(labelData[1]))
        else:
            label[num] = [x + bar_width for x in label[num - 1]]

    # Establishes the unique clicks bars
    rects = list()
    for num in range(numLabels):
        rect = plt.bar(
            label[num],
            labelData[num + 1],
            bar_width,
            edgecolor="white",
            color=colorList[num],
            label=label_names[num],
            align="edge",
        )
        rects.append(rect)

    # Sets x labels.
    plt.xticks(
        [r + bar_width * 2.5 for r in range(len(labelData[1]))],
        ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"],
    )

    # Sets X Axis margin.
    ax.margins(0.01, 0)

    # Add counts above the two bar graphs
    first = True

    for rect in rects:

        if first:
            allRects = rect
            first = False
        else:
            allRects = allRects + rect

    for rect in allRects:
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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig("figures/CountUniqueClicksByLevelPerOffice.png", bbox_inches="tight")
    reportData["figures"].append(10)


# Percent of All clicks by Office for level
def perc_total_unique_clicks_belong_office_by_level(reportData):
    # data to plot
    label_names = list()
    labelData = dict()
    labelData[1] = list()
    labelData[2] = list()
    labelData[3] = list()
    labelData[4] = list()
    labelData[5] = list()
    labelData[6] = list()

    count = 1
    # pulls all office Names and each levels unique clicks.
    for label, data in reportData["Labels"].items():
        label_names.append(
            "\n".join(textwrap.wrap(reportData["Labels"][label]["Name"], 15))
        )
        labelData[count].append(
            reportData["Labels"][label]["1"]["Percent_Of_All_Clicks"]
        )
        labelData[count].append(
            reportData["Labels"][label]["2"]["Percent_Of_All_Clicks"]
        )
        labelData[count].append(
            reportData["Labels"][label]["3"]["Percent_Of_All_Clicks"]
        )
        labelData[count].append(
            reportData["Labels"][label]["4"]["Percent_Of_All_Clicks"]
        )
        labelData[count].append(
            reportData["Labels"][label]["5"]["Percent_Of_All_Clicks"]
        )
        labelData[count].append(
            reportData["Labels"][label]["6"]["Percent_Of_All_Clicks"]
        )
        count += 1

    # create plot
    fig, ax = plt.subplots(figsize=(7.5, 3.75))
    bar_width = 0.16

    numLabels = len(label_names)
    label = [None] * numLabels
    colorList = [BLUE, DARK_RED, GREEN, PURPLE, LIGHT_BLUE, ORANGE]

    for num in range(numLabels):
        if num == 0:
            label[num] = np.arange(len(labelData[1]))
        else:
            label[num] = [x + bar_width for x in label[num - 1]]

    # Establishes the unique clicks bars
    rects = list()
    for num in range(numLabels):
        rect = plt.bar(
            label[num],
            labelData[num + 1],
            bar_width,
            edgecolor="white",
            color=colorList[num],
            label=label_names[num],
            align="edge",
        )
        rects.append(rect)

    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100))

    # Sets x labels.
    plt.xticks(
        [r + bar_width * 2.5 for r in range(len(labelData[1]))],
        ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"],
    )

    # Sets X Axis margin.
    ax.margins(0.01, 0)

    # Add counts above the bars
    first = True

    for rect in rects:

        if first:
            allRects = rect
            first = False
        else:
            allRects = allRects + rect

    for rect in allRects:
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

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        "figures/PercTotalUniqueClicksBelongOfficeByLevel.png", bbox_inches="tight"
    )
    reportData["figures"].append(11)
