# test.py
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


import unittest
from db import *
import os

db_file = "test.db"

class DBTests(unittest.TestCase):  

   @classmethod
   def setUpClass(cls):
      cls.dao = OfficeNotifierDAO("sqlite:///%s" % db_file)
      cls.usr1t = ("Mr Test 1", 997, "127.0.0.1")
      cls.usr2t = ("Mr Test 2", 998, "127.0.0.2")
      cls.grps = ("group1", "group2") 
      

   def test_UserCreation(self):
      """Try to add 2 records to 'users' table"""
      self.usr1 = self.dao.addUser(self.usr1t[0], self.usr1t[1], self.usr1t[2]) 
      self.usr2 = self.dao.addUser(self.usr2t[0], self.usr2t[1], self.usr2t[2]) 
      self.assertTrue( isinstance(self.usr1, User) and isinstance(self.usr2,User) )

   def test_GroupCreation(self):
      """Try to add 2 records to 'groups' table"""
      self.grp1 = self.dao.addGroup( self.grps[0] )
      self.grp2 = self.dao.addGroup( self.grps[1] )
      self.assertTrue ( isinstance(self.grp1, Group) and isinstance(self.grp2, Group) )


   def test_UserQuering(self):
      """Try to query users and compare them with hardcoded ones"""
      self.assertTrue ( self.dao.getUserById(1).name == self.usr1t[0] )
      self.assertTrue ( self.dao.getUserById(2).name == self.usr2t[0] )

   def test_GroupQuering(self):
      self.assertTrue( self.dao.getGroupById(1).name == self.grps[0] )
      self.assertTrue( self.dao.getGroupById(2).name == self.grps[1] )
  
   def test_notatest_just_cleanup(self):
      if os.path.exists(db_file):
          os.remove(db_file)

if __name__ == "__main__":
    DBTests.setUpClass()
    unittest.main()
    #os.remove(db_file)
