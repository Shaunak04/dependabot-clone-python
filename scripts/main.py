import pandas as pd
import urllib.request
import os
import subprocess
from pynpm import NPMPackage
import requests
import json
import os.path

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
                try:
                    if("-update" in lst):
                        file_name = lst[2]
                        df = pd.read_csv(path + file_name)
                        # CLONE REPO, USE NPM UPDATE, CREATE A PR
                        continue
                except:
                    print("couldn't open input.csv")
                    os.exit(0)
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
                            vers = [None for _ in range(rows)]

                        if(file_name[len(file_name)-3:]!="csv"):
                            print("invalid command\n")
                            continue
                        
                        for pkg in packages:
                            raw_path = "https://raw.githubusercontent.com/"
                            at_index = pkg.find('@')
                            dependency = pkg[0:at_index]
                            curr_version = pkg[at_index+1:]
                            print("Checking package: "+dependency + " for version: "+curr_version)
                            npm_call = 'npm show ' + dependency + ' version' 
                            latest_ver = subprocess.check_output(npm_call, shell=True)
                            output = latest_ver.decode('utf-8')

                            ind = 0
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
                                            vers[ind] = current_version
                                            if(not bad_Ver):
                                                bad_pkg[ind].append(dependency)
                                            satisfy[ind] = ((satisfy[ind]) and (current_version >= curr_version))

                                    except:
                                        print("Couldn't open package.json")
                                        satisfy[ind]  = False

                                        
                                except:
                                    status[ind] = False
                                    satisfy[ind] = False

                                ind +=1
                        try:
                            df['could_connect'] = status
                            df['version'] = vers
                            df['version_satisfied'] = satisfy
                            df['outdated packages'] = bad_pkg
                            df.to_csv("../outputs/output.csv", index = False)
                            print("""-------------------------------------\nOutput stored in ./outputs/output.csv\n--------------------------------------\n""")

                        except:
                            print("Could not process input")


                                
                            

if __name__ == "__main__":
    inp = Wrapper()
    inp.loop()