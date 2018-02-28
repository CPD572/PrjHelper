#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from sys import platform
import time
from kivy.uix.treeview import TreeViewLabel, TreeView
import re
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.button import Button
from kivy.adapters.models import SelectableDataItem
from kivy.properties import BooleanProperty, ObjectProperty

if 'linux' in platform:
    Builder.load_file('RepoSelector.kv')
    
class HoverBehavior(object):
    """Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget 
    """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        #Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass
    
class SelectedItems:
    pass    

    
class TreeViewSelectableItem(TreeViewLabel):
    
    def __init__(self, item = None, **kwargs):
        self.item = None
        super().__init__(**kwargs)
        if item is not None:
            self.item = item
            self.text = self.item.name

    def on_touch_up(self, touch):
        if self.is_selected and touch.is_double_tap:
            print(self.item.name)

class RepoSelectorScreen(Screen):
    
    def __init__(self, session=None, **kwargs):
        super(RepoSelectorScreen, self).__init__(**kwargs)
        #self.selected_repos = None
        self.bitbucketSession = None
        for key, value in list(filter(lambda tup: isinstance(tup[1], TreeView), self.ids.items())):
            value.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1]))
            #value.hide_root = True
            #value.indent_level=0
            
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
            
        
    def on_pre_enter(self, *args):
        Screen.on_pre_enter(self, *args)
        if self.bitbucketSession != None:
            if self.bitbucketSession.projects == []:
                self.selectableItems = []
                self.bitbucketSession.Get_projects()
                self.bitbucketSession.Get_modules_repo()
                
                #repo.project.key == 'MLP' and
                repos=list(filter(lambda repo: not re.match('00_\w+', repo.name)
                                     and not re.match('(\w|\W)+_demo$', repo.name), self.bitbucketSession.repositories))
                
                for item in list(self.repositories.keys()):
                    for regEx in self.RegEx[item]:
                        self.repositories[item] += list(filter(lambda repo: re.match(regEx, repo.name), repos))


                for id in self.tree_data_ids_list:
                    tree_view = self.ids[id+'_tree_view']
                    for repo in self.repositories[self.ids[id].text]:
                        tree_view.add_node(TreeViewSelectableItem(item = repo))
                        
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        Window.size = (600,600)
        time.sleep(.5)
        
        
