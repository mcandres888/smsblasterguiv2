# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
import flask_login
from models import *
from controllers import *
from sms import *


app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
ModelFactory.initialize(app.config)
User = ModelFactory.load(app.config, "user")
app.user = User

app.inbox = ModelFactory.load(app.config, "inbox")
app.sentitems = ModelFactory.load(app.config, "sentitems")
app.outbox = ModelFactory.load(app.config, "outbox")
app.phonebook = ModelFactory.load(app.config, "contacts")
app.group = ModelFactory.load(app.config, "groups")
app.sms = SMS(app.config)

Api = ApiController(app)
Admin = AdminController(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(email):
    
    if User.loadUser(email):
        return User
    return None


@login_manager.request_loader
def request_loader(request_):
    return None
    email = request_.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['pw']

    return user


#
# R O U T E S
#
@app.route('/')
@flask_login.login_required
def Main():
    return Admin.dashboard()
    #return Admin.login(app)
    #return app.send_static_file('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print request.method
    if request.method == 'GET':
        return Admin.login()
    email = request.form['email']
    password = request.form['password']
    if User.isPasswordOK(email, password):
        flask_login.login_user(User)
        return Admin.dashboard()

    return Admin.login( True)

@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return Admin.login()

@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    return Admin.dashboard()


@app.route('/inbox')
@flask_login.login_required
def inbox():
    return Admin.inbox()


@app.route('/sentitems')
@flask_login.login_required
def sentitems():
    return Admin.sentitems()


@app.route('/outbox')
@flask_login.login_required
def outbox():
    return Admin.outbox()


@app.route('/writemessage', methods=['GET', 'POST'])
@flask_login.login_required
def writemessage():
    print request.method
    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        app.sms.send(recipient, message)

    #return redirect("%swritemessage" % request.url_root) 
    return Admin.writemessage()


@app.route('/phonebook', methods=['GET', 'POST'])
@flask_login.login_required
def phonebook():
    if request.method == 'POST':
        Admin.phonebook_create(request.form)
    #return redirect("%sphonebook" % request.url_root) 
    return Admin.phonebook()

@app.route('/group',  methods=['GET', 'POST'])
@flask_login.login_required
def group():
    if request.method == 'POST':
        Admin.group_create(request.form)


    #return redirect("%sgroup" % request.url_root) 
    return Admin.group()




@app.route('/users')
@flask_login.login_required
def users():
    return Admin.users()

@app.route('/profile/<uuid>')
@flask_login.login_required
def profile(uuid):
    return Admin.profile(uuid)



@app.route('/users/list')
def users_list():
    return Admin.user_list()

@app.route('/inbox/list')
def inbox_list():
    return Admin.inbox_list()


@app.route('/sentitems/list')
def sentitems_list():
    return Admin.sentitems_list()

@app.route('/outbox/list')
def outbox_list():
    return Admin.outbox_list()

@app.route('/phonebook/list')
def phonebook_list():
    return Admin.phonebook_list()

@app.route('/group/list')
def group_list():
    return Admin.group_list()





@app.route('/images')
def images():
    return Admin.images()

@app.route('/images/list')
def images_list():
    return Admin.images_list()



@app.route('/videos')
def videos():
    return Admin.videos()

#############################
#  A P I
#############################

@app.route('/api/login', methods=["POST"])
def api_login():
    return Api.login()


@app.route('/api/register', methods=["POST"])
def api_register():
    return Api.register(app)



port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port), debug=True)
