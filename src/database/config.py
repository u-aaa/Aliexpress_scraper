from configparser import ConfigParser
from pathlib import Path
import os.path


HERE = Path(__file__).parents[1]
CONFIG_PATH = os.path.join(HERE, 'database\database.ini')

def config(filename=CONFIG_PATH, section='postgresql'):
    '''
    parses the database connection information
    :param filename: name of the files containing the database configuration details
    :param section: database
    :return: db
    '''
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db
