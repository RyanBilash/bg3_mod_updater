import configparser
import os

def generate():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'Mods_File': './download.json',
        'apikey': '',
        'Mods_Dir': os.path.expandvars(r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods")
    }
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    generate()