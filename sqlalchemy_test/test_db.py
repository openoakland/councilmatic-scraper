from opencivicdatadb import OpenCivicDataDB

# create db object
user, password, db = ('postgres', 'str0ng*p4ssw0rd', 'opencivicdata')
db = OpenCivicDataDB(user, password, db)

print(db.engine)
print(db.meta)

# create session
session = db.make_session()

# get the person tables
Person = db.tables.Person
Personcontactdetail = db.tables.Personcontactdetail

# get column names
person_colnames = Person.__table__.columns.keys()
personcontactdetail_colnames = Personcontactdetail.__table__.columns.keys()

for person in session.query(Person).order_by(Person.id):
    print("###Person", person.id)
    print(dir(person))
    for person_colname in person_colnames:
        print("%s: [%s]" % (person_colname, getattr(person, person_colname)))

    for personcontactdetail in person.opencivicdata_personcontactdetail_collection:
        print("####personcontactdetail", personcontactdetail.id)
        for personcontactdetail_colname in personcontactdetail_colnames:
            print("%s: [%s]" % (personcontactdetail_colname, getattr(personcontactdetail, personcontactdetail_colname)))
    
        
# close session
session.close()

# close database
db.dispose()
