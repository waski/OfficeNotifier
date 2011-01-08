# www.py
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

import config
import BaseHTTPServer
from jinja2 import Template
from db import OfficeNotifierDAO as DAO, Group, User, Billing
import re



dao = DAO()

class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    known_sections = ["home","users","groups", "ie"]    
    def do_GET(self):
        addr = re.findall("/(\w+)",self.path) or None
        if not addr:
            section = "home"
        else:
            section = addr[0].lower()
            if not section in self.known_sections:
                section = "home"
        
        status, users, groups, membership, billings = None, None, None, None, None
        
        self.send_response(200)
        self.end_headers()
        
        if section == "ie":
            self.wfile.write(file('www/ie.html').read().decode('UTF-8'))
            return
        
        if section == 'users':
            users = dao.getUsers()
        elif section == 'groups':
            groups = dao.getGroups()
            membership = {}
            for g in groups:
                membership[g.id] = g.getUsers()
        
        elif section == 'home':
            billings = dao.getBillings()

        # to-do: get phone status
        status = "bla bla bla"
        
        data = {
            'section' : section,
            'users': users,
            'groups': groups,
            'billings': billings,
            'membership' : membership,
            'status' : status,
        }
        raw_html = file('www/index.tmpl').read().decode('UTF-8')
        main_html = Template(raw_html).render(data)
        self.wfile.write(main_html)


server = BaseHTTPServer.HTTPServer(('',config.HTTP_PORT), WebRequestHandler)
server.serve_forever()
