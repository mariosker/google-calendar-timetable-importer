from __future__ import print_function

import itertools
import json
import os.path
import pickle
from datetime import date, datetime, timedelta

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


date_read = lambda d: datetime.strptime(d, '%Y/%m/%d').date()
time_read = lambda t: datetime.strptime(t, "%H:%M").time()

with open('program.json', encoding='utf8') as f:
    data = json.load(f)

# Init calendar
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

cal_id = data["calendar_data"][0]["calendar_id"]
if cal_id == "":
    calendar_name = "timetable" if data["calendar_data"][0][
        "calendar_name"] == "" else data["calendar_data"][0]["calendar_name"]
    calendar = {'summary': calendar_name, 'timeZone': 'Europe/Athens'}
    created_calendar = service.calendars().insert(body=calendar).execute()

# Read school duration
start_date = date_read(data["school-days"][0]["start_date"])
end_date = date_read(data["school-days"][0]["end_date"])

# Read no school dates:
no_school_days = set()
for i in data["dates"]:
    if i["end_date"] == "":
        no_school_days.add(date_read(i["start_date"]))
    else:
        date1 = date_read(i["start_date"])
        date2 = date_read(i["end_date"])

        for each_date in daterange(date1, date2):
            no_school_days.add(each_date)

# Set up weekly program
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
courses_per_day = [[] for i in range(len(weekdays))]

for count, day in enumerate(weekdays):
    (courses_per_day[count]).extend(
        [i for i in data["courses"] if i["weekday"] == day])

# Add events
for each_date in daterange(start_date, end_date):
    if (each_date.weekday() in [5, 6]) or (each_date in no_school_days):
        continue
    courses = courses_per_day[each_date.weekday()]
    for course in courses:
        event = {
            'summary': course["course"],
            'location': course["location"],
            'colorId': "4" if "ΕΡΓ" in course["course"] else '5',
            'start': {
                'dateTime':
                datetime.combine(each_date,
                                 time_read(course["start_time"])).isoformat(),
                'timeZone':
                'Europe/Athens',
            },
            'end': {
                'dateTime':
                datetime.combine(each_date,
                                 time_read(course["end_time"])).isoformat(),
                'timeZone':
                'Europe/Athens',
            },
        }

        if cal_id == "":
            event = service.events().insert(calendarId=created_calendar['id'],
                                            body=event).execute()
        else:
            event = service.events().insert(calendarId=cal_id,
                                            body=event).execute()
print("Done!")
