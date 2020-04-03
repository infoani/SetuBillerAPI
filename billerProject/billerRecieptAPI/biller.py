from typing import List, Optional
from datetime import datetime

from .models import Bill, Receipt, Customer, Payment
from .utils import PaymentUtils
from .exceptions import BillExactAmountMismatchException

class Biller:

    @staticmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()

        # currently bills have one-to-one relationship with accounts 
        # This may change in upcoming iterations.
        return [account.bills.get() for account in customerAccounts]

    @staticmethod
    def generateReceipt(paymentObject: Payment) -> dict:
        Biller.validateAndUpdatePayment(paymentObject)
        billObject = paymentObject.bill
        receipt = Receipt.objects.create(generatedOn=datetime.now(), bill=billObject, 
                            payment=paymentObject, receiptAmount=paymentObject.amountPaid)
        return receipt

    @staticmethod
    def validateAndUpdatePayment(paymentObject):
        billObject = paymentObject.bill
        if billObject.amountExactness == "EXACT":
            if paymentObject.amountPaid != billObject.billAmount:
                raise BillExactAmountMismatchException("Bill amount and paid amount dont match")
            else:
                billObject.paidAmount = billObject.billAmount
                billObject.billPaidFully = True
        else:
            billObject.paidAmount = paymentObject.paidAmount
        billObject.save()