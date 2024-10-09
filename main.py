import requests
import platform
import os
import json
import zipfile
import io
import atexit

package = requests
name = "bg3-updater"
ver=0.3
user_key = "k9zjCGLfWZgscJrJrc0O8eUnrl8tMyXgVCXnwdQ2fkMosr0=--xYdCouD24lqgueoK--RVWNhE0H2DN/7uK+j1bmkA=="
agent_string = "{}/{} -- {} -- {}/{}".format(name, ver, platform.platform(), package.__title__, package.__version__)

params = {
        "apikey":user_key,
        #"User-Agent":agent_string,
    }
url = "https://api.nexusmods.com/"
game_name = "baldursgate3"
#mods_dir = os.path.expandvars(r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods")
mods_dir = "./"

mod_list = {}

"""
json format
{
    /mod_id/{
        name
        update timestamp
        ???
    }
 
}


"""

def read_mods():
    global mod_list
    with open("./download.json", 'r') as modfile:
        mod_list = json.load(modfile)
        return True

    return False

def write_mods():
    if mod_list:
        with open("./download.json", 'w') as modfile:
            json.dump(mod_list, modfile)
            return True

    return False

def clean_dir():
    counter = 0
    dir_list = os.listdir(mods_dir)
    for filename in dir_list:
        if "info" in filename and filename.endswith(".json"):
            os.remove(mods_dir+"/"+filename)
            counter+=1

    return counter


def get_mod_details(id):
    response = package.get(url=(url + "v1/games/{}/mods/{}.json").format(game_name,id), headers=params)
    resp_text = json.loads(response.text)
    return resp_text

def get_mod_files(id):
    response = package.get(url=(url + "v1/games/{}/mods/{}/files.json?category=main").format(game_name, id), headers=params)
    resp_file = json.loads(response.text)
    main_file = resp_file["files"][0]
    if len(resp_file["files"]) > 1:
        for file in resp_file["files"]:
            #loop through all files to find primary if the first one is not primary
            if file["is_primary"]:
                main_file = file
                break
    return main_file

def update_mods():
    for mod_id in mod_list.keys():
        response = get_mod_details(id)
        #update all mods based on if there is a newer version
        if response["updated_timestamp"] > mod_list[mod_id]["timestamp"]:
            updated = response["updated_timestamp"]
            dst_file = "./"+mod_id+".zip"

            file_to_download = get_mod_files(mod_id)
            """
            need to add in request here to go from the file_to_download to the download link
            files/[id]/download_link.json
            """
            main_url=''
            response = requests.get(main_url, headers=params)
            if response.ok:
                #convert response to zip and extract zip to the mods folder
                zipped = zipfile.ZipFile(io.BytesIO(response.content))
                zipped.extractall(mods_dir)
                mod_list[mod_id]["timestamp"] = updated



id=87
#temp = package.get(url=(url + "v1/games/{}/mods/{}/files/{}/download_link.json").format(game_name, id, get_mod_files(87)["file_id"]), headers=params)

#temp = package.get(url="https://api.nexusmods.com/v1/games/baldursgate3/mods/87/files/36127/download_link.json?key=k9zjCGLfWZgscJrJrc0O8eUnrl8tMyXgVCXnwdQ2fkMosr0=--xYdCouD24lqgueoK--RVWNhE0H2DN/7uK+j1bmkA==&expires=1725696093", headers=params)

i = 0
#get_mod_files(213)

if __name__ == "__main__":

    pass
    #atexit.register(write_mods)
    #read_mods()
    #update_mods()