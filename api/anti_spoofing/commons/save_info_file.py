import os
from pathlib import Path
from datetime import datetime

pathDirectory = os.path.dirname(os.path.abspath(__file__))
pathDirInfo = os.path.join(
    pathDirectory, "../public/"+str(datetime.today().strftime('%m-%Y')))
pathFileInformation = os.path.join(
    pathDirInfo, str(
        datetime.today().strftime('%Y-%m-%d')) + ".txt")


def valid_exit_directory():
    if not os.path.isdir(pathDirInfo):
        os.mkdir(pathDirInfo)


"""
Metodo para escribir en un archivo
"""


def write_file(info):
    valid_exit_directory()
    time = datetime.now().time()
    file_save_info = open(pathFileInformation, "a")
    file_save_info.write(str(time) + " " + info + "\n")
    file_save_info.close()


"""
metodo para buscar una linea en el archivo segun el identificador que se envia por parametro
"""


def read_line(id):
    if Path(pathFileInformation).is_file() and os.path.isdir(pathDirInfo):
        search = open(pathFileInformation, "r")
        for line in search.readlines():
            if id in line:
                result = line.split()
                return {"result": result[2]}
    return {"result": "pending"}
