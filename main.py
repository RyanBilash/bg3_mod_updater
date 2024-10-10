import sys
import requests
import platform
import os
import json
import zipfile
import io
import atexit
import configparser
import config_gen

package = requests
config_path = './config.ini'
user_key = ''
mods_file = './download.json'
#mods_dir = os.path.expandvars(r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods")
mods_dir = './'


def get_config():
    global user_key, mods_file, mods_dir
    if os.path.isfile(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        user_key = config['DEFAULT']['apikey']
        mods_file = config['DEFAULT']['mods_file']
        #mods_dir = config['DEFAULT']['mods_dir'] #TODO: uncomment this when in beta testing
    else:
        # just want to generate the config and probably prompt the user that they need to put in the api key
        # as the config doesn't have one by default, so there's no need to continue running
        config_gen.generate()
        sys.exit()


params = {
    "apikey": user_key,
}
url = "https://api.nexusmods.com/"
game_name = "baldursgate3"

mod_list = {}


def read_mods():
    global mod_list
    with open(mods_file, 'r') as modfile:
        mod_list = json.load(modfile)
        return True

    return False


def write_mods():
    if mod_list:
        with open(mods_file, 'w') as modfile:
            json.dump(mod_list, modfile)
            return True

    return False


def clean_dir():
    counter = 0
    dir_list = os.listdir(mods_dir)
    #delete all the 'info' files extracted to the out directory
    for filename in dir_list:
        if "info" in filename and filename.endswith(".json"):
            os.remove(mods_dir + "/" + filename)
            counter += 1

    return counter


def get_mod_details(id):
    response = package.get(url=(url + "v1/games/{}/mods/{}.json").format(game_name, id), headers=params)
    resp_text = json.loads(response.text)
    return resp_text


def get_mod_files(id):
    response = package.get(url=(url + "v1/games/{}/mods/{}/files.json?category=main").format(game_name, id),
                           headers=params)
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
        if "timestamp" in mod_list[mod_id] or response["updated_timestamp"] > mod_list[mod_id]["timestamp"]:
            updated = response["updated_timestamp"]
            dst_file = "./" + mod_id + ".zip"

            file_to_download = get_mod_files(mod_id)
            """
            need to add in request here to go from the file_to_download to the download link
            files/[id]/download_link.json
            """
            main_url = ''
            response = requests.get(main_url, headers=params)
            if response.ok:
                #convert response to zip and extract zip to the mods folder
                zipped = zipfile.ZipFile(io.BytesIO(response.content))
                zipped.extractall(mods_dir)
                mod_list[mod_id]["timestamp"] = updated


id = 87
#temp = package.get(url=(url + "v1/games/{}/mods/{}/files/{}/download_link.json").format(game_name, id, get_mod_files(87)["file_id"]), headers=params)

#temp = package.get(url="https://api.nexusmods.com/v1/games/baldursgate3/mods/87/files/36127/download_link.json?key=k9zjCGLfWZgscJrJrc0O8eUnrl8tMyXgVCXnwdQ2fkMosr0=--xYdCouD24lqgueoK--RVWNhE0H2DN/7uK+j1bmkA==&expires=1725696093", headers=params)

i = 0
#get_mod_files(213)

if __name__ == "__main__":
    get_config()
    pass
    atexit.register(write_mods)
    read_mods()
    update_mods()
