from datetime import date

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
