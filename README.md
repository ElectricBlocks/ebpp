# EBPP

EBPP (Electric Blocks PandaPower) is a server that sends and receives simulation results for the mod [Electric Blocks](https://github.com/ElectricBlocks/electricblocks).

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Installation](#installation)
  * [Docker Install](#docker-install)
  * [Manual Install](#manual-install)
* [Usage](#usage)
  * [Client Requests](#client-requests)
  * [Server Responses](#server-responses)
* [License](#license)
* [Acknowledgements](#acknowledgements)

## About The Project

EBPP is a python HTTP server written using flask that receives power flow simulation requests, performs the simulation, and returns the results. We use pandapower to perform the simulations. This software is written specifically for use with the Electric Blocks mod, but could theoretically be used to call pandapower for other applications. The simulation software is decoupled from the actual server mod itself to allow for a single server to process simulations for multiple minecraft servers. EBPP does not track the state of the Minecraft world and so all calls are stateless. This means the Electric Blocks mod is responsible for tracking the state of blocks in the game. The mod must track connectivity, block state, and update events. It will then make requests to the server when needed. All Electric Blocks (except wires/lines) must be assigned a UUID. This allows EBPP to return the information results for each block in game.

### Built With

* [Python 3.8](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/)
* [PandaPower](http://www.pandapower.org/)
* [Docker](https://www.docker.com/) (Optional)

## Installation

When installing this software you have two options. The first option uses docker to automate the process. This option is easier to do, but requires that you have docker. The second option is the manual installation.

### Docker Install

First make sure you have docker installed on your computer/server. Then build with this command:

`docker build github.com/ElectricBlocks/ebpp -t ebpp`

Once the docker image is finished building, you can run with the command:

`docker run -d -p 1127:1127 ebpp`

### Manual Install

To install manually, make sure you have python3 installed and then run the following commands:

```sh
git clone https://github.com/ElectricBlocks/ebpp.git
cd ebpp
pip install -r requirements.txt
```

Once the python packages are installed, you can run with the command:

```sh
python ebpp.py
```

## Usage

Once the server is running, you can test it by going to http://127.0.0.1:1127 in your web browser. Make sure you are not using SSL. You should receive a simple text welcome response.

The endpoint for using the API is http://127.0.0.1:1127/api. This API sends and receives info using JSON. All packets must include a `status` key that contains the request type.

### Client Requests

**KEEP_ALIVE** checks if the server is responding to requests.

```json
{
    "status": "KEEP_ALIVE"
}
```

**SIM_REQUEST** requests that server perform a simulation. Properties for each element will depend on the type. EBPP does not do error checking and will just pass these values onto PandaPower.

```json
{
    "status": "SIM_REQUEST",
    "3phase": false,
    "elements": {
        "UUID": {
            "etype": "gen",
            "bus": "UUID of Bus",
            "p_mw": 1.0,
            "vm_pu": 120,
            "other_properties": "value",
            ...
        },
        ...
    }
}
```

### Server Responses

**KEEP_ALIVE** lets client know that serer is responding to requests.

```json
{
    "status": "KEEP_ALIVE",
    "response": "Keep alive request acknowledged"
}
```

**SIM_RESULT** results of the sim request. Results for each element will depend on type.

```json
{
    "status": "SIM_RESULT",
    "elements": {
        "UUID": {
            "etype": "gen",
            "p_mw": 1.0,
            "vm_pu": 120.0,
            "other_results": "value",
            ...
        },
        ...
    }
}
```

**JSON_ERROR** clients request could not be parsed as json.

```json
{
    "status": "JSON_ERROR",
    "response": "Some Error Message"
}
```

**INVALID_ERROR** clients request was able to be parsed, but an invalid status was given or there is some other issue with the request.

```json
{
    "status": "INVALID_ERROR",
    "response": "Some Error Message"
}
```

**PP_ERROR** client's SIM_REQUEST was accepted by EBPP, but PandaPower returned an error.

```json
{
    "status": "PP_ERROR",
    "response": "Some Error Message"
}
```

**CONV_ERROR** client's SIM_REQUEST was accepted by EBPP, but the PandaPower failed to converge on a stable result. The network is invalid or unstable.

```json
{
    "status": "CONV_ERROR",
    "response": "Some Error Message"
}
```

This software is in heavy development. This will probably change and break. Sorry ¯\\\_(ツ)\_/¯.

## License

Distributed under the GNU Affero General Public License. See `LICENSE.md` for more information.

## Acknowledgements

This software is developed by students at the University of Idaho for the Capstone Design class:

* Zachary Sugano - Project Lead - [zachoooo](https://github.com/zachoooo)
* Christian Whitfield - Team Member/Communications Lead - [oceanwhit](https://github.com/oceanwhit)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ElectricBlocks/ebpp.svg?style=flat-square
[contributors-url]: https://github.com/ElectricBlocks/ebpp/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ElectricBlocks/ebpp.svg?style=flat-square
[forks-url]: https://github.com/ElectricBlocks/ebpp/network/members
[stars-shield]: https://img.shields.io/github/stars/ElectricBlocks/ebpp.svg?style=flat-square
[stars-url]: https://github.com/ElectricBlocks/ebpp/stargazers
[issues-shield]: https://img.shields.io/github/issues/ElectricBlocks/ebpp.svg?style=flat-square
[issues-url]: https://github.com/ElectricBlocks/ebpp/issues
[license-shield]: https://img.shields.io/github/license/ElectricBlocks/ebpp.svg?style=flat-square
[license-url]: https://github.com/ElectricBlocks/ebpp/blob/master/LICENSE.md
