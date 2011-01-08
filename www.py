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




dao = DAO()

class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        section = self.path.replace("/","").lower() or "users"
        status, users, groups, membership = None, None, None, None
        
        self.send_response(200)
        self.end_headers()
        
        if section in ['users', 'groups', 'billings']:
            users = dao.getUsers()
            groups = dao.getGroups()
            membership = {}
        
            for g in groups:
                membership[g.id] = g.getUsers()

        # to-do: get phone status
        status = "bla bla bla"
        
        data = {
            'section' : section,
            'users': users,
            'groups': groups,
            'membership' : membership,
            'status' : status,
        }
        raw_html = file('www/index.tmpl').read().decode('UTF-8')
        main_html = Template(raw_html).render(data)
        self.wfile.write(main_html)


server = BaseHTTPServer.HTTPServer(('',config.HTTP_PORT), WebRequestHandler)
server.serve_forever()

