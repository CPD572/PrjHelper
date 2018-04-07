#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from behaviors.selectablebehavior import SelectedItemsView, SelectedItem, TreeViewSelectableItem
from behaviors.menubehavior import MenuBox, MenuButton
from kivy.uix.treeview import TreeViewLabel, TreeView
from kivy.core.window import Window
from kivy.lang import Builder
from sys import platform
from BitbucketAPI import Bitbucket, SelectedRepoVersion, Repository, Branch, Commit
from behaviors.windowbehavior import adapt_window
from Popups import ContentPopup
from prj_creator import ProjectCreator

Builder.load_string("""
    
#:import hex kivy.utils.get_color_from_hex

<ProjectsScreen>:
    BoxLayout:
        orientation: 'horizontal'
        id: main_box
        spacing: 5
        canvas:
            Color:
                rgba: hex('#303030')
            Rectangle:
                size: self.size
                pos: self.pos
        ScrollView:
            bar_width: '9dp'
            TreeView:
                id: scrolled_tree
                size_hint_y: None
""")

class ProjectsScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        super(ProjectsScreen, self).__init__(**kwargs)
        self.connection_session = session
        
        self.ids.scrolled_tree.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            
        self.treeview = self.ids.scrolled_tree
        self.treeview.root_options=dict(text='MicroLab Projects')
               
        self.selected_items_view = None

        self.creator = ProjectCreator()
        self.create_form = ContentPopup(title = "Create project")
        self.creator.bind(on_cancel = self.cancel_creating)
        self.creator.bind(on_submit = self.create_project)
        self.create_form.add_content(self.creator)
        
        self.entered = False
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        
        if self.connection_session != None and self.entered == False:
            self.selected_items_view = SelectedItemsView(label_text = 'Selected projects and repositories')
            self.ids.main_box.add_widget(self.selected_items_view)
            
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
            
            menu = MenuBox()
            change_view_button = MenuButton(text = 'Go to\nMLP')
            change_view_button.bind(on_release = self.on_change_view)
            
            clone_button = MenuButton(text = 'Create\nproject')
            clone_button.bind(on_release = self.on_create_prj_button_release)
            
            menu.add_button(change_view_button)
            menu.add_button(clone_button)
            self.ids.main_box.add_widget(menu)
            
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        adapt_window(((len(self.connection_session.projects)+4)*100,400))
        
    def on_change_view(self, button):
        self.manager.transition.duration = 0                                                                                     
        self.manager.current = 'RepoSelector'
        
    def on_selectable_item_double_tap(self,object,widget,item):
        
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
        self.selected_items_view.dispatch('on_add_item', selected_item, selected_item_text, tooltip_text)
        
    def on_create_prj_button_release(self, button):
        #Bitbucket.on_create_prj_button_release(self.selected_items_view.items)
        self.create_form.open()
    
    def cancel_creating(self, _):
        self.create_form.dismiss()
            
    def create_project(self, project):
        self.create_form.dismiss()
    
        