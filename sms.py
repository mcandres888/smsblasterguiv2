# all related to sms handling
from subprocess import call


class SMS(object):
    config = None
    gammu = "/usr/local/bin/gammu-smsd-inject"
    def __init__(self,config):
        self.config = config

    def send(self, recipient, message):
        self.sendSmart(recipient, message)


    def sendSmart(self, recipient, message):
        exec_str = "%s TEXT %s -text '%s'" % ( self.gammu, recipient, message)
        print exec_str
        call(exec_str, shell=True)

       
