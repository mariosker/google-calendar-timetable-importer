from __future__ import print_function

import datetime
import json
import os.path
import pickle
from datetime import *

from dateutil.relativedelta import *
from dateutil.rrule import *
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DATE_FORMAT = '%d/%m/%Y'
ΤΙΜΕΖΟΝΕ = "Europe/Athens"
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = None
lab_calendar = None
theory_calendar = None


def api_service():
    global service

    creds = None
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
    get_calendars()


def get_calendars():
    global theory_calendar
    global lab_calendar

    calendar_list = service.calendarList().list(pageToken=None).execute()
    for count, calendar_list_entry in enumerate(calendar_list['items']):
        print(str(count + 1) + ")", calendar_list_entry['summary'])

    theory_choice = int(input("Choose calendar for theory: ")) - 1
    theory_calendar = calendar_list['items'][theory_choice]['id']

    lab_choice = int(input("Choose calendar for lab: ")) - 1
    lab_calendar = calendar_list['items'][lab_choice]['id']


def get_data_from_json(filename):
    with open(filename, "r", encoding='utf8') as f:
        data = json.load(f)

    return data


def get_dates():
    holidays_file = input("Enter the holidays json: ")
    holidays = get_data_from_json(holidays_file)

    courses_file = input("Enter the courses json: ")
    courses = get_data_from_json(courses_file)

    return (holidays, courses)


def get_duration():
    start_date = input("When should the first event take place: ")
    end_date = input("When should the last event take place: ")
    start_date = datetime.strptime(start_date, DATE_FORMAT)
    end_date = datetime.strptime(end_date, DATE_FORMAT)
    return (start_date, end_date)


def process_holidays(holidays):
    days = set()
    for entry in holidays:
        if entry['end_date'] == '':
            days.add(datetime.strptime(entry['start_date'], DATE_FORMAT))
        else:
            start_date = datetime.strptime(entry['start_date'], DATE_FORMAT)
            end_date = datetime.strptime(entry['end_date'], DATE_FORMAT)
            for dt in rrule(DAILY, dtstart=start_date, until=end_date):
                days.add(dt)
    return days


def process_courses(courses):
    timetable = []
    for weekday in ["monday", "tuesday", "wednessday", "thursday", "friday"]:
        timetable.append(
            [entry for entry in courses if entry["weekday"] == weekday])
    return timetable


def add_course(day, course):
    start_date = day.replace(hour=int(course["start_time"][0:2]),
                             minute=int(course["start_time"][3:]))
    end_date = day.replace(hour=int(course["end_time"][0:2]),
                           minute=int(course["end_time"][3:]))
    event = {
        'summary': course['name'],
        'location': course["location"],
        'description': course['description'],
        'start': {
            'dateTime': start_date.isoformat(),
            'timeZone': ΤΙΜΕΖΟΝΕ,
        },
        'end': {
            'dateTime': end_date.isoformat(),
            'timeZone': ΤΙΜΕΖΟΝΕ,
        }
    }
    event = service.events().insert(
        calendarId=lab_calendar if
        (course['type'] == "lab") else theory_calendar,
        body=event).execute()


def add_courses(timetable, holidays, start_date, end_date):
    for day in rrule(DAILY, dtstart=start_date, until=end_date):
        if day in holidays or day.weekday() >= 5:
            continue
        else:
            for course in timetable[day.weekday()]:
                add_course(day, course)


def main():
    api_service()
    (start_date, end_date) = get_duration()
    (holidays, courses) = get_dates()
    holidays = process_holidays(holidays)
    timetable = process_courses(courses)
    add_courses(timetable, holidays, start_date, end_date)


if __name__ == "__main__":
    main()
