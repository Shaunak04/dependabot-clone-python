import pandas as pd
import urllib.request
import os
import subprocess
from pynpm import NPMPackage

class Wrapper:

    def loop(self):
        print("-----Welcome to de-py-ndency bot:-----\n")
        print("You can start by entering 'help'")
        while(1):
            command = input("Enter your command:")
            if(command=="help"):
                print("""List of valid commands:
                1. depy -i filname.csv package@version
                2. depy -i update filename.csv package@version
                3. exit
                4. documentation""")
                pass

            elif(command=="exit"):
                print("Thanks for using de-py-ndency bot")
                os._exit(0)
            else:
                lst = command.split(" ")
                print(lst)
                if("-update" in lst):
                    # CLONE REPO, USE NPM UPDATE, CREATE A PR
                    continue
                else:
                    if((len(lst)<4) or (lst[0]!='depy') or (lst[1]!='-i')):    
                        print("invalid command")
                        continue
                    
                    else:
                        file_name = lst[2]
                        if(file_name[len(file_name)-3:]!="csv"):
                            print("invalid command")
                            continue
                        
                        packages = lst[3:]
                        for pkg in packages:
                            at_index = pkg.find('@')
                            dependency = pkg[0:at_index]
                            curr_version = pkg[at_index+1:]
                            print(dependency, curr_version)
                            # npm_call = 'npm show ' + dependency + ' version' 
                            # latest_ver = subprocess.check_output(npm_call, shell=True)
                            # output = latest_ver.decode('utf-8')
                            print()
                    


class Parser:
    old_version_count = 0

class URL_connection:
    
    def connect(self, df):
        rows, cols = df.shape
        for i in range(rows):
            # for j in range(cols):
            
            repo_name = df.iloc[i, 0]
            repo_url = df.iloc[i, 1]
            
            try:
                fetch_url = urllib.request.urlopen(repo_url)
                con_status = fetch_url.getcode()
                print("Connection succesful for project: " + repo_name)

            except:
                print("Invalid URL for project: "+ repo_name)



class Input_parsing:

    default = False

    def main(*argv):
        path = '../inputs/inputt.csv'
        df = pd.read_csv(path)
        return df
        

if __name__ == "__main__":
    inp = Input_parsing()
    wp = Wrapper()
    wp.loop()
    # inp.main()