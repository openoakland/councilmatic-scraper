# encoding=utf-8
import sys
import os

# put the oakland directory in the python path
sys.path.append("%s/oakland" % os.getcwd())

from pupa.scrape import Jurisdiction, Organization
from .events import OaklandEventScraper
from .bills import OaklandBillScraper
from .people import OaklandPersonScraper
# from .vote_events import OaklandVoteEventScraper

class Oakland(Jurisdiction):
  ORGANIZATION_NAME = "Oakland City Council"
  division_id = "ocd-division/country:us/state:ca/place:oakland"
  classification = "legislature"
  name = "City of Oakland"
  url = "https://beta.oaklandca.gov/councils/city-council"

  scrapers = {
    "events": OaklandEventScraper,
    "people": OaklandPersonScraper,
    "bills": OaklandBillScraper
  }

  legislative_sessions = [{"identifier": str(start_year),
                           "name": ("%s Regular Session" % str(start_year)),
                           "start_date": ("%s-01-01" % str(start_year)),
                           "end_date": ("%s-12-31" % str(start_year + 3))}
                          for start_year
                          in range(1978, 2015, 4)]
  
  def get_organizations(self):
    org_names = [self.ORGANIZATION_NAME,
                 "Community and Economic Development Committee",
                 "Concurrent Meeting of the Oakland Redevelopment Successor Agency and Finance and Management Committee"
                 "Concurrent Meeting of the Oakland Redevelopment Successor Agency and the Community and Economic Development Committee",
                 "Finance and Management Committee", 
                 "Life Enrichment Committee",
                 
                 "Oakland Redevelopment Successor Agency and the Community and Economic Development Committee",
                 "Oakland Redevelopment Successor Agency and Finance and Management Committee",
                 "Office of the Mayor Annual Recess Agenda",
                 "Public Safety Committee",                 
                 "Public Works Committee",
                 
                 "Rules and Legislation Committee",
                 "Special Community and Economic Development Committee",
                 "Special Concurrent Meeting of the Education Partnership Committee and the Oakland Unified School District Board of Education",
                 "Special Concurrent Meeting of the Oakland Redevelopment Successor Agency and Community & Economic Development Committee",
                 "Special Concurrent Meeting of the Oakland Redevelopment Successor Agency and Finance and Management Committee",
                 

                 "Special Education Partnership Committee and the Oakland Unified School District Board of Education",
                 "Special Finance and Management Committee",
                 "Special Life Enrichment Committee",
                 "Special Oakland Redevelopment Successor Agency and Community & Economic Development Committee",
                 "Special Oakland Redevelopment Successor Agency and Finance and Management Committee",

                 "Special Public Safety Committee",
                 "Special Public Works Committee"
    ]

    for org_name in org_names:
      if org_name == self.ORGANIZATION_NAME:
        # people.py tries to find the Organization from the people.primary_org but people.primary_org is only classification.
        # If there are more than one Organization in the db with classification set to "legislature", a multiple records found
        # error gets thrown.
        org = Organization(name=org_name, classification="legislature")
        
        # add the standard city council positions
        for x in range(1,8):
          org.add_post(label="Council District {}".format(x),
                       role="Councilmember")
        
        # add the at large position
        org.add_post(label="Councilmember At Large", role="Councilmember")
      else:
        # For other Organizations, just set classification to "lower". No validation check is done for "lower".  The
        # Organizations need to be there for non council events.
        org = Organization(name=org_name, classification='lower') 
      
      yield org

