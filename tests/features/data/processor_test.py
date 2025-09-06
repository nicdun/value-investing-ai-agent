import pytest
from features.data.processor import get_quarter_from_date


class TestGetQuarterFromDate:
    """Test cases for the get_quarter_from_date function."""

    def test_q1_dates(self):
        """Test dates in Q1 (January, February, March)."""
        assert get_quarter_from_date("2024-01-01") == "2024Q1"  # January 1st
        assert get_quarter_from_date("2024-02-15") == "2024Q1"  # February 15th
        assert get_quarter_from_date("2024-03-31") == "2024Q1"  # March 31st

    def test_q2_dates(self):
        """Test dates in Q2 (April, May, June)."""
        assert get_quarter_from_date("2024-04-01") == "2024Q2"  # April 1st
        assert get_quarter_from_date("2024-05-15") == "2024Q2"  # May 15th
        assert get_quarter_from_date("2024-06-30") == "2024Q2"  # June 30th

    def test_q3_dates(self):
        """Test dates in Q3 (July, August, September)."""
        assert get_quarter_from_date("2024-07-01") == "2024Q3"  # July 1st
        assert get_quarter_from_date("2024-08-15") == "2024Q3"  # August 15th
        assert get_quarter_from_date("2024-09-30") == "2024Q3"  # September 30th

    def test_q4_dates(self):
        """Test dates in Q4 (October, November, December)."""
        assert get_quarter_from_date("2024-10-01") == "2024Q4"  # October 1st
        assert get_quarter_from_date("2024-11-15") == "2024Q4"  # November 15th
        assert get_quarter_from_date("2024-12-31") == "2024Q4"  # December 31st

    def test_different_years(self):
        """Test dates from different years."""
        assert get_quarter_from_date("2023-01-01") == "2023Q1"
        assert get_quarter_from_date("2022-06-15") == "2022Q2"
        assert get_quarter_from_date("2021-09-30") == "2021Q3"
        assert get_quarter_from_date("2020-12-31") == "2020Q4"

    def test_edge_cases(self):
        """Test edge cases for month boundaries."""
        # First day of each quarter
        assert get_quarter_from_date("2024-01-01") == "2024Q1"
        assert get_quarter_from_date("2024-04-01") == "2024Q2"
        assert get_quarter_from_date("2024-07-01") == "2024Q3"
        assert get_quarter_from_date("2024-10-01") == "2024Q4"

        # Last day of each quarter
        assert get_quarter_from_date("2024-03-31") == "2024Q1"
        assert get_quarter_from_date("2024-06-30") == "2024Q2"
        assert get_quarter_from_date("2024-09-30") == "2024Q3"
        assert get_quarter_from_date("2024-12-31") == "2024Q4"

    def test_middle_of_quarters(self):
        """Test dates in the middle of each quarter."""
        assert get_quarter_from_date("2024-02-15") == "2024Q1"  # Mid-February
        assert get_quarter_from_date("2024-05-15") == "2024Q2"  # Mid-May
        assert get_quarter_from_date("2024-08-15") == "2024Q3"  # Mid-August
        assert get_quarter_from_date("2024-11-15") == "2024Q4"  # Mid-November

    def test_historical_dates(self):
        """Test historical dates."""
        assert get_quarter_from_date("1995-01-01") == "1995Q1"
        assert get_quarter_from_date("2000-06-15") == "2000Q2"
        assert get_quarter_from_date("2015-09-30") == "2015Q3"
        assert get_quarter_from_date("2020-12-31") == "2020Q4"

    def test_future_dates(self):
        """Test future dates."""
        assert get_quarter_from_date("2025-01-01") == "2025Q1"
        assert get_quarter_from_date("2030-06-15") == "2030Q2"
        assert get_quarter_from_date("2050-09-30") == "2050Q3"
        assert get_quarter_from_date("2100-12-31") == "2100Q4"

    def test_date_format_consistency(self):
        """Test that the function consistently handles YYYY-MM-DD format."""
        # Test that the function expects YYYY-MM-DD format
        # and correctly extracts year and month
        test_date = "2024-12-25"  # December 25, 2024
        result = get_quarter_from_date(test_date)
        assert result == "2024Q4"

        # Verify the calculation logic
        year = int(test_date[:4])  # 2024
        month = int(test_date[5:7])  # 12
        quarter = (month - 1) // 3 + 1  # (12-1) // 3 + 1 = 4
        expected = f"{year}Q{quarter}"  # "2024Q4"
        assert result == expected

    def test_quarter_calculation_logic(self):
        """Test the mathematical logic of quarter calculation."""
        # Q1: months 1, 2, 3
        assert (1 - 1) // 3 + 1 == 1  # January
        assert (2 - 1) // 3 + 1 == 1  # February
        assert (3 - 1) // 3 + 1 == 1  # March

        # Q2: months 4, 5, 6
        assert (4 - 1) // 3 + 1 == 2  # April
        assert (5 - 1) // 3 + 1 == 2  # May
        assert (6 - 1) // 3 + 1 == 2  # June

        # Q3: months 7, 8, 9
        assert (7 - 1) // 3 + 1 == 3  # July
        assert (8 - 1) // 3 + 1 == 3  # August
        assert (9 - 1) // 3 + 1 == 3  # September

        # Q4: months 10, 11, 12
        assert (10 - 1) // 3 + 1 == 4  # October
        assert (11 - 1) // 3 + 1 == 4  # November
        assert (12 - 1) // 3 + 1 == 4  # December
