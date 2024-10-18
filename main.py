import sys
import requests
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
# mods_dir = os.path.expandvars(r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods")
mods_dir = './'
params = {
    "apikey": user_key,
}


def get_config():
    """
    Loads in config options of user_key, mods_file, and mods_dir from the designated config file
    user_key: api key
    mods_file: path to the file where mod information can be found
    mods_dir: path to the bg3 mods directory

    :return: None
    """
    global user_key, mods_file, mods_dir, params
    if os.path.isfile(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        user_key = config['DEFAULT']['apikey']
        params['apikey'] = user_key
        mods_file = config['DEFAULT']['mods_file']
        # mods_dir = config['DEFAULT']['mods_dir'] #TODO: uncomment this when in beta testing
    else:
        # just want to generate the config and probably prompt the user that they need to put in the api key
        # as the config doesn't have one by default, so there's no need to continue running
        config_gen.generate()
        sys.exit()


url = "https://api.nexusmods.com/"
game_name = "baldursgate3"

mod_list = {}


def read_mods():
    """
    Loads the list of mods and their associated information in from the designated mods_file

    :return: True if the mods were properly loaded in, False otherwise
    """
    global mod_list
    proper_keys = {'name', 'file_names', 'timestamps'}
    with open(mods_file, 'r') as modfile:
        mod_list = json.load(modfile)
        for key in mod_list:
            if set(mod_list[key].keys()) != proper_keys:
                mod_list = {}
                return False
            if len(mod_list[key]['timestamps']) != len(mod_list[key]['file_names']):
                mod_list = {}
                return False
        return True

    return False


def write_mods():
    """
    Writes the list of mods and their associated information into the designated mods_file

    :return: True if the file was successfully written to, False otherwise
    """
    if mod_list:
        with open(mods_file, 'w') as modfile:
            json.dump(mod_list, modfile)
            return True

    return False


def clean_dir():
    """
    Deletes all info.json files extracted to the mods directory.
    The looping here can be redundant, depending on if the extracted files overwrite instead of stacking like (1)

    :return: int, the number of files deleted
    """
    counter = 0
    dir_list = os.listdir(mods_dir)
    # delete all the 'info' files extracted to the out directory
    # this can probably just be replaced with something like os.remove(...+'info.json') because of overwriting
    for filename in dir_list:
        if "info" in filename and filename.endswith(".json"):
            os.remove(mods_dir + "/" + filename)
            counter += 1

    return counter


def get_mod_details(mod_id):
    """
    Requests mod details on the mod with the given id

    :param mod_id: int or str, mod id for a specific mod
    :return: full response details, as a json
    """
    response = package.get(url=(url + "v1/games/{}/mods/{}.json").format(game_name, mod_id), headers=params)
    resp_text = json.loads(response.text)
    return resp_text


def get_mod_file(mod_id, file_name=""):
    """
    Requests details on all the mod files, and only return the primary file

    :param mod_id: int or str, mod id for a specific mod
    :param file_name: str name of the mod file to obtain; shown in the mod files tab, the name listed for the mod file
    :return: details of the main mod file, as a json
    """

    main_file = None

    if file_name == "":
        response = package.get(url=(url + "v1/games/{}/mods/{}/files.json?category=main").format(game_name, mod_id),
                               headers=params)
        resp_file = json.loads(response.text)
        main_file = resp_file["files"][0]
        if len(resp_file["files"]) > 1:
            for file in resp_file["files"]:
                # loop through all files to find primary if the first one is not primary
                if file["is_primary"]:
                    main_file = file
                    break
    else:
        response = package.get(
            url=(url + "v1/games/{}/mods/{}/files.json?category=main,optional").format(game_name, mod_id),
            headers=params)
        resp_file = json.loads(response.text)
        for file in resp_file['files']:
            if file['name'] == file_name:
                main_file = file
                break

    return main_file


def update_mods():
    """
    Updates all mods in the mod_list, by downloading each file for each mod if they have had an update since the last
    update specified in the mod_list
    This functionality requires a premium Nexus account

    :return: None
    """
    for mod_id in mod_list.keys():
        for i in range(len(mod_list[mod_id]["file_names"])):
            file_name = mod_list[mod_id]["file_names"][i]
            mod_file = get_mod_file(mod_id, file_name)
            if mod_file["uploaded_timestamp"] > mod_list[mod_id]["timestamps"][i]:
                updated = mod_file['uploaded_timestamp']
                response = package.get(
                    url=(url + "v1/games/{}/mods/{}/files/{}/download_link.json").format(game_name, mod_id,
                                                                                         mod_file['id'][0]),
                    headers=params)
                links = json.loads(response.text)
                # links contains multiple download mirrors, so a future update could include multiple threads downloading from multiple mirrors
                file_request = requests.get(links[0]['URI'], headers=params)
                if response.ok:
                    zipped = zipfile.ZipFile(io.BytesIO(file_request.content))
                    zipped.extractall(mods_dir)
                mod_list[mod_id]['timestamps'][i] = updated


if __name__ == "__main__":
    get_config()
    if not read_mods():
        sys.exit()
    atexit.register(write_mods)

    update_mods()
