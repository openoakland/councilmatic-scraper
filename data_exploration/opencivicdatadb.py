import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Tables(object):
    def __init__(self):
        pass

class OpenCivicDataDB(object):
    def __init__(self, user='postgres', password='str0ng*p4ssw0rd', db='opencivicdata',
                 host='localhost', port=5432):
        self.user = user
        self.password = password
        self.db = db
        self.host = host
        self.port = port

        self.connect()
        
    def connect(self):
        '''Returns a connection and a metadata object'''
        # We connect with the help of the PostgreSQL URL
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(self.user, self.password, self.host, self.port, self.db)

        # The return value of create_engine() is our connection object   
        self.engine = sqlalchemy.create_engine(url, client_encoding='utf8')

        # We then bind the connection to MetaData()
        self.meta = sqlalchemy.MetaData(bind=self.engine, reflect=True)

        self.automap_tables()

    def automap_tables(self):
        Base = automap_base()

        # reflect the tables
        Base.prepare(self.engine, reflect=True)

        self.tables = Tables()

        self.tables.Membershipcontactdetail = Base.classes.opencivicdata_membershipcontactdetail
        self.tables.Membershiplink = Base.classes.opencivicdata_membershiplink
        self.tables.Organizationcontactdetail = Base.classes.opencivicdata_organizationcontactdetail
        self.tables.Organizationidentifier = Base.classes.opencivicdata_organizationidentifier
        self.tables.Jurisdiction = Base.classes.opencivicdata_jurisdiction
        self.tables.Organizationlink = Base.classes.opencivicdata_organizationlink
        self.tables.Organizationname = Base.classes.opencivicdata_organizationname
        self.tables.Organizationsource = Base.classes.opencivicdata_organizationsource
        self.tables.Personcontactdetail = Base.classes.opencivicdata_personcontactdetail
        self.tables.Personidentifier = Base.classes.opencivicdata_personidentifier
        self.tables.Personlink = Base.classes.opencivicdata_personlink
        self.tables.Personname = Base.classes.opencivicdata_personname
        self.tables.Personsource = Base.classes.opencivicdata_personsource
        self.tables.Membership = Base.classes.opencivicdata_membership
        self.tables.Division = Base.classes.opencivicdata_division
        self.tables.Postcontactdetail = Base.classes.opencivicdata_postcontactdetail
        self.tables.Post = Base.classes.opencivicdata_post
        self.tables.Postlink = Base.classes.opencivicdata_postlink
        self.tables.Billabstract = Base.classes.opencivicdata_billabstract
        self.tables.Billactionrelatedentity = Base.classes.opencivicdata_billactionrelatedentity
        self.tables.Billdocument = Base.classes.opencivicdata_billdocument
        self.tables.Billdocumentlink = Base.classes.opencivicdata_billdocumentlink
        self.tables.Billidentifier = Base.classes.opencivicdata_billidentifier
        self.tables.Billsource = Base.classes.opencivicdata_billsource
        self.tables.Billtitle = Base.classes.opencivicdata_billtitle
        self.tables.Billversion = Base.classes.opencivicdata_billversion
        self.tables.Billversionlink = Base.classes.opencivicdata_billversionlink
        self.tables.Billsponsorship = Base.classes.opencivicdata_billsponsorship
        self.tables.Eventagendamedia = Base.classes.opencivicdata_eventagendamedia
        self.tables.Eventagendamedialink = Base.classes.opencivicdata_eventagendamedialink
        self.tables.Eventdocument = Base.classes.opencivicdata_eventdocument
        self.tables.Eventdocumentlink = Base.classes.opencivicdata_eventdocumentlink
        self.tables.Eventparticipant = Base.classes.opencivicdata_eventparticipant
        self.tables.Eventlink = Base.classes.opencivicdata_eventlink
        self.tables.Eventmedia = Base.classes.opencivicdata_eventmedia
        self.tables.Eventmedialink = Base.classes.opencivicdata_eventmedialink
        self.tables.Eventagendaitem = Base.classes.opencivicdata_eventagendaitem
        self.tables.Relatedbill = Base.classes.opencivicdata_relatedbill
        self.tables.Eventsource = Base.classes.opencivicdata_eventsource
        self.tables.Votesource = Base.classes.opencivicdata_votesource
        self.tables.Votecount = Base.classes.opencivicdata_votecount
        self.tables.Person = Base.classes.opencivicdata_person
        self.tables.Billaction = Base.classes.opencivicdata_billaction
        self.tables.Eventlocation = Base.classes.opencivicdata_eventlocation
        self.tables.Event = Base.classes.opencivicdata_event
        self.tables.Eventrelatedentity = Base.classes.opencivicdata_eventrelatedentity
        self.tables.Personvote = Base.classes.opencivicdata_personvote
        self.tables.Bill = Base.classes.opencivicdata_bill
        self.tables.Legislativesession = Base.classes.opencivicdata_legislativesession
        self.tables.Organization = Base.classes.opencivicdata_organization
        self.tables.Voteevent = Base.classes.opencivicdata_voteevent

    def make_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def dispose(self):
        self.engine.dispose()
