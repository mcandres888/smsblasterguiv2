#!/usr/bin/env python


# this is the main sql prototype

import copy
import mysql.connector

class SQLPrototype:
    # base class
    _hostname = None
    _username = None
    _password = None
    _config = None
    cur = None
    cnx = None

    def infoLog(self, data):
        print data
       
    def clone(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        self.close()

    def reconnect(self):
        self.connect()

    def close(self):
        self.cnx.close()

    def exec_query (self, query_str):
        self.infoLog("[EXEC] %s" % query_str)
        self.reconnect()
        self.cur.execute(query_str)
        self.cnx.commit()
        self.close()

    def fetch_query (self, query_str):
        self.infoLog("[FETCH] %s" % query_str)
        self.reconnect()
        self.cur.execute(query_str)
        rows = self.cur.fetchall()
        self.close()
        return rows

    def fetch_one (self, query_str):
        self.infoLog("[FETCHONE] %s" % query_str)
        self.reconnect()
        self.cur.execute(query_str)
        data = self.cur.fetchone()
        self.close()
        return data


    def create_database(self, cursor, DB_NAME):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    def createDB (self, database, cnx):
        cur = cnx.cursor()
        self.infoLog("[createDB] %s" %  database)
        query_str = "create database %s" % database
        cur.execute(query_str)
	cnx.commit()
        self.close()



###################
#  Database Types
###################
class sl_mysql(SQLPrototype):
    def __init__(self, config, database):
        self._hostname = config['DBHOST']
        self._username = config['DBUSER']
        self._password = config['DBPASS']
        if database == None:
            self._database = config['DBNAME']
        else:
            self._database = database
        self._config = {
            'host': self._hostname,
            'port': 3306,
            'database': self._database,
            'user': self._username,
            'password': self._password,
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
        }

    def connect(self):
        try:
            self.cnx = mysql.connector.Connect(**self._config)
        except mysql.connector.errors.ProgrammingError, e:
            if e.errno == 1049 :  # unknown database  
                self.infoLog("Unknown database, creating one")
                # connect using minimal settings
                self.cnx = mysql.connector.Connect(
                    host =self._hostname,
                    port = 3306,
                    user = self._username,
                    password =  self._password
		)
                self.cur = self.cnx.cursor()
                self.create_database(self.cur, self._database)
                self.cnx.database = self._database
                self.cnx.close()
                self.cnx = mysql.connector.Connect(**self._config)
        self.cur = self.cnx.cursor()

    def convertToTimestamp (self, epoch_time ):
        return  datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')



# object factory
class SQLObjectFactory:
    # static factory that encapsulates prototype initialization

    __protoObject = None

    @staticmethod
    def initialize(config, database = None):
        sqlType = config['DBTYPE']
        print "sqlType ", sqlType 
        if sqlType == "mysql" :
            SQLObjectFactory.__protoObject =  sl_mysql(config, database)

        return SQLObjectFactory.__protoObject



