from typing import List, Optional
from datetime import datetime

from .models import Bill, Receipt, Customer, Payment
from .utils import PaymentUtils
from .exceptions import ObjectNotPresentException

class Biller:

    @staticmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()

        # currently bills have one-to-one relationship with accounts 
        # This may change in upcoming iterations.
        return [account.bills.get() for account in customerAccounts]

    @staticmethod
    def generateReceipt(paymentObject: Payment) -> dict:
        receipt = Receipt.objects.create(generatedOn=datetime.now(), bill=paymentObject.bill, 
                            payment=paymentObject, amount=paymentObject.amountPaid)
        return receipt
        