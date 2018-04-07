#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from behaviors.windowbehavior import adapt_window, isNewWindowBigger

class ContentPopup(Popup):
    
    #size = ListProperty([550, 150])
    
    def __init__(self, content_orientation = 'vertical', **kwargs):
        super(ContentPopup, self).__init__(**kwargs)
        self.content = BoxLayout(orientation = content_orientation)
        self.auto_dismiss = True
        self.window_size = [600,200]
        self.old_size = ()
        self.size_hint = None, None

    def on_open(self):
        if Window.size <= tuple(self.window_size):
            self.add_widget(self.content)
            self.old_size = Window.size
            adapt_window((600,200))
        else:
            self.size = self.window_size

    def add_content(self, content):
        self.remove_widget(self.content)
        self.content = content
        self.on_content(None, self.content)
        
    def remove_content(self):
        self.content.clear_widgets()

class StandartPopup(Popup):
    message = StringProperty()
    
    def __init__(self, message = '', **kwargs):
        Popup.__init__(self, **kwargs)
        self.register_event_type('on_content_changed')
        self.message = message  
        self.auto_dismiss = True
        self.b = BoxLayout(orientation = 'vertical')
        self.b.add_widget(Label(text = self.message))
        self.size = [550, 150]
        self.old_size = ()
        
    def on_open(self):
        if Window.size <= tuple(self.size):
            self.add_widget(self.b)
            self.old_size = list(Window.size)
            adapt_window((600,200))
        else:
            self.size = self.window_size
            
    def on_content_changed(self):
        pass
            
    def change_message(self, new_message):
        self.b.clear_widgets()
        self.message = new_message
        self.b.add_widget(Label(text = self.message))
        self.on_content(None, self.b)
        
    def on_dismiss(self):
        if self.old_size == ():
            return
        elif isNewWindowBigger(tuple(self.old_size)):
            adapt_window(self.old_size)
            self.old_size = ()
        else:
            print(tuple(self.old_size))
            print(Window.size)
    

class PopupMessage(StandartPopup):
    
    def __init__(self, message = '', **kwargs):
        StandartPopup.__init__(self, message, **kwargs)
        self.button = Button(size_hint=(.3, .3), pos_hint= {"center_x": .5, "bottom":1}, 
                            font_size=16, 
                            text="Close",
                            on_release = self.Close)
        self.b.add_widget(self.button)
        
        
    def Close(self, dummy):
        self.dismiss(animation=False)
        

class WarningPopup(PopupMessage):
    
    def __init__(self, message = '', **kwargs):
        PopupMessage.__init__(self,message, **kwargs)
        self.separator_color = [0, 255, 255, 1]
        self.title = 'User full name'

        
class ErrorPopup(PopupMessage):
    
    def __init__(self, message = '', **kwargs):
        PopupMessage.__init__(self, message , **kwargs)
        self.title = 'Error'
        self.separator_color = [255, 0, 0, 1]
        
