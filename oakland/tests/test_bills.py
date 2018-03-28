import os
import pytest
import pickle

from pupa.scrape.bill import Bill

from oakland import Oakland
from oakland.bills import OaklandBillScraper
from .util import *

def create_bill_scraper():
    jurisdiction = load_jurisdiction()
    #datadir = os.path.join(os.getcwd(), 'tests/_data')
    datadir = os.path.join(os.getcwd(), '_data')
    return OaklandBillScraper(jurisdiction, datadir)

def load_leg_summaries():
    leg_summaries = []
    for i in range(7):
        #curr_leg_summary = pickle.load(open("tests/data/leg_summary/leg_summary_%d.p" % i, "rb"))
        curr_leg_summary = pickle.load(open("data/leg_summary/leg_summary_%d.p" % i, "rb"))
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

def test_get_sponsor_org_cnt():
    sponsor_name = "Oakland Public Library"
    assert obs._get_sponsor_org_cnt(sponsor_name) > 0

    sponsor_name = "Larry Reid"    
    assert obs._get_sponsor_org_cnt(sponsor_name) == 0
    
def test_get_sponsor_entity_type():
    sponsor_name = "Oakland Public Library"
    assert obs._get_sponsor_entity_type(sponsor_name) == 'organization'

    sponsor_name = "Larry Reid"
    assert obs._get_sponsor_entity_type(sponsor_name) == 'person'    

def test_sponsors():
    # Test #1 - 2 organizations separated by a comma
    sponsors = 'Office Of The City Attorney, Oakland Police Department'

    expected = [('Office Of The City Attorney', 'Primary', True, 'organization'),
                ('Oakland Police Department', 'Regular', False, 'organization')]

    i = 0
    for sponsor_name, sponsorship_type, primary, entity_type in obs._sponsors(sponsors):
        expected_sponsor_name, expected_sponsorship_type, expected_primary, expected_entity_type = expected[i]

        assert sponsor_name == expected_sponsor_name
        assert sponsorship_type == expected_sponsorship_type
        assert primary == expected_primary
        assert entity_type == expected_entity_type
        
        i += 1

    # Test #2
    sponsors = 'Oakland Police Department,'

    expected = [('Oakland Police Department', 'Primary', True, 'organization')]

    i = 0
    for sponsor_name, sponsorship_type, primary, entity_type in obs._sponsors(sponsors):
        expected_sponsor_name, expected_sponsorship_type, expected_primary, expected_entity_type = expected[i]

        assert sponsor_name == expected_sponsor_name
        assert sponsorship_type == expected_sponsorship_type
        assert primary == expected_primary
        assert entity_type == expected_entity_type
        
        i += 1

    assert i == 1

# TODO: implement unit test    
def test_parse_action_description():
    assert False

# TODO: implement unit test    
def test_parse_responsible_org():
    assert False

# TODO: implement unit test    
def test_parse_referred_committee():
    assert False

# TODO: implement unit test
def test_does_organization_exist():
    assert False

@pytest.mark.django_db    
def test_does_person_exist():
    from opencivicdata.core.models import Person
    
    b = Person(name='Phil Chin')
    b.save()

    #assert obs._does_person_exist("Larry Reid")
    assert obs._does_person_exist("Phil Chin")

    assert not obs._does_person_exist("Foo Bar")

@pytest.mark.django_db    
# TODO: implement unit test
def test_create_organization():
    assert False

#@pytest.mark.django_db
def test_create_person():
    person = obs._create_person('Phil Chin', 'http://openoakland.org')

    schema = person._schema
    person_dict = person.as_dict()

    try:
        result = person.validate()
    except Exception:        
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


    
