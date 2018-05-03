#!/usr/bin/kivy
# -*- coding: utf-8 -*-
import os
os.environ['KIVY_IMAGE'] = 'pil,sdl2'
from BitbucketAPI import Bitbucket
from Login import LoginScreen
from All_Projects import ProjectsScreen
from RepoSelector import RepoSelectorScreen
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager
from MLProject import MicroLabPlatform


class ProjectConstructorApp(App):

    def build(self):
        
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.write()
        self.session = MicroLabPlatform()
        manager = ScreenManager()
        
        #adding screens to application
        manager.add_widget(LoginScreen(name = 'Login', session = self.session))
        manager.add_widget(RepoSelectorScreen(name = 'RepoSelector', session = self.session))
        manager.add_widget(ProjectsScreen(name = 'ProjectSelector', session = self.session))

            
        return manager


if __name__ == '__main__':
    ProjectConstructorApp().run()
