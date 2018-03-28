import re
from .const import ORGANIZATION_NAME

def remove_multiple_spaces(text_str):
  """
  Remove multiple spaces from string and trim white spaces from front and back.

  Parameters
  ----------
  text_str : str
    any text string

  Returns
  -------
  string
  """
  while "  " in text_str:
    text_str = text_str.replace('  ', ' ')

  return text_str.strip()

def parse_org(org_name):
  """
  Parse and standardize organization name.

  Parameters
  ----------
  org_name : str
    raw organization name

  Returns
  -------
  string
    a standardized version of the organization name
  """
  # get rid of stray asterisk
  org_name = org_name.replace('*', ' ')

  # replace '&' with and
  org_name = org_name.replace('&', ' and ')
    
  org_name = remove_multiple_spaces(org_name)

  # remove final ','
  org_name = org_name.rstrip(',')
  
  if "City Council" in org_name:
    org_name = 'Oakland City Council'
  else:
    org_name = org_name.replace("- CANCELLED", '').replace("- CANCELLATION", '')
    org_name = remove_multiple_spaces(org_name)
      
  return org_name
  
def remove_tags(text):
  TAG_RE = re.compile(r'<[^>]+>')
  
  return TAG_RE.sub('', text)

def does_organization_exist(organization_name):
  # Doing the import here is a little icky but if you did at the beginning of the file, models.__init__.py gets loaded
  # before django has time to initialize the database.
  from opencivicdata.core.models import Organization as ORM_Organization
        
  organization_list = ORM_Organization.objects.filter(name=organization_name)
        
  return (organization_list is not None and len(organization_list) > 0)

def create_organization(organization_name, source=None):
  from pupa.scrape.popolo import Organization as Popolo_Organization

  org = Popolo_Organization(name=organization_name, classification=get_classification(organization_name))
  
  if source is not None:
    org.add_source(source)  

  return org 

def get_classification(organization_name):
  if organization_name != ORGANIZATION_NAME:
    return 'committee'
  else:
    return 'legislature'
