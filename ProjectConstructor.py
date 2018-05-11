#!/usr/bin/kivy
# -*- coding: utf-8 -*-
import os

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from All_Projects import ProjectsScreen
from BitbucketAPI import Bitbucket
from Login import LoginScreen
from MLProject import MicroLabPlatform
from MlpArchitectureChanger import ChangeArchitectureScreen
from RepoSelector import RepoSelectorScreen


os.environ['KIVY_IMAGE'] = 'pil,sdl2'


class CustomScreenMenager(ScreenManager):
    
    def __init__(self, *args, **kwargs):
        super(CustomScreenMenager, self).__init__(*args, **kwargs)
        self.register_event_type('on_admin_connected')
        self.transition.duration = 0
        self.isMaximized, self.isMinimized, self.fullscreen = False, False, False
        self.window_size = ()
        Window.bind(on_minimize=self.on_window_minimize)
        Window.bind(on_maximize=self.on_window_maximize)
        Window.bind(on_restore=self.on_window_restore)
        
    def on_admin_connected(self, connection):
        self.add_widget(ChangeArchitectureScreen(name='ChangeArchitecture', session=connection))
        
    def change_screen(self, screen_name):
        self.prev_view = self.current
        self.current = screen_name
        
    def previuos_view(self):
        self.change_screen(self.prev_view)
        
    def on_window_minimize(self, w):
        self.isMinimized = True
        
    def on_window_maximize(self, w):
        self.isMaximized = True
        self.window_size = Window.size
        
    def on_window_restore(self, w):
        if self.isMaximized and not self.isMinimized:
            self.isMaximized = False
        
                
                
class ProjectConstructorApp(App):

    def build(self):
        
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.write()
        self.session = MicroLabPlatform()
        manager = CustomScreenMenager()
        
        #adding screens to application
        manager.add_widget(LoginScreen(name='Login', session=self.session))
        manager.add_widget(RepoSelectorScreen(name='RepoSelector', session=self.session))
        manager.add_widget(ProjectsScreen(name='ProjectSelector', session=self.session))

        return manager
    


if __name__ == '__main__':
    ProjectConstructorApp().run()
