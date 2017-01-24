# controllers
from flask import render_template, request, redirect, jsonify

# global variables
API_KEY = "ct43-31bg-72b7-7b4e"
ERROR_INVALID = { "msg" : "invalid key", "result" : "error"}
RESULT_OK = {"result" : "ok", "msg" : "none"}
LOGIN_INVALID = {"result" : "error", "msg": "Invalid Username / Password"}
LOGIN_OK = {"result" : "ok", "msg" : "Login Successful!"}
REGISTER_UNVAILABLE = {"result" : "error", "msg" : "Username not available!"}


class ApiController(object):
    _user = None
    _app = None
    
    def __init__(self, app):
        self._user = app.user
        self._app = app

    def isKeyInvalid (self, api_key):
        if api_key != API_KEY:
            return True
        return False

    def login(self):
        json_data = request.json
        if self.isKeyInvalid(json_data['api_key']):
            return jsonify(ERROR_INVALID)                                                                          
        # cehck user name                                                                                          
        if self._user.isPasswordOK(json_data['username'], json_data['password']) == False:
            return jsonify(LOGIN_INVALID)                                                                          
        result = {
            "result" : "ok",
            "msg" : "User successfully logged in.",
            "userdisplayname" : self._user.data['username'],
        }                                                                                                          
        return jsonify(result)               

    def register(self, json_data):
        json_data = request.json
        if self.isKeyInvalid(json_data['api_key']):
            return jsonify(ERROR_INVALID)                                                                          

        if self._user.isUserAvailable(json_data['username']) == False:
            return jsonify(REGISTER_UNVAILABLE)

        
        user_data = self._user.registerUser(json_data)
        result = {
            "result" : "ok",
            "msg" : "User successfully registered",
            "userdisplayname" : user_data['userdisplayname'],
        }
        return jsonify(result)


