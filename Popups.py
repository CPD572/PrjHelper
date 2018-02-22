#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class PopupMessage(Popup):
    message = StringProperty()
    
    def __init__(self, message = None, **kwargs):
        Popup.__init__(self, **kwargs)
        self.message = message  
        self.auto_dismiss = False
        self.b = BoxLayout(orientation = 'vertical')
        self.b.add_widget(Label(text = self.message))
        self.button = Button(size_hint=(.3, .3), pos_hint= {"center_x": .5, "bottom":1}, 
                            font_size=16, 
                            text="Close",
                            on_release = self.Close)
        self.b.add_widget(self.button)
        self.add_widget(self.b)
        self.size = [550, 150]
        
    def on_open(self):
        if Window.size <= tuple(self.size):
            Window.size = (600,200)
        
    def Close(self, dummy):
        self.dismiss(animation=False)
        
    def on_dismiss(self):
        Window.size = (400, 160)

class WarningPopup(PopupMessage):
    
    def __init__(self, message = None, **kwargs):
        PopupMessage.__init__(self,message, **kwargs)
        self.separator_color = [0, 255, 255, 1]
        self.title = 'User full name'

        
class ErrorPopup(PopupMessage):
    
    def __init__(self, message = None, **kwargs):
        PopupMessage.__init__(self, message , **kwargs)
        self.title = 'Error'
        self.separator_color = [255, 0, 0, 1]
        
