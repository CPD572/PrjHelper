#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from builtins import staticmethod
from datetime import datetime
import json
import math
import os
import requests
from xml.dom import minidom
import xml.etree.ElementTree as ElementTree
from sys import platform
from requests.exceptions import ConnectTimeout, ConnectionError

if 'win' in platform:
    file_route_spliter = '\\'
else:
    file_route_spliter = '/'

bitbucket_api_link = 'http://repo.microlab.club/rest/api/1.0/'
users = 'users'
projects_repo = 'projects'
page_start = '?start='

module_repos = 'repos'
userdatafolder = 'usr'
userfile = userdatafolder + file_route_spliter + 'user.mlbu'
password_separator = 'FF04'



def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class BitbucketUser:
    def __init__(self):
        self.username = u''
        self.password = u''
        self.encoded_password = u''
        
        if self.is_user_data_saved():
            self.load_userdata_from_file()
        
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
            with open(userfile,'w+') as f:
                print(prettify(user_data_tag), file=f)
                
    def delete_saved_user(self):
        if self.is_user_data_saved():
            os.remove(userfile)
            os.rmdir(userdatafolder)
        else:
            return
                
    def is_user_data_saved(self):
        return os.path.exists(userfile)
    
    def load_userdata_from_file(self):
        if os.path.exists(userfile):
            user_data = ElementTree.parse(userfile).getroot()
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
        self.key = u''
        self.id = 0
        self.name = u''
        self.type = u''
        self.link = u''
        
    def __call__(self, **kwargs):
        if 'key' in kwargs:
            self.key = kwargs['key']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'links' in kwargs:
            self.link = kwargs['links']['self'][0]['href']


class BitbucketRepo:
    
    def __init__(self):
        self.id = 0
        self.slug = u''
        self.name = u''
        self.scmId = u''
        self.forkable = False
        self.project = BitbucketProject()
        self.public = False
        self.http_link = u''
        self.ssh_link = u''
        
    def __str__(self):
        return '%s' % self.name


class Bitbucket:
    
    def __init__(self):
        self.user = BitbucketUser()
        self.has_access = False
        self.session = requests.Session()
        self.projects = []
        self.repositories = []
        
    def Login(self, user_name, password):
        self.user(user_name, password)
        self.session.auth = requests.auth.HTTPBasicAuth(self.user.username, self.user.password)
        url = bitbucket_api_link + users + '/'+ str(self.user.username)
        try:
            httpGetResponse = self.session.get(url, timeout = 5.0)
            self.jsonResponse = json.loads(httpGetResponse.text)
            if httpGetResponse.status_code == 200:
                self.has_access = True
                return 1
            else:
                return 0
        except:
            return -1
        
    def Change_user(self, name, password):
        self.has_access = False
        self.user.delete_user()
        self.user(name, password)
        
    def Paged_response_parse(self, url):
        pages = []
        isLastPage = False
        initial_url = url
        try:
            while isLastPage == False:
                http_response = self.session.get(url, timeout = 5.0)
                if http_response.status_code == 200:
                    self.jsonResponse = json.loads(str(http_response.text))
                    isLastPage = self.jsonResponse['isLastPage']
                    pages+=self.jsonResponse['values']
                    if isLastPage == False:
                        url = initial_url + page_start + str(self.jsonResponse['nextPageStart'])
                else:
                    return {'errors': [{'message': http_response.reason}]}
                
            return {'values': pages}
        
        except KeyError:
            return {'errors': [{'message': 'Something goes wrong. Incorrect JSON format received.'}]}
        
        except ConnectTimeout:
            return {'errors': [{'message': 'There is no server connection. Timeout was reached.'}]}
        
        except ConnectionError:
            return {'errors': [{'message': 'There is no server connection.'}]}
        
    def Get_projects(self):
        if self.has_access == True:
            url = bitbucket_api_link + projects_repo
            rsp = self.Paged_response_parse(url)
            if 'values' in rsp:
                for value in rsp['values']:
                    prj = BitbucketProject()
                    prj.key = value['key']
                    prj.id = value['id']
                    prj.name = value['name']
                    prj.type = value['type']
                    prj.link = value['links']['self'][0]['href']
                    self.projects.append(prj)
            else:
                return
        else:
            return


    def Get_modules_repo(self, project=u''):
        if self.has_access == True:
            if project == u'':
                url = bitbucket_api_link + module_repos
            else:
                url = bitbucket_api_link + projects_repo + u'/' + project + u'/' + module_repos
            
            rsp = self.Paged_response_parse(url)
            if 'values' in rsp:
                for value in rsp['values']:
                    repo = BitbucketRepo()
                    repo.id = value['id']
                    repo.name = value['name']
                    repo.project(**value['project'])
                    repo.forkable = value['forkable']
                    repo.scmId = value['scmId']
                    repo.slug = value['slug']
                    repo.public = value['public']
                    clone = value['links']['clone']
                    if clone[0]['name'] == 'http':
                        http_value = 0
                        ssh_value = 1
                    elif clone[1]['name'] == 'http':
                        http_value = 1
                        ssh_value = 0
                    repo.http_link = value['links']['clone'][http_value]['href']
                    repo.ssh_link = value['links']['clone'][ssh_value]['href']
                    self.repositories.append(repo)
            
                
