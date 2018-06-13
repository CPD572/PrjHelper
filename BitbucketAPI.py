#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from builtins import staticmethod, str
from datetime import datetime
import json
import math
import os
from sys import platform
from xml.dom import minidom
from urllib.parse import urlparse
import re

import requests
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout

import xml.etree.ElementTree as ElementTree


def search_env(env):
    envirement = str(env) if not isinstance(env, str) else env
    try:
        if 'win' in platform:
            path = os.popen('where '+ envirement).readline()[:-1]
        elif 'linux' in platform:
            path = os.popen('which '+ envirement).readline()[:-1]
            
    except IndexError:
        path = None
        
    if path is None:
        return False
    else:
        return True

bitbucket_url = ''
bitbucket_api_link = 'http://'+bitbucket_url+'/rest/api/1.0/'
users = 'users'
projects_repo = 'projects'
branches = 'branches'
commits = 'commits'
commits_on_branch = commits+'?until='
page_start = '?start='

module_repos = 'repos'

password_separator = 'FF04'

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class User(object):
    
    created = []
    
    def __init__(self, kwargs= None):
        if self in User.created:
            return
        self.name = u''
        self.slug = u''
        self.id = u''
        self.emailAddress = u''
        self.displayName = u''
        self.type = u''
        self.link = u''
        if kwargs is not None:
            if 'name' in kwargs:
                if not User.isCreated(kwargs['name']):
                    self(**kwargs)
                    User.created.append(self)
            
    def __str__(self):
        return '%s' % self.displayName
     
    def __repr__(self):
        return '%s' % self.displayName
     
    def __call__(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'slug' in kwargs:
            self.slug = kwargs['slug']
        if 'emailAddress' in kwargs:
            self.emailAddress = kwargs['emailAddress']
        if 'displayName' in kwargs:
            self.displayName = kwargs['displayName']
        else:
            self.displayName = self.name + ' [Deleted]'
        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'links' in kwargs:
            self.link = kwargs['links']['self'][0]['href']
            if not bitbucket_url in self.link:
                url = urlparse(self.link)
                self.link = url._replace(netloc=bitbucket_url).geturl()
        
                
                
    def __eq__(self, value):
        if hasattr(self, 'id') and hasattr(value, 'id'):
            return self.id == value.id
        elif hasattr(self, 'name') and hasattr(value, 'name'):
            return self.name == value.name
        elif hasattr(self, 'id') and isinstance(value, int):
            return self.id == value
        elif hasattr(self, 'name') and isinstance(value, str):
            return self.name == value
    
    def __new__(cls, *args, **kwargs):
        data = args[0]
        if 'id' in data and User.isCreated(data['id']):
            return User.created[User.created.index(data['id'])]
        elif 'name' in data and User.isCreated(data['name']):
            return User.created[User.created.index(data['name'])]
        else:
            return super(User, cls).__new__(cls)
                
    @staticmethod
    def isCreated(userInfo):
        return userInfo in User.created


 
class LogedUser(User):                
    def __init__(self, userfile, **kwargs):
        if self in User.created:
            return
        self.password = u''
        self.encoded_password = u''
        self.userfile = userfile
        self.isAdmin = False
        super(LogedUser, self).__init__(kwargs)
        if self.is_user_data_saved():
            self.load_userdata_from_file()
        
        
        
    def __call__(self, **kwargs):
        User.__call__(self, **kwargs)
        if 'password' in kwargs:
            self.password = kwargs['password']
            self.encode_password()
                
    def __new__(cls, *args, **kwargs):
        return User.__new__(cls, *args, **kwargs)
    
    def __eq__(self, id):
        return self.id == id
                
    def is_user_data_saved(self):
        return os.path.exists(self.userfile)
    
    def load_userdata_from_file(self):
        user_data = ElementTree.parse(self.userfile).getroot()
        self.encoded_password = user_data.find('.//password').text
        self.decode_password()
        self.slug = user_data.find('.//user').attrib['name']
                        
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
                
    def delete_user(self):
        self.slug = u''
        self.password = u''
        self.encoded_password = u''
        
    def save_user(self):
        if not os.path.exists(os.path.dirname(self.userfile)):
            os.mkdir(os.path.dirname(self.userfile))
        if not os.path.exists(self.userfile):
            created = datetime.now()
            user_data_tag = ElementTree.Element('user_data')
            user_tag = ElementTree.SubElement(user_data_tag, 'user', {'name': self.slug})
            user_password_tag = ElementTree.SubElement(user_tag,'password')
            user_password_tag.text = self.encoded_password
            created_tag = ElementTree.SubElement(user_tag, 'created')
            date_tag = ElementTree.SubElement(created_tag, 'date')
            date_tag.text = str(created.date())
            time_tag = ElementTree.SubElement(created_tag, 'time')
            time_tag.text = str(created.time())[:8]
            with open(self.userfile,'w+') as f:
                print(prettify(user_data_tag), file=f)
                
                
    def delete_saved_user(self):
        if self.is_user_data_saved():
            os.remove(self.userfile)
            os.rmdir(os.path.dirname(self.userfile))
        else:
            return 



   
class Project:
    
    def __init__(self, kwargs = None):
        self.repositories = []
        if kwargs is None:
            self.key = u''
            self.id = 0
            self.name = u''
            self.type = u''
            self.link = u''
        else:
            self(kwargs)
        
    def __call__(self, kwargs):
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
            if not bitbucket_url in self.link:
                url = urlparse(self.link)
                self.link = url._replace(netloc=bitbucket_url).geturl()

    def __eq__(self, projectKey):
        return self.key == projectKey



class Branch(object):
    
    def __init__(self, kwargs):
        self.commits = []
        if kwargs is None: 
            self.id = ''
            self.displayId = ''
            self.latestCommit = ''
            self.latestChangeset = ''
            self.isDefault = False
        else:
            self(kwargs)
        
    def __call__(self, kwargs):
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'displayId' in kwargs:
            self.displayId = kwargs['displayId']
        if 'latestCommit' in kwargs:
            self.latestCommit = kwargs['latestCommit']
        if 'latestChangeset' in kwargs:
            self.latestChangeset = kwargs['latestChangeset']
        if 'isDefault' in kwargs:
            self.isDefault = kwargs['isDefault']


           
            
class Commit(object):
    
    def __init__(self, kwargs):
        if kwargs is None: 
            self.id = ''
            self.displayId = ''
            self.author = None
            self.authorTimestamp = None
            self.message = ''
            self.parents = []
        else:
            self(kwargs)
        
    def __call__(self, kwargs):
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'displayId' in kwargs:
            self.displayId = kwargs['displayId']
        if 'author' in kwargs:
            self.author = User(kwargs['author'])
        if 'authorTimestamp' in kwargs:
            self.authorTimestamp = kwargs['authorTimestamp']
        if 'message' in kwargs:
            self.message = kwargs['message']
        if 'parents' in kwargs:
            self.parents = [Commit(kwargs['parents'])]




class Repository:
    
    def __init__(self, kwargs = None):
        self.branches = []
        if kwargs is None:
            self.id = 0
            self.slug = u''
            self.name = u''
            self.scmId = u''
            self.forkable = False
            self.project = Project()
            self.public = False
            self.http_link = u''
            self.ssh_link = u''
        else:
            self(kwargs)
        
    def __str__(self):
        return '%s' % self.name
    
    def __call__(self, kwargs):
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'slug' in kwargs:
            self.slug = kwargs['slug']
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'scmId' in kwargs:
            self.scmId = kwargs['scmId']
        if 'forkable' in kwargs:
            self.forkable = kwargs['forkable']
        if 'project' in kwargs:
            self.project= Project(kwargs['project'])
        if 'public' in kwargs:
            self.public = kwargs['public']
        if 'links' in kwargs:
            clone = kwargs['links']['clone']
            if clone[0]['name'] == 'http':
                http_value = 0
                ssh_value = 1
            elif clone[1]['name'] == 'http':
                http_value = 1
                ssh_value = 0
            self.http_link = kwargs['links']['clone'][http_value]['href']
            if not bitbucket_url in self.http_link:
                url = urlparse(self.http_link)
                user_name, _ = url.netloc.split('@')
                self.http_link = url._replace(netloc=user_name+'@'+bitbucket_url).geturl()
            self.ssh_link = kwargs['links']['clone'][ssh_value]['href']
            if not bitbucket_url in self.ssh_link:
                url = urlparse(self.ssh_link)
                user_name, _ = url.netloc.split('@')
                self.ssh_link = url._replace(netloc=user_name+'@'+bitbucket_url).geturl()
        if 'branches' in kwargs:
            self.branches = kwargs['branches']

    def __eq__(self, repoName):
        return self.name == repoName



class Bitbucket:
    
    url = property()
    
    def __init__(self, userfile, link):
        global bitbucket_api_link
        global bitbucket_url
        bitbucket_url = link
        bitbucket_api_link = urlparse(bitbucket_api_link)._replace(netloc=bitbucket_url).geturl()
        self._url = bitbucket_api_link
        
        self.user = LogedUser(userfile)
        self.has_access = False
        self.session = requests.Session()
        self.projects = []
        self.progress_string = "Starting load data from Bitbucket"
        
    @url.setter
    def url(self, new_url):
        global bitbucket_api_link
        self._url = urlparse(bitbucket_api_link)._replace(netloc=new_url).geturl()
        bitbucket_api_link = self._url
        
    @url.getter
    def url(self):
        return self._url
        
    def Login(self, user_name, password):
        self.user(slug = user_name, password = password)
        self.session.auth = requests.auth.HTTPBasicAuth(self.user.slug, self.user.password)
        url = self._url + users + '/'+ str(self.user.slug)
        try:
            httpGetResponse = self.session.get(url, timeout = 5.0)
            self.jsonResponse = json.loads(httpGetResponse.text)
            if httpGetResponse.status_code == 200:
                self.user(**self.jsonResponse)
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
            return {'errors': [{'message': 'Incorrect JSON format received.'}]}
        
        except ConnectTimeout:
            return {'errors': [{'message': 'There is no server connection. Timeout was reached.'}]}
        
        except ConnectionError:
            return {'errors': [{'message': 'There is no server connection.'}]}
        
        except ReadTimeout:
            return {'errors': [{'message': 'There is no server connection. Timeout was reached.'}]}
        
    def parse_response(self, url):
        http_response = self.session.get(url, timeout = 5.0)
        if http_response.status_code == 200:
            return json.loads(str(http_response.text))
        else:
            return {'errors': [{'message': http_response.reason}]}
        
    def get_repo_branches(self, repo):
        if self.has_access == True:
            url = self._url + projects_repo + '/' + repo.project.key + '/' + module_repos + '/' + repo.slug + '/' + branches
            rsp = self.Paged_response_parse(url)
            if 'values' in rsp:
                for value in rsp['values']:
                    branch = Branch(value)
                    commits_on_this_branch = self.get_repo_commits_on_branch(repo, branch)
                    branch.commits += commits_on_this_branch
                    repo.branches.append(branch)
                    
    def get_repo_commits_on_branch(self, repo, branch):
        url = self._url + projects_repo + '/' + repo.project.key + '/' + module_repos + '/' + repo.slug + '/' + commits_on_branch + branch.id
        rsp = self.Paged_response_parse(url)
        requested_commits = []
        if 'values' in rsp:
            for value in rsp['values']:
                requested_commits.append(Commit(value))
                
            return requested_commits
        elif 'errors' in rsp:
            return []
        
    def GetProjectByKey(self, key):
        if isinstance(key, str):
            return self.projects[self.projects.index(key)]
        else:
            return self.projects[self.projects.index(str(key))]
        
    def GetRepositoryByName(self, project, repoName):
        if isinstance(project, Project):
            if isinstance(repoName, str): 
                return project.repositories[project.repositories.index(repoName)]
            else:
                return project.repositories[project.repositories.index(str(repoName))]  
        else:
            prj = self.GetProjectByKey(project)
            
        if isinstance(repoName, str):
            return prj.repositories[prj.repositories.index(repoName)]
        else:
            return prj.repositories[prj.repositories.index(str(repoName))]    
    
        
    def Get_projects(self):
        if self.has_access == True:
            url = self._url + projects_repo
            rsp = self.Paged_response_parse(url)
            if 'values' in rsp:
                for value in rsp['values']:
                    project = Project(value)
                    project.repositories = self.Get_modules_repo(project.key)
                    self.projects.append(project)
                   
            else:
                return
            self.progress_string = "Finished" 
        else:
            return


    def Get_modules_repo(self, project_key=u''):
        if self.has_access == True:
            repositories = []
            if project_key == u'':
                url = self._url + module_repos
            else:
                url = self._url + projects_repo + u'/' + project_key + u'/' + module_repos
            
            rsp = self.Paged_response_parse(url)
            if 'values' in rsp:
                for value in rsp['values']:
                    repo = Repository(value)
                    self.progress_string = "Load " + repo.name + " data"
                    self.get_repo_branches(repo)
                    repositories.append(repo)
                    
            return repositories
        
    def Get_repository_by_response(self, response):
        return Repository(response)
                    
    @staticmethod
    def clone_selected(selected_items):
        if search_env('git') is True:
            for item in selected_items:
                print(item)
            
            
            return {'success': 'The selected repositories are cloned to ...'}
        else:
            return {'error': 'You have no git installed on your computer.\nPlease install git and try again'}               
    

class SelectedRepoVersion(object):
    def __init__(self,repo, branch=None, commit=None,**kwargs):
        super(SelectedRepoVersion, self).__init__(**kwargs)
        self.repo = repo
        self.branch = branch
        self.commit = commit
        self.displayText = ''
        if commit is not None and branch is not None:
            self.displayText = repo.name+'/'+branch.displayId+'/'+commit.displayId
        elif branch is not None and commit is None:
            self.displayText = repo.name+'/'+branch.displayId
        elif branch is None and commit is None:
            self.displayText = repo.name+'/master'     
       
            
    def __eq__(self, other):
        return self.repo is other.repo and self.branch is other.branch and self.commit is other.commit
    
    def __str__(self):
        return '%s' % self.displayText
    
    
