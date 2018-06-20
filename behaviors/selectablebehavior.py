#!/usr/bin/kivy
# -*- coding: utf-8 -*-

import os, sys
import re
from sys import platform

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.widget import Widget

from behaviors.hoverbehavior import HoverBehavior


app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    
Builder.load_string("""
#:import hex kivy.utils.get_color_from_hex

<Tooltip>:
    size_hint: None, None
    size: self.texture_size[0]+5, self.texture_size[1]+5
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 0.7
        Rectangle:
            size: self.size
            pos: self.pos

<HoverButton>:
    size_hint: [None, None]
    background_normal: self.inactive_img if not self.hovered else self.active_img
    background_down: self.active_img
    size: 15, 14
    pos_hint: {'center_x': .5, "center_y":.5}


<SelectedItem>:
    orientation: 'horizontal'
    size_hint: [None, None]
    canvas:
        Color:
            rgba: hex('#303030')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [2,]
        
        
<SelectedItemsView>:
    spacing: 6
    orientation: 'vertical'
    size_hint: [None,1]
    Label:
        id: view_label
        size_hint: [1, None]
        height: root.label_height
        text: root.label_text
    ScrollView:
        bar_width: '9dp'
        StackLayout:
            size_hint: [1,None]
            id: stack
            height: root.height - root.label_height - root.spacing
            orientation: 'lr-tb'
            spacing: 5
            padding: 5
            canvas:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5,]
    
""")


class ToolTip(Label):
    pass

class HoverButton(Button, HoverBehavior):                        
    active_img = os.path.abspath(app_path + '/img/close_active.png')    
    inactive_img = os.path.abspath(app_path + '/img/close_inactive.png')

class SelectedItemLabel(Label, HoverBehavior):
    
    def __init__(self, text, tooltip_text, **kwargs):
        self.text = text
        self.bind(on_touch_down = self.on_click)
        self.tooltip = ToolTip(text = tooltip_text)
        self.disabled_color = [1,1,1,1]
        capital_letters_number = len(re.findall('([A-Z])', text))
        numbers = len(re.findall('([0-9])', text))
        self.item_name_len = (capital_letters_number*11)+1 + (numbers*11)+1 + ((len(text)-numbers-capital_letters_number)*7)+1
        super(SelectedItemLabel, self).__init__(**kwargs)
    
    def on_enter(self, pos):
        self.tooltip.pos = (pos[0]+20, pos[1] - 2 - self.tooltip.size[1])
        Window.add_widget(self.tooltip)
        
    def on_leave(self, pos):
        Window.remove_widget(self.tooltip)
        
    def on_click(self, instance, touch):
        if touch.button == "right":
            pass
   
class SelectedItem(BoxLayout):
    def __init__(self, text, tooltip_text, **kwargs):
        super(SelectedItem, self).__init__(**kwargs)
        self.label = SelectedItemLabel(text, tooltip_text)
        self.add_widget(self.label)
        self.button = HoverButton()
        self.button.bind(on_release = self.on_delete)
        self.add_widget(self.button)
        self.size = (self.label.item_name_len+self.button.size[0]+2, self.button.size[1]+5)
    
    def on_delete(self, button):
        self.parent.parent.parent.dispatch('on_delete_item', self)
        Window.remove_widget(self.label.tooltip)
    
class SelectedItemsView(BoxLayout):
    
    label_text = StringProperty()
    label_height = NumericProperty()
    
    def __init__(self, label_text, halign=None, text_color=None, bold_text=False, **kwargs):
        self.register_event_type('on_add_item')
        self.register_event_type('on_delete_item')
        super(SelectedItemsView, self).__init__(**kwargs)
        self.label_height = '30dp'
        self.label_text = label_text
        self.stack = self.ids.stack
        self.items = list()
        self.widgets = list()
        self.selectedItem_height = self.size[1] - self.label_height - self.spacing
        self.stack.bind(minimum_size=lambda w, size: w.setter('height')(w, size[1] if size[1] > self.selectedItem_height else self.selectedItem_height))
        #self.stack.bind(on_touch_up=self.on_stack_view_touch_up)
        if halign is not None:
            self.ids.view_label.halign = halign
        if text_color is not None:
            self.ids.view_label.color = text_color
        if bold_text:
            self.ids.view_label.bold = bold_text
        
    def on_add_item(self, item, item_text, tooltip_text):
        if list(filter(lambda widget: widget.label.text == item_text, self.widgets)) == []:
            self.items.append(item)
            new_widget = SelectedItem(text = item_text, tooltip_text=tooltip_text)
            if (new_widget.label.item_name_len + new_widget.button.size[0]+2) > self.width:
                new_widget.size = (self.width - 2*self.spacing, 2*new_widget.size[1])
                new_widget.label.text = new_widget.label.text[:int((len(new_widget.label.text)+1)/2)] + '\n' + new_widget.label.text[int((len(new_widget.label.text)+1)/2):]
            self.widgets.append(new_widget)
            self.stack.add_widget(new_widget)
            
        elif not item in self.items:
            pass
        
    def on_delete_item(self, widget):
        if '\n' in widget.label.text:
            widget.label.text = widget.label.text.replace("\n", "")
        item_filtered = list(filter(lambda x: widget.label.text in x.label.text, self.widgets))
        if len(item_filtered) != 1:
            return
        item = self.items[self.widgets.index(item_filtered[-1])]
        
        self.items.remove(item)
        self.widgets.remove(widget)
        self.stack.remove_widget(widget)
        
    def on_size(self, a, b):
        self.selectedItem_height = self.size[1] - self.label_height - self.spacing

    def remove_items(self):
        self.stack.clear_widgets()
        self.items.clear()
        self.widgets.clear()

    def on_stack_view_touch_up(self, widget, touch):
        print("Stack touched up")

    
class TreeViewSelectableItem(TreeViewLabel, HoverBehavior):
    
    def __init__(self, item = None, text = None, **kwargs):
        self.item = None
        self.register_event_type('on_double_tap')
        self.register_event_type('on_press')
        self.register_event_type('on_grab')
        self.register_event_type('on_finish_grabing')
        self.register_event_type('on_grab_moving')
        self.is_grabing = False
        super().__init__(**kwargs)
        if item is not None and text is not None:
            self.item = item
            self.text = text

    def on_press(self, item):
        pass

    def on_grab(self, touch):
        pass

    def on_finish_grabing(self, touch):
        pass

    def on_grab_moving(self, touch):
        pass

    def on_touch_move(self, touch):
        if self.is_grabing is False and self.is_selected:
            self.is_grabing = True
            self.dispatch('on_grab', touch)
        elif self.is_grabing is True and self.is_selected:
            self.dispatch('on_grab_moving', touch)

    def on_touch_up(self, touch):
        if self.is_selected and not touch.is_mouse_scrolling:
            if touch.is_double_tap:
                self.is_selected = False
                self.dispatch('on_double_tap', self, self.item)
            elif not touch.is_triple_tap and not self.is_grabing:
                self.dispatch('on_press', self.item)
            elif self.is_grabing is True:
                self.is_grabing = False
                self.dispatch('on_finish_grabing', touch)
            
            if not touch.is_mouse_scrolling:
                pass
            
    def on_double_tap(self, widget, item):
        pass

    