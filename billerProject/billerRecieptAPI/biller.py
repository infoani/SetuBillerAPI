from typing import List, Optional

from .models import Bill, Receipt, Customer, Payment
from .utils import PaymentUtils
from .exceptions import BillExactAmountMismatchException, BillFullyPaidAlreadyException
from django.db.models.functions import datetime
from django.utils import timezone

class Biller:

    @staticmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()

        # currently bills have one-to-one relationship with accounts 
        # This may change in upcoming iterations.
        return [bill for account in customerAccounts 
                for bill in account.bills.all() if not bill.billPaidFully]

    @staticmethod
    def generateReceipt(paymentObject: Payment) -> dict:
        Biller.validateAndUpdatePayment(paymentObject)
        billObject = paymentObject.bill
        receipt = Receipt.objects.create(generatedOn=datetime.datetime.now(tz=timezone.get_current_timezone()), bill=billObject, 
                            payment=paymentObject, receiptAmount=paymentObject.amountPaid)
        paymentObject.receiptGenerated = True
        paymentObject.save()
        return receipt

    @staticmethod
    def validateAndUpdatePayment(paymentObject):
        billObject = paymentObject.bill
        if billObject.amountExactness == "EXACT":
            if billObject.billPaidFully == True:
                raise BillFullyPaidAlreadyException(
                    "Payment received but Bill has been paid in full already. Extra amount will be refunded")

            if paymentObject.amountPaid != billObject.billAmount:
                raise BillExactAmountMismatchException(
                    "Payment received but Bill amount and paid amount dont match")
            else:
                billObject.paidAmount = billObject.billAmount
                billObject.billPaidFully = True
        else:
            billObject.paidAmount += paymentObject.amountPaid
        billObject.save()