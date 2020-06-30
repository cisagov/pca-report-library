"""Tests for Report Generation functions."""
# Third-Party Libraries
from customer.closing import (appearance_above_ave, behavior_above_ave,
                              indicators_above_ave, overall_trend,
                              relevancy_above_ave, sender_above_ave)
import pytest


class TestAboveAve:
    """Test Above Average functions."""

    parameters = {
        "behavior": [
            (
                [
                    "greed - True",
                    "duty_obligation - True",
                    "curiosity - True",
                    "fear - True",
                ],
                "for the behavior category, emails eliciting feelings of greed, duty/obligation to respond, curiosity, or fear",
            ),
            (
                ["duty_obligation - True", "curiosity - True", "fear - True"],
                "for the behavior category, emails eliciting feelings of duty/obligation to respond, curiosity, or fear",
            ),
            (
                ["curiosity - True", "fear - True"],
                "for the behavior category, emails eliciting feelings of curiosity, or fear",
            ),
            (
                ["curiosity - True", "fear - True"],
                "for the behavior category, emails eliciting feelings of curiosity, or fear",
            ),
        ],
        "sender": [
            (
                [
                    "internal - Specific",
                    "internal - Generic",
                    "external - Spoofed",
                    "external - Unknown",
                ],
                "for the sender category, emails from spoofed known internal departments, plausible sounding internal sources, believably real external sources, or unknown external senders",
            ),
            (
                ["internal - Generic", "external - Spoofed", "external - Unknown"],
                "for the sender category, emails from plausible sounding internal sources, believably real external sources, or unknown external senders",
            ),
            (
                ["external - Spoofed", "external - Unknown"],
                "for the sender category, emails from believably real external sources, or unknown external senders",
            ),
            (
                ["external - Unknown"],
                "for the sender category, emails from unknown external senders",
            ),
        ],
        "relevancy": [
            (
                ["organization - True"],
                "for the relevancy category, emails referencing organizationally relevant topics",
            ),
            (
                ["organization - True", "public News - True"],
                "for the relevancy category, emails referencing organizationally relevant topics, or specific publicly available information rather than generic content",
            ),
            (
                ["public News - True"],
                "for the relevancy category, emails referencing specific publicly available information rather than generic content",
            ),
        ],
        "appearance": [
            (
                ["link_domain - Spoofed"],
                "for the appearance category, emails with hyperlinked text rather than bare URLs",
            ),
            (
                ["link_domain - Spoofed", "link_domain - Fake"],
                "for the appearance category, emails with hyperlinked text rather than bare URLs, or written out URLs rather than hyperlinked text",
            ),
            (
                ["link_domain - Spoofed", "link_domain - Fake", "logo_graphics - True"],
                "for the appearance category, emails with hyperlinked text rather than bare URLs, written out URLs rather than hyperlinked text, or HTML formatting or graphics",
            ),
            (
                [
                    "link_domain - Spoofed",
                    "link_domain - Fake",
                    "logo_graphics - True",
                    "grammar - Proper",
                ],
                "for the appearance category, emails with hyperlinked text rather than bare URLs, written out URLs rather than hyperlinked text, HTML formatting or graphics, or proper grammar and professional formatting",
            ),
            (
                [
                    "link_domain - Spoofed",
                    "link_domain - Fake",
                    "logo_graphics - True",
                    "grammar - Proper",
                    "grammar - Decent",
                ],
                "for the appearance category, emails with hyperlinked text rather than bare URLs, written out URLs rather than hyperlinked text, HTML formatting or graphics, proper grammar and professional formatting, or decent grammar",
            ),
            (
                [
                    "link_domain - Spoofed",
                    "link_domain - Fake",
                    "logo_graphics - True",
                    "grammar - Proper",
                    "grammar - Decent",
                    "grammar - Poor",
                ],
                "for the appearance category, emails with hyperlinked text rather than bare URLs, written out URLs rather than hyperlinked text, HTML formatting or graphics, proper grammar and professional formatting, decent grammar, or poor grammar",
            ),
        ],
    }

    mock_reportData = [
        (
            {
                "complexity": {
                    "behavior": {
                        "greed - True": {
                            "emails_sent": 35,
                            "unique_clicks": 6,
                            "click_rate": 17.14,
                        },
                        "fear - True": {
                            "emails_sent": 0,
                            "unique_clicks": 0,
                            "click_rate": 0.0,
                        },
                        "curiosity - True": {
                            "emails_sent": 71,
                            "unique_clicks": 4,
                            "click_rate": 5.63,
                        },
                        "duty_obligation - True": {
                            "emails_sent": 105,
                            "unique_clicks": 11,
                            "click_rate": 10.48,
                        },
                    },
                    "relevancy": {
                        "public_news - True": {
                            "emails_sent": 0,
                            "unique_clicks": 0,
                            "click_rate": 0.0,
                        },
                        "organization - True": {
                            "emails_sent": 35,
                            "unique_clicks": 6,
                            "click_rate": 17.14,
                        },
                    },
                    "sender": {
                        "authoritative - High": {
                            "emails_sent": 0,
                            "unique_clicks": 0,
                            "click_rate": 0.0,
                        },
                        "authoritative - Low": {
                            "emails_sent": 70,
                            "unique_clicks": 5,
                            "click_rate": 7.14,
                        },
                        "internal - Specific": {
                            "emails_sent": 35,
                            "unique_clicks": 6,
                            "click_rate": 17.14,
                        },
                        "internal - Generic": {
                            "emails_sent": 106,
                            "unique_clicks": 8,
                            "click_rate": 7.55,
                        },
                        "external - Spoofed": {
                            "emails_sent": 0,
                            "unique_clicks": 0,
                            "click_rate": 0.0,
                        },
                        "external - Unknown": {
                            "emails_sent": 71,
                            "unique_clicks": 4,
                            "click_rate": 5.63,
                        },
                    },
                    "appearance": {
                        "logo_graphics - True": {
                            "emails_sent": 0,
                            "unique_clicks": 0,
                            "click_rate": 0.0,
                        },
                        "link_domain - Spoofed": {
                            "emails_sent": 177,
                            "unique_clicks": 17,
                            "click_rate": 9.6,
                        },
                        "link_domain - Fake": {
                            "emails_sent": 35,
                            "unique_clicks": 1,
                            "click_rate": 2.86,
                        },
                        "grammar - Proper": {
                            "emails_sent": 106,
                            "unique_clicks": 13,
                            "click_rate": 12.26,
                        },
                        "grammar - Decent": {
                            "emails_sent": 70,
                            "unique_clicks": 2,
                            "click_rate": 2.86,
                        },
                        "grammar - Poor": {
                            "emails_sent": 36,
                            "unique_clicks": 3,
                            "click_rate": 8.33,
                        },
                    },
                },
                "Click_Rate": "8.49",
            },
            "for the behavior category, emails eliciting feelings of greed, or duty/obligation to respond; for the relevancy category, emails referencing organizationally relevant topics; for the sender category, emails from spoofed known internal departments; and for the appearance category, emails with hyperlinked text rather than bare URLs, or proper grammar and professional formatting",
        )
    ]

    @pytest.mark.parametrize("indicator,expected", parameters["behavior"])
    def test_behavior(self, indicator, expected):
        """Verify returned behavior string matches expectation."""
        assert behavior_above_ave(indicator) == expected

    @pytest.mark.parametrize("indicator,expected", parameters["sender"])
    def test_sender(self, indicator, expected):
        """Verify sender behavior string matches expectation."""
        assert sender_above_ave(indicator) == expected

    @pytest.mark.parametrize("indicator,expected", parameters["relevancy"])
    def test_relevancy(self, indicator, expected):
        """Verify relevancy behavior string matches expectation."""
        assert relevancy_above_ave(indicator) == expected

    @pytest.mark.parametrize("indicator,expected", parameters["appearance"])
    def test_appearance(self, indicator, expected):
        """Verify appearance behavior string matches expectation."""
        assert appearance_above_ave(indicator) == expected

    @pytest.mark.parametrize("reportData,expected", mock_reportData)
    def test_indicators_above_ave(self, reportData, expected):
        """Verify above average indicator matches expectation."""
        assert indicators_above_ave(reportData) == expected


