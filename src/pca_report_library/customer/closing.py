"""Generate closing statement."""

__all__ = [
    "appearance_above_ave",
    "behavior_above_ave",
    "closing_builder",
    "deltas",
    "email_closing",
    "indicators_above_ave",
    "overall_trend",
    "pairwise",
    "relevancy_above_ave",
    "reporting_closing",
    "sender_above_ave",
    "text_list_separator",
]

# Standard Python Libraries
from itertools import tee
import json

from ..utility.gets import get_level_description, get_max_number


def reporting_closing(reportData):
    """Create closing comments about user reports."""
    highest_report_level = get_max_number(reportData, "User_Reports", "int")

    highest_deception_report_level = get_level_description(highest_report_level)

    # TODO account for the highest report num and ratio being the same.
    count = 0

    while True:

        max_time_gap_level = get_max_number(reportData, "Time_Gap_TD", "float", count)
        if max_time_gap_level:
            # Only set report_ratio_level if we get a valid value for max_time_gap_level
            report_ratio_level = max_time_gap_level

        if (
            count == 5
            or reportData["Level"][str(report_ratio_level)].get("Gap_Type") == "(LEAD)"
        ):
            break
        count += 1

    deception_report_ratio_level = get_level_description(report_ratio_level)

    reportData["Closing-Report-Highest-Level"] = highest_report_level
    reportData["Closing-Report-Highest-Deception"] = highest_deception_report_level
    reportData["Closing-Report-Highest-Subject"] = reportData["Level"][
        str(highest_report_level)
    ]["Subject"]
    reportData["Closing-Report-Highest-User_Reports"] = reportData["Level"][
        str(highest_report_level)
    ]["User_Reports"]
    reportData["Closing-Report-Highest-User_Report_Rate"] = reportData["Level"][
        str(highest_report_level)
    ]["Report-Rate"]
    reportData["Closing-Report-Highest-Time_Gap"] = (
        reportData["Level"][str(highest_report_level)]["Time_Gap"]
        .replace("hr", "hour")
        .replace("min", "minute")
        .replace("sec", "second")
    )
    reportData["Closing-Report-Highest-Gap_Type"] = (
        reportData["Level"][str(highest_report_level)]["Gap_Type"]
        .replace("(", "")
        .replace(")", "")
    )

    reportData["Closing-Report-Lead-Deception"] = deception_report_ratio_level
    reportData["Closing-Report-Lead-Level"] = report_ratio_level
    reportData["Closing-Report-Lead-Subject"] = reportData["Level"][
        str(report_ratio_level)
    ]["Subject"]
    reportData["Closing-Report-Lead-Time_Gap"] = (
        reportData["Level"][str(report_ratio_level)]["Time_Gap"]
        .replace("hr", "hour")
        .replace("min", "minute")
        .replace("sec", "second")
    )

    return reportData


