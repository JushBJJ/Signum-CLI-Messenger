from config import *
import network


def load_pages(messages: dict, page: dict, page_size: int, config: dict):
    page_index = 0
    page.clear()
    page[0] = []

    favorite_account_addresses = list(config["favorites"].keys())

    # Load all favourite accounts
    for i in range(len(favorite_account_addresses)):
        if i % page_size == 0 and i != 0:
            page_index += 1
            page[page_index] = []

        page[page_index].append(favorite_account_addresses[i])

    # Load rest of the accounts
    for i in range(0, len(messages.keys())):
        if i % page_size == 0 and i != 0:
            page_index += 1
            page[page_index] = []

        sender = list(messages.keys())[i]

        if sender in favorite_account_addresses:
            continue

        page[page_index].append(sender)

    total_pages = len(page.keys())
    return page, total_pages


def load_messages_config(config: dict, passphrase: str = None):
    print("Loading saved messages...")
    messages = {}

    index = 1
    total_transactions = len(config["transactions"])

    # Load messages from config
    for tx in config["transactions"]:
        print("Loading transaction " + str(index) + " of " + str(total_transactions) + " from config...")
        index += 1
        transaction = config["transactions"][tx]
        sender = transaction["sender"]
        message = transaction["message"]

        if transaction.get("encrypted") != None:
            # DecryptFrom
            data = transaction["data"]
            nonce = transaction["nonce"]
            is_text = transaction["is_text"]

            message = network.request("decryptFrom&account="+sender+"&data="+data+"&nonce="+nonce+"&decryptedMessageIsText="+is_text+"&secretPhrase="+passphrase, config)

            if message.get("errorCode") != None:
                print(fgRED + "Error: Could not decrypt message!" + fgWHITE)

                # Print info
                print(fgYELLOW + "Sender: " + fgWHITE + sender)
                print(fgYELLOW + "Data: " + fgWHITE + data)
                print(fgYELLOW + "Nonce: " + fgWHITE + nonce)
                print(fgYELLOW + "Is Text: " + fgWHITE + is_text)
                print(fgYELLOW + "Transaction ID: " + fgWHITE + tx)

                inpt("Press any enter to continue...")
                continue

            message = message["decryptedMessage"]
        if transaction["from_me"]:
            sender = transaction["recipient"]
            transaction["sender_name"] = transaction["recipient_name"]

        if sender not in messages.keys():
            messages[sender] = []

        messages[sender].append({
            "recipient": transaction["recipient"],
            "fee": transaction["fee"],
            "date": transaction["date"],
            "sender_name": transaction["sender_name"],
            "from_me": transaction["from_me"],
            "message": message
        })

    return messages


def load_messages_server(config: dict, messages: dict, passphrase: str = None):
    print("Finding new messages... (This may take a while)")
    # Load *new* messages that have not been saved
    transaction_ids = network.request("getAccountTransactionIds&account="+config["address"], config)
    index = 1
    total_transactions = len(transaction_ids["transactionIds"])
    for tx in transaction_ids["transactionIds"]:
        print("Loading transaction " + str(index) + " of " + str(total_transactions) + " from server...")
        index += 1
        if tx in config["transactions"]:
            continue

        transaction = network.request("getTransaction&transaction="+tx, config)
        attachment = transaction.get("attachment")
        encrypted = False

        if attachment == None:
            continue
        elif attachment.get("message") == None:
            if attachment.get("encryptedMessage") == None:
                continue
            encrypted = True

        message = attachment.get("message") if encrypted == False else attachment["encryptedMessage"]
        sender = transaction["senderRS"]
        recipient = transaction["recipientRS"]

        if recipient == config["address"] and attachment.get("encryptedMessage") != None:
            message = attachment.get("encryptedMessage")
        elif attachment.get("message") != None:
            message = attachment.get("message")
        elif attachment.get("encryptToSelfMessage") == None:
            message = "[ENCRYPTED MESSSAGE]"
            encrypted = False
        else:
            message = attachment.get("encryptToSelfMessage")

        data = None
        nonce = None
        is_text = False

        if encrypted:
            data = message.get("data")
            nonce = message.get("nonce")
            is_text = str(message.get("isText")).lower()

            sender_id = transaction["sender"]

            # Decrypt Message
            message = network.request("decryptFrom&account="+sender_id+"&data="+data+"&nonce="+nonce+"&decryptedMessageIsText="+is_text+"&secretPhrase="+passphrase, config)

            if message.get("errorCode") != None:
                print(fgRED + "Error: Could not decrypt message!" + fgWHITE)

                # Print info
                print(fgYELLOW + "Sender: " + fgWHITE + sender)
                print(fgYELLOW + "Data: " + fgWHITE + data)
                print(fgYELLOW + "Nonce: " + fgWHITE + nonce)
                print(fgYELLOW + "Is Text: " + fgWHITE + is_text)
                print(fgYELLOW + "Transaction ID: " + fgWHITE + tx)

                print(fgYELLOW+"Error Message: " + fgWHITE + str(message.get("errorDescription")))

                inpt("Press any enter to continue...")
                continue

            message = message["decryptedMessage"]

        if sender not in messages.keys() and sender != config["address"]:
            messages[sender] = []

        # Get sender name
        account = network.request("getAccount&account="+transaction["sender"], config)
        recipient = network.request("getAccount&account="+transaction["recipient"], config)

        name = account.get("name")
        recipient_name = recipient.get("name")

        if name == None:
            name = "No name"

        if recipient_name == None:
            recipient_name = "No name"

        new_tx = {
            "sender": transaction["senderRS"],
            "recipient": transaction["recipientRS"],
            "fee": int(transaction["feeNQT"])/(10**8),
            "date": transaction["timestamp"],
            "sender_name": name,
            "recipient_name": recipient_name,
            "from_me": False,
            "message": message
        }

        if sender == config["address"]:
            new_tx["sender_name"] = recipient_name
            sender = transaction["recipientRS"]
            new_tx["from_me"] = True

        if sender not in messages.keys():
            messages[sender] = []

        new_tx["message"] = message
        messages[sender].append(new_tx)

        # Reverse sender and recipient
        if sender == config["address"]:
            new_tx["sender_name"] = name

        if encrypted:
            new_tx["message"] = ""
            new_tx["data"] = data
            new_tx["nonce"] = nonce
            new_tx["is_text"] = is_text
            new_tx["encrypted"] = True

        config["transactions"][tx] = new_tx

    return messages
