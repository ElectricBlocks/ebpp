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
    for uuid,element in elements.items():
        element_type = utils.get_or_error("etype", element)
        if element_type == "bus":
            # Fill required properties
            req_props = utils.required_props["bus"]
            vn_kv = element.get("vn_kv", 20.0)
            i = pp.create_bus(net, name=uuid, vn_kv=vn_kv)

            # Fill optional properties
            for prop, value in element.items():
                if prop not in req_props:
                    net.bus[prop][i] = value
            
            buses[uuid] = i
    
    for uuid,element in elements.items():
        element_type = utils.get_or_error("etype", element)
        req_props = utils.required_props[element_type]
        index = None

        # Create with required props
        if element_type == "load":
            bus = utils.get_or_error("bus", element)
            p_mw = utils.get_or_error("p_mw", element)
            index = pp.create_load(net, buses[bus], p_mw=p_mw, name=uuid)
            pass
        elif element_type == "gen":
            bus = utils.get_or_error("bus", element)
            p_mw = utils.get_or_error("p_mw", element)
            vm_pu = utils.get_or_error("vm_pu", element)
            index = pp.create_gen(net, buses[bus], p_mw=p_mw, vm_pu=vm_pu, name=uuid)
        elif element_type == "ext_grid":
            bus = utils.get_or_error("bus", element)
            index = pp.create_ext_grid(net, buses[bus], name=uuid)
        elif element_type == "line":
            from_bus = utils.get_or_error("from_bus", element)
            to_bus = utils.get_or_error("to_bus", element)
            length_km = utils.get_or_error("length_km", element)
            std_type = utils.get_or_error("std_type", element)
            index = pp.create_line(net, buses[from_bus], buses[to_bus], length_km, std_type, name=uuid)
        elif element_type == "bus":
            pass # Already handled above
        else:
            raise InvalidError(f"Element type {element_type} is invalid or not implemented!")

        # Fill optional props
        for prop, value in element.items(): # BUG This does not fill optional props from Optimal Power Flow
            if prop not in req_props:
                try:
                    net[element_type][prop][index] = value
                except:
                    raise InvalidError(f"Unable to set property {prop}.")
    
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

    for uuid,element in elements.items():
        results[uuid] = {}
        element_type = elements[uuid]["etype"]
        results[uuid]["etype"] = element_type
        index = pp.get_element_index(net, element_type, uuid, exact_match=True)
        results[uuid].update(net["res_" + element_type].iloc[index].to_dict())

    message["elements"] = results
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
