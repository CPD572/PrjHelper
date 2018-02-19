from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from BitbucketAPI import Bitbucket
import Login
from RepoSelector import RepoSelectorScreen

class ProjectConstructorApp(App):

    def build(self):
        Config.set('graphics', 'width', '400')
        Config.set('graphics', 'height', '160')
        Config.set('graphics', 'resizable', 'False')
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.write()
        self.session = Bitbucket()
        manager = ScreenManager()
        manager.add_widget(Login.LoginScreen(name = 'Login', session = self.session))
        manager.add_widget(RepoSelectorScreen(name = 'RepoSelector'))
        return manager


if __name__ == '__main__':
    ProjectConstructorApp().run()