import json
import os.path

default = "strainmap.json"

def load(path=default):
    if path == default:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
    with open(path, "r") as strainf:
        strain_map = json.load(strainf, encoding="utf-8")
    des_strain_map = {v[0]: k for k, v in strain_map.items()}
    return strain_map, des_strain_map
