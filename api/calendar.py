import requests
from datetime import datetime, timedelta
from ics import Calendar, Event
from flask import Flask, Response

app = Flask(__name__)

@app.route('/calendar')
def generate_calendar():
    events_url = "https://bw.biathlonresults.com/modules/sportapi/api/Events?SeasonId=2425"
    response = requests.get(events_url)
    
    if response.status_code == 200:
        events_data = response.json()
        level_1_events = [event for event in events_data if event['Level'] == 1]
        calendar = Calendar()

        for event in level_1_events:
            event_id = event['EventId']
            competitions_url = f"https://bw.biathlonresults.com/modules/sportapi/api/Competitions?EventId={event_id}&Language=EN"
            comp_response = requests.get(competitions_url)

            if comp_response.status_code == 200:
                competitions_data = comp_response.json()

                for competition in competitions_data:
                    race_id = competition["RaceId"]
                    event_name = competition["ShortDescription"]
                    description = competition["Description"]
                    start_time_str = competition["StartTime"]
                    location = competition["Location"]
                    
                    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    end_time = start_time + timedelta(hours=1)

                    ical_event = Event()
                    ical_event.name = event_name
                    ical_event.begin = start_time
                    ical_event.end = end_time
                    ical_event.location = location
                    ical_event.description = description
                    calendar.events.add(ical_event)

        # Generate ICS file response
        ics_data = str(calendar)
        return Response(ics_data, content_type="text/calendar", headers={"Content-Disposition": "attachment;filename=ibu.ics"})
    else:
        return Response("Failed to fetch events data.", status=500)

if __name__ == '__main__':
    app.run(debug=True)
