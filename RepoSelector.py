#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from sys import platform
import time

if 'linux' in platform:
    Builder.load_file('RepoSelector.kv')

class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.repos = None
        self.bitbucketSession = None
        if session != None:
            self.bitbucketSession = session
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.bitbucketSession != None:
            if self.bitbucketSession.projects == []:
                self.bitbucketSession.Get_projects()
                self.bitbucketSession.Get_modules_repo()
    
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        Window.size = (600,600)
        time.sleep(.5)

        
