import re

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
