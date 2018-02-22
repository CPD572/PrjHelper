#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from BitbucketAPI import Bitbucket
import Login
from RepoSelector import RepoSelectorScreen
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager


class ProjectConstructorApp(App):

    def build(self):
        Config.set('graphics', 'width', '400')
        Config.set('graphics', 'height', '160')
        Config.set('graphics', 'resizable', 'False')
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.write()
        appWindow = Window
        self.session = Bitbucket()
        manager = ScreenManager()
        manager.add_widget(Login.LoginScreen(name = 'Login', session = self.session))
        manager.add_widget(RepoSelectorScreen(name = 'RepoSelector', session = self.session))
        return manager


if __name__ == '__main__':
    ProjectConstructorApp().run()
