from config import *
import urllib

import settings
import network
import page


def load_messages(config: dict):
    # Ask for passphrase
    passphrase = inpt(fgYELLOW + "Enter your passphrase: " + fgWHITE)
    passphrase = urllib.parse.quote_plus(passphrase)

    messages = page.load_messages_config(config, passphrase=passphrase)
    messages = page.load_messages_server(config, messages, passphrase=passphrase)

    # Reverse transaction list on each sender
    for sender in messages.keys():
        messages[sender] = messages[sender][:: -1]
    return messages


def send_message(config: dict, to: str = ""):
    clear_screen()
    print(fgBLUE+"Send Message"+fgWHITE)
    message = inpt(fgYELLOW + "Message: " + fgWHITE)
    to = inpt(fgYELLOW + "To (Address): " + fgWHITE) if to == "" else to
    encrypted = getch(fgYELLOW + "Encrypted (y/n): " + fgWHITE)
    passphrase = inpt(fgYELLOW + "Passphrase: " + fgWHITE)

    passphrase = urllib.parse.quote_plus(passphrase)
    message = urllib.parse.quote_plus(message)

    # Check if account id exists
    type = "getAccount&account="+to
    recipient_id = network.request(type, config)
    if recipient_id.get("errorCode") != None:
        print(fgRED + "Error: " + recipient_id["errorDescription"] + fgWHITE)
        inpt("Press Enter to continue...")
        return
    else:
        to = recipient_id["account"]
        type = "sendMessage&recipient="+to+"&secretPhrase="+passphrase+"&broadcast=true&feeNQT="+str(config["fee"])+"&deadline="+str(config["deadline"])

        if encrypted == "y":
            type += "&messageToEncryptToSelf="+message+"&messageToEncrypt="+message+"&messageToEncryptToSelfIsText=true&messageToEncryptIsText=true"
        else:
            type += "&message="+message+"&messageIsText=true"

        # Send Message
        response = network.request(type, config, method="POST")
        if response.get("errorDescription") == None:
            is_encrypted = str(encrypted == 'y')
            print(fgGREEN + "Message sent! (" + is_encrypted + ")"+fgWHITE)
            inpt("Press any enter to continue...")
        else:
            print(fgRED + "Error: " + fgWHITE + str(response.get("errorDescription")))
            inpt("Press any enter to continue...")
    return


def read_message(config: dict):
    messages = load_messages(config)
    save_config(config)

    # Page list of senders
    current_page = 0
    page_size = 5
    selected_sender = ""
    pages = {}

    # Pre-load pages
    pages, total_pages = page.load_pages(messages, pages, page_size, config)

    # Load Pages
    while True:
        clear_screen()
        selected_sender = ""
        print("\n" + fgYELLOW + "Messages (" + config["address"] + ")")
        print("Press [Up] or [Down] to load next page | [1]-["+str(page_size)+"] to select sender."+fgWHITE)
        # Print pages
        for i in range(0, page_size):
            if i >= len(pages[current_page]):
                break

            sender = pages[current_page][i]

            # Check if sender in favorites
            favorite = ""
            if sender in config["favorites"].keys():
                favorite = "*"

            print(str(i+1) + ")"+favorite + " " + sender, end="")

            # Print name
            if sender in config["favorites"].keys():  # May uprise a potential bug
                print(" ("+config["favorites"][sender]+")")
                continue
            else:
                print(" ("+messages[sender][0]["sender_name"]+")")

        print(fgYELLOW+"Page " + str(current_page+1) + "/" + str(total_pages), " | [N] Message new recipient | [R] Refresh | [F] Add New Favorite | [Q] Quit")

        # Get user input
        user_input = getch(fgYELLOW + "" + fgWHITE)

        if user_input == "w" or user_input == "H":
            # Up
            if current_page > 0:
                current_page -= 1
        elif user_input == "s" or user_input == "P":
            # Down
            if current_page < total_pages - 1:
                current_page += 1
        elif user_input.isdigit():
            try:
                selected_sender = pages[current_page][int(user_input)-1]
            except IndexError:
                continue

            while True:
                clear_screen()

                print("\n" + fgYELLOW + "Messages from " + selected_sender + fgWHITE + " ("+messages[selected_sender][0]["sender_name"]+")")
                for i in range(0, len(messages[selected_sender])):
                    date = convert_timestamp(messages[selected_sender][i]["date"])
                    name = "(You) | " if messages[selected_sender][i]["from_me"] else ""

                    # Date
                    print(name+fgGREEN + date + fgWHITE, end="")

                    # Fee
                    print(" | " + fgGREEN + "Fee: " + str(messages[selected_sender][i]["fee"]) + fgWHITE + ": ", end="")

                    # Message
                    print(messages[selected_sender][i]["message"])

                print("\n" + fgYELLOW + "Press [N] to send a new message to " + selected_sender + " | [R] Refresh | [Q] Quit")

                # Get user input
                user_input = getch(fgYELLOW + "" + fgWHITE)

                if user_input == "n":
                    # Send message
                    send_message(config, to=selected_sender)
                elif user_input == "r":
                    current_page = 0
                    pages = {}

                    load_messages(config)
                    pages, total_pages = page.load_pages(messages, pages, page_size, config)
                elif user_input == "q":
                    break

        elif user_input == "n":
            send_message(config)
        elif user_input == "r":
            current_page = 0
            selected_sender = ""
            pages = {}

            load_messages(config)
            pages, total_pages = page.load_pages(messages, pages, page_size, config)
        elif user_input == "f":
            config = settings.add_favorite(config)
        elif user_input == "q":
            # Exit
            break
