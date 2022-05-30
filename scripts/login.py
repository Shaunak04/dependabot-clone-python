import requests
import json
from git import Repo

####
# inputs
####
username = 'Shaunak04'

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
    
# make more requests using "gh_session" to create repos, list issues, etc.