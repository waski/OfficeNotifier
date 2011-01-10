# db.py
#       
# Copyright 2011 Satanowski <satanowski@gmail.com>
#       
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# --*-- encoding:utf-8 --*--


from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from datetime import datetime
import logging as log
import inspect
import hashlib

log.basicConfig(level=log.INFO)

Base = declarative_base()


class User(Base):
    """User class.
User is defined by following: id(id), name(name), phone number(gsm) and 
ip adress (ip). """

    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    name = Column(String)
    gsm  = Column(String)
    ip = Column(String(15))
    hashstring = Column(String(40))
    lastping = Column(DateTime, nullable=True)

    def __init__(self, name, gsm, ip):
        self.name = name
        self.gsm = gsm
        self.ip = ip
        self.hashstring = hashlib.sha1(name+str(gsm)+ip+str(self.__hash__())).hexdigest()
        self.lastping = None;
 
    def __repr__(self):
        return "<User('%s','%s', '%s', '%s', '%s')>" % (self.name, self.gsm, self.ip, self.lastping, self.hashstring)

    def getGroups(self):
        """Returns list of group objects which user is member of."""
        return [m.group for m in self.membership]

   
    def belongs2(self, group):
        """Returns True if user is a member of given group."""
        if group:
            return group in self.getGroups()
   
    def _updatePing(self):
        self.lastping = datetime.now()
        
    def getRelatedUsers(self):
        """Returns list of members of all groups the users is member of"""
        alist = []
        for g in self.getGroups():
            for u in g.getUsers():
                if u not in alist:
                    alist.append(u)
        return alist



class Billing(Base):
    """Holds time and content of message sent to particular user"""

    __tablename__ = "bilings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    time = Column(DateTime, nullable=False)
    sms = Column(String, nullable=False)
 
    user = relation(User, backref=backref('billings', order_by=id))

    def __init__(self, user_id, sms):
        self.user_id = user_id
        self.sms = sms
        self.time = datetime.now()
 
    def __repr__(self):
        return "<Billing('%s:%s')>" % (self.time, self.sms)


 
class Group(Base):

    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __init__(self, name):
        self.name = name
 
    def __repr__(self):
        return "<Group('%s')>" % (self.name,)

    def getUsers(self):
        """Returns list of users that are members of this group."""
        return [m.user for m in self.membership]



class Membership(Base):
    """Defines user's group membership."""

    __tablename__ = "membership"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    
    user  = relation(User, backref=backref('membership', order_by=id))
    group = relation(Group, backref=backref('membership', order_by=id))

    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
 
    def __repr__(self):
        return "<Membership('%s:%s')>" % (self.user_id, self.group_id)



class OfficeNotifierDAO(object):
    """Simple class grouping methods needed to operate on sqlite DB"""

    DB_FILE = "notifier.db"

    def __init__(self,uri=None):      
        self.engine = create_engine(
        uri or "sqlite:///%s" % (self.DB_FILE,), echo=False)
        self.metadata = Base.metadata
        self.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()


    def getUsers(self):
        """Return list of user objects"""
        return self.session.query(User).all() or []


    def getUserById(self, user_id):
        """Returns object of user of given Id."""
        usr = self.session.query(User).filter(User.id==user_id).all()
        if len(usr)>0:
            return usr[0]
        else:
            return None


    def getGroupById(self, group_id):
        """Returns object of group of given Id."""
        grp = self.session.query(Group).filter(Group.id==group_id).all()
        if len(grp)>0:
            return grp[0]
        else:
            return None


    def getGroups(self):
        """Returns list of all defined groups."""
        return self.session.query(Group).all() or []


    def getBillings(self):
        """Returns list of all billing records."""
        return self.session.query(Billing).all() or []


    def addUser(self, userName=None, userGsm=None, userIp=None):
        """Adds new user into the DB and returns it's object."""
        if userName and userGsm and userIp:
            u = User(userName, userGsm, userIp)
            if u:
                self.session.add(u)
                self.session.commit()
            return u


    def addGroup(self, groupName=None):
        """Adds new group into the DB and returns it's object."""
        if groupName:
            g = Group(groupName)
            if g:
                self.session.add(g)
                self.session.commit()
            return g


    def addBilling(self, user=None, sms=None):
        """Adds new billing into the DB and returns it's object."""
        if isinstance(user, User) and sms:
            b = Billing(user.id, sms)
            if b:
                self.session.add(b)
                self.session.commit()
            return b


    def addUser2Group(self, user=None, group=None):
        """Creates a Membership record."""
        if isinstance(user,User) and isinstance(group, Group):
            if not user.belongs2(group):
                user.membership.append( Membership(user.id, group.id ) )
                self.session.commit()


    def delUser(self, user=None):
        """Removes user from DB"""
        if isinstance(user,User):
            # first remove user's membership records
            for m in user.membership: 
                self.session.delete(m)
            # then the billing records
            for b in user.billings: 
                self.session.delete(b)
            # and finally the user record#FFFFFF
            self.session.delete(user)
            self.session.commit()


    def delGroup(self,group=None):
        """Removes group from DB"""
        if isinstance(group, Group):
            # first remove user's membership records
            for m in group.membership: 
                self.session.delete(m)
            # and finally the group record
            self.session.delete(group)
            self.session.commit()

            
    def pingUser(self,user=None):
        """Stores current time as a time stamp of the last successful 
ping of user's computer'"""
        if isinstance(user, User):
            user._updatePing()
            self.session.commit()

                
    def pingUserAndHisGroups(self,user=None):
        """Stores current time as a time of last succesful ping for 
user and all members of his groups"""
        if isinstance(user, User):
            for u in user.getRelatedUsers():
                self.pingUser(u)




if __name__ == "__main__":
    dao = OfficeNotifierDAO()
    print "Users:"
    print dao.getUsers()

    print "Groups:"
    print dao.getGroups()

    print "Billings:"
    print dao.getBillings()
