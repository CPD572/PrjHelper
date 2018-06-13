#!/usr/bin/kivy
# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton

from behaviors.menubehavior import MenuBox, MenuButton
from behaviors.selectablebehavior import SelectedItemsView, TreeViewSelectableItem
from behaviors.windowbehavior import adapt_window
import xml.etree.ElementTree as ElementTree
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as hex
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button


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
            padding: 5
            orientation: 'vertical'
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, None
                height: 200
                BoxLayout:
                    id: info_repo_text
                    orientation: 'horizontal'
                    spacing: 5
                    canvas:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5,]
                BoxLayout:
                    id: layers_checkboxes
                    orientation: 'horizontal'
                    spacing: 5
                    height: 50

                    
                    
                      
        BoxLayout:
            id: repos
            size_hint: [.7, 1]
            spacing: 5
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
        self.selected_view = SelectedItemsView(label_text="References:", size_hint=[1,1], halign='left', text_color=hex("#2bb3e7"), bold_text=True)
        self.entered = False
        self.previous_pushed_button = None
        self.window_size = (900,500)
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.connection_session != None and self.entered == False:
            mlp_project=self.connection_session.GetProjectByKey("MLP")
            
            #list of repositories added to TreeView
            for repository in mlp_project.repositories:
                node = TreeViewSelectableItem(item=repository, text=repository.name)
                node.bind(on_press = self.update_repo_info)
                self.ids.scrolled_tree.add_node(node)
                
            #first element to be selected
            first_item = self.ids.scrolled_tree.get_root().nodes[0]
            self.ids.scrolled_tree.select_node(first_item)
            first_item.dispatch('on_press', first_item)
                
            self.ids.layers_checkboxes.add_widget( Label(text="Software layer: ", size_hint=(None,None), height=40, pos_hint={"bottom":1}))
            dropdown = DropDown()
            for layer in self.connection_session.architecture:
                if layer.hasSublayers:
                    for sublayer in layer.getSublayers():
                        btn = Button(text=str(layer)+"/"+str(sublayer), size_hint_y=None, height=30)
                        btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                        dropdown.add_widget(btn)
                else:  
                    btn = Button(text=str(layer), size_hint_y=None, height=30)
                    btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                    dropdown.add_widget(btn)

            mainbutton = Button(text='Hello', size_hint=(None, None), height=40, pos_hint={"bottom":1})
            mainbutton.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
            self.ids.layers_checkboxes.add_widget(mainbutton)
                
                    
            self.ids.info.add_widget(self.selected_view)
            
            menu = MenuBox(manager=self.manager)
            
            export_button = MenuButton(text = 'Export to\n.mlparch')
            export_button.bind(on_release = self.export_to_mlparch)
            menu.add_button(export_button)
            
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
        
        
    def on_togle_press(self, button):
        print(button.parent.children)
        #layer = self.connection_session.architecture
        #if layer[layer.index(button.text)].hasSublayers and len(button.parent.children) == 1:
        #    #===================================================================================
        #    button.parent.add_widget(ToggleButton(group='layers', size_hint=[1,1], text=str(layer), on_press=self.on_togle_press))
        #    #===================================================================================
        #    self.previous_pushed_button = button
        
    def export_to_mlparch(self, button):
        print('Exporting...\nFinished')
        

    def update_repo_info(self, widget, item):
        print(widget)