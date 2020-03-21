# Insert your school's timetable in Google Calendar

## Installation
You have to clone the repo in your machine and then install the required modules found in the [requirements file](./requirements.txt). Also you have to go to [Google's calendar api site](https://developers.google.com/calendar), enable the api and copy credentials.json file in your folder.

## Usage
Change the [program.json](./program.json) file as you see fitting and run [main.py](./main.py)

## Configure Program.json
<ul>
<li>calendar_data: Insert either calendar_name or calendar_id. If you don't insert either of those default is calendar_name="timetable".</li>
<li>school_dates: insert when semester starts and when ends.</li>
<li>dates: insert when there are non school dates (if end_date="" then the event is configured only for one day).</li>
<li>courses: add courses name, day, start_time, end_time and location).</li>
</ul>

__Dates should have the Year/ Month/ Day format. </br>
Hour should have the 24h format.__
