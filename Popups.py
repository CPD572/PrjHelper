#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from behaviors.windowbehavior import adapt_window, isNewWindowBigger

class StandartPopup(Popup):
    message = StringProperty()
    
    def __init__(self, message = '', **kwargs):
        Popup.__init__(self, **kwargs)
        self.register_event_type('on_content_changed')
        self.message = message  
        self.auto_dismiss = False
        self.b = BoxLayout(orientation = 'vertical')
        self.b.add_widget(Label(text = self.message))
        self.size = [550, 150]
        self.old_size = ()
        
    def on_open(self):
        if Window.size <= tuple(self.size):
            self.add_widget(self.b)
            self.old_size = Window.size
            adapt_window((600,200))
            
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
        elif not isNewWindowBigger(self.old_size):
            
            adapt_window(self.old_size)
            self.old_size = ()
    

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
        
