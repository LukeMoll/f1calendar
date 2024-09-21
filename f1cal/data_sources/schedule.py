"""
    Interfacing with https://github.com/sportstimes/f1 (available at https://f1calendar.com/)
"""

import icalendar

import requests

__all__ = ["get_next_grand_prix", "get_all_upcoming_grands_prix"]

# This URL doesn't include Sprint races; will need to update to handle that.
URL = "https://files-f1.motorsportcalendars.com/f1-calendar_gp.ics"

def fetch_ics() -> icalendar.Calendar:
    # Fetch the URL
    res = requests.get(URL)
    # Decode the ICS

    # TODO: check response code?
    # otherwise throw an exception so the caller can say "data unavailable" or something

    ics = icalendar.Calendar.from_ical(res.content)
    
    return ics

def get_next_grand_prix():
    ics = fetch_ics()

    

    # Find the next Event that isn't in the past
    # Depending on how convenient the `icalendar` object is to work with, we could define a new object
    # to deal with F1 events.

def get_all_upcoming_grands_prix():
    ...
    # Probably need to define some logic for whether we're interested in this season or next season
    # For now, can return all the Events between now and the end of the calendar year.