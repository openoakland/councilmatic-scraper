import os
import pytest
import pickle

from pupa.scrape.bill import Bill

from oakland import Oakland
from oakland.events import OaklandEventScraper
from .util import *

def create_event_scraper():
    jurisdiction = load_jurisdiction()
    datadir = os.path.join(os.getcwd(), 'tests/_data')
    return OaklandEventScraper(jurisdiction, datadir)

def load_event_agendas():
    event_agendas = []
    for i in range(30):
        curr_event_agenda = pickle.load(open("tests/data/event_agenda/event_agenda_%d.p" % i, "rb"))
        event_agendas.append(curr_event_agenda)

    return event_agendas

es = create_event_scraper()
event_agendas = load_event_agendas()

# TODO: implement unit test
def test_parse_event_name():
    assert False

def test_parse_meeting_date():
    event = event_agendas[0]['event']

    print("###test_parse_meeting_date - event:", event)
    print("###test_parse_meeting_date - event['Meeting Date']:", event['Meeting Date'])
    print("###test_parse_meeting_date - event['iCalendar']['url']:", event['iCalendar']['url'])
    event_date = es._parse_meeting_date(event['Meeting Date'], event['iCalendar']['url'])

    print("###test_parse_meeting_date - event_date:", event_date)
    
    assert event_date.year == 2017 and event_date.month == 12 and event_date.day == 14

# TODO: implement unit test    
def test_parse_meeting_location():
    assert False

# TODO: implement unit test    
def test_parse_meeting_status():
    assert False

# TODO: agenda can be a generator so pickling isn't working right. Come up with another way to unit test this
"""
def test_process_event_agenda():
    event, agenda = event_agendas[0]['event'], event_agendas[0]['agenda']

    print("###test_process_event_agenda - event:", event)
    print("###test_process_event_agenda - agenda:", agenda)    
    
    obj = es._process_event_agenda(event, agenda).__next__()
    print("###test_process_event_agenda - obj:", type(obj), obj)
    
    assert False
"""
