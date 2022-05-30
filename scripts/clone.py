import time
import git
from git import RemoteProgress
import requests
import json
from git import Repo

class Login:
    def login(self):
        username = 'Rohitashwadutta'
        # from https://github.com/user/settings/tokens

        token = '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'
        repos_url = 'https://api.github.com/user/repos'

        # create a re-usable session object with the user creds in-built
        gh_session = requests.Session()
        gh_session.auth = (username, token)

        # get the list of repos belonging to me
        repos = json.loads(gh_session.get(repos_url).text)

        # print the repo names
        for repo in repos:
            print(repo['name'])

# class CloneProgress(RemoteProgress):
#     def update(self, op_code, cur_count, max_count=None, message=''):
#         if message:
#             print(message)

# print('Cloning into %s' % git_root)
# git.Repo.clone_from('https://github.com/your-repo', '/your/repo/dir', 
#         branch='master', progress=CloneProgress())

if __name__ == "__main__":    
    lg = Login()
    lg.login()