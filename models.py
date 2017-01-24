# models class
import requests
import flask_login
from flask import render_template, request, redirect, jsonify
import uuid
import json
import time
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sql import SQLObjectFactory as SQL

def infoLog(data):
    print data




class User(flask_login.UserMixin):
    _db = "users"
    data = None
    db = None
    config = None

    def setConfig(self, config):
        self.config = config

    def setDB(self, dbInstance):
        self.db = dbInstance
        
    def isUserAvailable(self, username):
        query_str = "SELECT * FROM users WHERE email='%s'" % username
        result = self.db.fetch_one(query_str)
        if result == None:
            infoLog( "username still available")
            return True
        else:
            infoLog( "username  unavailable")
            return False

    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))

        url = '%s/_design/data/_view/userList' % (self._db)
        result = self.couchdb.get(url)
        # create the table data
        tableData = {} 
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        tableData['recordsTotal'] = len(result['rows'])
        tableData['recordsFiltered'] = len(result['rows']) # must be filtered based on key
        # recreate data
        tableData['data'] = []
        for x in result['rows']:
            date_created =  datetime.datetime.fromtimestamp(
                    x['value']['date_created']).strftime('%Y-%m-%d %H:%M:%S')
            actions = "<a href='%s/profile/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x['id'] )
            tableData['data'].append([
                x['id'],
                x['value']['userdisplayname'],
                x['value']['username'],
                date_created,
                "registered",
                actions
            ])

        return tableData





    def getByUUID(self, uuid):
        self.data = self.get(uuid) 
        print self.data
        return self.data


    def loadUser( self, username):

        query_str = "SELECT * FROM users WHERE email='%s'" % (username)
        result = self.db.fetch_one(query_str)
        print "waaa"

        if result == None:
            infoLog( "username  unavailable")
            return False
        else:
            self.id = result[1]
            self.data = {}
            self.data['_id'] = result[0]
            self.data['email'] = result[1]
            self.data['username'] = result[3]
        
            return True
        return False



    def isPasswordOK( self, username, password):

        query_str = "SELECT * FROM users WHERE email='%s'" % (username)
        result = self.db.fetch_one(query_str)

        print result
        if result == None:
            infoLog( "username  unavailable")
            return False
        else:
            # check user data
            self.id = result[3]
            self.data = {}
            self.data['_id'] = result[0]
            self.data['email'] = result[1]
            self.data['username'] = result[3]
            if check_password_hash(result[2], password):
                infoLog("password ok")
                return True
            else:
                infoLog("incorrect password")
        return False






    def registerUser(self, json_data):
        query_str = "INSERT INTO users (username, password, email )VALUES('%s', '%s' , '%s')" % (json_data['username'].split('@')[0], generate_password_hash(json_data['password']), json_data['username'])

        json_data = {
                "username" : json_data['username'],
                "userdisplayname" : json_data['username'].split('@')[0],
                "password" : generate_password_hash(json_data['password']),
                "date_created" : int(time.time())
        }
        self.data = json_data
        self.db.exec_query(query_str)
        return self.data


    def create(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password) 


class TableModel(object):
    data = None
    db = None
    config = None

    def setConfig(self, config):
        self.config = config

    def setDB(self, dbInstance):
        self.db = dbInstance

    def tableData(self, requestInfo):
        pass


class Inbox(TableModel):
    table = "inbox"

    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))
        search = requestInfo.get("search[value]")

        tableData = {} 

        # get count
        query_str = "SELECT ID FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        tableData['recordsFiltered'] = len(result) # must be filtered based on key
        search = '%' + search + '%'

        query_str = "SELECT * FROM %s WHERE SenderNumber LIKE '%s' LIMIT %d,%d" % (self.table,search,  start, length)
        result = self.db.fetch_query(query_str)
        # create the table data
        tableData['recordsTotal'] = len(result)
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        # recreate data
        tableData['data'] = []
        for x in result:
            date_recieved = x[1].strftime('%Y-%m-%d %H:%M:%S')
            actions = "<a href='%s/profile/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x[10] )
            tableData['data'].append([
                x[3],
                date_recieved,
                x[8],
                actions
            ])

        return tableData


class SentItems(TableModel):
    table = "sentitems"

    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))
        search = requestInfo.get("search[value]")

        tableData = {} 

        # get count
        query_str = "SELECT ID FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        tableData['recordsFiltered'] = len(result) # must be filtered based on key
        search = '%' + search + '%'

        query_str = "SELECT * FROM %s WHERE DestinationNumber LIKE '%s' LIMIT %d,%d" % (self.table,search,  start, length)
        result = self.db.fetch_query(query_str)
        # create the table data
        tableData['recordsTotal'] = len(result)
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        # recreate data
        tableData['data'] = []
        for x in result:
            date_sent = x[2].strftime('%Y-%m-%d %H:%M:%S')
            actions = "<a href='%s/profile/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x[10] )
            tableData['data'].append([
                x[5],
                date_sent,
                x[10],
                x[14],
                actions
            ])

        return tableData


