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
    
    def __init__(self, session=None, window = Window, **kwargs):
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.window = window
        
        
    def on_pre_leave(self, *args):
        Screen.on_pre_leave(self, *args)
        #self.window.hide()
        time.sleep(.5)
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        self.window.size = (600,200)
        time.sleep(.5)
        print('entered the RepoSelector page')
        self.window.show()
        #Window.show()
        #Window.show()
        #Window.show()
        #Window.show()
        