def email_closing(reportData, level, order):
    """Create closing comments about the emails."""
    # Section 1: Build out the sender text.
    if int(level) <= 2:
        deception_level = "low "
    elif int(level) <= 4:
        deception_level = "moderate"
    elif int(level) <= 6:
        deception_level = "high"

    levelDict = reportData["Level"][str(level)]

    if levelDict["Complexity"]["Authoritative"] != 0:
        authoritative_text = (
            " The authoritative tone was also a key sophisticated phishing technique intended to persuade the"
            " targeted user into clicking the link without first questioning it."
        )
    else:
        authoritative_text = ""

    # Sender Options:
    if (
        levelDict["Complexity"]["External"] == 0
        and levelDict["Complexity"]["Internal"] == 0
    ):
        sender_text = (
            f'an external sending address with no known connection to {reportData["Acronym"]}'
            f' ({levelDict["From_Address"].split("<")[1].replace(">", "")})'
        )

    elif (
        levelDict["Complexity"]["External"] == 1
        and levelDict["Complexity"]["Internal"] == 0
    ):
        sender_text = f'an external, but believable address with a spoofed display name ({levelDict["From_Address"].split("<")[0]})'

    elif (
        levelDict["Complexity"]["External"] == 0
        and levelDict["Complexity"]["Internal"] == 1
    ):
        sender_text = f'an unknown internal address with a organizational relevant display name ({levelDict["From_Address"].split("<")[0]})'

    elif (
        levelDict["Complexity"]["External"] == 0
        and levelDict["Complexity"]["Internal"] == 2
    ):
        sender_text = f'a (fully or partially) spoofed internal address with a known or believable display name ({levelDict["From_Address"].split("<")[0]})'

    # Section 2: Builds out appearance text

    if levelDict["Complexity"]["Grammar"] == 0:
        grammar_text = " poor grammar"
    elif levelDict["Complexity"]["Grammar"] == 1:
        grammar_text = " only using decent grammar with some errors"
    elif levelDict["Complexity"]["Grammar"] == 2:
        grammar_text = ""

    if (
        not levelDict["Complexity"]["Grammar"] == 2
        and levelDict["Complexity"]["Link_Domain"] == 0
    ):
        grammar_text = f'{grammar_text}{" and"}'

    if levelDict["Complexity"]["Logo_Graphics"] == 1:
        logo_text = (
            " Additionally the email contained advanced formatting such "
            "as graphics or logos to lessen user suspicion. "
        )
    else:
        logo_text = ""

    if levelDict["Complexity"]["Link_Domain"] == 0:
        link_text = "an external link with no known organizational connection"
        appearance_text = (
            "Red flags in the appearance that should have caused user hesitation were "
            f"{grammar_text} {link_text}.{logo_text}{authoritative_text}"
        )

    elif levelDict["Complexity"]["Link_Domain"] == 1:
        link_text = (
            f"a spoofed or hidden link ({levelDict['Display_Link']}) requiring the extra "
            "step of hovering over or long - pressing(on mobile phone) to verify legitimacy"
        )

        if levelDict["Complexity"]["Grammar"] == 2:
            appearance_text = (
                "The sophisticated techniques designed to fool the recipient were the use of proper grammar to blend in with "
                f"professional communications and a spoofed or hidden link ({levelDict['Display_Link']}) requiring the extra "
                f"step of hovering over or long - pressing (on mobile phone) to verify legitimacy. {logo_text}{authoritative_text}"
            )
        elif levelDict["Complexity"]["Grammar"] != 2:
            appearance_text = (
                f"Red flags in the appearance that should have caused user hesitation were {grammar_text}. "
                f"A sophisticated technique designed to fool the recipient was a spoofed or hidden link ({levelDict['Display_Link']})"
                f" requiring the extra step of hovering over or long - pressing (on mobile phone) to verify legitimacy. {logo_text}{authoritative_text}"
            )

    # Section 3: Builds out relevancy
    relevancy_text = " In a final attempt to draw users to click, added relevancy was implied by{}{}{}"
    organization_text = ""
    public_news_text = ""
    conjunction_text = "    "

    if levelDict["Complexity"]["Organization"] == 1:
        organization_text = " including content associated with the organization"
    if levelDict["Complexity"]["Public_News"] == 1:
        public_news_text = (
            " creating a feel that the content originated as public news."
        )

    if organization_text and public_news_text:
        conjunction_text = " and"
    elif public_news_text:
        conjunction_text = "."
    else:
        relevancy_text = ""

    relevancy_text = relevancy_text.format(
        organization_text, conjunction_text, public_news_text
    )

    reportData[f"Closing-{order}-Clicks-Click_Rate"] = levelDict["Click_Rate"]
    reportData[f"Closing-{order}-Clicks-Level"] = level
    reportData[f"Closing-{order}-Clicks-Deception_Level"] = deception_level
    reportData[f"Closing-{order}-Clicks-Subject"] = levelDict["Subject"]
    reportData[f"Closing-{order}-Clicks-Sender_Text"] = sender_text
    reportData[f"Closing-{order}-Clicks-Appearance_Text"] = appearance_text
    reportData[f"Closing-{order}-Clicks-Relevancy_Text"] = relevancy_text

    if reportData["User_Report_Provided"]:
        reportData[f"Closing-{order}-Clicks-User_Reports"] = levelDict["User_Reports"]
        reportData[f"Closing-{order}-Clicks-User_Report_Rate"] = levelDict[
            "Report-Rate"
        ]

    return reportData


