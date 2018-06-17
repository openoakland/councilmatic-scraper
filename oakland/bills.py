from legistar.bills import LegistarBillScraper
from pupa.scrape import Bill, VoteEvent, Organization, Person
from pupa.utils import _make_pseudo_id
from .util import *
from .const import ORGANIZATION_NAME

from datetime import datetime
from collections import defaultdict
from pytz import timezone
import re

class OaklandBillScraper(LegistarBillScraper):
    LEGISLATION_URL = 'https://oakland.legistar.com/Legislation.aspx'
    BASE_URL = "https://oakland.legistar.com/"
    TIMEZONE = "US/Pacific"

    VOTE_OPTIONS = {'abstained': 'abstain',
                    'aye' : 'yes',
                    'nay' : 'no',
                    'conflict' : 'absent',
                    'maternity': 'excused',
                    'paternity' : 'excused',
                    'bereavement': 'excused',
                    'non-voting' : 'not voting',
                    'jury duty' : 'excused',
                    'absent' : 'absent',
                    'medical' : 'excused',
                    'vacant': 'absent',
                    'recused': 'excused'}
    
    SESSION_STARTS = (2014, 2010, 2006, 2002, 1996)

    def __init__(self, *args, **kwargs):
        super(LegistarBillScraper, self).__init__(*args, **kwargs)

        self.added_organizations = set()
        self.added_people = set()
        
    def scrape(self):
        cutoff_year = self.now().year - 2
        cnt = 0

        #search_text = "Subject:FY 2017-19 Mayor And Council Budget Priorities From"
        #for leg_summary in self.legislation(search_text=search_text, created_after=datetime(2016, 1, 1)):
        for leg_summary in self.legislation(created_after=datetime(cutoff_year, 1, 1)):
            cnt += 1

            print("###scrape - leg_summary:", leg_summary)

            """
            if cnt > 5:
                raise StopIteration
            else:
                yield self._process_legistlation(leg_summary)
            """
            yield self._process_legistlation(leg_summary)
            
            
    def _process_legistlation(self, leg_summary):
        # get legDetails because sometimes title is missing from leg_summary
        leg_details = self.legDetails(leg_summary['url'])
            
        leg_type = BILL_TYPES[leg_summary['Type']]
        file_number = leg_summary['File\xa0#']

        title = self._parse_title(leg_summary['Title'])
        if title == '':
            # if title is missing from leg_summary, try to get it from leg_details
            title = self._parse_title(leg_details['Title'])

            if title == '':
                title = '***UNKNOWN***'
                
        assert (title != '')

        file_created_dt = self._parse_date_str(leg_summary['File\xa0Created'])
        legislative_session = self._sessions(file_created_dt)
            
        bill = Bill(identifier=file_number,
                    title=title,
                    legislative_session=None,
                    classification=leg_type,
                    from_organization={"name":"Oakland City Council"})
        bill.add_source(leg_summary['url'], note='web')
        
        history = self.history(leg_summary['url'])

        if leg_details['Name']:
            bill.add_title(leg_details['Name'], note='created by administrative staff')

        if 'Summary' in leg_details :
            bill.add_abstract(leg_details['Summary'], note='')

        bill.add_identifier(file_number, note='File number')

        raw_sponsors = leg_details.get('Sponsors', [])

        for sponsor, sponsorship_type, primary, entity_type in self._sponsors(raw_sponsors):
            # hack to make sure sponsor is in the db before creating the billsponsorship
            if (entity_type == 'organization' and sponsor != ORGANIZATION_NAME and 
                sponsor not in self.added_organizations and 
                not does_organization_exist(sponsor)):

                self.added_organizations.add(sponsor)
                yield create_organization(sponsor, leg_summary['url'])
            """
            elif (entity_type == 'person' and sponsor not in self.added_people
                and not self._does_person_exist(sponsor)): 

                self.added_people.add(sponsor)
                yield self._create_person(sponsor, 'Sponsor', leg_summary['url'])
            """    
            bill.add_sponsorship(sponsor, sponsorship_type, entity_type, primary)

        for attachment in leg_details.get('Attachments', []) :
            if attachment['label']:
                bill.add_document_link(attachment['label'],
                                       attachment['url'],
                                       media_type="application/pdf")

        history = list(history)

        if history :
            earliest_action = min(self.toTime(action['Date']) 
                                  for action in history)

            bill.legislative_session = self._sessions(earliest_action)
        else :
            bill.legislative_session = str(self.SESSION_STARTS[0])

        action_key_set = set()
        for action in history :
            print("###action", action)
            
            action_description = action['Action']
            if not action_description :
                continue

            """
            Fix for issue with duplicate actions with:
            https://oakland.legistar.com/LegislationDetail.aspx?ID=2907735&GUID=54971489-FEBD-4066-8E6F-524BF00E409A&Options=ID|Text|&Search=Subject%3a%09FY+2017-19+Mayor+And+Council+Budget+Priorities+From%3a%09Office+Of+The+City+Administrator+Recommendation
            Key off of "Action By" and "Action". Only keep the first action seen. 
            """
            action_by = action['Action\xa0By']
            action_key = '%s|%s' % (action_by, action_description)
            if action_key in action_key_set:
                continue
            else:
                action_key_set.add(action_key)
            
            action_class = ACTION_CLASSIFICATION[self._parse_action_description(action_description)]
            action_date = self.toDate(action['Date'])
            responsible_org = self._parse_responsible_org(action['Action\xa0By'])

            if responsible_org == 'Town Hall Meeting':
                continue
            else :                    
                act = bill.add_action(action_description,
                                      action_date,
                                      organization={'name': responsible_org},
                                      classification=action_class)

            if 'url' in action['Action\xa0Details']:
                action_detail_url = action['Action\xa0Details']['url']
                
                if action_class == 'referral-committee' :
                    action_details = self.actionDetails(action_detail_url)
                    referred_committee = self._parse_referred_committee(action_details['Action text'])
                        
                    act.add_related_entity(referred_committee,
                                           'organization',
                                           entity_id = _make_pseudo_id(name=referred_committee))

                # Voting events
                result, votes = self.extractVotes(action_detail_url)

                if result and votes :
                    action_vote = VoteEvent(legislative_session=bill.legislative_session, 
                                            motion_text=action_description,
                                            organization={'name': responsible_org},
                                            classification=action_class,
                                            start_date=action_date,
                                            result=result,
                                            bill=bill)
                    action_vote.add_source(action_detail_url, note='web')
                    
                    for option, voter in votes :
                        action_vote.vote(option, voter)


                    yield action_vote
            
        text = self.text(leg_summary['url'])

        if text :
            bill.extras = {'local_classification' : leg_summary['Type'],
                           'full_text' : remove_tags(text)}
        else :
            bill.extras = {'local_classification' : leg_summary['Type']}

        yield bill

    def extractVotes(self, action_detail_url) :
        action_detail_page = self.lxmlize(action_detail_url)
        try:
            vote_table = action_detail_page.xpath("//table[@id='ctl00_ContentPlaceHolder1_gridVote_ctl00']")[0]
        except IndexError:
            self.warning("No votes found in table")
            return None, []
        votes = list(self.parseDataTable(vote_table))
        vote_list = []
        
        for vote, _, _ in votes :
            raw_option = vote['Vote'].lower()
            print("###extractVotes - raw_option:", raw_option)
            
            if 'label' in vote['Person Name']:
                vote_list.append((self.VOTE_OPTIONS.get(raw_option, raw_option), 
                                  vote['Person Name']['label']))
            else:
                vote_list.append((self.VOTE_OPTIONS.get(raw_option, raw_option), 
                                  vote['Person Name']))            

        action_detail_div = action_detail_page.xpath(".//div[@id='ctl00_ContentPlaceHolder1_pageTop1']")[0]
        action_details = self.parseDetails(action_detail_div)
        result = action_details['Result'].lower()

        return result, vote_list
        
    def _sessions(self, action_date) :
        for session in self.SESSION_STARTS :
            if action_date >= datetime(session, 1, 1, tzinfo=timezone(self.TIMEZONE)) :
                return str(session)

    def _parse_date_str(self, date_str):
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        dt = dt.replace(tzinfo=timezone(self.TIMEZONE))

        return dt
            
    def _parse_title(self, raw_title):
        # match in between Subject and From
        p = re.compile("Subject:(.*?)Fro+m:", re.DOTALL | re.MULTILINE)
        m = p.match(raw_title)
        if m:
            parsed_title = remove_multiple_spaces(m.group(1))
        else:
            # match in between Subject and From
            p = re.compile("Subject:(.*?)$", re.DOTALL | re.MULTILINE)
            m = p.match(raw_title)
            if m:
                parsed_title = remove_multiple_spaces(m.group(1))
            else:
                parsed_title = remove_multiple_spaces(raw_title)

        if parsed_title == '':
            # handle case where there's a "Subject:" and a "From:" but the subject is empty
            parsed_title = remove_multiple_spaces(raw_title)
        else:
            assert ("Subject:" not in parsed_title), "###_parse_title - raw_title: %s" % raw_title

        return parsed_title

    def _get_sponsor_org_cnt(self, sponsor_name):
        lower_sponsor_name = sponsor_name.lower()

        cnt = 0
        for org_keyword in ['depart', 'office', 'commission', 'oakland', 'public']:
            if org_keyword in lower_sponsor_name:
                cnt += 1

        return cnt
    
    def _get_sponsor_entity_type(self, sponsor_name):
        if self._get_sponsor_org_cnt(sponsor_name) > 0:
            return 'organization'
        else:
            return 'person'

    def _sponsors(self, sponsors) :
        def clean_sponsor(sponsor):
            sponsor = sponsor.replace('&', ' and ')
            return remove_multiple_spaces(sponsor)
            
        if isinstance(sponsors, str):
            if ',' in sponsors:
                _sponsors = remove_multiple_spaces(sponsors)
                sponsors = []
                for sponsor in _sponsors.split(','):
                    sponsor = clean_sponsor(sponsor)
                    if sponsor != '':
                        sponsors.append({'label': sponsor}) 
            else:
                sponsors = [{'label': clean_sponsor(sponsors)}]

        for i, sponsor in enumerate(sponsors) :
            if i == 0 :
                primary = True
                sponsorship_type = "Primary"
            else :
                primary = False
                sponsorship_type = "Regular"
            
            sponsor_name = sponsor['label']
            if sponsor_name.startswith(('(in conjunction with',
                                        '(by request of')) :
                continue 
            
            entity_type = self._get_sponsor_entity_type(sponsor_name)
                
            yield sponsor_name, sponsorship_type, primary, entity_type

    def _parse_action_description(self, action_description):
        action_description = action_description.replace('*', '')

        return remove_multiple_spaces(action_description)

    def _parse_responsible_org(self, raw_responsible_org):
        if raw_responsible_org == 'City Council' :
            return 'Oakland City Council'
        elif raw_responsible_org == 'Administration' :
            return 'Mayor'

        responsible_org = parse_org(raw_responsible_org)

        if responsible_org == '':
            # Sometimes the responsible_org is missing. Default to Oakland City Council.
            # i.e. https://oakland.legistar.com/LegislationDetail.aspx?ID=3033419&GUID=F2ABDA03-BFBC-4663-84CC-8AF0B2C15C08&Options=ID|Text|&Search=Of+Intention+To+Form+The+Koreatown%2fNorthgate+Community+Benefit+District+2017
            # 5/16/2017
            responsible_org = 'Oakland City Council'

        assert (responsible_org != '')
        return responsible_org

    def _parse_referred_committee(self, raw_reffered_committed):
        referred_committee = parse_org(raw_reffered_committee.rsplit(' to the ', 1)[-1])

        if referred_committee == '':
            # default to Oakland City Council
            referred_committee = 'Oakland City Council'

        assert (referred_committee != '')
        return referred_committee
        
    def _does_person_exist(self, person_name):
        from opencivicdata.core.models import Person

        # handle the special case for "Larry Reid"
        if person_name == "Larry Reid" or person_name == "Laurence E. Reid":
            person_queryset1 = Person.objects.filter(name="Larry Reid")
            person_queryset2 = Person.objects.filter(name="Laurence E. Reid")

            return (person_queryset1.count() + person_queryset2.count() > 0)

        # filter Lynette McElhaney (should be added already in people.py)
        if person_name == "Lynette McElhaney":
            return True
        
        person_queryset = Person.objects.filter(name=person_name)
        
        return (person_queryset.count() > 0)

    def _create_person(self, person_name, role, source):
        # Setting birth_date to 'unknown' because of issue with 'Larry Reid' and pupa.importers._prepare_imports().
        # A SameNameError exception gets thrown there is more than one person with the same name and a least one of
        # the person's birth_date's is ''. opencivicdata.birth_date is a varchar. Using the sentinel date, '1900-01-01'.
        person = Person(name=person_name, role=role, birth_date='1900-01-01')
        person.add_source(source)

        # If the person came through from people.py, he or she would belong to a committee (organization).  Since we don't know
        # the committee that the person belongs to, just add them to "unknown".  Otherwise, you'll get the following error:
        #   File "/home/postgres/councilmatic/lib/python3.4/site-packages/pupa/importers/memberships.py", line 62, in postimport
        #     raise NoMembershipsError(person_ids)
        person.add_membership('Unknown')
        
        return person

