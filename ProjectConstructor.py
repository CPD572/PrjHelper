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


class ProjectConstructorApp(App):

    def build(self):
        
        Config.set('graphics', 'resizable', 'False')
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.write()
        self.session = Bitbucket()
        manager = ScreenManager()
        
        #adding screens to application
        login_screen = LoginScreen(name = 'Login', session = self.session)
        manager.add_widget(login_screen)
        manager.add_widget(RepoSelectorScreen(name = 'RepoSelector', session = self.session))
        manager.add_widget(ProjectsScreen(name = 'ProjectSelector', session = self.session))
        
        #auto log in if user data saved
        if self.session.user.slug != u'':
            login_screen.Submit()
            
        return manager


if __name__ == '__main__':
    ProjectConstructorApp().run()
