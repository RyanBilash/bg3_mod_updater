import requests
import platform
import csv
import json

package = requests

user_key = "k9zjCGLfWZgscJrJrc0O8eUnrl8tMyXgVCXnwdQ2fkMosr0=--xYdCouD24lqgueoK--RVWNhE0H2DN/7uK+j1bmkA=="
agent_string = "{} -- {}/{}".format(platform.platform(), package.__title__, package.__version__)

params = {
        "apikey":user_key,
        "User-Agent":agent_string,
        "md5":"h951XP1TMJ9boDWyDS2rSg",
        "expires":"1725695474"
    }
#&md5=h951XP1TMJ9boDWyDS2rSg&expires=1725695474&user_id=79838608
url = "https://api.nexusmods.com/"
game_name = "baldursgate3"

"""mod_lists = open("mod_list.csv", "r")
spamreader = csv.reader(mod_lists, delimeter=', ')
for row in spamreader:
    pass
"""

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
            if file["is_primary"]:
                main_file = file
                break
    return main_file

def update_mods():
    for id in mod_list.keys():
        response = get_mod_details(id)
        if response["updated_timestamp"] > mod_list[id]["timestamp"]:
            file_to_download = get_mod_files(id)
            pass

id=87
#temp = package.get(url=(url + "v1/games/{}/mods/{}/files/{}/download_link.json").format(game_name, id, get_mod_files(87)["file_id"]), headers=params)

temp = package.get(url="https://api.nexusmods.com/v1/games/baldursgate3/mods/87/files/36127/download_link.json?key=k9zjCGLfWZgscJrJrc0O8eUnrl8tMyXgVCXnwdQ2fkMosr0=--xYdCouD24lqgueoK--RVWNhE0H2DN/7uK+j1bmkA==&expires=1725696093", headers=params)

i = 0
get_mod_details(213)

