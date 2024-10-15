import configparser
import json
import os

def generate():
    """
    Generates a config file, containing default information for mods_file, apikey, and mods_dir
    mods_file is defaulted to ./download.json
    apikey is left empty, and requires the user to input theirs manually
    mods_dir is located based on the default bg3 mods folder

    :return: None
    """
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Mods_File': './download.json',
        'apikey': '',
        'Mods_Dir': os.path.expandvars(r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods")
    }
    with open('./download.json', 'w') as jsonfile:
        json.dump({},jsonfile)
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    generate()