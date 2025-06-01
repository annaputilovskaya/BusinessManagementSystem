from datetime import date, datetime, timedelta

from fastapi import HTTPException, status


def check_dates(start_date, end_date):
    """
    Validate start and end dates.

    Args:
        start_date (date | None): Beginning of the period of evaluations.
        end_date (date | None): End of the period of evaluations.

    Returns:
        start_date (date | None): Validated beginning of the period of evaluations.
        end_date (date | None): Validated end of the period of evaluations.

    Raises:
        - 400 Bad Request: If start date is greater than end date.

    """

    if not start_date:
        start_date = date(2025, 1, 1)
    if not end_date:
        end_date = date.today()
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Incorrect dates interval."}
        )
    return start_date, end_date


def get_first_and_last_day_of_month(day: date) -> tuple[date, date]:
    """
    Returns the first and the last day of the month for a given date.

    Args:
        daу (date): A date object.

    Returns:
        tuple: A tuple of date objects representing the first and
            the last day of the month for the input date.
    """
    first_day = day.replace(day=1)
    next_month = day.replace(day=28) + timedelta(days=4)
    first_day_next_month = next_month.replace(day=1)
    last_day = first_day_next_month - timedelta(days=1)
    return first_day, last_day
