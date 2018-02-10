from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from BitbucketAPI import Bitbucket
import Popups

class LoginScreen(Screen):

    username = ObjectProperty()
    password = ObjectProperty()
    session = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.bitbucketSession = Bitbucket()
        if self.bitbucketSession.user.username == u'':
            self.saveUserData = False
        else:
            self.username.text = self.bitbucketSession.user.username
            self.password.text = self.bitbucketSession.user.password
            self.saveUserData = True
            
    def Submit(self):
        tmp = self.bitbucketSession.Login(self.username.text, self.password.text)
        if tmp == 1:
            the_popup = Popups.WarningPopup(self.bitbucketSession.jsonResponse['displayName'])
            the_popup.open()
            
            #submit functionality
            #    check if Save login checkbox is checked
            #        create XML with user data 'file.mlbu' 
            #    change screen to RepoSelector
            if self.saveUserData == True:
                self.bitbucketSession.user.save_user()
            
        elif tmp == 0:
            the_popup = Popups.ErrorPopup(self.bitbucketSession.jsonResponse['errors'][0]['message'])
            the_popup.open()
            self.reset_form()
        elif  tmp == -1:
            the_popup = Popups.ErrorPopup('There is no server connection. Timeout was reached.')
            the_popup.open()
            
            
    def on_save_data_checkbox(self, checkbox, value):
        if value:
            self.saveUserData = True
        else:
            self.saveUserData = False
            
    def reset_form(self):
        self.username.text = ''
        self.password.text = ''
        self.bitbucketSession.user.delete_user()
        
        
        