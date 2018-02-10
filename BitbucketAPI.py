import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
from datetime import datetime
import requests
import json
import os
import math

projects_uri = 'http://repo.microlab.club/rest/api/1.0/'
users = 'users/'
projects_repo = 'projects/'
userdatafolder = 'usr/'
userfile = userdatafolder+'user.mlbu'
password_separator = 'FF04'

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class BitbucketUser:
    def __init__(self):
        if self.is_user_data_saved():
            self.load_userdata_from_file()
        else:
            self.username = u''
            self.password = u''
            self.encoded_password = u''
        
    def delete_user(self):
        self.username = u''
        self.password = u''
        self.encoded_password = u''
        
    def __call__(self, name, password):
        self.username = name 
        self.password = password
        self.encode_password()
        
    def save_user(self):
        if not os.path.exists(userdatafolder):
            os.mkdir(userdatafolder)
        if not os.path.exists(userfile):
            created = datetime.now()
            user_data_tag = ElementTree.Element('user_data')
            user_tag = ElementTree.SubElement(user_data_tag, 'user', {'name': self.username})
            user_password_tag = ElementTree.SubElement(user_tag,'password')
            user_password_tag.text = self.encoded_password
            created_tag = ElementTree.SubElement(user_tag, 'created')
            date_tag = ElementTree.SubElement(created_tag, 'date')
            date_tag.text = str(created.date())
            time_tag = ElementTree.SubElement(created_tag, 'time')
            time_tag.text = str(created.time())[:8]
            with open('usr/user.mlbu','w+') as f:
                print(prettify(user_data_tag), file=f)
                
    def is_user_data_saved(self):
        return os.path.exists(userfile)
    
    def load_userdata_from_file(self):
        if os.path.exists('usr/user.mlbu'):
            user_data = ElementTree.parse('usr/user.mlbu').getroot()
            self.encoded_password = user_data[0][0].text
            self.decode_password()
            self.username = user_data[0].attrib['name']
                        
    def encode_password(self):
        if self.password == u'':
            return
        calc_password = []
        pass_bytes = [*map(ord, self.password)]
        for i in pass_bytes:
            calc_password.append(i**2 + i*2 + 1)
        self.encoded_password = password_separator.join([hex(p).upper()[2:] for p in calc_password])
        
    def decode_password(self):
        if self.encoded_password == u'':
            return
        result_word = []
        for i in self.encoded_password.split(password_separator):
            result_word.append(int(math.sqrt(int(i,16))-1))
        self.password = ''.join(map(chr,result_word))                    
    
    
class BitbucketProject:
    
    def __init__(self):
        pass

class Bitbucket:
    
    def __init__(self):
        self.user = BitbucketUser()
        self.has_access = False
        self.session = requests.Session()
        
    def Login(self, user_name, password):
        self.user(user_name, password)
        self.session.auth = requests.auth.HTTPBasicAuth(self.user.username, self.user.password)
        url = projects_uri + users + str(self.user.username)
        #try:
        httpGetResponse = self.session.get(url, timeout = 5.0)
        self.jsonResponse = json.loads(httpGetResponse.text)
        if httpGetResponse.status_code == 200:
            self.has_access = True
            return 1
        else:
            return 0
        #except:
        #    return -1
        
    def Change_user(self, name, password):
        self.has_access = False
        self.user.delete_user()
        self.user(name, password)
        