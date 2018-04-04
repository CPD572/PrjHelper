#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.config import Config
from BitbucketAPI import Bitbucket
import Popups
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from sys import platform
import time
from threading import Thread
from kivy.clock import Clock

load_finished = False
timing_event = None

Builder.load_string("""
<CustomButton@Button>:
    font_size: 16

<LoginScreen>:
    username: user_name
    password: password
    saveUserData: isSaved
    
    BoxLayout:
        id: login
        orientation: "vertical"
        padding: 10
        spacing: 10
        
        BoxLayout:
            Label:
                text: 'User Name'
                size_hint_x: .7
            TextInput:
                id: user_name
                multiline: False
                write_tab: False
                selection_color: [0.1843, 0.6549, 0.8313, .5]
                focus: True
        BoxLayout:
            Label:
                text: 'Password'
                size_hint_x: .7
            TextInput:
                id: password
                multiline: False
                write_tab: False
                password: True
                
        BoxLayout:
            size_hint: [None, None]
            height: "20dp"
            orientation: "horizontal"
            pos_hint: {"right": .95, "bottom": 0}
            Label:
                text: 'Save login'
                font_size: 14
            CheckBox:
                id: isSaved
                #on_active: root.on_save_data_checkbox(self, self.active)
                size_hint: [.1, 1]
    
        BoxLayout:
            size_hint_y: None
            width: 100
            height: "30dp"
            CustomButton:
                id: submit_button
                text: "Submit"
                pos_hint: {"center_x": .5, "bottom":1}
                on_release: root.Submit()
            
""")

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
        global timing_event
        tmp = self.connection_session.Login(self.username.text, self.password.text)
        
        #if username and password are correct
        if tmp == 1:
            
            
            #check if Save login checkbox is checked
            if self.saveUserData.active == True:
                
            #   create XML with user data 'usr.mlbu' 
                self.connection_session.user.save_user()
            
            #the user data have to be deleted if "Save login" is unchecked
            else:
                self.connection_session.user.delete_saved_user()
            
            if self.connection_session.projects == []:
                self.thread = Thread(target=self.connection_session.Get_projects)
                self.thread.daemon = True
                
                
                self.popup = Popups.StandartPopup(title = 'Progress', message = self.connection_session.progress_string)
                timing_event = Clock.schedule_interval(self.on_popup_content, .1)
                
                self.thread.start()
                self.popup.open()
                
            elif self.loged_in == True:
                self.manager.transition.duration = 0
                self.manager.current = 'RepoSelector'

        
        #if username or password are incorrect
        elif tmp == 0:
            popup = Popups.ErrorPopup(message = self.connection_session.jsonResponse['errors'][0]['message'])
            self.loged_in = False
            popup.open()
            self.reset_form()
            
        #No internet connection or server is not responding
        elif  tmp == -1:
            popup = Popups.ErrorPopup(message = 'There is no server connection. Timeout was reached.')
            popup.open()
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
        Config.set('graphics', 'resizable', 'False')
        Screen.on_enter(self, *args)
        if self.autologin == True and self.loged_in == False:
            self.ids.submit_button.trigger_action()
        
        
    def on_popup_content(self, _):
        global load_finished, timing_event
        if self.connection_session.progress_string != "Finished":
            self.popup.change_message(self.connection_session.progress_string)
        elif load_finished is False:
            self.popup.dismiss(animation=False)
            load_finished = True
        elif load_finished is True:
            timing_event.cancel()
            #change screen to RepoSelector        
            self.manager.transition.duration = 0   
            self.manager.current = 'RepoSelector'        
            self.loged_in = True 
  
        
    def on_pre_leave(self, *args):
        Screen.on_pre_leave(self, *args)
        if hasattr(self, 'thread'):
            del self.thread
