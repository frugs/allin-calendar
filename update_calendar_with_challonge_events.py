import os
import httplib2
import datetime
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import challongeservice
import dateutil.parser


SCOPES = ['https://www.googleapis.com/auth/calendar']
APPLICATION_NAME = 'Challonge Event updater'
CREDENTIALS_FILE_NAME = 'allinbotServiceAccountCredentials.json'
CHALLONGE_API_KEY = os.getenv('CHALLONGE_API_KEY', '')
TRACKED_TOURNAMENT_SUBDOMAINS = ["proxytempest", "thenydus", "all-inspiration"]
CALENDAR_ID = "3om5b2vfubpugkf3vr6fahh01k@group.calendar.google.com"


def create_calendar_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_NAME, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service


def main():
    calendar_service = create_calendar_service()
    challonge_service = challongeservice.create_service(CHALLONGE_API_KEY)

    now = datetime.datetime.now(datetime.timezone.utc)

    upcoming_tournaments = []
    for subdomain in TRACKED_TOURNAMENT_SUBDOMAINS:
        tournaments = challonge_service.tournaments().index(subdomain=subdomain)
        upcoming_tournaments.extend([
            tournament["tournament"]
            for tournament
            in tournaments
            if tournament["tournament"]["state"] == "pending"
            and dateutil.parser.parse(tournament["tournament"]["start_at"]) > now])

    for tournament in upcoming_tournaments:
        start_time = dateutil.parser.parse(tournament["start_at"])
        end_time = start_time + datetime.timedelta(hours=3)

        timeMin = start_time - datetime.timedelta(minutes=1)
        timeMax = start_time + datetime.timedelta(minutes=1)

        eventsResult = calendar_service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=timeMin.isoformat(),
            timeMax=timeMax.isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        if not events or all(map(lambda event: tournament["name"] not in event["summary"], events)):
            tournament_event = {
                "summary": "{} ({})".format(tournament["name"], tournament["full_challonge_url"]),
                "description": tournament["description"],
                "gadget.display": "icon",
                "gadget.link": tournament["full_challonge_url"],
                "gadget.iconLink": tournament["live_image_url"],
                "start": {
                    "dateTime": start_time.isoformat()
                },
                "end": {
                    "dateTime": end_time.isoformat()
                }
            }

            calendar_service.events().insert(
                calendarId='3om5b2vfubpugkf3vr6fahh01k@group.calendar.google.com',
                body=tournament_event).execute()

            print("{} added to calendar.".format(tournament["name"]))


if __name__ == "__main__":
    main()
