from faker import Faker
from random import choice, randint
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string and database name
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

fake = Faker()

# Connect to MongoDB
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def init_data(num_customers: int, num_accounts: int, num_transactions: int):
    # Generate customers
    customers = []
    for _ in range(num_customers):
        customers.append({
            "clientNumber": fake.uuid4()[:8],  # Generate a random client number
            "name": fake.company()  # Generate a random company name
        })

    # Generate  accounts
    accounts = []
    for _ in range(num_accounts):
        accounts.append({
            "accountNumber": fake.uuid4()[:8],  # Generate a random account number
            "customer": choice(customers)  # Assign a random customer to the account
        })

    # Generate 10,000 transactions
    transactions = []
    for _ in range(10000):
        transaction_type = choice(["Credit", "Debit"])
        action_date = fake.date_time_between(start_date="-1y", end_date="now")
        value_date = action_date + timedelta(days=randint(1, 10))
        amount = randint(1, 10000)
        account = choice(accounts)

        if transaction_type == "Debit":
            if choice([True, False]):
                payment_info = {
                    "outgoingWirePayment": {
                        "beneficiaryName": fake.name(),
                        "beneficiaryAddress": fake.address(),
                        "creditCurrency": fake.currency_code(),
                        "exchangeRate": fake.random_number(digits=2)
                    }
                }
            else:
                payment_info = {
                    "achCreditBatch": create_ach_batch(randint(3,20))
                }
        else:
            payment_info = {
                "incomingInteractReceive": {
                    "invoiceNumber": fake.uuid4(),
                    "paymentReference": fake.uuid4()
                }
            }

        transactions.append({
            "type": transaction_type,
            "actionDate": action_date,
            "valueDate": value_date,
            "amount": amount,
            "accountNumber": account["accountNumber"],
            "clientNumber": account["customer"]["clientNumber"],
            "paymentInfo": payment_info
        })

    # Insert transactions into MongoDB
    collection.insert_many(transactions)

    print("Transactions inserted successfully.")


def create_ach_batch(num_items: int):
    # Create a list to store the ACHCreditBatch items
    items = []

    # Generate ACHCreditBatch items
    for _ in range(num_items):
        item = {
            "beneficiaryName": fake.name(),
            "beneficiaryAccount": fake.iban(),
            "transactionCode": fake.random_number(digits=6),
            "payment_amount": fake.random_number(digits=4)
        }
        items.append(item)

    return items


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    init_data(10, 100, 1000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
