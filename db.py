# --*-- encoding:utf-8 --*--

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from datetime import datetime
import logging as log
import inspect

log.basicConfig(level=log.INFO)


Base = declarative_base()


class User(Base):
   __tablename__ = "users"
 
   id = Column(Integer, primary_key=True)
   name = Column(String)
   gsm  = Column(String)
   ip = Column(String(15))
   #----------------------------------------------------------------------
   def __init__(self, name, gsm, ip):
      """Constructor"""
      self.name = name
      self.gsm = gsm
      self.ip = ip
 
   def __repr__(self):
      return "<User('%s','%s', '%s')>" % (self.name, self.gsm, self.ip)

   def getGroups(self):
      return [m.group for m in self.membership]

   def _addMe2Group(self, group):
      if group and not self.belongs2(group):
         self.membership.append(Membership(self.id, group.id))

   def belongs2(self, group):
      if group:
         return group in self.getGroups()

########################################################################
class Billing(Base):
   __tablename__ = "bilings"
   id = Column(Integer, primary_key=True)
   user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
   time = Column(DateTime, nullable=False)
   sms = Column(String, nullable=False)
 
   user = relation(User, backref=backref('billings', order_by=id))
   #----------------------------------------------------------------------
   def __init__(self, sms):
      """Constructor"""
      self.sms = sms
      self.time = datetime.now()
 
   def __repr__(self):
      return "<Billing('%s:%s')>" % (self.time, self.sms)

 
########################################################################
class Group(Base):
   __tablename__ = "groups"
   id = Column(Integer, primary_key=True)
   name = Column(String, nullable=False)
   #----------------------------------------------------------------------
   def __init__(self, name):
      """Constructor"""
      self.name = name
 
   def __repr__(self):
      return "<Group('%s')>" % (self.name,)
    
   def getGUsers(self):
      return [m.user for m in self.membership]

   def _addUser(self, user):
      if user and not user.belongs2(self):
         self.membership.append(Membership(user.id, self.id))
         

########################################################################
class Membership(Base):
   __tablename__ = "membership"
   id = Column(Integer, primary_key=True)
   user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
   group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
	
   user  = relation(User, backref=backref('membership', order_by=id))
   group = relation(Group, backref=backref('membership', order_by=id))
   #----------------------------------------------------------------------
   def __init__(self, user_id, group_id):
      """Constructor"""
      self.user_id = user_id
      self.group_id = group_id
 
   def __repr__(self):
      return "<Membership('%s:%s')>" % (self.user_id, self.group_id)


########################################################################
class OfficeNotifierDAO(object):
   """Simple class grouping methods needed to operate on sqlite DB"""
   DB_FILE = "notifier.db"

   def __init__(self):
      self.engine = create_engine("sqlite:///%s" % (self.DB_FILE,), echo=False)
      self.metadata = Base.metadata
      self.metadata.create_all(self.engine)
      self.session = sessionmaker(bind=self.engine)()

   def getUsers(self):
      return self.session.query(User).all() or []

   def getGroups(self):
      return self.session.query(Group).all() or []

   def getBillings(self):
      return self.session.query(Billing).all() or []

   def addUser(self, userName=None, userGsm=None, userIp=None):
      if not userName or not userGsm or not userIp:
         return None

      u = User(userName, userGsm, userIp)
      self.session.add(u)
      self.session.commit()
      return u

   def addGroup(self, groupName=None):
      if not groupName:
         return None #to-do:error logging

      g = Group(groupName)
      self.session.add(g)
      self.session.commit()
      return g

   def addUserToGroup(self, user=None, group=None):
      if not user or not group:
         return None #to-do:error logging
      group._addUser(user)
      self.session.commit()
			

   

if __name__ == "__main__":
   dao = OfficeNotifierDAO()
   print "Users:"
   print dao.getUsers()

   print "Groups:"
   print dao.getGroups()

   print "Billings:"
   print dao.getBillings()

