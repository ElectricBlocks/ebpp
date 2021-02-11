import json
import pandapower as pp

from errors import InvalidError

required_props = {
    "bus": ["vn_kv"],
    "load": ["bus", "p_mw"],
    "ext_grid": ["bus"],
    "line": ["from_bus", "to_bus", "length_km", "std_type"],
    "switch": ["bus", "element", "et"],
    "trafo": ["hv_bus", "lv_bus", "sn_mva", "vn_hv_kv", "vn_lv_kv", "vk_percent", "vkr_percent", "pfe_kw", "i0_percent"],
    "storage": ["bus", "p_mw", "max_e_mwh"],
    "gen": ["bus", "p_mw"]
}

def get_or_error(key, input_dict):
    if key in input_dict:
        return input_dict[key]
    else:
        raise InvalidError(f"Could not get key \"{key}\" from dictionary.")
