import datetime as dt


def get_date_chunks(start_date, end_date):
    """
    Generates a list of overlapping date-range tuples. The end date of one
    chunk becomes the start date of the next.

    Args:
        start_date: The beginning date of the period (as a datetime object).
        end_date: The final end date of the period (as a datetime object).

    Returns:
        A list of tuples, where each tuple contains a start and end datetime object.
    """
    date_chunks = []
    current_start = start_date

    while current_start < end_date:
        # Calculate the end of the chunk (7 days from the current start)
        potential_end = current_start + dt.timedelta(days=7)

        # The end of this chunk is either 7 days away or the final end_date
        current_end = min(potential_end, end_date)

        # Add the date chunk to our list
        date_chunks.append((current_start, current_end))

        # The start of the next chunk is the end of this one
        current_start = current_end

    return date_chunks
