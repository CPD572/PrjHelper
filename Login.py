#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from BitbucketAPI import Bitbucket
import Popups
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from sys import platform
import time


if 'linux' in platform:
    Builder.load_file('Login.kv')

class LoginScreen(Screen):

    username = ObjectProperty()
    password = ObjectProperty()
    saveUserData = ObjectProperty()
    
    def __init__(self,session=None, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        if session != None:
            self.bitbucketSession = session
            if self.bitbucketSession.user.username != u'':
                self.username.text = self.bitbucketSession.user.username
                self.password.text = self.bitbucketSession.user.password
                self.saveUserData.active = True
            else:
                self.saveUserData.active = False
        else:       
            self.bitbucketSession = Bitbucket()
            
    def is_user_data_saved(self):
        return self.bitbucketSession.user.is_user_data_saved()
            
    def Submit(self):

        tmp = self.bitbucketSession.Login(self.username.text, self.password.text)
        
        #if username and password are correct
        if tmp == 1:
            
            
            #check if Save login checkbox is checked
            if self.saveUserData.active == True:
                
            #   create XML with user data 'file.mlbu' 
                self.bitbucketSession.user.save_user()
            
            #the user data have to be deleted if "Save login" is unchecked
            else:
                self.bitbucketSession.user.delete_saved_user()
                
            #change screen to RepoSelector
            self.manager.transition.duration = 0
            self.manager.current = 'RepoSelector'
        
        #if username or password are incorrect
        elif tmp == 0:
            the_popup = Popups.ErrorPopup(self.bitbucketSession.jsonResponse['errors'][0]['message'])
            the_popup.open()
            self.reset_form()
            
        #No internet connection or server is not responding
        elif  tmp == -1:
            the_popup = Popups.ErrorPopup('There is no server connection. Timeout was reached.')
            the_popup.open()

            
    def reset_form(self):
        self.username.text = ''
        self.password.text = ''
        self.saveUserData.active = False
        self.bitbucketSession.user.delete_user()
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        Window.size = (400, 160)    

