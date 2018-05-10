#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeView
from kivy.uix.tabbedpanel import TabbedPanelItem, TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder
from behaviors.selectablebehavior import SelectedItemsView, TreeViewSelectableItem
from behaviors.menubehavior import MenuBox, MenuButton
import os
from BitbucketAPI import Bitbucket, SelectedRepoVersion, Repository, Branch, Commit
from behaviors.windowbehavior import adapt_window
from prj_creator import ProjectCreator
from Popups import ContentPopup
from kivy.uix.scrollview import ScrollView

Builder.load_string("""
#:import hex kivy.utils.get_color_from_hex

<RepoSelectorScreen>:
    BoxLayout:
        orientation: 'horizontal'
        id: main_box
        spacing: 5
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            id: selected_view
            
            TabbedPanel:
                do_default_tab: False
                tab_height: 30
                id: root_tabb
                           
""")


class Tab(TabbedPanelItem):
    
    def __init__(self, text, **kwargs):
        super(Tab, self).__init__(**kwargs)
        self.text = text
        self.scroll = ScrollView(bar_width='9dp', do_scroll_y=True)
        self.tree = TreeView(root_options={'text': 'MLP'}, size_hint_y=None)
        self.tree.bind(minimum_height=self.tree.setter('height'))
    
     
class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        
        super(RepoSelectorScreen, self).__init__(**kwargs)
        self.id = 'repo_selector_screen'
        self.connection_session = session
        self.creator = ProjectCreator()
        self.create_form = ContentPopup(title = "Create project")
        self.creator.bind(on_cancel = self.cancel_creating)
        self.creator.bind(on_submit = self.create_project)
        self.create_form.add_content(self.creator)
        
        self.window_size = (1400,800)
        self.old_size = self.window_size
        
        self.entered = False
        self.selectedItemViews = []
        
    def on_pre_leave(self, *args):
        Screen.on_pre_leave(self, *args)
        self.old_size = Window.size
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        adapt_window(self.old_size if self.old_size > self.window_size else self.window_size)
        if self.connection_session != None and self.entered == False:
            mlp_project=self.connection_session.GetProjectByKey("MLP")     
                   
            for layer in self.connection_session.architecture:
                tab = Tab(str(layer))
                if layer.hasSublayers:
                    subTabbedPanel = TabbedPanel(do_default_tab=False, tab_height=30)
                    for subLayerName, functionalSubLayers in layer.modules.items():
                        subTab = Tab(subLayerName)
                        nestedTabbedPanel = TabbedPanel(do_default_tab=False, tab_height=30)
                        for functionalSubLayer in functionalSubLayers.keys():
                            functionalSubTab = Tab(functionalSubLayer)
                            for name in functionalSubLayers[functionalSubLayer]:
                                repo = self.connection_session.GetRepositoryByName("MLP", name)
                                selectableRepo = TreeViewSelectableItem(item = repo, text = repo.name)
                                selectableRepo.bind(on_double_tap = self.on_selectable_item_double_tap)
                                functionalSubTab.tree.add_node(selectableRepo)
                                for branch in repo.branches:
                                    selectableBranch = TreeViewSelectableItem(item = branch, text = branch.displayId) 
                                    selectableBranch.bind(on_double_tap = self.on_selectable_item_double_tap)         
                                    functionalSubTab.tree.add_node(selectableBranch, selectableRepo)
                            functionalSubTab.scroll.add_widget(functionalSubTab.tree)
                            functionalSubTab.add_widget(functionalSubTab.scroll)
                            nestedTabbedPanel.add_widget(functionalSubTab)
                        subTab.add_widget(nestedTabbedPanel)
                        subTabbedPanel.add_widget(subTab)
                    tab.add_widget(subTabbedPanel)
                else:
                    repoNames = layer.modules.keys()
                    for name in repoNames:
                        repo = self.connection_session.GetRepositoryByName("MLP", name)
                        selectableRepo = TreeViewSelectableItem(item = repo, text = repo.name)
                        selectableRepo.bind(on_double_tap = self.on_selectable_item_double_tap)
                        tab.tree.add_node(selectableRepo)
                        for branch in repo.branches:                                                          
                            selectableBranch = TreeViewSelectableItem(item = branch, text = branch.displayId) 
                            selectableBranch.bind(on_double_tap = self.on_selectable_item_double_tap)         
                            tab.tree.add_node(selectableBranch, selectableRepo)                              
                    tab.scroll.add_widget(tab.tree)
                    tab.add_widget(tab.scroll)
                self.ids.root_tabb.add_widget(tab)
                
            self.tabs = list(reversed(self.ids.root_tabb.get_tab_list())) 
               
            stack = BoxLayout(orientation='horizontal', spacing=5, padding=5, size_hint_x=None)
            stack.bind(minimum_width=stack.setter('width'))
            for tabb in self.tabs:
                selected = SelectedItemsView(label_text=tabb.text, width='180dp')
                stack.add_widget(selected)
                self.selectedItemViews.append(selected)
                
            srolable = ScrollView(bar_width='9dp',do_scroll_x=True, do_scroll_y=False)  
            srolable.add_widget(stack)
            self.ids.selected_view.add_widget(srolable)
                    
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
        self.create_form.open()
            
        
    def on_selectable_item_double_tap(self,object,widget,item):
        instance_to_dispatch = list(filter(lambda x: x.label_text == self.ids.root_tabb.current_tab.text,                                                                 
                                   self.selectedItemViews))[-1]
        
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
        
        