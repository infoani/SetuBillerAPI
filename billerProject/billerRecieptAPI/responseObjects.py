from .templateResponses import *
from django.forms.models import model_to_dict

class ResponseObjects:

    @staticmethod
    def customerNotFoundResponseObject():
        statusMessageTemplate["status"] = OverallStatus.NOT_FOUND.value
        statusMessageTemplate["success"] = False
        customerNotFoundResponse = dict(**statusMessageTemplate, **customerDoesNotExistErrorMessageTemplate)
        return customerNotFoundResponse

    @staticmethod
    def customerFoundWithBillObjects(customerObj, billObjects):
        statusMessageTemplate["status"] = OverallStatus.SUCCESS.value
        statusMessageTemplate["success"] = True
        customerDataInBillTemplate.get("data").get("customer")["name"] = customerObj.customerName
        
        billListItems = tuple(map(ResponseObjects._includeBillDetailsInTemplate, billObjects))
        billStatusDetailsTemplate.get("billDetails").update({
            "billFetchStatus" : BillFetchStatus.AVAILABLE.value,
            "bills" : billListItems
        })
        customerFoundWithBillResponse = dict(**statusMessageTemplate,
                                            **customerDataInBillTemplate, **billStatusDetailsTemplate)
        return customerFoundWithBillResponse

    @staticmethod
    def _includeBillDetailsInTemplate(billObject):
        customerAccount = billObject.customerAccount
        billAmount = billObject.billAmount

        billDict = model_to_dict(billObject, exclude=["customerAccount", "billAmount"])
        accountDict = model_to_dict(customerAccount, fields=["accountId"])
        billDict.update(accountDict)

        # current template. Need to change if more action on aggregarte is required
        billDict.setdefault("aggregates", {})['total'] = {
            "displayName": "Total Outstanding", 
            "amount": {
                "value":billAmount
            }
        }

        return billDict