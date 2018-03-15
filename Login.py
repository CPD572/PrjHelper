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
        self.loged_in = False
        self.left_top_cord = ()
        if session != None:
            self.connection_session = session
            if self.connection_session.user.slug != u'':
                self.username.text = self.connection_session.user.slug
                self.password.text = self.connection_session.user.password
                self.saveUserData.active = True
                self.autologin = True
            else:
                self.saveUserData.active = False
                self.autologin = False
        else:       
            self.connection_session = Bitbucket()
            
    def is_user_data_saved(self):
        return self.connection_session.user.is_user_data_saved()
            
    def Submit(self):

        tmp = self.connection_session.Login(self.username.text, self.password.text)
        
        #if username and password are correct
        if tmp == 1:
            
            
            #check if Save login checkbox is checked
            if self.saveUserData.active == True:
                
            #   create XML with user data 'file.mlbu' 
                self.connection_session.user.save_user()
            
            #the user data have to be deleted if "Save login" is unchecked
            else:
                self.connection_session.user.delete_saved_user()
            
            if self.connection_session.projects == []:
                self.connection_session.Get_projects()
                
            #change screen to RepoSelector
            self.manager.transition.duration = 0
            self.manager.current = 'RepoSelector'
            
            self.loged_in = True
        
        #if username or password are incorrect
        elif tmp == 0:
            the_popup = Popups.ErrorPopup(self.connection_session.jsonResponse['errors'][0]['message'])
            self.loged_in = False
            the_popup.open()
            self.reset_form()
            
        #No internet connection or server is not responding
        elif  tmp == -1:
            the_popup = Popups.ErrorPopup('There is no server connection. Timeout was reached.')
            the_popup.open()
            self.loged_in = False

            
    def reset_form(self):
        self.username.text = ''
        self.password.text = ''
        self.saveUserData.active = False
        self.connection_session.user.delete_user()
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.loged_in == True:
            Window.left, Window.top = self.left_top_cord
        Window.size = (400, 160)
        self.left_top_cord = (Window.left, Window.top)
        
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        #self.Submit()

        
