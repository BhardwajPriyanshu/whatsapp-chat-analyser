import pandas as pd
from datetime import datetime
import re


def preprocess(data):
    pattern = '\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s?[ ]?[ap]m'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)



    datetimes_12hr = dates


    def convert_datetime_to_24hr(dt_str):
        cleaned = dt_str.replace('\u202f', ' ').replace('\u00A0', ' ').strip().lower()

        try:
            dt = datetime.strptime(cleaned, "%d/%m/%y, %I:%M %p")
            return dt.strftime("%d/%m/%y, %H:%M")
        except ValueError:
            return None  # or f"Invalid: {dt_str}" if you want to track errors


    dates = [convert_datetime_to_24hr(dt) for dt in datetimes_12hr if convert_datetime_to_24hr(dt)]

    df = pd.DataFrame({'user_message':messages,'message_date':dates})

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['message_date'] = pd.to_datetime(
    df['message_date'],
    format='mixed',
    dayfirst=True,
    errors='coerce'  # Prevents crashes on badly formatted rows
    )
    df['message_date'] = pd.to_datetime(df['message_date'], format="%m/%d/%y, %H:%M")

# Fix years interpreted as 1925 instead of 2025
    df['message_date'] = df['message_date'].apply(
        lambda dt: dt.replace(year=dt.year + 100) if dt.year < 1970 else dt
    )


# Assuming df['message_date'] contains strings like "07/12/22, 9:20 pm"
    df['message_date'] = pd.to_datetime(df['message_date'], format="%m/%d/%y, %H:%M", errors='coerce')

    df['only_date'] = df['message_date'].dt.date
    df['year'] = df['message_date'].dt.year
    df['month_num'] = df['message_date'].dt.month
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df