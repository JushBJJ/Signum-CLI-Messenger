import json
import colorama
import datetime
import os
import time

if os.name == "posix":
    from getch import getch as py_getch
else:
    from msvcrt import getch as py_getch

# Foreground Colours
fgBLACK = colorama.Fore.BLACK
fgRED = colorama.Fore.RED
fgGREEN = colorama.Fore.GREEN
fgYELLOW = colorama.Fore.YELLOW
fgBLUE = colorama.Fore.BLUE
fgWHITE = colorama.Fore.WHITE

# Background Colours
bgBLACK = colorama.Back.BLACK
bgGREEN = colorama.Back.GREEN
bgWHITE = colorama.Back.WHITE

colorama.init()

# Main keys for config.json
required_keys = {
    "host": str,
    "port": str,
    "is_local": bool,
    "address": str,
    "deadline": int,
    "fee": int,
    "peers": list,
    "favorites": dict,
    "transactions": dict
}

# Keys for transaction dictionary in config.json
required_tx_keys_out = str
required_tx_keys_in = {
    "sender": str,
    "recipient": str,
    "fee": float,
    "date": int,
    "sender_name": str,
    "recipient_name": str,
    "from_me": bool,
    "message": str
}

error = False
passphrase = ""


def convert_timestamp(timestamp: int):
    genesis = datetime.datetime.strptime("2014-08-11 12:00:00", "%Y-%m-%d %H:%M:%S")

    genesis_unix = time.mktime(genesis.timetuple())
    timestamp_unix = genesis_unix+timestamp
    return str(datetime.datetime.fromtimestamp(timestamp_unix))


def inpt(prompt: str = ""):
    # This function is to fix bugs where printing colours do not work when using inpt()
    print(prompt, end="")
    return input()


def getch(output: str):
    print(output, end="")
    try:
        key = py_getch().decode("utf-8")
    except UnicodeDecodeError:
        key = "\x00"  # Just a guess, need a better way for this
    if key == "\x00":
        key = py_getch().decode("utf-8")
    return key


def clear_screen():
    # Clear screen (Windows)
    print(bgBLACK + chr(27) + "[2J")


def print_config_error(type: str, key: str, real_value: type = None, expected_value: type = None):
    global error

    if type == "Missing":
        print(fgRED + "Error: Missing key '" + fgYELLOW + key + fgRED + "' in config.json" + fgWHITE)
    elif type == "Incorrect Value":
        print(fgRED + "Error: Type for key '" + fgYELLOW + key + fgRED + "' should be " + fgGREEN+str(expected_value) + fgRED + " not " + fgGREEN+str(real_value) + fgWHITE)

    error = True


def load_config():
    print("Loading config...")

    try:
        config = json.load(open("config.json"))
    except FileNotFoundError:
        print(fgRED + "Error: config.json not found" + fgWHITE)

        # Create config.json by prompting user
        print(fgYELLOW + "Creating config.json..." + fgWHITE)
        config = {}

        input_text = {
            "host": "Enter host: ",
            "port": "Enter port: ",
            "address": "Enter address (e.g: S-UBNP-U2C7-NH2J-7RXVW): ",
            "fee": fgBLUE+"\nExample: 0.00735 is 735000 in NQT. [0.00735×( 10^8 )]"+fgYELLOW+"\nFee (in NQT): "+fgWHITE
        }

        # Prompt user for host
        for key in required_keys.keys():
            if key == "is_local":
                config[key] = False
                continue
            elif key == "deadline":
                config[key] = 60
                continue
            elif key == "peers":
                # All featured peers' web wallet in https://explorer.signum.network/peers/
                config[key] = [
                    "europe.signum.network",
                    "europe1.signum.network",
                    "europe3.signum.network",
                    "brazil.signum.network",
                    "uk.signum.network",
                    "singapore.signum.network",
                    "canada.signum.network",
                    "australia.signum.network",
                    "latam.signum.network"
                ]
                continue
            elif key == "favorites":
                config[key] = {}
                continue
            elif key == "transactions":
                config[key] = {}
                continue

            config[key] = inpt(fgYELLOW + input_text[key] + fgWHITE)

            if key == "fee":
                config[key] = int(config[key])

        save_config(config)

    # Check if main keys are valid
    for key in required_keys:
        if key not in config:
            print_config_error(type="Missing", key=key)

        elif type(config[key]) != required_keys[key]:
            print_config_error(type="Incorrect Value", key=key, real_value=type(config[key]), expected_value=required_keys[key])

    # Check if transaction keys (out) are valid
    for key in config["transactions"].keys():
        if type(key) != required_tx_keys_out:
            print_config_error(type="Incorrect Value", key=key, real_value=type(key), expected_value=required_tx_keys_out)

        else:
            # Check transaction keys (in)
            for key_in in required_tx_keys_in:
                if key_in not in config["transactions"][key]:
                    print("Error in transaction: "+key)
                    print_config_error(type="Missing", key=key_in)

                elif type(config["transactions"][key][key_in]) != required_tx_keys_in[key_in]:
                    print("Error in transaction: "+key)
                    print_config_error(type="Incorrect Value", key=key_in, real_value=type(config["transactions"][key][key_in]), expected_value=required_tx_keys_in[key_in])

    if error:
        print("Press enter to exit...")
        inpt()
        exit()

    return config


def save_config(config: dict):
    json.dump(config, open("config.json", "w"), indent=4)
