from legistar.people import LegistarPersonScraper
import datetime
import re
from inspect import getmembers

from pupa.scrape import Person, Organization

class OaklandPersonScraper(LegistarPersonScraper):
  MEMBERLIST = 'https://oakland.legistar.com/DepartmentDetail.aspx?ID=16958&GUID=2D327FEC-719C-41C0-B4E7-927B22957C03&R=39695131-3de7-453f-bf97-90e53ac5b592'
  TIMEZONE = "US/Pacific"
  ALL_MEMBERS = "8:8"

  def scrape(self):
    print('OaklandPersonScraper.scrape')

    for councilman, committees in self.councilMembers():
      p = Person(' '.join((councilman['First name'], councilman['Last name'])))
      print(p)
      print(councilman)
      print(committees)

      yield councilman, committees

    yield {}

