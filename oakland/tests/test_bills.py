import os
import pytest

from pupa.scrape import Bill as ScrapeBill
from pupa.scrape import Person as ScrapePerson
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers import BillImporter, OrganizationImporter, PersonImporter
from opencivicdata.core.models import Jurisdiction, Person, Organization, Membership, Division
from opencivicdata.legislative.models import Bill

from oakland.bills import OaklandBillScraper

def create_jurisdiction():
    Division.objects.create("ocd-division/country:us/state:ca/place:oakland", name='USA')
    j = Jurisdiction.objects.create(id='jid', division_id='ocd-division/country:us')
    j.legislative_sessions.create(identifier='1899', name='1899')
    j.legislative_sessions.create(identifier='1900', name='1900')

    return j

def create_org():
    return Organization.objects.create(id='org-id', name='House', classification='lower',
                                       jurisdiction_id='jid')    


@pytest.mark.django_db
def test_remove_tags():
    jurisdiction = create_jurisdiction()
    datadir = os.path.join(os.getcwd(), 'tests/_data')
    obs = OaklandBillScraper(jurisdiction, datadir)

    tag_text = "<foo>bar</foo>"
    tagless_text = "bar"

    # TODO: Maybe remove_tags() should be changed to a class method so an OaklandBillScraper object doesn't need to be instantiated.
    assert obs.remove_tags(tag_text) == tagless_text


    
