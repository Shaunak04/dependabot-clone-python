import pandas as pd
import urllib.request
import os
import subprocess
import requests
import json
import os.path
import git
from git import Repo
import random
import shutil
import stat
from github import Github

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
                """)
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
                        token = input("Enter your Personal Access Token (check https://github.com/settings/tokens): ")
                        repos_url = 'https://api.github.com/user/repos'

                        try:
                            # create a re-usable session object with the user creds in-built
                            gh_session = requests.Session()
                            gh_session.auth = (username, token)
                            print("Login successfull, "+username)

                        except:
                            print("Could not login, check your credentials and internet connection")



                        for pkg in packages:
                            raw_path = "https://raw.githubusercontent.com/"
                            at_index = pkg.find('@')
                            dependency = pkg[0:at_index]
                            curr_version = pkg[at_index+1:]

                            print("Checking package: " + dependency + " for version: " + curr_version)
                            
                            ind = 0
                            for i in range(rows):                
                                cloned_link = df.iloc[i, 1][0:19] + username + df.iloc[i, 1][26:]
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
                                        print("opened successully")
                                    try:
                                        with open('package.json') as json_file:
                                            data = json.load(json_file)
                                            current_version = data['dependencies'][dependency]
                                            if(len(current_version)==0):
                                                raise Exception("invalid version")
                                            
                                            if(current_version[0]=='^' or current_version[0]=='~'):
                                                current_version = current_version[1:]
                                            bad_Ver = current_version >= curr_version
                                            vers[ind].append(current_version)
                                            print(cloned_link, bad_Ver)
                                            if(not bad_Ver):

                                                gg = Github(username, token)
                                                github_user = gg.get_user()
                                                repo = gg.get_repo(df.iloc[i, 1][19:])
                                                myfork = github_user.create_fork(repo)
                                                print(myfork)
                                                try:
                                                    Repo.clone_from(cloned_link, "../repos/")
                                                    print("Repo cloned successfully in ../repos/")

                                                except:
                                                    print("Couldn't clone repo, check if you have permissions/access")

                                                bad_pkg[ind].append(dependency)
                                                # UPDATE THE VERSION USING SUBPROCESS
                                                
                                                

                                                npm_call = 'npm install ' + dependency + '@'+curr_version
                                                print(npm_call) 
                                                subprocess.check_call(npm_call, shell=True, cwd = "../repos/")
                                                subprocess.check_call("git add .", shell=True, cwd = "../repos/")
                                                print("added")
                                                subprocess.check_call("git commit -m 'depyndency-bot'", shell=True, cwd = "../repos/")
                                                print("committed")
                                                subprocess.check_call("git push origin main", shell=True, cwd = "../repos/")
                                                print("pushed")
                                                update_pkg[ind].append(dependency)
                                                s = requests.Session()
                                                ttl = "chores: updated "+dependency+" from version: "+str(current_version)+" to : "+ str(curr_version)
                                                data1 = json.dumps({"title" : ttl , "body":"Please accept changes by de-py-ndency bot at", "head" : "Rohitashwadutta:main", "base" : "main"})
                                                auth1 = {"Authorization" : "token " + token}
                                                print("started request")
                                                pr_url = "https://api.github.com/repos/" + df.iloc[i, 1][19:]+"/pulls"
                                                print(pr_url)
                                                r = s.post(pr_url, headers = auth1, data = data1)
                                                print(r.text)
                                                temp = r.json()["html_url"]
                                                
                                                pr_links[ind] = temp
                                                print("pr raised")

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
                         
                        if os.path.isfile('package.json'):
                            os.remove('package.json')

                        continue

                    else:
                        if((len(lst)<4) or (lst[0]!='depy') or (lst[1]!='-i')):
                            print("invalid command\n")
                            continue
                        
                        else:
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
                            if os.path.isfile('package.json'):
                                os.remove('package.json')
                except:
                    print("Could not process input")                         

if __name__ == "__main__":
    inp = Wrapper()
    inp.loop()