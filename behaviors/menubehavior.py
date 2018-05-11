# !/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


Builder.load_string("""
<MenuBox>:
    id: menu
    size_hint: [None, 1]
    width: "100dp"
    orientation: 'vertical'
    StackLayout:
        id: menu_actions
        orientation: 'lr-tb'
        size_hint: [None, 1]
    Button:
        size_hint: [1, None]
        height: "30dp"
        #pos_hint:{'center': .5, "bottom":1}
        text: "Log out"
        on_release: root.on_logout()
        
        
<MenuButton>:
    height: "60dp"
    size_hint: [1, None]
""")

class MenuButton(Button):
    pass

class MenuBox(BoxLayout): 
    change_view_button_text = StringProperty()
       
    def __init__(self, **kwargs):
        super(MenuBox, self).__init__(**kwargs)
        
    def add_button(self, button):
        button.height = '60dp'
        button.size_hint= (1, None)
        button.pos_hint={'center': .5, "top":1}
        self.ids.menu_actions.add_widget(button)
          
    def on_button_release(self):
        self.on_menubutton_release_callback()
    
    def on_logout(self):
        self.manager.change_screen('Login')
                                      
