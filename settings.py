from config import *
import network


def change_address(config: dict):
    clear_screen()
    print(fgYELLOW + "Enter new address: " + fgWHITE)
    new_address = inpt(fgYELLOW + "Address: " + fgWHITE)

    # Check if address exists
    type = "getAccount&account="+new_address
    response = network.request(type, config)
    if response.get("errorCode") != None:
        print(fgRED + "Error: Account Address " + fgYELLOW + new_address + fgRED + " does not exist!" + fgWHITE)
        inpt("Press any enter to continue...")
        return

    config["address"] = new_address
    save_config(config)
    print(fgGREEN + "Address changed!" + fgWHITE)
    save_config(config)
    inpt("Press any enter to continue...")
    return config


def change_fee(config: dict):
    clear_screen()
    print(fgYELLOW + "\n\nExample: 0.00735 is 735000 in NQT. [0.00735×(10^8 )]" + fgWHITE)
    new_fee = inpt(fgYELLOW + "Fee (in NQT): " + fgWHITE)

    config["fee"] = int(new_fee)
    save_config(config)
    print(fgGREEN + "Fee changed!" + fgWHITE)
    save_config(config)
    inpt("Press any enter to continue...")
    return config


def change_deadline(config: dict):
    clear_screen()
    print(fgYELLOW + "Enter new deadline (minutes): " + fgWHITE)
    new_deadline = inpt(fgYELLOW + "Deadline: " + fgWHITE)

    config["deadline"] = int(new_deadline)
    save_config(config)
    print(fgGREEN + "Deadline changed!" + fgWHITE)
    save_config(config)
    inpt("Press any enter to continue...")
    return config


def clear_transactions(config: dict):
    config["transactions"] = {}
    save_config(config)
    print(fgGREEN + "Transactions cleared!" + fgWHITE)
    inpt("Press any enter to continue...")
    return config


def edit_favorites(config: dict):
    clear_screen()
    print(fgYELLOW + "Edit Favorites")
    print("[1] Add New Favorite")
    print("[2] Remove Favorite")
    print("[3] Clear Favorites")
    print("[4] Back")
    print(fgWHITE)

    commands = {
        "1": add_favorite,
        "2": remove_favorite,
        "3": clear_favorites,
        "4": None
    }

    while True:
        user_input = getch(fgYELLOW + "" + fgWHITE)

        if user_input in commands.keys():
            config = commands[user_input](config)
            break

    save_config(config)
    inpt("Press any enter to continue...")
    return config


def add_favorite(config: dict):
    clear_screen()
    address = inpt(fgYELLOW + "Address: " + fgWHITE)
    name = inpt(fgYELLOW + "Name: " + fgWHITE)

    config["favorites"][address] = name
    save_config(config)
    print(fgGREEN + "Favorite added!" + fgWHITE)
    inpt("Press any enter to continue...")
    return config


def remove_favorite(config: dict):
    clear_screen()
    print(fgYELLOW + "Remove Favorite")

    # Input the address/name they want to remove
    # If the address or name exists, remove it from the config["favorites"]

    print(fgYELLOW + "Enter the address/name of the favorite to remove. " + fgWHITE)
    user_input = inpt(fgYELLOW + "Address/Name: " + fgWHITE)

    if user_input in config["favorites"].keys():
        del config["favorites"][user_input]
        print(fgGREEN + "Favorite removed!" + fgWHITE)
    elif user_input in config["favorites"].values():
        for key, value in config["favorites"].items():
            if value == user_input:
                del config["favorites"][key]
                print(fgGREEN + "Favorite removed!" + fgWHITE)
                break
    else:
        print(fgRED + "Favorite does not exist!" + fgWHITE)

    save_config(config)
    inpt("Press any enter to continue...")
    return config


def clear_favorites(config: dict):
    config["favorites"] = {}
    save_config(config)
    print(fgGREEN + "Favorites cleared!" + fgWHITE)
    inpt("Press any enter to continue...")
    return config


def change_host_or_port(config: dict):
    while True:
        clear_screen()
        # Change host or port
        print(fgYELLOW + "Change Host or Port" + fgWHITE)
        print("[1] Change Host")
        print("[2] Change Port")
        print("[3] Back")

        num = getch(fgYELLOW + ">" + fgWHITE)

        if num == "1":
            config["host"] = inpt(fgYELLOW + "Host: " + fgWHITE)
            print(fgGREEN + "Host changed!" + fgWHITE)
        elif num == "2":
            config["port"] = inpt(fgYELLOW + "Port: " + fgWHITE)
            print(fgGREEN + "Port changed!" + fgWHITE)
        elif num == "3":
            return config
        else:
            print(fgRED + "Invalid input!" + fgWHITE)
            inpt("Press enter to continue...")
            continue

        return config


def settings(config: dict):
    """
    Settings

    1. Change Address
    2. Change default fee
    3. Change default deadline
    4. Clear Transactions
    5. Edit Favorites
    6. Change Host/Port
    7. Quit
    """
    commands = {
        "1": change_address,
        "2": change_fee,
        "3": change_deadline,
        "4": clear_transactions,
        "5": edit_favorites,
        "6": change_host_or_port
    }

    while True:
        clear_screen()
        print(fgYELLOW + "Settings" + fgWHITE)
        print("1. Change Address")
        print("2. Change default fee")
        print("3. Change default deadline")
        print("4. Clear Transactions")
        print("5. Edit Favorites")
        print("6. Change Host/Port")
        print("7. Quit")

        user_input = getch(fgYELLOW + "> " + fgWHITE)

        if user_input in commands.keys():
            commands[user_input](config)
        elif user_input == "7":
            break
    pass
