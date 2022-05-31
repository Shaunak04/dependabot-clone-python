import pandas as pd
import urllib.request
import os
import subprocess
from pynpm import NPMPackage
import requests
import json
import os.path
import git
from git import Repo


# def create_pull_request(project_name, repo_name, title, description, head_branch, base_branch, git_token, gh_session):
#     print("call me hello")
#     """Creates the pull request for the head_branch against the base_branch"""
#     git_pulls_api = "https://github.com/api/v3/repos/{0}/{1}/pulls".format(
#         project_name,
#         repo_name)
#     headers = {
#         "Authorization": "token {0}".format(git_token),
#         "Content-Type": "application/json"}

#     payload = {
#         "title": title,
#         "body": description,
#         "head": head_branch,
#         "base": base_branch,
#     }
#     print(gh_session)
#     r = gh_session.post(
#         git_pulls_api,
#         headers = headers,
#         data = json.dumps(payload))

#     if not r.ok:
#         print("Request Failed: {0}".format(r.text))
    
#     print("asdasdas", r)


class Wrapper:

    # data members
    df = None
    path = None
    logged_in = False
    gh_session = None
    # constructor
    def __init__(self):
        global df
        global path
        global gh_session
        df = None
        path = '../inputs/'
        
    # CLI loop
    def loop(self):
        print("-----Welcome to de-py-ndency bot:-----\n")
        print("You can start by entering 'help'")
        while(True):
            command = input("Enter your command: ")
            if(command=="help"):
                print("""List of valid commands:
                1. depy -i filename.csv package@version
                2. depy -update -i filename.csv package@version
                3. exit
                4. documentation""")
                pass

            elif(command=="exit"):
                print("Thanks for using de-py-ndency bot\n")
                os._exit(0)

            else:
                lst = command.split(" ")
                try:
                    if("-update" in lst and lst[1]=="-update"):
                        file_name = path + lst[3]
                        df, rows, cols, packages, satisfy, status, bad_pkg, vers = None, None,None, None,None, None, None, None
                        if(not os.path.exists(file_name)):    
                            print("Invalid input file. Make sure the input.csv is present in ./inputs folder\n")
                            continue

                        else:
                            df = pd.read_csv(file_name)
                            rows, cols = df.shape
                            packages = lst[4:]
                            satisfy = [True for _ in range(rows)]
                            update_pkg = [[] for _ in range(rows)]
                            bad_pkg = [[] for _ in range(rows)]
                            status = [True for _ in range(rows)]
                            vers = [[] for _ in range(rows)]
                            pr_links = [None for _ in range(rows)]

                        if(file_name[len(file_name)-3:]!="csv"):
                            print("invalid command\n")
                            continue
                        
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

                        try:
                            Repo.clone_from("https://github.com/dyte-in/react-sample-app/", "../repos/")
                            print("Repo cloned successfully in ../repos/")

                        except:
                            print("Couldn't clone repo, check if you have permissions/access")

                        for pkg in packages:
                            raw_path = "https://raw.githubusercontent.com/"
                            at_index = pkg.find('@')
                            dependency = pkg[0:at_index]
                            curr_version = pkg[at_index+1:]
                            print("Checking package: " + dependency + " for version: " + curr_version)
                            
                            ind = 0
                            for i in range(rows):                            
                                repo_name = df.iloc[i, 0]
                                repo_url = raw_path + df.iloc[i, 1][19:] +'/main/package.json'
                                try:
                                    fetch_url = urllib.request.urlopen(repo_url)
                                    con_status = fetch_url.getcode()
                                    print(repo_url)
                                    r = requests.get(repo_url, allow_redirects=True)
                                    with open('package.json', "wb") as file:
                                        response = requests.get(repo_url)
                                        file.write(response.content)
                                        status[ind] = ((status[ind]) and True)
                                        print("opened successully")
                                    try:
                                        with open('package.json') as json_file:
                                            data = json.load(json_file)
                                            current_version = data['dependencies'][dependency]
                                            if(len(current_version)==0):
                                                raise Exception("invalid version")
                                            
                                            if(current_version[0]=='^' or current_version[0]=='~'):
                                                current_version = current_version[1:]

                                            bad_Ver = current_version>=curr_version
                                            vers[ind].append(current_version)
                                            print(bad_Ver)
                                            if(not bad_Ver):
                                                bad_pkg[ind].append(dependency)
                                                # UPDATE THE VERSION USING SUBPROCESS
                                                npm_call = 'npm install ' + dependency + '@'+curr_version 
                                                latest_ver = subprocess.check_output(npm_call, shell=True)
                                                output = latest_ver.decode('utf-8')
                                                update_pkg[ind].append(dependency)

                                                # CREATING PR
                                                # create_pull_request("octocat", "Hello-World", "test API call", "ignore pls", "master", "test", token, gh_session)

                                                print(output)

                                            satisfy[ind] = ((satisfy[ind]) and (current_version >= curr_version))

                                    except:
                                        bad_pkg[ind].append(dependency)
                                        satisfy[ind]  = False

                                        
                                except:
                                    status[ind] = False
                                    satisfy[ind] = False

                                ind +=1
                        try:
                            df['could_connect'] = status
                            df['version'] = vers
                            df['version_satisfied'] = satisfy
                            df['outdated/absent packages'] = bad_pkg
                            df['updated packages'] = update_pkg
                            df['PR link'] = pr_links
                            df.to_csv("../outputs/update.csv", index = False)
                            print("""-------------------------------------\nOutput stored in ./outputs/update.csv\n--------------------------------------\n""")

                        except:
                            print("Could not process input") 
                        continue

                    else:
                        if((len(lst)<4) or (lst[0]!='depy') or (lst[1]!='-i')):    
                            print("invalid command\n")
                            continue
                        
                        else:
                            print("ghusna")
                            file_name = path + lst[2]
                            df, rows, cols, packages, satisfy, status, bad_pkg, vers = None, None,None, None,None, None, None, None
                            if(not os.path.exists(file_name)):    
                                print("Invalid input file. Make sure the input.csv is present in ./inputs folder\n")
                                continue

                            else:
                                df = pd.read_csv(file_name)
                                rows, cols = df.shape
                                packages = lst[3:]
                                satisfy = [True for _ in range(rows)]
                                status = [True for _ in range(rows)]
                                bad_pkg = [[] for _ in range(rows)]
                                vers = [[] for _ in range(rows)]

                            if(file_name[len(file_name)-3:]!="csv"):
                                print("invalid command\n")
                                continue
                            
                            for pkg in packages:
                                raw_path = "https://raw.githubusercontent.com/"
                                at_index = pkg.find('@')
                                dependency = pkg[0:at_index]
                                curr_version = pkg[at_index+1:]
                                print("Checking package: "+dependency + " for version: "+curr_version)
                                ind = 0
                                for i in range(rows):                            
                                    repo_name = df.iloc[i, 0]
                                    repo_url = raw_path + df.iloc[i, 1][19:] +'/main/package.json'
                                    try:
                                        fetch_url = urllib.request.urlopen(repo_url)
                                        con_status = fetch_url.getcode()
                                        r = requests.get(repo_url, allow_redirects=True)
                                        with open('package.json', "wb") as file:
                                            response = requests.get(repo_url)
                                            file.write(response.content)
                                            status[ind] = ((status[ind]) and True)

                                        try:
                                            with open('package.json') as json_file:
                                                data = json.load(json_file)
                                                current_version = data['dependencies'][dependency]
                                                if(len(current_version)==0):
                                                    raise Exception("invalid version")
                                                
                                                if(current_version[0]=='^' or current_version[0]=='~'):
                                                    current_version = current_version[1:]
                                                bad_Ver = current_version>=curr_version
                                                vers[ind].append(current_version)
                                                if(not bad_Ver):
                                                    bad_pkg[ind].append(dependency)

                                                satisfy[ind] = ((satisfy[ind]) and (current_version >= curr_version))

                                        except:
                                            bad_pkg[ind].append(dependency)
                                            satisfy[ind]  = False

                                            
                                    except:
                                        status[ind] = False
                                        satisfy[ind] = False

                                    ind +=1
                            try:
                                df['could_connect'] = status
                                df['version'] = vers
                                df['version_satisfied'] = satisfy
                                df['outdated/absent packages'] = bad_pkg
                                df.to_csv("../outputs/output.csv", index = False)
                                print("""-------------------------------------\nOutput stored in ./outputs/output.csv\n--------------------------------------\n""")
                            except:
                                print("Could not track")
                except:
                    print("Could not process input")                         

if __name__ == "__main__":
    inp = Wrapper()
    inp.loop()