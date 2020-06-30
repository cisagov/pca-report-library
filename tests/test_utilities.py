"""Tests for Utility functions."""
# Third-Party Libraries
import pytest
from utility.gets import get_level_description, get_max_number
from utility.time import time_to_string


class TestGets:
    """Test get functions."""

    data = [
        (
            {
                "Level": {
                    "1": {"User_Reports": 185},
                    "2": {"User_Reports": 38},
                    "3": {"User_Reports": 305},
                    "4": {"User_Reports": 115},
                    "5": {"User_Reports": 110},
                    "6": {"User_Reports": 232},
                }
            },
            "User_Reports",
            "int",
            0,
            "3",
        ),
        (
            {
                "Level": {
                    "1": {"Time_Gap_TD": 2787.361},
                    "2": {"Time_Gap_TD": 29.373000000000005},
                    "3": {"Time_Gap_TD": 97.39600000000064},
                    "4": {"Time_Gap_TD": 85.021},
                    "5": {"Time_Gap_TD": 132.969},
                    "6": {"Time_Gap_TD": 623138.0},
                }
            },
            "Time_Gap_TD",
            "float",
            0,
            "6",
        ),
    ]

    @pytest.mark.parametrize("reportData,value_name,type,position,expected", data)
    def test_get_max(self, reportData, value_name, type, position, expected):
        """Validate expected max value is returned."""
        assert get_max_number(reportData, value_name, type, position) == expected

    @pytest.mark.parametrize(
        "level,expected",
        [
            ("1", "lowest"),
            ("2", "low"),
            ("3", "moderate"),
            ("4", "moderate"),
            ("5", "high"),
            ("6", "highest"),
        ],
    )
    def test_get_level(self, level, expected):
        """Validate expected level description is returned."""
        assert get_level_description(level) == expected

    @pytest.mark.parametrize("level", ["0", "7"])
    def test_get_level_fail(self, level):
        """Validate out of range level raises ValueError."""
        with pytest.raises(ValueError):
            get_level_description(level)


class TestTimeToString:
    """Test time functions."""

    @pytest.mark.parametrize(
        "secondsInput,expected",
        [
            (623138.0, "7 days 5 hours 5 minutes 38 seconds"),
            (161.0, "2 minutes 41 seconds"),
            (118.0, "1 minute 58 seconds"),
        ],
    )
    def test_time_to_string(self, secondsInput, expected):
        """Validate seconds is converted to correct string."""
        assert time_to_string(secondsInput) == expected