def closing_builder(assessment_ID):
    """Build closing with comments."""
    dataFile = "reportData_" + assessment_ID + ".json"
    print("\tGenerating Closing for " + assessment_ID + " Report...")
    # Loads report data into a dictionary from json file.
    with open(dataFile) as f:
        reportData = json.load(f)

    # Compares to 0 as a string because the dict has been flattened.
    if reportData["Sum_Unique_Clicks"] != 0:
        click_rates = []
        # Finds the top two  Campaigns
        for num in range(1, 7):
            click_rates.append(float(reportData["Level"][str(num)]["Click_Rate"]))

        click_rates.sort(reverse=True)

        # TODO Account for click rates being the same.
        max_click_rate = click_rates.pop(0)

        for num in range(1, 7):
            if reportData["Level"][str(num)]["Click_Rate"] == max_click_rate:
                highest_level = num

        # Sets text for Highest Click Number
        reportData = email_closing(reportData, highest_level, 1)

        max_click_rate = click_rates.pop(0)

        for num in range(1, 7):
            if reportData["Level"][str(num)]["Click_Rate"] == max_click_rate:
                second_level = num

        # Sets text for Second Click Number or set Multiple_Clicks to false if 0 clicks.
        if reportData["Level"][str(second_level)]["User_Clicks"] != 0:
            reportData["Multiple_Clicks"] = "true"
            reportData = email_closing(reportData, second_level, 2)
        else:
            reportData["Multiple_Clicks"] = "false"

        if reportData["User_Report_Provided"]:
            reportData = reporting_closing(reportData)
            reportData["Report-Rate-Trend"] = overall_trend(reportData, "Report-Rate")

        reportData["Indicators-Above-Ave"] = indicators_above_ave(reportData)
        reportData["Click-Rate-Trend"] = overall_trend(reportData)

        reportData["No_Clicks"] = "false"

    else:
        reportData["No_Clicks"] = "true"
        reportData["Multiple_Clicks"] = "false"
        for order in [1, 2]:
            reportData[f"Closing-{order}-Clicks-Click_Rate"] = 0
            reportData[f"Closing-{order}-Clicks-Level"] = 0
            reportData[f"Closing-{order}-Clicks-Deception_Level"] = 0
            reportData[f"Closing-{order}-Clicks-Subject"] = ""
            reportData[f"Closing-{order}-Clicks-Sender_Text"] = ""
            reportData[f"Closing-{order}-Clicks-Appearance_Text"] = ""
            reportData[f"Closing-{order}-Clicks-Relevancy_Text"] = ""
            reportData[f"Closing-{order}-Clicks-User_Reports"] = 0

    with open("reportData_" + reportData["RVA_Number"] + ".json", "w") as fp:
        json.dump(reportData, fp, indent=4)


def indicators_above_ave(reportData):
    """Build the sentence indicating which indicators are above the average click rate.

    :param reportData:
    :return above_ave_indicators:
    """
    above_ave_indicator_text = []

    for complexity_type in ["behavior", "relevancy", "sender", "appearance"]:
        temp_indicators = []
        for indicator, values in reportData["complexity"][complexity_type].items():
            if float(values["click_rate"]) > float(reportData["Click_Rate"]):
                temp_indicators.append(indicator)

        if len(temp_indicators) != 0:
            if complexity_type == "behavior":
                above_ave_indicator_text.append(behavior_above_ave(temp_indicators))
            elif complexity_type == "relevancy":
                above_ave_indicator_text.append(relevancy_above_ave(temp_indicators))
            elif complexity_type == "sender":
                above_ave_indicator_text.append(sender_above_ave(temp_indicators))
            elif complexity_type == "appearance":
                above_ave_indicator_text.append(appearance_above_ave(temp_indicators))

    compiled_above_ave_text = ""
    for index, text in enumerate(above_ave_indicator_text):
        if compiled_above_ave_text == "":
            compiled_above_ave_text = text
        else:
            compiled_above_ave_text = f"{compiled_above_ave_text} {text}"

        compiled_above_ave_text = text_list_separator(
            index, len(above_ave_indicator_text), compiled_above_ave_text, "semicolon"
        )

    return compiled_above_ave_text


def text_list_separator(index, length, text, punctuation_type="comma"):
    """Add the comma or the or based on length of list.

    :param text:
    :return text:
    """
    if (index + 1) < length:
        if (index + 1) < length - 1:
            if punctuation_type == "comma":
                text = f"{text},"
            elif punctuation_type == "semicolon":
                text = f"{text};"
        else:
            if punctuation_type == "comma":
                text = f"{text}, or"
            elif punctuation_type == "semicolon":
                text = f"{text}; and"

    return text


