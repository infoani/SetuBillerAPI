class ObjectNotPresentException(Exception):
    
    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"ObjectNotPresentException({self._m})"

class BillWithBillerIdDoesNotExist(Exception):

    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"BillWithBillerIdDoesNotExist({self._m})"

class BillExactAmountMismatchException(Exception):
    
    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"BillExactAmountMismatchException({self._m})"
    
class BillFullyPaidAlreadyException(Exception):
    
    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"BillFullyPaidAlreadyException({self._m})"

class PaymentRefIdAlreadyExists(Exception):

    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"PaymentRefIdAlreadyExists({self._m})"