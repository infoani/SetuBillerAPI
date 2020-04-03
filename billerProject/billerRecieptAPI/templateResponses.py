from enum import Enum

class BillFetchStatus(Enum):
    AVAILABLE = "AVAILABLE"
    NO_OUTSTANDING = "NO_OUTSTANDING"

class OverallStatus(Enum):
    SUCCESS = 200
    NOT_FOUND = 404

class BillRecurrance(Enum):
    ONCE = "ONE_TIME"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"

class BillAmountExactness(Enum):
    EXACT = "EXACT"
    INEXACT = "INEXACT"

statusMessageTemplate = {
    "status"  : None,
    "success" : False,
}

customerDataInBillTemplate = {
    "data"   : {
        "customer" : {
            "name" : None
        }
    }
}

billStatusDetailsTemplate = {
    "billDetails" : {
        "billFetchStatus" : None,
        "bills"           : []
    }
}

customerDoesNotExistErrorMessageTemplate = {
    "error" : {
        "code"        : "customer-not-found",
        "title"       : "Customer not found",
        "traceID"     : "",
        "description" : "The requested customer was not found in the biller system.",
        "param"       : "",
        "docURL"      : "",
    }
}

billObjectDetailsTemplate = {
    "billerBillID"    : "12123131322",
    "generatedOn"     : "2019-08-01T08:28:12Z",
    "recurrence"      : "ONE_TIME",
    "amountExactness" : "EXACT",
    "customerAccount" : {
        "id" : "8208021440"
    },
    "aggregates" : {
        "total" : {
            "displayName" : "Total Outstanding",
            "amount" : {
                "value" : 99000
            }
        }
    }
}