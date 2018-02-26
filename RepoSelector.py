#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter
from sys import platform
import time
from kivy.uix.listview import ListItemButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.treeview import TreeViewNode, TreeViewLabel, TreeView
import re
import weakref
from kivy.uix.tabbedpanel import TabbedPanelItem

if 'linux' in platform:
    Builder.load_file('RepoSelector.kv')
    
    
class Selector(TreeViewNode):
    pass

class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        super(RepoSelectorScreen, self).__init__(**kwargs)
        #self.selected_repos = None
        self.bitbucketSession = None
        for key, value in list(filter(lambda tup: isinstance(tup[1], TreeView), self.ids.items())):
            value.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            
        self.tree_data_ids_list = list(filter(lambda x: x != 'bsw' and x != 'esw' and not re.match('(\w|\W)+_tree_view$', x),list(self.ids.keys())))

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
            self.ids.bsw_io.text:['^'+self.ids.bsw_io.text.lower()+'_(\w|\W)+', '^avr_(\w|\W)+', '^hal_(\w|\W)+'],
            self.ids.esw_sens.text:['^'+self.ids.esw_sens.text.lower()+'_(\w|\W)+'],
            self.ids.esw_act.text:['^'+self.ids.esw_act.text.lower()+'_(\w|\W)+'],
            self.ids.esw_pwrmng.text:['^'+self.ids.esw_pwrmng.text.lower()+'_(\w|\W)+'],
            self.ids.lib.text:['^'+self.ids.lib.text.lower()+'_(\w|\W)+']
            }
        
        if session != None:
            self.bitbucketSession = session
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.bitbucketSession != None:
            if self.bitbucketSession.projects == []:
                self.bitbucketSession.Get_projects()
                self.bitbucketSession.Get_modules_repo()
                
                repos=list(filter(lambda repo: repo.project.key == 'MLP' and not re.match('00_\w+', repo.name)
                                     and not re.match('(\w|\W)+_demo$', repo.name), self.bitbucketSession.repositories))
                
                for item in list(self.repositories.keys()):
                    for regEx in self.RegEx[item]:
                        self.repositories[item] += list(filter(lambda repo: re.match(regEx, repo.name), repos))


                for id in self.tree_data_ids_list:
                    for repo in self.repositories[self.ids[id].text]:
                        self.ids[id+'_tree_view'].add_node(TreeViewLabel(text = repo.name))
    
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        Window.size = (600,600)
        time.sleep(.5)

        
