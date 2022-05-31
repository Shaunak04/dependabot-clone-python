import time
import git
from git import repo
import requests
import json
from git import Repo

class Login:
    def login(self):
        # username = 'Rohitashwadutta'
        username = input("Enter your Github username: ")

        # from https://github.com/user/settings/tokens
        # token = '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'
        token = input("Enter your Personal Access Token (check https://github.com/settings/tokens): ")
        repos_url = 'https://api.github.com/user/repos'

        try:
            # create a re-usable session object with the user creds in-built
            gh_session = requests.Session()
            gh_session.auth = (username, token)
            print("Login successfull, "+username)

        except:
            print("Could not login, check your credentials and internet connection")

    
        Repo.clone_from("https://github.com/dyte-in/react-sample-app/", "../repos/")

if __name__ == "__main__":    
    lg = Login()
    lg.login()