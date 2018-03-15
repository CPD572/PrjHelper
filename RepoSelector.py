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
from behaviors.selectablebehavior import SelectedItem, SelectedItemsView, TreeViewSelectableItem
from behaviors.menubehavior import MenuBox
from sys import platform
import re
import time

if 'linux' in platform:
    Builder.load_file('RepoSelector.kv')
     
class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.id = 'repo_selector_screen'
        self.tabbs = reversed(self.ids.root_tabb.get_tab_list())
        self.connection_session = session
        
        
        for key, value in list(filter(lambda tup: isinstance(tup[1], TreeView), self.ids.items())):
            value.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            
        self.tree_data_ids_list = list(filter(lambda x: x != 'bsw' and x != 'esw' and isinstance(self.ids[x], TabbedPanelItem),list(self.ids.keys())))

        self.repositories = {
            'ASW'   :[],
            'HMI'   :[],
            'COM'   :[],
            'IO'    :[],
            'SENS'  :[],
            'ACT'   :[],
            'PWRMNG':[],
            'LIB'   :[]
            }
        #RegEx for ASW differs so it has to be chancged according to used repo names 
        self.RegEx = {
            'ASW'   :['^asw_(\w|\W)+', '^0_(\w|\W)+', '^1_(\w|\W)+', '^drive_(\w|\W)+', '^sys_(\w|\W)+'], 
            'HMI'   :['^hmi_(\w|\W)+'],
            'COM'   :['^com_(\w|\W)+'],
            'IO'    :['^io_(\w|\W)+', '^avr_(\w|\W)+', '^hal_(\w|\W)+', '^mcal_(\w|\W)+'],
            'SENS'  :['^sens_(\w|\W)+'],
            'ACT'   :['^act_(\w|\W)+'],
            'PWRMNG':['^pwrmng_(\w|\W)+'],
            'LIB'   :['^lib_(\w|\W)+']
            }
        
        self.entered = False
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        new_width, new_height = (1600,400)
        
        old_width, old_height = Window.size
        Window.left, Window.top = (Window.left-(new_width-old_width)/2,Window.top-(new_height-old_height)/2)
        Window.size = (new_width, new_height)
        if self.connection_session != None and self.entered == False:
                
            #repo.project.key == 'MLP' and
            mlp_project=list(filter(lambda project: project.key == 'MLP', self.connection_session.projects))[-1]
            
            for item in list(self.repositories.keys()):
                for regEx in self.RegEx[item]:
                    self.repositories[item] += list(filter(lambda repo: re.match(regEx, repo.name), mlp_project.repositories))
            
            
            for id in self.tree_data_ids_list:
                tree_view = self.ids[id+'_tree_view']
                tree_view.root_options = {'text': 'MLP'}
                for repo in self.repositories[self.ids[id].text]:
                    selectableRepo = TreeViewSelectableItem(item = repo, text = repo.name)
                    selectableRepo.bind(on_double_tap = self.on_selectable_item_double_tap)
                    tree_view.add_node(selectableRepo)
                    for branch in repo.branches:
                        selectableBranch = TreeViewSelectableItem(item = branch, text = branch.displayId)
                        selectableBranch.bind(on_double_tap = self.on_selectable_item_double_tap)
                        tree_view.add_node(selectableBranch, selectableRepo)
                        for commit in branch.commits:
                            selectableCommit = TreeViewSelectableItem(item = commit, text = commit.message)
                            selectableCommit.bind(on_double_tap = self.on_selectable_item_double_tap)
                            tree_view.add_node(selectableCommit, selectableBranch)
                    
            for tabb in self.tabbs:
                selected = SelectedItemsView(label_text = tabb.text)
                self.ids.selected_items_lists.add_widget(selected)
                    
            self.ids.main_box.add_widget(MenuBox(change_view_button_text = 'All Projects', on_menu_button_release = self.on_change_view))
            self.entered = True
                        
        
    def on_selectable_item_double_tap(self,object,item):
        instance_to_dispatch = list(filter(lambda x: x.label_text == self.ids.root_tabb.current_tab.text,                                                                 
                                   list(filter(lambda n: isinstance(n, SelectedItemsView),self.ids.selected_items_lists.children))))[-1]
        instance_to_dispatch.dispatch('on_add_item', item)   
        
    def on_change_view(self):
        self.manager.transition.duration = 0                                                                                     
        self.manager.current = 'ProjectSelector'