class Outbox(TableModel):
    table = "outbox"

    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))
        search = requestInfo.get("search[value]")

        tableData = {} 

        # get count
        query_str = "SELECT ID FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        tableData['recordsFiltered'] = len(result) # must be filtered based on key
        search = '%' + search + '%'

        query_str = "SELECT * FROM %s WHERE DestinationNumber LIKE '%s' LIMIT %d,%d" % (self.table,search,  start, length)
        result = self.db.fetch_query(query_str)
        # create the table data
        tableData['recordsTotal'] = len(result)
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        # recreate data
        tableData['data'] = []
        for x in result:
            date_sent = x[2].strftime('%Y-%m-%d %H:%M:%S')
            actions = "<a href='%s/profile/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x[10] )
            tableData['data'].append([
                x[6],
                date_sent,
                x[10],
                actions
            ])

        return tableData


class Contacts(TableModel):
    table = "contacts"
 
    def create ( self, json_data, group_data):
        query_str = "INSERT INTO %s (contact_name, contact_number, notes, group_id, group_name )VALUES('%s', '%s', '%s', %d, '%s')" % (self.table, json_data['contact_name'], json_data['contact_number'], json_data['notes'], group_data["id"], group_data["name"])
        self.db.exec_query(query_str)

        return  self.db.getLastInsertedId()
        



    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))
        search = requestInfo.get("search[value]")

        tableData = {} 

        # get count
        query_str = "SELECT ID FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        tableData['recordsFiltered'] = len(result) # must be filtered based on key
        search = '%' + search + '%'

        query_str = "SELECT * FROM %s WHERE contact_name LIKE '%s' LIMIT %d,%d" % (self.table,search,  start, length)
        result = self.db.fetch_query(query_str)
        # create the table data
        tableData['recordsTotal'] = len(result)
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        # recreate data
        tableData['data'] = []
        for x in result:
            actions = "<a href='%s/phonebook/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x[0] )
            tableData['data'].append([
                x[1],
                x[5],
                x[2],
                x[3],
                actions
            ])

        return tableData


class Groups(TableModel):
    table = "groups"
    def getAll (self):
        query_str = "SELECT * FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        data = []
        for x in result:
            data.append({
                "id" : x[0],
                "name" : x[1],
            })
        return data

    def get(self, id):
        query_str = "SELECT * FROM %s WHERE id=%d LIMIT 1" % (self.table, int(id))
        result = self.db.fetch_one(query_str)
        if result == None:
            return None

        data = {
            "id" : result[0],
            "name" : result[1],
        }
        return data



    def tableData(self, requestInfo):
        # request info data
        draw = int(requestInfo.get("draw"))
        start = int(requestInfo.get("start"))
        length = int(requestInfo.get("length"))
        search = requestInfo.get("search[value]")

        tableData = {} 

        # get count
        query_str = "SELECT ID FROM %s" % (self.table)
        result = self.db.fetch_query(query_str)
        tableData['recordsFiltered'] = len(result) # must be filtered based on key
        search = '%' + search + '%'

        query_str = "SELECT * FROM %s WHERE group_name LIKE '%s' LIMIT %d,%d" % (self.table,search,  start, length)
        result = self.db.fetch_query(query_str)
        # create the table data
        tableData['recordsTotal'] = len(result)
        # draw must be different from last draw
        tableData['draw'] = draw + 1 # this must be the index / page
        # recreate data
        tableData['data'] = []
        for x in result:
            actions = "<a href='%s/group/%s'><button type='button' class='btn btn-block btn-success'> View </button></a>" % ( request.url_root, x[0] )
            tableData['data'].append([
                x[1],
                x[2],
                actions
            ])

        return tableData
    
    def create ( self, json_data ):
        query_str = "INSERT INTO %s (group_name, notes )VALUES('%s', '%s')" % (self.table, json_data['group_name'], json_data['notes'])
        self.db.exec_query(query_str)

    def bindGroupContact ( self, group_id, contact_id ):
        query_str = "INSERT INTO contact_group (contact_id, group_id )VALUES(%d, %d)" % (contact_id, group_id)
        self.db.exec_query(query_str)







# global db
dbInstance = None


class ModelFactory:
    @staticmethod
    def initialize(config):
        global dbInstance
        if dbInstance == None:
            print "dbInstance not yet initialized"
            dbInstance = SQL.initialize(config)
        else:
            print "couchInstance already created"
    @staticmethod
    def load(config, modelType):
        global dbInstance
        if dbInstance == None:
            raise Exception("initialize ModelFactory first")

        protoype = None
        if modelType == "user":
            prototype = User()

        elif modelType == "inbox":
            prototype = Inbox()

        elif modelType == "sentitems":
            prototype = SentItems()

        elif modelType == "outbox":
            prototype = Outbox()

        elif modelType == "contacts":
            prototype = Contacts()

        elif modelType == "groups":
            prototype = Groups()

        prototype.setDB(dbInstance)
        prototype.setConfig(config)
        

        return prototype 