def behavior_above_ave(behavior):
    """Build out the behaviors that are above the click rate.

    and returns as a text string.
    :param behavior:
    :return behavior_text:
    """
    behavior_text = "for the behavior category, emails eliciting feelings of"
    for index, indicator in enumerate(behavior):
        if indicator == "greed - True":
            behavior_text = f"{behavior_text} greed"
        elif indicator == "duty_obligation - True":
            behavior_text = f"{behavior_text} duty/obligation to respond"
        elif indicator == "curiosity - True":
            behavior_text = f"{behavior_text} curiosity"
        elif indicator == "fear - True":
            behavior_text = f"{behavior_text} fear"

        behavior_text = text_list_separator(index, len(behavior), behavior_text)

    return behavior_text


def sender_above_ave(sender):
    """Build out the sender indicators that are above the click rate and returns as a text string.

    :param sender:
    :return sender_text:
    """
    sender_text = "for the sender category, emails from"
    for index, indicator in enumerate(sender):
        if indicator == "internal - Specific":
            sender_text = f"{sender_text} spoofed known internal departments"
        elif indicator == "internal - Generic":
            sender_text = f"{sender_text} plausible sounding internal sources"
        elif indicator == "external - Spoofed":
            sender_text = f"{sender_text} believably real external sources"
        elif indicator == "external - Unknown":
            sender_text = f"{sender_text} unknown external senders"
        elif indicator == "authoritative - High":
            sender_text = f"{sender_text} speaking with power at a level above the recipient or associated with a state or federal entity"
        elif indicator == "authoritative - Low":
            sender_text = f"{sender_text} speaking with power at a peer level with the recipient or associated with a local/corporate entity"
        sender_text = text_list_separator(index, len(sender), sender_text)

    return sender_text


def relevancy_above_ave(relevancy):
    """Build out the relevancy indicators that are above the click rate and returns as a text string.

    :param relevancy:
    :return relevancy_text:
    """
    relevancy_text = "for the relevancy category, emails referencing"
    for index, indicator in enumerate(relevancy):
        if indicator == "organization - True":
            relevancy_text = f"{relevancy_text} organizationally relevant topics"
        elif indicator == "public News - True":
            relevancy_text = f"{relevancy_text} specific publicly available information rather than generic content"

        relevancy_text = text_list_separator(index, len(relevancy), relevancy_text)

    return relevancy_text


def appearance_above_ave(appearance):
    """Build out the appearance indicators that are above the click rate and returns as a text string.

    :param appearance:
    :return appearance_text:
    """
    appearance_text = "for the appearance category, emails with"
    for index, indicator in enumerate(appearance):
        if indicator == "link_domain - Spoofed":
            appearance_text = (
                f"{appearance_text} hyperlinked text rather than bare URLs"
            )
        elif indicator == "link_domain - Fake":
            appearance_text = (
                f"{appearance_text} written out URLs rather than hyperlinked text"
            )
        elif indicator == "logo_graphics - True":
            appearance_text = f"{appearance_text} HTML formatting or graphics"
        elif indicator == "grammar - Proper":
            appearance_text = (
                f"{appearance_text} proper grammar and professional formatting"
            )
        elif indicator == "grammar - Decent":
            appearance_text = f"{appearance_text} decent grammar"
        elif indicator == "grammar - Poor":
            appearance_text = f"{appearance_text} poor grammar"

        appearance_text = text_list_separator(index, len(appearance), appearance_text)

    return appearance_text


def overall_trend(reportData, click_rate_type="Click_Rate"):
    """Find the overall trend of decreasing or increasing between click_rate or report rate.

    :param reportData:
    :param type:
    :return trend text:
    """
    rates = []
    for num in range(1, 7):
        rates.append(reportData["Level"][str(num)][click_rate_type])

    rate_deltas = deltas(pairwise(rates))

    increase = 0
    decrease = 0
    same = 0

    for delta in rate_deltas:
        if delta > 0:
            increase += 1
        elif delta < 0:
            decrease += 1
        else:
            same += 1

    if increase > decrease and increase > same:
        return "increased"
    if decrease > same and increase != decrease:
        return "decreased"
    if increase == decrease or increase == same or same == decrease:
        return "varied"

    return "remained the same"


def deltas(pairs):
    """Find deltas between numbers.

    Example: 2 5 3 4 -> 3, -2, 1
    """
    for left, right in pairs:
        yield right - left


def pairwise(iterable):
    """Pair numbers with item before and after.

    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
