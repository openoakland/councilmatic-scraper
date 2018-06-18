# encoding=utf-8
import sys
import os

# put the oakland directory in the python path
sys.path.append("%s/oakland" % os.getcwd())

from pupa.scrape import Jurisdiction, Organization
from .events import OaklandEventScraper
from .bills import OaklandBillScraper
from .people import OaklandPersonScraper
from .const import ORGANIZATION_NAME
from .util import *

class Oakland(Jurisdiction):
  ORGANIZATION_NAME = ORGANIZATION_NAME
  division_id = "ocd-division/country:us/state:ca/place:oakland"
  classification = "legislature"
  name = "City of Oakland"
  url = "https://beta.oaklandca.gov/councils/city-council"

  scrapers = {
    #"events": OaklandEventScraper,
    #"people": OaklandPersonScraper,
    "bills": OaklandBillScraper
  }

  legislative_sessions = [{"identifier": str(start_year),
                           "name": ("%s Regular Session" % str(start_year)),
                           "start_date": ("%s-01-01" % str(start_year)),
                           "end_date": ("%s-12-31" % str(start_year + 3))}
                          for start_year
                          in range(1978, 2015, 4)]

  # TODO: should organizations get added to the database on a get??? Maybe, there's a better place
  # for this like in the constructor. New organizations seem to get created all the time. Maybe, they
  # should get dynamically created during scrape() for events and bills.
  def get_organizations(self):
    org_names = [self.ORGANIZATION_NAME,
                 "Special Education Partnership Committee",
                 "Special Rules and Legislation Committee",
                 "Unknown"]

    for org_name in org_names:
      org = create_organization(org_name, 'https://oakland.legistar.com')
        
      # add the standard city council positions
      for x in range(1,8):
        org.add_post(label="Council District {}".format(x), role="Councilmember")
        
      # add the at large position
      org.add_post(label="Councilmember At Large", role="Councilmember")

      yield org