class AdminController(object):
    _user = None
    _app = None
    _breadcrumbs = {
        "Home" : { "href" : "/Dashboard" , "class": "fa fa-dashboard"},
        "User" : { "href" : "/Users" , "class": "fa fa-users"},
        "UserProfile" : { "href" : "/Profile" , "class": "fa fa-user"},
    }
    
    def __init__(self, app):
        self._user = app.user
        self._app = app

    def login(self, isError=False):
        message =  "Sign in to start your session"
        if isError:
            message = "Incorrect email or password"

        data = {
            "message" : message
        }
        return render_template ('login.html', data=data)

    # base data will be the user data
    def getBaseData (self):
        data = {
            "title" : "RegrowHelmet",
            "username" : "Marc Andres",
            "domain" : request.url_root,
            "nav" : self.getNav()
        }
        return data

    # eventually nav will be different per user type
    def getNav(self):
        domain = request.url_root
        nav = [
            { "href" : "%sdashboard" % domain, "class" : "fa fa-dashboard", "text" : "Dashboard" },
            { "href" : "%sinbox" % domain, "class" : "fa fa-inbox", "text" : "Inbox" },
            { "href" : "%soutbox" % domain, "class" : "fa fa-rocket", "text" : "Outbox" },
            { "href" : "%swritemessage" % domain, "class" : "fa fa-edit", "text" : "Write Message" },
            { "href" : "%ssentitems" % domain, "class" : "fa fa-external-link", "text" : "Sent Items" },
            { "href" : "%sphonebook" % domain, "class" : "fa fa-book", "text" : "PhoneBook" },
            { "href" : "%sgroup" % domain, "class" : "fa fa-group", "text" : "Groups" },
        ]    
        return nav

    def dashboard(self):
        data = self.getBaseData()
        return render_template('main.html', data=data)

    def phonebook(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Contact",
            "titleSecond" : "List",
            "boxTitle" : "Phonebook Table",
            "headers" : ["Name", "Group", "Number", "Notes", "Action"],
            "data_url" : "/phonebook/list",
            "groups" : self._app.group.getAll(),
        }

        data['subData'] = subData
        data['tableHtml'] = "table_withform_contact.html"

        return render_template('tableTemplate.html', data=data)


    def group(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Group",
            "titleSecond" : "List",
            "boxTitle" : "Group Table",
            "headers" : ["Group Name", "Notes", "Action"],
            "data_url" : "/group/list"
        }

        data['subData'] = subData
        data['tableHtml'] = "table_withform_group.html"

        return render_template('tableTemplate.html', data=data)

    def phonebook_create(self, json_data):

        group_data = self._app.group.get(json_data['group'])
        contact_id = self._app.phonebook.create(json_data, group_data)
        self._app.group.bindGroupContact(group_data["id"], contact_id)

    def group_create(self, json_data):
        self._app.group.create(json_data)




    def inbox(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Inbox",
            "titleSecond" : "List",
            "boxTitle" : "Messages Table",
            "headers" : ["From", "Date", "Message", "Action"],
            "data_url" : "/inbox/list"
        }

        data['subData'] = subData
        data['tableHtml'] = "table.html"

        return render_template('tableTemplate.html', data=data)



    def sentitems(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Sent Items",
            "titleSecond" : "List",
            "boxTitle" : "Messages Table",
            "headers" : ["To", "Date", "Message","Status", "Action"],
            "data_url" : "/sentitems/list"
        }

        data['subData'] = subData
        data['tableHtml'] = "table.html"

        return render_template('tableTemplate.html', data=data)


    def outbox(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Outbox",
            "titleSecond" : "List",
            "boxTitle" : "Messages Table",
            "headers" : ["To", "Date", "Message", "Action"],
            "data_url" : "/outbox/list"
        }

        data['subData'] = subData
        data['tableHtml'] = "table.html"

        return render_template('tableTemplate.html', data=data)




    def users(self):
        data = self.getBaseData()
        subData = {
            "titleFirst" : "Users",
            "titleSecond" : "List",
            "boxTitle" : "Registered User Table",
            "headers" : ["Id", "Name", "Email", "Date Registered", "Status", "Action"],
            #"data_url" : "/admin/users/list"
            "data_url" : "/users/list"
        }

        data['subData'] = subData
        data['tableHtml'] = "table.html"
        print data

        return render_template('tableTemplate.html', data=data)

    def createBreadCrumbs ( self, linkList ):
        # this will create the list of bread crumbs, first is the active
        counter = 0
        breadCrumbs = []
        for x in linkList:
            if x in self._breadcrumbs:
                # create the data
                active = ""
                if counter == 0:
                    active = "active"
                
                temp = {
                    "title" : x,
                    "href" : self._breadcrumbs[x]['href'],
                    "class" : self._breadcrumbs[x]['class'],
                    "active" : active,
                }
                breadCrumbs.append(temp)
                counter = counter + 1
        return breadCrumbs


    def writemessage(self ):
        data = self.getBaseData()

        breadCrumbs = self.createBreadCrumbs(['UserProfile', 'User', 'Home'])

        subData = {
            "titleFirst" : "Write Message",
            "breadcrumbs" : breadCrumbs,
        }

        data['subData'] = subData


        return render_template('formTemplate.html', data=data)




    def profile(self, uuid):
        data = self.getBaseData()

        breadCrumbs = self.createBreadCrumbs(['UserProfile', 'User', 'Home'])

        subData = {
            "titleFirst" : "User Profile",
            "breadcrumbs" : breadCrumbs,
            "boxTitle" : "Registered User Table",
            "headers" : ["Id", "Name", "Email", "Date Registered", "Status", "Action"],
            "data_url" : "/users/list"
        }

        data['subData'] = subData
        print data


        return render_template('profileTemplate.html', data=data)


  
    def images(self):
        data = self.getBaseData()
        return render_template('images.html', data=data)

 
    def images_list(self):
        data = {}
        data['draw'] = 1
        data['recordsTotal'] = 20
        data['recordsFiltered'] = 20
        data['data'] = []
        data['data'].append(["id", "thumb", "size", "user", "date", "<button>Test</button>"])


        return jsonify(data)

 
    def user_list(self):
        data = self._app.user.tableData(request.args)
        return jsonify(data)

    def inbox_list(self):
        data = self._app.inbox.tableData(request.args)
        return jsonify(data)

    def sentitems_list(self):
        data = self._app.sentitems.tableData(request.args)
        return jsonify(data)

    def outbox_list(self):
        data = self._app.outbox.tableData(request.args)
        return jsonify(data)

    def phonebook_list(self):
        data = self._app.phonebook.tableData(request.args)
        return jsonify(data)

    def group_list(self):
        data = self._app.group.tableData(request.args)
        return jsonify(data)









