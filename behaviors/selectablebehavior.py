#!/usr/bin/kivy
# -*- coding: utf-8 -*-

from kivy.uix.treeview import TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from behaviors.hoverbehavior import HoverBehavior
from sys import platform
import re
from kivy.core.window import Window

if 'win' in platform:
    file_route_spliter = '\\'
else:
    file_route_spliter = '/'
    
    
Builder.load_file('behaviors'+file_route_spliter+'selectablebehavior.kv')
    
 
 
class SelectedItem(BoxLayout):
    
    class HoverButton(Button, HoverBehavior):
        pass
    
    def __init__(self, text, **kwargs):
        self.item_name = text
        capital_letters_number = len(re.findall('([A-Z])', text))
        self.item_name_len = capital_letters_number*9.5 + (len(text)-capital_letters_number)*7.5
        super(SelectedItem, self).__init__(**kwargs)
    
    def on_delete(self):
        self.parent.parent.parent.dispatch('on_delete_item', self)
    
class SelectedItemsView(BoxLayout):
    
    label_text = StringProperty()
    label_height = NumericProperty()
    
    def __init__(self, label_text, **kwargs):
        self.register_event_type('on_add_item')
        self.register_event_type('on_delete_item')
        super(SelectedItemsView, self).__init__(**kwargs)
        self.label_height = '30dp'
        self.label_text = label_text
        self.stack = self.ids.stack
        self.items = set()
        selectedItem_height = Window.size[1] - self.label_height - self.spacing
        self.stack.bind(minimum_size=lambda w, size: w.setter('height')(w, (size[1] if size[1] > selectedItem_height else selectedItem_height)))
        
    def on_add_item(self, item):
        if not item in self.items:
            self.items.add(item)
            self.stack.add_widget(SelectedItem(text = item.name))
        
    def on_delete_item(self, widget):
        item_filtered = list(filter(lambda x: x.name == widget.item_name, self.items))
        if len(item_filtered) != 1:
            return
        item = item_filtered[-1]
        self.items.remove(item)
        self.stack.remove_widget(widget)

    
class TreeViewSelectableItem(TreeViewLabel):
    
    def __init__(self, item = None, text = None, **kwargs):
        self.item = None
        self.register_event_type('on_double_tap')
        super().__init__(**kwargs)
        if item is not None and text is not None:
            self.item = item
            self.text = text

    def on_touch_up(self, touch):
        if self.is_selected:
            if touch.is_double_tap:
                self.dispatch('on_double_tap', self.item)
            
            print(self.item)    
            
    def on_double_tap(self,item):
        pass
    
    
    