import os
import hmac
import hashlib
import argparse
from urllib import urlencode

class Link(object):
    DEFAULT_ENDPOINT = "https://www.instamojo.com"
    def __mac(self, data, salt):
        """
        This method takes a dictionary `data` and returns the Message
        Authentication Code (MAC) for that dictionary. This uses the HMAC-SHA1
        algorithm.

        The MAC is generated thus:

        We create a list of all values from the dictionary and sort them in the
        order of their keys. We then concatenate all these values together,
        separated by a pipe (|) character. If any of the values is a list, we
        splat (contatenate, without a separator) the list by sorting the values
        alphabetically. We then use the HMAC-SHA1 algorithm to generate the
        signature. The key for the signature generation is the salt provided by
        Instamojo
        """
        if data:
            message = '|'.join(
                    str(i)
                    if not isinstance(i, list)
                    else str(''.join(sorted(i)))
                    for i in zip(*sorted(
                        data.iteritems(),
                        key=lambda s: s[0].lower()
                        )
                        )[1]
                    ) # Message that needs the MAC.
            print message
            mac = hmac.new(
                    str(salt),
                    message,
                    hashlib.sha1,
                    ).hexdigest()
            return mac
        else:
            raise Exception(
                    "Dictionary to sign is empty or None"
                    )

    def __str__(self):
        return self.link

    def __init__(self,
            url=None,
            username=None, offer_slug=None,
            name=None, email=None, phone=None,
            amount=None,
            custom_fields={},
            sign=False, salt=None,
            readonly=[], hidden=[], intent=None,
            endpoint=DEFAULT_ENDPOINT
            ):
        if not endpoint:
            endpoint = self.DEFAULT_ENDPOINT
        if url:
            if url.startswith("https://www.instamojo.com"):
                url = url.replace("https://www.instamojo.com", endpoint)
            elif url.startswith("http://www.instamojo.com"):
                url = url.replace("http://www.instamojo.com", endpoint)
            elif url.startswith("instamojo.com"):
                url = url.replace("instamojo.com", endpoint)
            elif url.startswith("www.instamojo.com"):
                url = url.replace("www.instamojo.com", endpoint)
            else:
                raise Exception("URL is not valid")
        else:
            url = "{endpoint}/{username}/{offer_slug}/".format(
                    endpoint=endpoint,
                    username=username,
                    offer_slug=offer_slug,
                    )

        data_dict = {
                "data_name": name,
                "data_email": email,
                "data_phone": phone,
                "data_amount": amount,
                "intent": intent,
                }

        if custom_fields:
            cf_dict = {
                    "data_{key}".format(key=key): value
                    for key, value in custom_fields.iteritems()
                    if key.startswith("Field_")
                    }
            data_dict.update(cf_dict)
        else:
            cf_dict = None

        query_dict = {
                key: value
                for key, value in data_dict.iteritems()
                if value
                }

        if readonly:
            readonly_fields = []
            for field in readonly:
                readonly_fields.append("data_{field}".format(field=field))
        else:
            readonly_fields = None

        if hidden:
            hidden_fields = []
            for field in hidden:
                hidden_fields.append("data_{field}".format(field=field))
        else:
            hidden_fields = None

        if sign:
            if not salt:
                raise Exception("Can't sign without salt")
            if not readonly_fields:
                raise Exception(
                        "Please specify what fields needs to be signed "
                        "(as readonly fields)"
                        )
            to_sign = {
                    key: value
                    for key, value in query_dict.iteritems()
                    if key in readonly_fields
                    }
            mac = self.__mac(to_sign, salt)
            query_dict.update({"data_sign": mac})

        if readonly_fields:
            query_dict.update({"data_readonly": readonly_fields})

        if hidden_fields:
            query_dict.update({"data_hidden": hidden_fields})

        query_string = urlencode(query_dict, doseq=True)
        self.link = "{url}?{query_string}".format(
                url=url,
                query_string=query_string
                )

