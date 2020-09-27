import json

from errors import InvalidError

def get_or_error(key, input_dict):
    if key in input_dict:
        return input_dict[key]
    else:
        raise InvalidError(f"Could not get key \"{key}\" from dictionary.")