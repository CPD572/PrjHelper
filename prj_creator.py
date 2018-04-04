#!/usr/bin/kivy
# -*- coding: utf-8 -*-

import os, sys
from Popups import ContentPopup
from tkinter import filedialog, Tk
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

root = Tk()
root.withdraw()

Builder.load_string("""
<CustomButton@Button>:
    font_size: 14

<ProjectCreator>:
    orientation: "vertical"
    padding: 10
    spacing: 10
    project_name_input: prj_name_input
    project_path_input: prj_path_input
    size_hint: 1, 1
    
    BoxLayout:
        spacing: 5
        Label:
            halign: 'right'
            text: 'Project Name:'
            size_hint: None, 1
        TextInput:
            id: prj_name_input
            multiline: False
            write_tab: False
            selection_color: [0.1843, 0.6549, 0.8313, .5]
            focus: True
            size_hint: 1, 1
    BoxLayout:
        spacing: 5
        TextInput:
            id: prj_path_input
            multiline: False
            write_tab: False
            size_hint: 1, 1
        CustomButton:
            text: 'Browse for\\nworkspace'
            on_press: root.Browse()
            size_hint: None, 1
    
    BoxLayout:
        pos_hint: {"center_x": .5, "bottom":1}
        size_hint: None, None
        width: 200
        height: "30dp"
        spacing: 10
        CustomButton:
            id: submit_button
            text: "Submit"
            on_release: root.dispatch('on_submit')
        CustomButton:
            id: cancel_button
            text: "Cancel"
            on_release: root.dispatch('on_cancel')
        
""")


class ProjectCreator(BoxLayout):
    project_name = StringProperty()
    project_path = StringProperty()
    project_name_input = ObjectProperty()
    project_path_input = ObjectProperty()
    
    def __init__(self):
        super(ProjectCreator, self).__init__()
        self.register_event_type('on_submit')
        self.register_event_type('on_cancel')
        
    def on_submit(self):
        print("Submit")
    
    def on_cancel(self):
        print("Cancel")
        
    def Browse(self):
        prev_dir = self.project_path
        path = filedialog.askdirectory()
        print(path)
        if path == '':
            path = prev_dir
        self.project_path = os.path.abspath(path)
        self.project_path_input.text = self.project_path
