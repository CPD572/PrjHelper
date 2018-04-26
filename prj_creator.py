#!/usr/bin/kivy
# -*- coding: utf-8 -*-

import os, sys
from Popups import ContentPopup
from tkinter import filedialog, Tk
from tkinter.messagebox import showerror, showinfo
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

root = Tk()
root.withdraw()

Builder.load_string("""
<FormButton@Button>:
    font_size: 14

<ProjectCreator>:
    orientation: "vertical"
    padding: 10
    spacing: 10
    project_name_input: prj_name_input
    workspace_path_input: prj_path_input
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
        FormButton:
            text: 'Browse for\\nworkspace'
            on_press: root.Browse()
            size_hint: None, 1
    
    BoxLayout:
        pos_hint: {"center_x": .5, "bottom":1}
        size_hint: None, None
        width: 200
        height: "30dp"
        spacing: 10
        FormButton:
            id: submit_button
            text: "Submit"
            on_release: root.Submit()
        FormButton:
            id: cancel_button
            text: "Cancel"
            on_release: root.Cancel()
        
""")


class ProjectCreator(BoxLayout):
    project_name = StringProperty()
    workspace_path = StringProperty()
    project_name_input = ObjectProperty()
    workspace_path_input = ObjectProperty()
    
    def __init__(self):
        super(ProjectCreator, self).__init__()
        self.register_event_type('on_submit')
        self.register_event_type('on_cancel')
        self.default_workspace_path = ''
        sys_home = os.getenv("HOMEPATH") if "win32" in sys.platform else os.getenv("HOME")
        self.project_path = ''
        temp_path = os.path.abspath(sys_home+"/workspace")
        if os.path.exists(temp_path):
            self.default_workspace_path = temp_path
            self.workspace_path_input.text = self.default_workspace_path
            
    def on_submit(self):
        pass
    
    def on_cancel(self):
        pass
        
    def Submit(self):
        if self.workspace_path_input.text == "" or self.workspace_path_input.text == None:
            showerror(title = "Workspace problem", message = "Please select workspace")
            return
        if self.project_name_input.text == "" or self.project_name_input.text == None:
            showerror(title = "Project name problem", message = "Please enter the project name")
            return
        
        self.project_name = self.project_name_input.text
        self.workspace_path = self.workspace_path_input.text
        
        if os.path.exists(os.path.abspath(self.workspace_path)):
            prj_path = os.path.join(self.workspace_path, self.project_name)
            if os.path.exists(prj_path):
                showerror(title = "Project name problem", message = "Project "+self.project_name+" already exist")
                return
            else:
                os.mkdir(prj_path)
                self.is_created = True
                self.project_path = prj_path
                self.dispatch('on_submit')
                return
        else:
            showerror(title = "Project name problem", message = "There is no such workspace")
            return                                                                            
            
    
    def Cancel(self):
        self.workspace_path_input.text = self.default_workspace_path
        self.project_name_input.text = ''
        self.dispatch('on_cancel')
        
    def Browse(self):
        prev_dir = self.workspace_path
        path = filedialog.askdirectory()
        print(path)
        if path == '':
            path = prev_dir
        self.workspace_path = os.path.abspath(path)
        self.workspace_path_input.text = self.workspace_path
