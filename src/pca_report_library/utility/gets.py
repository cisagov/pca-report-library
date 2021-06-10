"""Get elements from data."""
__all__ = ["get_max_number", "get_level_description"]


def get_max_number(reportData, value_name, type, postion=0):
    """Get the max number from a specific metric."""
    report_numbers = list()

    for num in range(1, 7):
        if type == "int":
            try:
                report_numbers.append(reportData["Level"][str(num)][value_name])
            except ValueError:
                report_numbers.append(0)

        elif type == "float":
            try:
                report_numbers.append(reportData["Level"][str(num)][value_name])
            except ValueError:
                report_numbers.append(0)

    for i in range(len(report_numbers)):
        if report_numbers[i] is None:
            report_numbers[i] = 0

    report_numbers.sort(reverse=True)

    # TODO Account for click rates being the same.
    max_report_number = report_numbers.pop(postion)

    for num in range(1, 7):
        if reportData["Level"][str(num)][value_name] == max_report_number:
            return str(num)


def get_level_description(level):
    """Convert level number to a word description."""
    if int(level) == 1:
        deception = "lowest"
    elif int(level) == 2:
        deception = "low"
    elif int(level) == 3 or int(level) == 4:
        deception = "moderate"
    elif int(level) == 5:
        deception = "high"
    elif int(level) == 6:
        deception = "highest"
    else:
        raise ValueError(f"{level} is an invalid Complexity level.")

    return deception
