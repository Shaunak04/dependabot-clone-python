import pandas as pd
import urllib.request
import os
import subprocess
from pynpm import NPMPackage
import requests
import json


class Wrapper:

    # data members
    df = None
    path = None
    logged_in = False
    # constructor
    def __init__(self):
        global df
        global path
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
                2. depy -i -update filename.csv package@version
                3. exit
                4. documentation""")
                pass

            elif(command=="exit"):
                print("Thanks for using de-py-ndency bot\n")
                os._exit(0)

            else:
                lst = command.split(" ")
                if("-update" in lst):
                    file_name = lst[2]
                    df = pd.read_csv(path + file_name)
                    # CLONE REPO, USE NPM UPDATE, CREATE A PR
                    continue

                else:
                    if((len(lst)<4) or (lst[0]!='depy') or (lst[1]!='-i')):    
                        print("invalid command\n")
                        continue
                    
                    else:
                        status = []
                        satisfy = []
                        file_name = lst[2]
                        df = pd.read_csv(path + file_name)
                        if(file_name[len(file_name)-3:]!="csv"):
                            print("invalid command\n")
                            continue
                        
                        rows, cols = df.shape
                        packages = lst[3:]
                        for pkg in packages:
                            raw_path = "https://raw.githubusercontent.com/"
                            at_index = pkg.find('@')
                            dependency = pkg[0:at_index]
                            curr_version = pkg[at_index+1:]
                            print(dependency, curr_version)
                            npm_call = 'npm show ' + dependency + ' version' 
                            latest_ver = subprocess.check_output(npm_call, shell=True)
                            output = latest_ver.decode('utf-8')
                            
                            for i in range(rows):                            
                                repo_name = df.iloc[i, 0]
                                repo_url = raw_path + df.iloc[i, 1][19:] +'/main/package.json'

                                try:
                                    fetch_url = urllib.request.urlopen(repo_url)
                                    con_status = fetch_url.getcode()
                                    r = requests.get(repo_url, allow_redirects=True)
                                    with open('package.json', "wb") as file:
                                        # get request
                                        response = requests.get(repo_url)
                                        # write to file
                                        file.write(response.content)
                                        status.append("successfull connection")

                                    try:
                                        with open('package.json') as json_file:
                                            data = json.load(json_file)
                                            current_version = data['dependencies'][dependency]
                                            if(len(current_version)==0):
                                                raise Exception("invalid version")
                                            
                                            if(current_version[0]=='^' or current_version[0]=='~'):
                                                current_version = current_version[1:]

                                            satisfy.append(current_version >= curr_version)

                                    except:
                                        print("Couldn't open package.json")
                                        satisfy.append(False)

                                        
                                except:
                                    status.append("invalid url")
                                    satisfy.append(False)
                        print(status)
                        print(satisfy)
                        df['tracking_status'] = status
                        df['satisfy'] = satisfy
                        df.to_csv("../outputs/output.csv", index = False) 


                                
                            

if __name__ == "__main__":
    inp = Wrapper()
    inp.loop()