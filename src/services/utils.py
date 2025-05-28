from datetime import date


def check_dates(start_date, end_date):
    """
    Validate start and end dates.

    Args:
        start_date (date | None): Beginning of the period of evaluations.
        end_date (date | None): End of the period of evaluations.

    Returns:
        start_date (date | None): Validated beginning of the period of evaluations.
        end_date (date | None): Validated end of the period of evaluations.
    """

    if not start_date:
        start_date = date(2025, 1, 1)
    if not end_date:
        end_date = date.today()
    return start_date, end_date
