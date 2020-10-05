import json
import sys

import pandapower as pp
import pandas as pd
from flask import Flask, request
from pandapower import LoadflowNotConverged

import utils
from errors import ConvError, InvalidError, JsonError, PPError

app = Flask(__name__)

# ERROR HANDLING

@app.errorhandler(InvalidError)
def invalid_error(error):
    """Replies with an invalid error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(JsonError)
def json_error(error):
    """Replies with an json error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(PPError)
def pp_error(error):
    """Replies with a pandapower error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(ConvError)
def conv_error(error):
    """Reples with a pandapower convergence error"""
    return json.dumps(error.to_dict())

# API ENTRY POINTS

@app.route("/")
def index():
    return "Welcome to Electric Blocks Panda Power. Please visit <a href=\"https://github.com/Electric-Blocks\">https://github.com/Electric-Blocks</a> for more info."

@app.route("/api", methods=["GET", "POST"])
def api():
    try:
        json.loads(request.data)
    except:
        raise JsonError("Could not parse json from request data")

    status = utils.get_or_error("status", request.json)
    if status == "SIM_REQUEST":
        return sim_request(request.json)
    elif status == "KEEP_ALIVE":
        return keep_alive()
    else:
        raise InvalidError(f"Status \"{status}\" is not a valid status code.")

# RESPONSES

def keep_alive():
    message = {}
    message["status"] = "KEEP_ALIVE"
    message["response"] = "Keep alive request acknowledged"
    return json.dumps(message)

def sim_request(data):
    is_three_phase = utils.get_or_error("3phase", data)
    elements = utils.get_or_error("elements", data)
    buses = {}

    net = pp.create_empty_network()
    
    # Start by adding all buses to the network
    for key in elements:
        element = elements[key]
        element_type = utils.get_or_error("type", element)
        if element_type == "bus":
            vn_kv = element.get("vn_kv", 20.0)
            i = pp.create_bus(net, name=key, vn_kv=vn_kv)
            buses[i] = key
    
    
    try:
        if is_three_phase:
            pp.runpp_3ph(net)
        else:
            pp.runpp(net)
    except LoadflowNotConverged:
        raise ConvError("Load flow did not converge.")
    except (KeyError, ValueError) as e:
        raise PPError(str(e))
    except Exception as e:
        raise PPError("Unknown exception has occured: " + str(e))

    message = {}
    message["status"] = "SIM_RESULT"
    results = {}

    # TODO Parse results

    par = []
    res = []
    for tb in list(net.keys()):
        if not tb.startswith("_") and isinstance(net[tb], pd.DataFrame) and len(net[tb]) > 0:
            if 'res_' in tb:
                res.append(tb)
            else:
                par.append(tb)

    message["response"] = results
    return json.dumps(message)

# PROGRAM MAIN ENTRY POINT


if __name__ == "__main__":
    """ Entry point for program
    Just calls run and starts listening for requests
    """
    host_addr = "0.0.0.0"
    debug_flag = False
    argc = len(sys.argv)
    if argc == 1:
        print("No arguments passed. Using defaults.")
    elif argc == 2:
        if sys.argv[1] == "-d":
            print("Running flask in debug mode.")
            host_addr = "127.0.0.1"
            debug_flag = True
        else:
            print(f"The flag {sys.argv[1]} is not a valid flag.")
    else:
        print("Invalid number of arguments given.")
    app.run(host=host_addr, port="1127", debug=debug_flag)
