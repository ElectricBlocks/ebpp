import json
import pandapower as pp

from errors import InvalidError

required_props = {
    "bus": ["etype", "vn_kv"],
    "load": ["etype", "bus", "p_mw"],
    "ext_grid": ["etype", "bus"],
    "line": ["etype", "from_bus", "to_bus", "length_km", "std_type"],
    "switch": ["etype", "bus", "element", "et"],
    "trafo": ["etype", "hv_bus", "lv_bus", "std_type"],
    "storage": ["etype", "bus", "p_mw", "max_e_mwh"],
    "gen": ["etype", "bus", "p_mw", "vm_pu", "slack"]
}

def get_or_error(key, input_dict):
    if key in input_dict:
        return input_dict[key]
    else:
        raise InvalidError(f"Could not get key \"{key}\" from dictionary.")
