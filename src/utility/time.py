"""Convert times."""
__all__ = ["time_to_string", "format_timedelta_to_HHMMSS"]


def time_to_string(secondsInput):
    """Convert time in seconds to a string description."""
    string = ""
    prior = False  # Used to ensure if the preceding period has a value that the following are all included.

    # Creates the desired time calculations
    days = secondsInput / (24 * 3600)
    hours = (secondsInput % (24 * 3600)) // 3600
    minutes = secondsInput % 3600 // 60
    seconds = secondsInput % 60

    if days >= 2:
        string += "{:0.0f} days ".format(days)
        prior = True
    elif days == 1:
        string += "{:0.0f} day ".format(days)
        prior = True

    if hours >= 2 or prior:
        string += "{:0.0f} hours ".format(hours)
        prior = True
    elif hours == 1 or prior:
        string += "{:0.0f} hour ".format(hours)
        prior = True

    if minutes >= 2 or prior:
        string += "{:0.0f} minutes ".format(minutes)
        prior = True
    elif minutes == 1 or prior:
        string += "{:0.0f} minute ".format(minutes)
        prior = True

    if seconds >= 2 or prior:
        string += "{:0.0f} seconds".format(seconds)
        prior = True
    elif seconds == 1 or prior:
        string += "{:0.0f} second".format(seconds)
        prior = True

    return string


def format_timedelta_to_HHMMSS(td):
    """Convert time delta to HH:MM:SS."""
    hours, remainder = divmod(td, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = "0{}".format(minutes)
    if seconds < 10:
        seconds = "0{}".format(seconds)
    return "{}:{}:{}".format(hours, minutes, seconds)
