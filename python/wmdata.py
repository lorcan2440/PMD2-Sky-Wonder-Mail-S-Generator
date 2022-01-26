import json
import os

dataSource = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data.json')

with open(dataSource, 'r') as f:
    allData = json.load(f)

WMSkyDungeon = allData['WMSkyDungeon']
WMSkyItem = allData['WMSkyItem']
WMRewardType = allData['WMRewardType']
WMSkyPoke = allData['WMSkyPoke']
WMSGenData = allData['WMSGenData']
WMSStruct = allData['WMSStruct']


def inverse_dict(orig: dict) -> dict:
    inv_map = {}
    for k, v in orig.items():
        inv_map[v] = min([inv_map.get(v, []) + [k]])

    for k, v in inv_map.items():
        inv_map[k] = v[0]

    return inv_map

