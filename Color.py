# from colorama import Fore, Style, init
# from typing import Any
# init()

# graph ={
# 'drones_number': 5, 
# 'start_zone': 'start', 
# 'end_zone': 'end', 
# 'hubs': {
#         'start': {'coordinate': (0, 0), 'zone': 'priority', 'color': 'green', 'max_drones': "inf", 'holde': 5}, 
#         'end': {'coordinate': (5, 0), 'zone': 'restricted', 'color': 'green', 'max_drones': 5, 'holde': 0}, 
#         'a': {'coordinate': (1, 2), 'zone': 'priority', 'color': 'red', 'max_drones': 1, 'holde': 0, "state": "full"}, 
#         'b': {'coordinate': (2, 2), 'zone': 'priority', 'color': 'red', 'max_drones': 1, 'holde': 0}, 
#         'c': {'coordinate': (3, 2), 'zone': 'priority', 'color': 'red', 'max_drones': 1, 'holde': 0}, 
#         'j': {'coordinate': (4, 2), 'zone': 'priority', 'color': 'red', 'max_drones': 1, 'holde': 0}, 
#         'd': {'coordinate': (1, -2), 'zone': 'priority', 'color': 'red', 'max_drones': 1, 'holde': 0}, 
#         'e': {'coordinate': (4, -2), 'zone': 'normal', 'color': 'red', 'max_drones': 1, 'holde': 0}, 
#         'f': {'coordinate': (3, -2), 'zone': 'normal', 'color': 'red', 'max_drones': 1, 'holde': 0}}, 
# 'graph': {
#         'start': [{'to': 'c', 'capacity': 1, 'holde': 0, }, {'to': 'e', 'capacity': 1, 'holde': 0}], 
#         'c': [{'to': 'start', 'capacity': 1, 'holde': 0}, {'to': 'b', 'capacity': 1, 'holde': 0}, {'to': 'j', 'capacity': 1, 'holde': 0}], 
#         'a': [{'to': 'b', 'capacity': 1, 'holde': 0}], 'b': [{'to': 'a', 'capacity': 1, 'holde': 0}, {'to': 'c', 'capacity': 1, 'holde': 0}], 
#         'j': [{'to': 'c', 'capacity': 1, 'holde': 0}, {'to': 'end', 'capacity': 1, 'holde': 0}], 
#         'end': [{'to': 'j', 'capacity': 1, 'holde': 0}, {'to': 'f', 'capacity': 1, 'holde': 0}], 
#         'e': [{'to': 'start', 'capacity': 1, 'holde': 0}, {'to': 'f', 'capacity': 1, 'holde': 0}], 
#         'd': [{'to': 'f', 'capacity': 1, 'holde': 0}], 'f': [{'to': 'd', 'capacity': 1, 'holde': 0}, {'to': 'e', 'capacity': 1, 'holde': 0}, {'to': 'end', 'capacity': 1, 'holde': 0}]}, 
# 'distances': {
#     'start': [3, 'c'], 'end': [0, 'end'], 'a': [4, 'b'], 'b': [3, 'c'], 'c': [2, 'j'], 'j': [1, 'end'], 'd': [3, 'f'], 'e': [4, 'f'], 'f': [2, 'end']}
#     }



# class Color:
#     all_color: dict = {}
#     def __init__(self, graph):
#         self.map = graph
#         Color.all_color = Color.get_zone_color(graph)
#         ...


#     @staticmethod
#     def get_zone_color(graph: dict[str, Any]) -> dict[str, str]:
#         all_color: dict[str, str] = {}
#         for zone in graph["hubs"]:
#             color_name: str = graph["hubs"][zone]["color"] or "white"
#             all_color[zone] = COLOR_MAP.get(
#                 color_name.lower(),
#                 Fore.WHITE    # unknown color → white fallback
#             )
#         return all_color


# COLOR_MAP: dict[str, str] = {}

# def get_zone_color(graph):
#     all_color: dict[str, str] = {}
#     for zone in graph["hubs"]:
#         color_name: str = graph["hubs"][zone]["color"] or "white"
#         all_color[zone] = COLOR_MAP.get(
#             color_name.lower(),
#             Fore.WHITE    # unknown color → white fallback
#         )
#     return all_color

# print(get_zone_color(graph))