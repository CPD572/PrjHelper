#!/usr/bin/kivy
# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from behaviors.menubehavior import MenuBox, MenuButton
from behaviors.selectablebehavior import SelectedItemsView, TreeViewSelectableItem
from behaviors.windowbehavior import adapt_window
import xml.etree.ElementTree as ElementTree


Builder.load_string("""

<ChangeArchitectureScreen>:
    BoxLayout:
        orientation: 'horizontal'
        id: main_box
        spacing: 5
        
        BoxLayout:
            id: info
            size_hint: [1, 1]
            spacing: 5
            orientation: 'horizontal'
            
            
        BoxLayout:
            id: repos
            size_hint: [.7, 1]
            canvas:
                Color:
                    rgba: hex('#303030')
                Rectangle:
                    size: self.size
                    pos: self.pos
            ScrollView:
                scroll_type: ['bars']
                bar_width: '12dp'
                size_hint_y: 1
                TreeView:
                    id: scrolled_tree
                    hide_root: True
                    size_hint_y: None
 
""")

class ChangeArchitectureScreen(Screen):
    
    def __init__(self,session=None, **kwargs):
        super(ChangeArchitectureScreen, self).__init__(**kwargs)
        self.connection_session = session
        self.ids.scrolled_tree.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
        self.entered = False
        
        self.window_size = (900,500)
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.connection_session != None and self.entered == False:
            mlp_project=self.connection_session.GetProjectByKey("MLP")
            for repository in mlp_project.repositories:
                node = TreeViewSelectableItem(item=repository, text=repository.name)
                self.ids.scrolled_tree.add_node(node)
            
            menu = MenuBox(manager=self.manager)
            prev_view = MenuButton(text = 'Back')
            prev_view.bind(on_release = self.on_back_button_press)
            menu.add_button(prev_view)
            self.ids.main_box.add_widget(menu)
            
            self.entered = True
            
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        self.manager.bind(on_unmaximaze = self.on_unmaximaze)
        adapt_window(self.window_size if not self.manager.isMaximized else self.manager.window_size )
            
    def on_back_button_press(self, button):
        self.manager.previuos_view()
        
        
    def on_unmaximaze(self, manager):
        adapt_window(self.window_size)
        