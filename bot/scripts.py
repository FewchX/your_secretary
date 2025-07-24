import datetime

def calculate_user_utc(user_time):
    """Calculates the user's UTC offset based on their local time and the current time."""
    # If user_time is not provided, default to UTC  
    if not user_time:
        return 0  # Default to UTC if no time is provided
    try:
        user_time = datetime.datetime.strptime(user_time, "%H:%M")
    except ValueError:
        raise ValueError("Invalid time format. Use HH:MM format.")
    # Calculate the difference in hours and minutes
    now = datetime.datetime.now()
    now_time = f"{now.hour}:{now.minute}"
    now_time = datetime.datetime.strptime(now_time, "%H:%M")
    utc_offset = (user_time - now_time).total_seconds() / 3600  # Convert to hours
    return round(utc_offset)
    