def main():
    description = """
    This program helps you create Instamojo URLs, with optional signing. This
    is particularly useful if you need to pre-fill some of the fields in the
    Instamojo offer purchase forms. You may pre-fill any or all of the name,
    the email address and the phone number of the buyer, along with any custom
    fields that you may have created.

    Optionally, you may choose to mark any of the custom fields in the form as
    hidden fields- this will add the attribute type="hidden" on that field in
    the purchase form and this will not normally be visible on the front-end.

    Also optionally, you may choose to mark any of the fields in the form as
    readonly. This will add the attribute "readonly" on that field in the
    purchase form and that field will not normally be editable on the
    front-end.

    However, a determined user may edit the field by editing the HTML source of
    the page or by modifying the query string parameters in the URL. If you
    require protection against such edits, please contact the Instamojo team
    and request them to enable signing on the offers where you'd like such
    protection.
    """

    epilog = """
    Examples:

    1. $ python {name} www.instamojo.com/demo/demo-offer/ --name "Aditya
         Sengupta"

    2. $ python {name} www.instamojo.com/demo/demo-offer/ --name "Aditya
         Sengupta" --email aditya@instamojo.com --phone 02240044008

    3. $ python {name} www.instamojo.com/demo/demo-offer/ --name "Aditya
         Sengupta" --email aditya@instamojo.com --phone 02240044008
         --readonly=name,email

    4. $ python {name} www.instamojo.com/demo/demo-offer/ --name "Aditya
         Sengupta" --email aditya@instamojo.com --phone 02240044008
         --readonly=name,email --intent buy

    4. $ python {name} www.instamojo.com/demo/demo-offer/ --name "Aditya
         Sengupta" --email aditya@instamojo.com --phone 02240044008
         --readonly=name,email --intent buy --custom
         Field_48905=Instamojo,Field_53198=26

    """.format(name=__file__)

    parser = argparse.ArgumentParser(
            "Create Instamojo URLs",
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("url", help="Instamojo offer URL without parameters")
    parser.add_argument("--username", help="Your Instamojo username")
    parser.add_argument("--slug", help="Your Instamojo offer slug")
    parser.add_argument("--name", help="Name of the buyer")
    parser.add_argument("--email", help="Email address of the buyer")
    parser.add_argument("--phone", help="Phone number of the buyer")
    parser.add_argument("--amount", help="Amount for this transaction")
    parser.add_argument("--custom", help="Custom fields")
    parser.add_argument("--readonly", help="Fields that should be readonly")
    parser.add_argument("--hidden", help="Fields that should be hidden")
    parser.add_argument("--sign", help="Sign this URL", action="store_true")
    parser.add_argument("--salt", help="Salt to sign the URL")
    parser.add_argument("--intent", type=str, choices=["buy",])
    parser.add_argument("--endpoint", help="Endpoint for the URL to be signed")

    args = parser.parse_args()

    custom_fields = {}
    if args.custom:
        cf_list = args.custom.split(',')
        for cf_kvp in cf_list:
            cf_name, cf_value = cf_kvp.split('=')
            custom_fields.update({cf_name: cf_value})

    if args.readonly:
        readonly = args.readonly.split(',')
    else:
        readonly = []

    if args.hidden:
        hidden = args.hidden.split(',')
    else:
        hidden = []

    if args.sign:
        if args.salt:
            salt = args.salt
        elif os.getenv("instamojo_salt") is not None:
            salt = os.getenv("instamojo_salt")
        else:
            raise Exception("Can't sign URL without salt")

    link = Link(
            url=args.url,
            name=args.name, email=args.email, phone=args.phone,
            amount=args.amount,
            custom_fields=custom_fields,
            sign=args.sign, salt=args.salt,
            readonly=readonly, hidden=hidden, intent=args.intent,
            endpoint=args.endpoint,
            )
    print link

if __name__ == "__main__":
    main()
