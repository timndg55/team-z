import time
import json
from uuid import uuid4 as get_uuid


def _basket(order: list) -> list:
    """
    Split the orders section of a transaction into a list of dict containing
    name, flavour, size, price and iced keys and values

    Parameters
    ----------
    order: list
        The order section of the transaction split at the comma delimiter

    Returns
    -------
    list
        A basket which contains all products purchased in this transaction
    """

    result = []
    for i in range(0, len(order), 3):
        product = {}

        # If name section in the order string contains the dash character, then
        # there is usually a flavour included.
        if "-" in order[i + 1]:
            product_split = order[i + 1].split(" - ")
            product["name"] = product_split[0]
            product["flavour"] = product_split[1]
        else:
            product["name"] = order[i + 1]
            product["flavour"] = ""

        # If the size section is empty then we just leave it set to `None`
        product["size"] = "" if not order[i] else order[i]
        product["price"] = float(order[i + 2])

        # The name and flavour should be capitalized
        product["name"] = product["name"].title()
        if product["flavour"]:
            product["flavour"] = product["flavour"].title()

        # Default to non-iced
        product["iced"] = False
        # Remove these sections from the name
        for remove in ["Flavoured ", "Speciality ", "Iced "]:
            if remove in product["name"]:
                product["name"] = product["name"].replace(remove, "")
                # If we are removing Iced then toggle the dictionary entry `iced`
                if remove == "Iced ":
                    product["iced"] = True

        result.append(product)

    return result


def get_raw_transactions(data) -> list:
    """
    Transform and clean the raw data from the CSV file into a list of transactions
    in which we are able to find unique products and locations. Each transaction
    is assigned a UUID string

    Returns
    -------
    list
        A list of transactions along with the basket of items purchased in the transaction.
    """

    transactions = []  # Each transaction contains a basket

    for row in data:
        # Split the comma delimited order section and pass that into the
        # `_basket()` function
        order = row["Orders"].split(",")
        basket = _basket(order)

        card_details = row["Card Details"].split(",")[0]

        transactions.append(
            {
                "id": str(get_uuid()),
                "basket": basket,
                "datetime": int(
                    time.mktime(time.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S"))
                ),
                "location": row["Location"],
                "payment_type": row["Payment Type"],
                "transaction_total": row["Cost"],
                "card_details": None if card_details == "None" else card_details,
            }
        )

    return transactions
