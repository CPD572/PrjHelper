#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from behaviors.selectablebehavior import SelectedItemsView, SelectedItem, TreeViewSelectableItem
from behaviors.menubehavior import MenuBox
from kivy.uix.treeview import TreeViewLabel, TreeView
from kivy.core.window import Window
from kivy.lang import Builder
from sys import platform
import BitbucketAPI as Bitbucket

Builder.load_file('projects_view.kv')
    

class ProjectsScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        super(ProjectsScreen, self).__init__(**kwargs)
        self.connection_session = session
        
        self.ids.scrolled_tree.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            
        self.treeview = self.ids.scrolled_tree
        self.treeview.root_options=dict(text='MicroLab Projects')
               
        self.selected_items_view = None              
        
        self.entered = False
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.connection_session != None and self.entered == False:
            self.selected_items_view = SelectedItemsView(label_text = 'Selected projects and repositories')
            self.ids.main_box.add_widget(self.selected_items_view)
            self.ids.main_box.add_widget(MenuBox(change_view_button_text = 'Go to\nMLP', on_menu_button_release = self.on_change_view))
            for project in self.connection_session.projects:
                node = TreeViewLabel(text = project.name)
                self.treeview.add_node(node)
                for repo in project.repositories:
                    if repo.project.name == project.name:
                        selectableRepo = TreeViewSelectableItem(item = repo, text = repo.name)
                        selectableRepo.bind(on_double_tap = self.on_selectable_item_double_tap)
                        self.treeview.add_node(selectableRepo, node)
                        for branch in repo.branches:
                            selectableBranch = TreeViewSelectableItem(item = branch, text = branch.displayId)
                            selectableBranch.bind(on_double_tap = self.on_selectable_item_double_tap)
                            self.treeview.add_node(selectableBranch, selectableRepo)
                            for commit in branch.commits:
                                selectableCommit = TreeViewSelectableItem(item = commit, text = commit.message)
                                selectableCommit.bind(on_double_tap = self.on_selectable_item_double_tap)
                                self.treeview.add_node(selectableCommit, selectableBranch)
                        
            self.entered = True
            
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        new_width, new_height = ((len(self.connection_session.projects)+4)*100,400)
        old_width, old_height = Window.size
        Window.left, Window.top = (Window.left-(new_width-old_width)/2,Window.top-(new_height-old_height)/2)
        Window.size = (new_width, new_height)
        
    def on_change_view(self):
        self.manager.transition.duration = 0                                                                                     
        self.manager.current = 'RepoSelector'
        
    def on_selectable_item_double_tap(self,object,widget,item):
        
        branch = None
        commit = None
        if isinstance(item, Bitbucket.BitbucketCommit):
            commit = item
            branch = widget.parent_node.item
            repo = widget.parent_node.parent_node.item
        elif isinstance(item, Bitbucket.BitbucketBranch):
            repo = widget.parent_node.item
            branch = item
            if branch != []:
                commit = branch.commits[0]
        elif isinstance(item, Bitbucket.BitbucketRepo):
            repo = item
            if repo.branches != []:
                branch = list(filter(lambda commit: commit.displayId == "master", repo.branches))[-1]
                if branch.commits != []:
                    commit = branch.commits[0]
            
        selected_item = Bitbucket.SelectedRepoVersion(repo, branch, commit)
        self.selected_items_view.dispatch('on_add_item', selected_item, selected_item.displayText)
        