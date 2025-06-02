from datetime import date
from contextlib import nullcontext as does_not_raise

import pytest
from fastapi import HTTPException

from src.services.utils import check_dates, get_first_and_last_day_of_month


@pytest.mark.parametrize(
    "start_date, end_date, expected_start_date, expected_end_date, expectation",
    [
        (
            None,
            date(2025, 1,30),
            date(2025, 1, 1),
            date(2025, 1,30),
            does_not_raise(),
        ),
        (
            date(2025, 2, 1),
            None,
            date(2025, 2, 1),
            date.today(),
            does_not_raise(),
        ),
        (
            date(2025, 1, 30),
            date(2025, 1, 1),
            date(2025, 1, 30),
            date(2025, 1, 1),
            pytest.raises(HTTPException),
        ),
        (
            date(2025, 1, 2),
            date(2025, 1, 30),
            date(2025, 1, 2),
            date(2025, 1, 30),
            does_not_raise(),
        ),
    ]
)
def test_check_dates(
        start_date, end_date, expected_start_date, expected_end_date, expectation
):
    with expectation:
        assert check_dates(start_date, end_date) == (
            expected_start_date,
            expected_end_date,
        )


@pytest.mark.parametrize(
    "day, first_day, last_day",
    [
        (
            date(2024, 2, 6),
            date(2024, 2, 1),
            date(2024, 2, 29)
        ),
        (
            date(2025, 2, 16),
            date(2025, 2, 1),
            date(2025, 2, 28)
        ),
        (
            date(2024, 12, 15),
            date(2024, 12, 1),
            date(2024, 12, 31)
        ),
        (
            date(2025, 1, 20),
            date(2025, 1, 1),
            date(2025, 1, 31)
        ),
    ]
)
def test_get_first_and_last_day_of_month(
        day, first_day, last_day
):
    assert get_first_and_last_day_of_month(day) == (first_day, last_day)