class TestTrends:
    """Test overall trend functions."""

    trend_data = [
        {
            "Level": {
                "1": {"Click_Rate": 8.33},
                "2": {"Click_Rate": 2.86},
                "3": {"Click_Rate": 2.86},
                "4": {"Click_Rate": 8.33},
                "5": {"Click_Rate": 11.43},
                "6": {"Click_Rate": 17.14},
            }
        },
        {
            "Level": {
                "1": {"Click_Rate": 17.14, "User_Report_Rate": "4.58%"},
                "2": {"Click_Rate": 11.43},
                "3": {"Click_Rate": 8.33},
                "4": {"Click_Rate": 2.86},
                "5": {"Click_Rate": 2.86},
                "6": {"Click_Rate": 8.33},
            }
        },
        {
            "Level": {
                "1": {"Click_Rate": 3.83},
                "2": {"Click_Rate": 1.87},
                "3": {"Click_Rate": 13.61},
                "4": {"Click_Rate": 17.65},
                "5": {"Click_Rate": 36.97},
                "6": {"Click_Rate": 0.0},
            }
        },
    ]

    click_trend_expected = ["increased", "decreased", "increased"]

    @pytest.mark.parametrize(
        "reportData,expected", tuple(zip(trend_data, click_trend_expected))
    )
    def test_overall_trend(self, reportData, expected):
        """Validate expected trend is found."""
        assert overall_trend(reportData) == expected
