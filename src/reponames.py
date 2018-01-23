#!/bin/python

""" 

Script to get all repository's names. This is just a test script to start working with Bitbucket API and is gonna be refactor.
To get this script working in the command line, please, enter the command "pip install requests" if you already has install the pip. If not
Google will help you to install it.

"""

import requests
import json
import os

project_uri = 'http://repo.microlab.club/rest/api/1.0/projects/MLP/repos/'
username = ''
password = ''
repositories = []

session = requests.Session()

username = input('Username: ')
password = input('Password: ')

session.auth = requests.auth.HTTPBasicAuth(username, password)

httpGetResponse = session.get(project_uri)

response_pages = list()
response_pages.append(json.loads(httpGetResponse.text))

if httpGetResponse.status_code == 200:
    
    if response_pages[-1]["isLastPage"] is False:
        nextPageStarts = response_pages[0]["nextPageStart"]
    
        while response_pages[-1]["isLastPage"] is False:
        
            response_pages.append(json.loads(session.get(project_uri + '?start=' + str(nextPageStarts)).text))
            if "nextPageStart" in list(response_pages[-1].keys()):
                nextPageStarts = response_pages[-1]["nextPageStart"]
        
    
    for i in range(len(response_pages)):
        for j in range(response_pages[i]['size']):
                repositories.append(response_pages[i]['values'][j]['slug'])

else:
    for i in range(len(response_pages[-1]['errors'])):
        print(response_pages[-1]['errors'][i]['message'] )