from config import *

import network
import message
import settings


def print_title():
    clear_screen()

    # Title
    print(fgBLUE + "Signum Messenger" + fgWHITE)
    print("Github: " + fgGREEN + "https://github.com/JushBJJ/Signum-CLI-Messenger" + fgWHITE)


def print_user_info(config: dict):
    print("Host: " + fgGREEN + config["host"] + fgWHITE)
    print("Port: " + fgGREEN + config["port"] + fgWHITE)
    print("Address: " + fgGREEN + config["address"] + fgWHITE)

    if config["is_local"] == False:
        print(fgRED + "WARNING: You are not connected to your own local node!" + fgWHITE)


def print_menu():
    print("\n" + fgYELLOW + "Menu" + fgWHITE)
    print("1. Messages")
    print("2. Settings")
    print("3. Exit")


def run_command(config: dict):
    commands = {
        "1": message.read_message,
        "2": settings.settings
    }

    # Get user input
    while True:
        user_input = getch(fgYELLOW + "> " + fgWHITE)

        if user_input in commands.keys():
            commands[user_input](config)
            break
        elif user_input == "3":
            exit()
        else:
            # Clear line
            print("\r" + " " * (len(user_input)-1), end="")


def main():
    # Load config
    config = load_config()
    config, connected = network.connect_to_network(config)

    if not connected:
        return

    # Update Peers
    print("Updating peers...")
    is_ip = network.requires_port(config["host"])
    peers = network.request("getPeers", config, is_ip=is_ip)["peers"]

    # TODO: How do I use the API among peers that are not wallet hosts?
    """
    # Concatenate new peers
    for peer in peers:
        if peer not in config["peers"]:
            config["peers"].append(peer)
    """

    save_config(config)

    while True:
        print_title()
        print_user_info(config)
        print_menu()
        run_command(config)


if __name__ == "__main__":
    main()
