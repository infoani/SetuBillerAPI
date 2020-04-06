from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Bill, Receipt, Customer, Payment
from .utils import PaymentUtils
from .exceptions import BillExactAmountMismatchException, BillFullyPaidAlreadyException
from django.db.models.functions import datetime
from django.utils import timezone

class Biller(ABC):

    @staticmethod
    @abstractmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()
        return [bill for account in customerAccounts 
                for bill in account.bills.all() if not bill.billPaidFully]

    def generateReceipt(self, paymentObject: Payment) -> dict:
        self.validateAndUpdatePayment(paymentObject)
        receipt = Receipt.objects.create(
            generatedOn=datetime.datetime.now(tz=timezone.get_current_timezone()), 
                                                bill=paymentObject.bill, 
                                                payment=paymentObject, 
                                                receiptAmount=paymentObject.amountPaid)
        paymentObject.receiptGenerated = True
        paymentObject.save()
        return receipt
    
    @abstractmethod
    def validateAndUpdatePayment(self, paymentObject):
        pass


class ExactBiller(Biller):

    @staticmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()
        return [bill for account in customerAccounts 
                for bill in account.bills.all() if not bill.billPaidFully and bill.amountExactness == "EXACT"]
    
    def validateAndUpdatePayment(self, paymentObject):
        super().validateAndUpdatePayment(paymentObject)
        billObject = paymentObject.bill
        if billObject.billPaidFully == True:
            raise BillFullyPaidAlreadyException(
                "Payment received but Bill has been paid in full already. Extra amount will be refunded")

        if paymentObject.amountPaid != billObject.billAmount:
            raise BillExactAmountMismatchException(
                "Payment received but Bill amount and paid amount dont match")
        else:
            billObject.paidAmount = billObject.billAmount
            billObject.billPaidFully = True

        billObject.save()

class ExactUpBiller(Biller):
    
    @staticmethod
    def getBills(customer: Customer) -> List[Bill]:
        customerAccounts = customer.accounts.all()
        return [bill for account in customerAccounts 
                for bill in account.bills.all() if not bill.billPaidFully and bill.amountExactness == "EXACT_UP"]

    def validateAndUpdatePayment(self, paymentObject):
        super().validateAndUpdatePayment(paymentObject)
        raise BillExactAmountMismatchException(
                "Exact Up called")