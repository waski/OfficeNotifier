from db import *

dao = OfficeNotifierDAO() 

print """
USAGE:
    dao.addUser( .........adding new user
    dao.addGroup( ........adding new group
    dao.addUser2Group ....creating user's membership
    
    dao.getUsers() .......prints list of users
    dao.getGroups() ......prints list of groups

    and so on...

    Try to type "dao." to see more of its options
"""

def printUsers():
    for u in dao.getUsers():
        print "%d\t%s\t\t%s\t\t%s" % (u.id, u.name, u.gsm, u.ip)


