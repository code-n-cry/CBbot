import json
import requests
import sys


def XRPSender(service, secret, account, destination, amount):

    if not service:
        return "[XRPSender]{error} No service"
        return False

    if not secret:
        return "[XRPSender]{error} No secret key"
        return False

    if not account:
        return "[XRPSender]{error} No account"
        return False

    if not destination:
        return "[XRPSender]{error} No destination"
        return False

    if not amount:
        return "[XRPSender]{error} No amount"
        return False

    try:
        normalized_amount = float(amount) * 1000000
        normalized_amount = str(int(normalized_amount))
    except Exception:
        return "[XRPSender]{exception} Invalid amount: %s"
        return False

    signed_request = {
        "method":
        "sign",
        "params": [{
            "secret": secret,
            "tx_json": {
                "TransactionType": "Payment",
                "Account": account,
                "Destination": destination,
                "Amount": normalized_amount
            },
        }]
    }

    try:
        response = requests.post(service, data=json.dumps(signed_request))
        signed_response = json.loads(response.text)
    except Exception:
        return "[XRPSender]{exception} %s"
        return False

    if not "result" in signed_response:
        return "[XRPSender]{error} No result in the signed response"
        return False

    if not "status" in signed_response["result"]:
        return "[XRPSender]{error} No status in the signed response"
        return False

    if signed_response["result"]["status"] != "success":
        if "error_message" in signed_response["result"]:
            return "[XRPSender]{error} Error in the signed response: %s" % signed_response[
                "result"]["error_message"]
        else:
            return "[XRPSender]{error} Error in the signed response"
        return False

    if not "tx_blob" in signed_response["result"]:
        return "[XRPSender]{error} No Tx Blob"
        return False

    tx_blob = signed_response["result"]["tx_blob"]

    return "You're going to send %s XRP to %s" % (amount, destination)

    while True:
        validation = raw_input("Do you confirm this transaction? [yes/no] ")
        if validation in ('y', 'ye', 'yes'):
            break
        if validation in ('n', 'no'):
            return False

    submit_tx = {"method": "submit", "params": [{"tx_blob": tx_blob}]}

    try:
        response = requests.post(service, data=json.dumps(submit_tx))
        submitted_response = json.loads(response.text)
    except Exception, e:
        return "[XRPSender]{exception} %s" % e
        return False

    if submitted_response["result"]["status"] != "success":
        if "error_message" in submitted_response["result"]:
            return "[XRPSender]{error} Error in the submitted response: %s" % submitted_response[
                "result"]["error_message"]
        else:
            return "[XRPSender]{error} Error in the submitted response"
        return False

    return "XRP sent ;)"

    return True
