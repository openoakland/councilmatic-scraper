import os
import pytest
import pickle

from pupa.scrape.popolo import Person

from oakland import Oakland
from oakland.people import OaklandPersonScraper
from .util import *

def create_people_scraper():
    jurisdiction = load_jurisdiction()
    datadir = os.path.join(os.getcwd(), 'tests/_data')
    return OaklandPersonScraper(jurisdiction, datadir)
    
def load_councilmen():
    councilmen = []
    for i in range(8):
        curr_councilman = pickle.load(open("tests/data/councilman/councilman_%d.p" % i, "rb"))
        councilmen.append(curr_councilman)

    return councilmen

ps = create_people_scraper()
councilmen = load_councilmen()

# TODO: implement unit test
def test_assign_district():
    assert False

def test_process_councilman():
    councilman = councilmen[0]

    print("###test_process_councilman - councilman:", councilman)

    obj = ps._process_councilman(councilman).__next__()

    print("###test_process_councilman - obj:", type(obj), obj)
    
    assert isinstance(obj, Person)

    # TODO: add more assertions




