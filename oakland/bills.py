from legistar.bills import LegistarBillScraper
from pupa.scrape import Bill, VoteEvent
from pupa.utils import _make_pseudo_id
from datetime import datetime
from collections import defaultdict
from pytz import timezone
import re

class OaklandBillScraper(LegistarBillScraper):
    LEGISLATION_URL = 'https://oakland.legistar.com/Legislation.aspx'
    BASE_URL = "https://oakland.legistar.com/"
    TIMEZONE = "US/Pacific"

    VOTE_OPTIONS = {'affirmative' : 'yes',
                    'negative' : 'no',
                    'conflict' : 'absent',
                    'maternity': 'excused',
                    'paternity' : 'excused',
                    'bereavement': 'excused',
                    'non-voting' : 'not voting',
                    'jury duty' : 'excused',
                    'absent' : 'absent',
                    'medical' : 'excused'}
    
    TAG_RE = re.compile(r'<[^>]+>')
    
    SESSION_STARTS = (2014, 2010, 2006, 2002, 1996)

    def sessions(self, action_date) :
        for session in self.SESSION_STARTS :
            if action_date >= datetime(session, 1, 1, tzinfo=timezone(self.TIMEZONE)) :
                return str(session)

    def parse_date_str(self, date_str):
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        dt = dt.replace(tzinfo=timezone(self.TIMEZONE))

        return dt

    def scrape(self):
        cnt = 0
        
        for leg_summary in self.legislation(created_after=datetime(2014, 1, 1)):
            cnt += 1
            
            leg_type = BILL_TYPES[leg_summary['Type']]
            file_number = leg_summary['File\xa0#']
            title = self._parse_title(leg_summary['Title'])
            file_created_dt = self.parse_date_str(leg_summary['File\xa0Created'])
            legislative_session = self.sessions(file_created_dt)
            
            bill = Bill(identifier=file_number,
                        title=title,
                        legislative_session=None,
                        classification=leg_type,
                        from_organization={"name":"Oakland City Council"})
            bill.add_source(leg_summary['url'], note='web')

            leg_details = self.legDetails(leg_summary['url'])
            history = self.history(leg_summary['url'])

            if leg_details['Name']:
                bill.add_title(leg_details['Name'],
                               note='created by administrative staff')

            if 'Summary' in leg_details :
                bill.add_abstract(leg_details['Summary'], note='')

            bill.add_identifier(file_number, note='File number')

            for sponsorship in self._sponsors(leg_details.get('Sponsors', [])) :
                sponsor, sponsorship_type, primary = sponsorship
                bill.add_sponsorship(sponsor, sponsorship_type,
                                     'person', primary)

            
            for attachment in leg_details.get('Attachments', []) :
                if attachment['label']:
                    bill.add_document_link(attachment['label'],
                                           attachment['url'],
                                           media_type="application/pdf")

            history = list(history)

            if history :
                earliest_action = min(self.toTime(action['Date']) 
                                      for action in history)

                bill.legislative_session = self.sessions(earliest_action)
            else :
                bill.legislative_session = str(self.SESSION_STARTS[0])

            for action in history :
                action_description = action['Action']
                if not action_description :
                    continue
                    
                action_class = ACTION_CLASSIFICATION[action_description]

                action_date = self.toDate(action['Date'])
                responsible_org = action['Action\xa0By']
                if responsible_org == 'City Council' :
                    responsible_org = 'Oakland City Council'
                elif responsible_org == 'Administration' :
                    responsible_org = 'Mayor'
                   
                if responsible_org == 'Town Hall Meeting' :
                    continue
                else :
                    act = bill.add_action(action_description,
                                          action_date,
                                          organization={'name': responsible_org},
                                          classification=action_class)

                if 'url' in action['Action\xa0Details'] :
                    action_detail_url = action['Action\xa0Details']['url']
                    if action_class == 'referral-committee' :
                        action_details = self.actionDetails(action_detail_url)
                        referred_committee = action_details['Action text'].rsplit(' to the ', 1)[-1]
                        act.add_related_entity(referred_committee,
                                               'organization',
                                               entity_id = _make_pseudo_id(name=referred_committee))
                        
                    print("###in scraper - action_detail_url:", action_detail_url)
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
                               'full_text' : self.remove_tags(text)}
            else :
                bill.extras = {'local_classification' : leg_summary['Type']}

            """
            if cnt > 100:
                raise StopIteration
            else:
                yield bill
            """
            yield bill

    # move this later
    def remove_tags(self, text):
        return self.TAG_RE.sub('', text)

    # TODO: this was from events.py.  Change to a mixin later?
    def __remove_multiple_spaces(self, text_str):
        while "  " in text_str:
            text_str = text_str.replace('  ', ' ')
            
        return text_str

    def _parse_title(self, raw_title):
        parsed_title = raw_title.replace('Subject:', '')
        return self.__remove_multiple_spaces(parsed_title).strip()
    
    def _sponsors(self, sponsors) :
        if isinstance(sponsors, str):
            # there's only one name for sponsor
            primary = True
            sponsorship_type = "Primary"
            sponsor_name = sponsors
            yield sponsor_name, sponsorship_type, primary

            # ok - this is a little funky. Need to do this because this is a generator
            raise StopIteration
        else:
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

                yield sponsor_name, sponsorship_type, primary
                

BILL_TYPES = {'Informational Report': None,
              'City Resolution': 'resolution',
              'Report and Recommendation': None,
              'Ordinance': None,
              'ORSA Resolution': 'resolution'
          }

ACTION_CLASSIFICATION = {
    'Scheduled': 'filing',
    'In Committee': None,
    'To be Scheduled': 'introduction',
    'In Council': None,
    'Filed': 'filing',
    'Passed': 'passage',
    'Withdrawn and Rescheduled': 'withdrawal',
    'Approved the Recommendation of Staff, and Forward': 'committee-passage'
}
