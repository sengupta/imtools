import argparse
import requests
from decimal import Decimal
from pprint import pprint


class InstamojoClient(object):
    PAYMENT_REQUEST_CREATE_ENDPOINT = (
        "https://www.instamojo.com/api/1.1/payment-requests/")

    def __init__(self, api_key, auth_token):
        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": api_key,
            "X-Auth-Token": auth_token})

    def payment_request(
            self, purpose, amount,
            buyer_name, email, phone,
            redirect_url=None, webhook=None,
            allow_repeated_payments=False,
            send_email=True, send_sms=True):
        response = self.session.post(
            self.PAYMENT_REQUEST_CREATE_ENDPOINT,
            data=dict(
                purpose=purpose,
                amount=amount,
                buyer_name=buyer_name,
                email=email,
                phone=phone,
                redirect_url=redirect_url,
                webhook=webhook,
                allow_repeated_payments=allow_repeated_payments,
                send_email=send_email,
                send_sms=send_sms))
        response.raise_for_status()
        return response.json()


def main():
    description = """
    This program allows you to create a Payment Request on Instamojo.

    This requires an API key and an Auth Token, both of which can be retrieved from:

    https://www.instamojo.com/developers/
    """

    epilog = """
    Examples:

    1. $ python {name} "Test payment link" 12.34 <API_KEY> <AUTH_TOKEN>

    2. $ python {name} "Test payment link" 12.34 <API_KEY> <AUTH_TOKEN>
         --buyer_name "Aditya Sengupta" --email aditya@instamojo.com --phone
         7022622382"

    3. $ python {name} "Test payment link" 12.34 <API_KEY> <AUTH_TOKEN>
         --buyer_name "Aditya Sengupta" --email aditya@instamojo.com --phone
         7022622382" --send_email --send_sms

    4. $ python {name} "Test payment link" 12.34 <API_KEY> <AUTH_TOKEN>
         --buyer_name "Aditya Sengupta" --email aditya@instamojo.com --phone
         7022622382 --send_email --send_sms --redirect_url "http://www.example.com"
    """

    parser = argparse.ArgumentParser(
            "Create Instamojo Payment Requests",
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("purpose", help="Purpose of payment")
    parser.add_argument("amount", help="Amount to be paid")
    parser.add_argument("api_key", help="API Key")
    parser.add_argument("auth_token", help="Auth Token")
    parser.add_argument("--buyer_name", help="Buyer's name")
    parser.add_argument("--email", help="Buyer's email address")
    parser.add_argument("--phone", help="Buyer's phone number")
    parser.add_argument("--redirect_url", help="Redirect URL")
    parser.add_argument("--webhook", help="Webhook URL")
    parser.add_argument(
            "--allow_repeated_payments",
            help="Allow multple payments on the same payment request URL",
            action="store_true")
    parser.add_argument(
        "--send_email", help="Send payment request via email", action="store_true")
    parser.add_argument(
        "--send_sms", help="Send payment request via phone", action="store_true")

    args = parser.parse_args()

    client = InstamojoClient(api_key=args.api_key, auth_token=args.auth_token)
    payment_request = client.payment_request(
        purpose=args.purpose,
        amount=Decimal(args.amount).quantize(Decimal('1.00')),
        buyer_name=args.buyer_name,
        email=args.email,
        phone=args.phone,
        redirect_url=args.redirect_url,
        webhook=args.webhook,
        allow_repeated_payments=args.allow_repeated_payments,
        send_email=args.send_email,
        send_sms=args.send_sms)
    pprint(payment_request)

if __name__ == "__main__":
    main()
