import logging
import pandas as pd

from datetime import datetime

logger = logging.getLogger(__name__)

MONTHS = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}

SEASON_TREND = {
    1: 'Winter', 4: 'Spring', 7: 'Summer', 10: 'Autumn'
}

seasons = {
    1: "Winter",
    2: "Spring",
    3: "Summer",
    4: "Autumn"
}

def check_dates_format_trend(dates):
    """Convert a list of dates from various formats to datetime objects."""
    if not dates:
        return []
    try:
        if isinstance(dates[0], str):
            if dates[0].startswith("0000"):
                return [datetime.strptime(d.replace("0000", "2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
            elif len(dates[0].split("-")) == 2:
                return [datetime.strptime("2000-" + d, "%Y-%m-%d") for d in dates]
            elif dates[0] in MONTHS.values():
                return [datetime.strptime(f"2000-{k:02d}-01", "%Y-%m-%d") for d in dates for k, v in MONTHS.items() if v == d]
            elif dates[0] in SEASON_TREND.values():
                return [datetime.strptime(f"2000-{k:02d}-01", "%Y-%m-%d") for d in dates for k, v in SEASON_TREND.items() if v == d]
            else:
                for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y"):
                    try:
                        return [datetime.strptime(d, fmt) for d in dates]
                    except ValueError:
                        continue
        return dates
    except Exception as e:
        logger.error(f"Errore in check_dates_format_trend: {e}")
        return []

def convertToTime(date_str):
    """Convert ISO datetime string to 'YYYY-MM-DD' format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Errore in convertToTime: {e}")
        return None

def get_season(date):
    """Return season code based on the given date."""
    year = date.year
    spring = pd.date_range(f"{year}-03-01", f"{year}-05-31")
    summer = pd.date_range(f"{year}-06-01", f"{year}-08-31")
    autumn = pd.date_range(f"{year}-09-01", f"{year}-11-30")

    if date in spring:
        return 2
    elif date in summer:
        return 3
    elif date in autumn:
        return 4
    return 1  # Default: Winter
