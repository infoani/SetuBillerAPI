from .biller import *
from .models import Bill

class BillerFactory:

    @staticmethod
    def getBiller(bill):
        if bill.amountExactness == "EXACT":
            return ExactBiller()
        elif bill.amountExactness == "EXACT_UP":
            return ExactUpBiller()