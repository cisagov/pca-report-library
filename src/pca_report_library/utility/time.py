"""Convert times."""

__all__ = [
    "time_to_string",
    "format_timedelta_to_HHMMSS",
]


def time_to_string(seconds_input):
    """Convert time in seconds to a string description."""
    string = ""
    # Used to ensure if the preceding period has a value that the
    # following are all included.
    prior = False
    # Creates the desired time calculations
    days, seconds = divmod(seconds_input, 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days >= 2:
        string += f"{days:0.0f} days "
        prior = True
    elif days == 1:
        string += f"{days:0.0f} day "
        prior = True

    if hours >= 2 or prior:
        string += f"{hours:0.0f} hours "
        prior = True
    elif hours == 1 or prior:
        string += f"{hours:0.0f} hour "
        prior = True

    if minutes >= 2 or prior:
        string += f"{minutes:0.0f} minutes "
        prior = True
    elif minutes == 1 or prior:
        string += f"{minutes:0.0f} minute "
        prior = True

    if seconds >= 2 or prior:
        string += f"{seconds:0.0f} seconds"
        prior = True
    elif seconds == 1 or prior:
        string += f"{seconds:0.0f} second"
        prior = True

    return string


def format_timedelta_to_HHMMSS(in_time_delta):
    """Convert time delta to HH:MM:SS."""
    hours, remainder = divmod(in_time_delta, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = f"0{minutes}"
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{hours}:{minutes}:{seconds}"
