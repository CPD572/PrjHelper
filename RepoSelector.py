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
        
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        Window.size = (600,200)
        time.sleep(.5)

        
