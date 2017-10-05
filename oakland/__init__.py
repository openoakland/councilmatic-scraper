# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import OaklandEventScraper
# from .bills import OaklandBillScraper
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
    # "bills": OaklandBillScraper,
    # "vote_events": OaklandVoteEventScraper,
  }

  def get_organizations(self):
    org = Organization(name=self.ORGANIZATION_NAME, classification="legislature")

    # add the standard city council positions
    for x in range(1,8):
        org.add_post(label=f"Council District {x}", role="Councilmember")

    # add the at large position
    org.add_post(label="Councilmember At Large", role="Councilmember")
    yield org
