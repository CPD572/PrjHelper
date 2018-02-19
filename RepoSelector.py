from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
import time

Builder.load_string("""
<RepoSelectorScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            orientation: 'horizontal'
            #size_hint_x: .25
            height: 30
            
            TabbedPanel:
                do_default_tab: False
                tab_height: 30
                
                TabbedPanelItem:
                    text: "ASW"
                    Label:
                        text: "ASW panel content"
                        
                TabbedPanelItem:
                    text: "BSW"
                    BoxLayout:
                        orientation: 'vertical'
                        TabbedPanel:
                            do_default_tab: False
                            tab_height: 30
                            
                            TabbedPanelItem:
                                text: "HMI"
                                Label:
                                    text: "ASW panel content"
                                    
                            TabbedPanelItem:
                                text: "COM"
                                Label:
                                    text: "ASW panel content"
                                    
                            TabbedPanelItem:
                                text: "IO"
                                Label:
                                    text: "ASW panel content"
                        
                TabbedPanelItem:
                    text: "ESW"
                    Label:
                        text: "CDD panel content"
                        
        BoxLayout:
            size_hint_y: None
            orientation: 'vertical'
            height: "30dp"
            Button:
                pos_hint:{'center': .5, "bottom":1}
                text: "Logout"
                on_release: 
                    root.manager.transition.duration = 0
                    root.manager.current = 'Login'
                
""")


class RepoSelectorScreen(Screen):
    
    def __init__(self, **kwargs):
        super(RepoSelectorScreen, self).__init__(**kwargs)
    
    def on_enter(self, *args):
        Screen.on_enter(self, *args)
        Window.size = (600,200)
        time.sleep(1)
        Window.show()
        