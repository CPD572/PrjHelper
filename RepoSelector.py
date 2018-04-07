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
from behaviors.menubehavior import MenuBox, MenuButton
from sys import platform
import re, os
import time
from BitbucketAPI import Bitbucket, SelectedRepoVersion, Repository, Branch, Commit
from behaviors.windowbehavior import adapt_window
from prj_creator import ProjectCreator
from Popups import ContentPopup

Builder.load_string("""
#:import hex kivy.utils.get_color_from_hex

<RepoSelectorScreen>:
    BoxLayout:
        orientation: 'horizontal'
        id: main_box
        spacing: 5
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 585
            id: selected_view
            
            TabbedPanel:
                do_default_tab: False
                tab_height: 30
                id: root_tabb
                
                TabbedPanelItem:
                    id: asw
                    text: "ASW"
                    ScrollView:
                        bar_width: '9dp'
                        TreeView:
                            id: asw_tree_view
                            size_hint_y: None
                        
                    
                TabbedPanelItem:
                    id: bsw
                    text: "BSW"
                    TabbedPanel:
                        do_default_tab: False
                        tab_height: 30
                        
                        TabbedPanelItem:
                            id: bsw_hmi
                            text: "HMI"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: bsw_hmi_tree_view
                                    size_hint_y: None
                                
                        TabbedPanelItem:
                            id: bsw_com
                            text: "COM"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: bsw_com_tree_view
                                    size_hint_y: None
                                
                        TabbedPanelItem:
                            id: bsw_io
                            text: "IO"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: bsw_io_tree_view
                                    size_hint_y: None
                        
                TabbedPanelItem:
                    id: esw
                    text: "ESW"
                    TabbedPanel:
                        do_default_tab: False
                        tab_height: 30
                        
                        TabbedPanelItem:
                            id: esw_sens
                            text: "SENS"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: esw_sens_tree_view
                                    size_hint_y: None
                                
                        TabbedPanelItem:
                            id: esw_act
                            text: "ACT"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: esw_act_tree_view
                                    size_hint_y: None
                                
                        TabbedPanelItem:
                            id: esw_pwrmng
                            text: "PWRMNG"
                            ScrollView:
                                bar_width: '9dp'
                                TreeView:
                                    id: esw_pwrmng_tree_view
                                    size_hint_y: None
                                    
                TabbedPanelItem:
                    id: lib
                    text: "LIB"
                    BoxLayout:
                    ScrollView:
                        bar_width: '9dp'
                        TreeView:
                            id: lib_tree_view
                            size_hint_y: None
                            
                            
        BoxLayout:
            orientation: 'horizontal'
            id: selected_items_lists
            spacing: 5
#            canvas:
#                Color:
#                    rgba: 1, 0, 0, 1
#                Rectangle:
#                    size: self.size
#                    pos: self.pos
""")

     
class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.id = 'repo_selector_screen'
        self.tabs = list(reversed(self.ids.root_tabb.get_tab_list()))
        self.connection_session = session
        self.creator = ProjectCreator()
        self.create_form = ContentPopup(title = "Create project")
        self.creator.bind(on_cancel = self.cancel_creating)
        self.creator.bind(on_submit = self.create_project)
        self.create_form.add_content(self.creator)
        
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
        self.selectedItemViews = []
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        adapt_window((1600,400))
        if self.connection_session != None and self.entered == False:
                
            mlp_project=list(filter(lambda project: project.key == 'MLP', self.connection_session.projects))[-1]
            
            for item in list(self.repositories.keys()):
                for regEx in self.RegEx[item]:
                    self.repositories[item] += list(filter(lambda repo: re.match(regEx, repo.name) and not re.match("((\w|\W)+_demo|(\w|\W)+_test)", repo.name), mlp_project.repositories))
            
            
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
                   
            for tabb in self.tabs:
                selected = SelectedItemsView(label_text = tabb.text)
                self.ids.selected_items_lists.add_widget(selected)
                self.selectedItemViews.append(selected)
                    
            menu = MenuBox()
            change_view_button = MenuButton(text = 'All projects')
            change_view_button.bind(on_release = self.on_change_view)
            
            clone_button = MenuButton(text = 'Create\nproject')
            
            clone_button.bind(on_release = self.on_create_prj_button_release)
            
            
            menu.add_button(change_view_button)
            menu.add_button(clone_button)
            self.ids.main_box.add_widget(menu)
            
            self.entered = True
            
            
    def cancel_creating(self, _):
        self.create_form.dismiss()
            
    def create_project(self, project):
            
        for layer in self.selectedItemViews:
            os.mkdir(os.path.join(project.project_path, layer.label_text))
        
        self.create_form.dismiss()

    def on_create_prj_button_release(self, button):
        #all_items = []
        #for view in self.selectedItemViews:
        #    all_items += view.items
            
        self.create_form.open()
            
        
    def on_selectable_item_double_tap(self,object,widget,item):
        instance_to_dispatch = list(filter(lambda x: x.label_text == self.ids.root_tabb.current_tab.text,                                                                 
                                   list(filter(lambda n: isinstance(n, SelectedItemsView),self.ids.selected_items_lists.children))))[-1]
        
        branch = None
        commit = None
        if isinstance(item, Commit):
            commit = item
            branch = widget.parent_node.item
            repo = widget.parent_node.parent_node.item
        elif isinstance(item, Branch):
            repo = widget.parent_node.item
            branch = item
            if branch.commits != []:
                commit = branch.commits[0]
        elif isinstance(item, Repository):
            repo = item
            if repo.branches != []:
                branch = list(filter(lambda commit: commit.displayId == "master", repo.branches))[-1]
                if branch.commits != []:
                    commit = branch.commits[0]
            
        selected_item = SelectedRepoVersion(repo, branch, commit)
        selected_item_text = selected_item.displayText.split('/')[0]
        tooltip_text = selected_item.displayText.replace(selected_item_text+'/', '')
        instance_to_dispatch.dispatch('on_add_item', selected_item, selected_item_text, tooltip_text)
        
    def on_change_view(self, button):
        self.manager.transition.duration = 0                                                                                     
        self.manager.current = 'ProjectSelector'
        
        