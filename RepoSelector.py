#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeViewLabel, TreeView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from hoverbehavior import HoverBehavior
from sys import platform
import re
import time

if 'linux' in platform:
    Builder.load_file('RepoSelector.kv')
 
screen_item = None

class SelectedItem(BoxLayout):
    
    class HoverButton(Button, HoverBehavior):
        pass
    
    def __init__(self, text, **kwargs):
        self.item_name = text
        capital_letters_number = len(re.findall('([A-Z])', text))
        self.item_name_len = capital_letters_number*9.5 + (len(text)-capital_letters_number)*7.5
        super(SelectedItem, self).__init__(**kwargs)
    
    def on_delete(self):
        self.parent.parent.dispatch('on_delete_item', self)
    
class SelectedItemsView(BoxLayout):
    
    label_text = StringProperty()
    
    def __init__(self, label_text, **kwargs):
        self.register_event_type('on_add_item')
        self.register_event_type('on_delete_item')
        super(SelectedItemsView, self).__init__(**kwargs)
        self.label_text = label_text
        self.stack = list(filter(lambda x: isinstance(x, StackLayout), self.children))[-1]
        self.items = set()
        
    def on_add_item(self, item):
        if not item in self.items:
            self.items.add(item)
            self.stack.add_widget(SelectedItem(text = item.name))
            print(self.pos)
        
    def on_delete_item(self, widget):
        item_filtered = list(filter(lambda x: x.name == widget.item_name, self.items))
        if len(item_filtered) != 1:
            return
        item = item_filtered[-1]
        self.items.remove(item)
        self.stack.remove_widget(widget)

    
class TreeViewSelectableItem(TreeViewLabel):
    
    def __init__(self, item = None, **kwargs):
        self.item = None
        super().__init__(**kwargs)
        if item is not None:
            self.item = item
            self.text = self.item.name

    def on_touch_up(self, touch):
        if self.is_selected and touch.is_double_tap:
            
            active_tabb = screen_item.ids.root_tabb.current_tab
            instance_to_dispatch = list(filter(lambda x: x.label_text == active_tabb.text, 
                                               list(filter(lambda n: isinstance(n, SelectedItemsView),screen_item.ids.selected_items_lists.children))))[-1]
            instance_to_dispatch.dispatch('on_add_item', self.item)
             

class RepoSelectorScreen(Screen):
    
    
    class LogOutButton(Button):
        pass
    
    def __init__(self, session=None, **kwargs):
        global screen_item
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.id = 'repo_selector_screen'
        self.tabbs = reversed(self.ids.root_tabb.get_tab_list())
        self.bitbucketSession = None
        for key, value in list(filter(lambda tup: isinstance(tup[1], TreeView), self.ids.items())):
            value.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            
        self.tree_data_ids_list = list(filter(lambda x: x != 'bsw' and x != 'esw' and isinstance(self.ids[x], TabbedPanelItem),list(self.ids.keys())))

        self.repositories = {
            self.ids.asw.text:[],
            self.ids.bsw_hmi.text:[],
            self.ids.bsw_com.text:[],
            self.ids.bsw_io.text:[],
            self.ids.esw_sens.text:[],
            self.ids.esw_act.text:[],
            self.ids.esw_pwrmng.text:[],
            self.ids.lib.text:[]
            }
        #RegEx for ASW differs so it has to be chancged according to used repo names 
        self.RegEx = {
            self.ids.asw.text:['^'+self.ids.asw.text.lower()+'_(\w|\W)+', '^0_(\w|\W)+', '^1_(\w|\W)+', '^drive_(\w|\W)+', '^sys_(\w|\W)+'], 
            self.ids.bsw_hmi.text:['^'+self.ids.bsw_hmi.text.lower()+'_(\w|\W)+'],
            self.ids.bsw_com.text:['^'+self.ids.bsw_com.text.lower()+'_(\w|\W)+'],
            self.ids.bsw_io.text:['^'+self.ids.bsw_io.text.lower()+'_(\w|\W)+', '^avr_(\w|\W)+', '^hal_(\w|\W)+', '^mcal_(\w|\W)+'],
            self.ids.esw_sens.text:['^'+self.ids.esw_sens.text.lower()+'_(\w|\W)+'],
            self.ids.esw_act.text:['^'+self.ids.esw_act.text.lower()+'_(\w|\W)+'],
            self.ids.esw_pwrmng.text:['^'+self.ids.esw_pwrmng.text.lower()+'_(\w|\W)+'],
            self.ids.lib.text:['^'+self.ids.lib.text.lower()+'_(\w|\W)+']
            }
        
        if session != None:
            self.bitbucketSession = session
            
        #saving the screen instance for global purposes
        screen_item = self
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.bitbucketSession != None:
            if self.bitbucketSession.projects == []:
                self.selectableItems = []
                self.bitbucketSession.Get_projects()
                self.bitbucketSession.Get_modules_repo()
                
                #repo.project.key == 'MLP' and
                repos=list(filter(lambda repo: repo.project.key == 'MLP' and not re.match('00_\w+', repo.name)
                                     and not re.match('(\w|\W)+_demo$', repo.name) and not re.match('(\w|\W)+_test$', repo.name), self.bitbucketSession.repositories))
                
                for item in list(self.repositories.keys()):
                    for regEx in self.RegEx[item]:
                        self.repositories[item] += list(filter(lambda repo: re.match(regEx, repo.name), repos))


                for id in self.tree_data_ids_list:
                    tree_view = self.ids[id+'_tree_view']
                    tree_view.root_options = {'text': 'MLP'}
                    for repo in self.repositories[self.ids[id].text]:
                        tree_view.add_node(TreeViewSelectableItem(item = repo))
                        
                for tabb in self.tabbs:
                    self.ids.selected_items_lists.add_widget(SelectedItemsView(label_text = tabb.text))
                
                self.ids.main_box.add_widget(self.LogOutButton())
                        
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        new_width, new_height = (1600,400)
        old_width, old_height = Window.size
        Window.left, Window.top = (Window.left-(new_width-old_width)/2,Window.top-(new_height-old_height)/2)
        Window.size = (new_width, new_height)
   
