from datetime import datetime
import datetime as dt

months = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

season_trend = {
    1: 'Winter',
    4: 'Spring',
    7: 'Summer',
    10: 'Autumn'
}

seasons = {
    1: "Winter",
    2: "Spring",
    3: "Summer",
    4: "Autumn"
}


def check_dates_format_trend(dates):
    """Converte una lista di date da diversi formati a oggetti datetime standard."""
    try:
        if not dates:
            return []

        if isinstance(dates[0], str):
            if dates[0].startswith("0000"):  # Caso annual month by month point
                dates = [dt.datetime.strptime(d.replace("0000", "2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
            elif len(dates[0].split("-")) == 2:  # Caso formato 01-01
                dates = [dt.datetime.strptime("2000-" + d, "%Y-%m-%d") for d in dates]
            elif dates[0] in months.values():  # Caso "Jan", "Feb", ecc.
                create_dates = []
                for d in dates:
                    for key, val in months.items():
                        if val == d:
                            create_dates.append(dt.datetime.strptime(f"2000-{key:02d}-01", "%Y-%m-%d"))
                dates = create_dates
            elif dates[0] in season_trend.values():  # Caso "Winter", "Spring", ecc.
                create_dates = []
                for d in dates:
                    for key, val in season_trend.items():
                        if val == d:
                            create_dates.append(dt.datetime.strptime(f"2000-{key:02d}-01", "%Y-%m-%d"))
                dates = create_dates
            else:  # Formati standard ISO
                parsed_dates = []
                for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
                    try:
                        parsed_dates = [dt.datetime.strptime(str(d), fmt) for d in dates]
                        break  # Se riesce a fare il parsing, esce
                    except ValueError:
                        continue
                dates = parsed_dates

        return dates

    except Exception as e:
        print(f"Errore in check_dates_format_trend: {e}")
        return []
    

def convertToTime(date_str):
    return dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")


def get_season(date):
    year = str(date.year)
    seasons = {
        'spring': pd.date_range(start=pd.Timestamp(year+'-03-01'), end=pd.Timestamp(year+'-05-31')),
        'summer': pd.date_range(start=pd.Timestamp(year+'-06-01'), end=pd.Timestamp(year+'-08-31')),
        'autumn': pd.date_range(start=pd.Timestamp(year+'-09-01'), end=pd.Timestamp(year+'-11-30'))
    }
    if date in seasons['spring']:
        return 1
    elif date in seasons['summer']:
        return 2
    elif date in seasons['autumn']:
        return 3
    else:
        return 0
