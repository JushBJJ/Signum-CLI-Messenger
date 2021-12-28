from config import *
import requests


def request(type: str, config: dict, is_ip: bool = False, method: str = "GET") -> dict:
    if not is_ip:
        is_ip = requires_port(config["host"])

    port = ":"+config["port"] if is_ip == True else ""

    try:
        if method == "GET":
            return requests.get("https://" + config["host"] + port + "/burst?requestType=" + type).json()
        elif method == "POST":
            return requests.post("https://" + config["host"] + port + "/burst?requestType=" + type).json()
    except:
        if method == "GET":
            return requests.get("http://" + config["host"] + port + "/burst?requestType=" + type).json()
        elif method == "POST":
            return requests.post("http://" + config["host"] + port + "/burst?requestType=" + type).json()
    return {}


def requires_port(host: str):
    return ".signum.network" not in host


def connect_to_network(config: dict):
    connected = False

    print("Connecting to network...")
    try:
        is_ip = requires_port(config["host"])
        # Attempt to connect to selected hosts
        print("Attempting to connect to " + fgGREEN + config["host"] + fgWHITE)
        request("getMyInfo", config, is_ip=is_ip)["host"]

        if config["host"] != "localhost":
            config["is_local"] = False
        else:
            config["is_local"] = True

        connected = True
    except:
        print(fgRED + "Error: Could not connect to " + fgGREEN + config["host"] + fgRED + "!" + fgWHITE)
        config["is_local"] = False
        # Connect to other peers
        for peer in config["peers"]:
            try:
                is_ip = requires_port(peer)

                temp_config = config
                temp_config["host"] = peer
                temp_config["port"] = "8125" if is_ip == True else ""

                print("Attempting to connect to peer: " + fgGREEN + peer+temp_config["port"] + fgWHITE)
                request("getMyInfo", temp_config, is_ip=is_ip)["host"]

                connected = True
                break
            except:
                pass

            if connected:
                break

            print(fgRED + "Error: Could not connect to " + fgGREEN+peer+fgRED + "!" + fgWHITE)

    if not connected:
        print(fgRED + "Error: Could not connect to any peer!" + fgWHITE)

    return config, connected
