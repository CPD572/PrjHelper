# !/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty


Builder.load_string("""
<MenuBox>:
    id: menu
    size_hint: [None, 1]
    width: "100dp"
    orientation: 'vertical'
    BoxLayout:
        id: menu_actions
        size_hint: [None, 1]
        Button:
            size_hint: [1, None]
            height: "60dp"
            pos_hint:{'center': .5, "top":1}
            text: root.change_view_button_text
            on_release: root.on_button_release()
    Button:
        size_hint: [1, None]
        height: "30dp"
        pos_hint:{'center': .5, "bottom":1}
        text: "Log out"
        on_release: root.on_logout()
""")


class MenuBox(BoxLayout): 
    change_view_button_text = StringProperty()
       
    def __init__(self, change_view_button_text, on_menu_button_release, **kwargs):
        super(MenuBox, self).__init__(**kwargs)
        self.change_view_button_text = change_view_button_text
        self.on_menubutton_release_callback = on_menu_button_release
          
    def on_button_release(self):
        self.on_menubutton_release_callback()
    
    def on_logout(self):
        self.parent.parent.manager.transition.duration = 0
        self.parent.parent.manager.current = 'Login'
                                      