BILL_TYPES = {'Informational Report': None,
              'City Resolution': 'resolution',
              'Report and Recommendation': None,
              'Ordinance': None,
              'ORSA Resolution': 'resolution'
          }

ACTION_CLASSIFICATION = {
    'Accepted': 'passage',
    'Accepted as Amended': 'amendment-passage',
    'Adopted': 'passage',
    'Adopted as Amended': 'amendment-passage',
    'Approved as Amended on Introduction for Final Passage': 'amendment-passage',
    'Approve with the following amendments': 'amendment-passage',
    'Approve as Submitted': 'passage',
    'Approved': 'passage',
    'Approved as Amended': 'amendment-passage',
    'Approved as Amended the Recommendation of Staff, and Forward': 'passage',
    'Approved As Amended On Introduction and Scheduled for Final Passage': 'amendment-passage',    
    'Approved for Final Passage': 'passage',
    'Approved On Introduction and Scheduled for Final Passage': 'committee-passage',
    'Approved the Recommendation of Staff, and Forward': 'committee-passage',
    'Continued': None,
    'Denied': 'failure',
    'Filed': 'filing',
    'Forwarded with No Recommendation': None,
    'In Committee': None,
    'In Council': None,
    'No Action Taken': None,
    'Not Adopted': 'failure',
    'Passed': 'passage',
    'Received and Filed': 'filing',
    'Received and Forwarded': 'filing',
    'Referred': 'introduction',
    'Rescheduled': 'withdrawal',
    'Scheduled': 'filing',
    'To be Scheduled': 'introduction',
    'Withdrawn and Rescheduled': 'withdrawal',
    'Withdrawn with No New Date': 'withdrawal'
}


