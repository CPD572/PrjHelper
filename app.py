from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
import Login
#import RepoSelector

class ProjectConstructorApp(App):

    def build(self):
        Config.set('graphics', 'width', '400')
        Config.set('graphics', 'height', '160')
        Config.set('graphics', 'resizable', 'False')
        Config.write()
        manager = ScreenManager()
        manager.add_widget(Login.LoginScreen(name = 'Login'))
        #manager.add_widget(RepoSelector.Selector(name = 'RepoSelector'))
        return manager


if __name__ == '__main__':
    ProjectConstructorApp().run()