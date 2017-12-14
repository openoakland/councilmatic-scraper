import os
import pytest

from pupa.scrape.bill import Bill

from oakland import Oakland
from oakland.bills import OaklandBillScraper

import pickle

def load_jurisdiction():
    juris = pickle.load( open( "tests/data/juris/juris.p", "rb" ) )
    print("###load_jurisdiction:", juris)

    return juris

def create_bill_scraper():
    jurisdiction = load_jurisdiction()
    datadir = os.path.join(os.getcwd(), 'tests/_data')
    return OaklandBillScraper(jurisdiction, datadir)

def load_leg_summaries():
    leg_summaries = []
    for i in range(7):
        curr_leg_summary = pickle.load(open("tests/data/leg_summary/leg_summary_%d.p" % i, "rb"))
        leg_summaries.append(curr_leg_summary)

    return leg_summaries
    
obs = create_bill_scraper()
leg_summaries = load_leg_summaries()

# TODO: implement unit test
def test_sessions():
    assert False

def test_parse_date_str():
    leg_summary = leg_summaries[0]
    raw_file_created = leg_summary['File\xa0Created']
    print("###test_parse_date_str - raw_file_created:", raw_file_created)
    
    parsed_file_created = obs._parse_date_str(raw_file_created)
    print("###test_parse_date_str - parsed_file_created:", type(parsed_file_created), parsed_file_created)
    
    assert parsed_file_created.year == 2017 and parsed_file_created.month == 11 and parsed_file_created.day == 30

# TODO: implement unit test
def test_parse_title():
    assert False

# TODO: implement unit test    
def test_get_sponsor_entity_type():
    assert False

# TODO: implement unit test    
def test_sponsors():
    assert False

# TODO: implement unit test    
def test_parse_action_description():
    assert False

# TODO: implement unit test    
def test_parse_responsible_org():
    assert False

# TODO: implement unit test    
def test_parse_referred_committee():
    assert False

@pytest.mark.django_db
def test_process_legistlation():    
    print("###test_process_legistlation - leg_summaries[0]:", leg_summaries[0])

    print("###test_process_legistlation - obs:", type(obs), obs)
    #print("###test_process_legistlation - obs:", dir(obs))
    bill = obs._process_legistlation(leg_summaries[0]).__next__()

    print("###test_process_legistlation - bill:", type(bill), bill)    
    assert isinstance(bill, Bill)

    #print("###test_process_legistlation - bill:", dir(bill))

    for attrib_name in [x for x in dir(bill) if not x.startswith('_') and not x.startswith('add_')]:
        print("###%s:" % attrib_name, getattr(bill, attrib_name))

    # TODO: add more assertions
    assert len(bill.classification) == 1 and bill.classification[0] == 'resolution'
    assert len(bill.documents) == 1 and bill.documents[0]['note'] == 'View Report'
    assert bill.identifier == '17-0451'
    assert bill.legislative_session == '2014'
    assert bill.title == 'Cannabis Regulatory Commission'
    

    
