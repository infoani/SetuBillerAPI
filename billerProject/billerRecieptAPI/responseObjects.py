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
        customerDataInBillTemplate.get("data").get("customer")["name"] = customerObj.name
        
        billListItems = tuple(map(ResponseObjects._includeBillDetailsInTemplate, billObjects))
        billStatusDetailsTemplate.get("billDetails").update({
            "billFetchStatus" : BillFetchStatus.AVAILABLE.value if billListItems else BillFetchStatus.NO_OUTSTANDING.value,
            "bills" : billListItems
        })
        customerDataInBillTemplate.get("data").update(billStatusDetailsTemplate)
        customerFoundWithBillResponse = dict(**statusMessageTemplate,
                                            **customerDataInBillTemplate,)
        return customerFoundWithBillResponse

    @staticmethod
    def _includeBillDetailsInTemplate(billObject):
        customerAccount = billObject.customerAccount
        billAmount = billObject.billAmount

        billDict = model_to_dict(billObject, exclude=["customerAccount", "billAmount", "paidAmount", "billPaidFully"])
        accountDict = model_to_dict(customerAccount, fields=["id"])
        billDict.update({"customerAccount" : accountDict})

        # current template. Need to change if more action on aggregarte is required
        billDict.setdefault("aggregates", {})['total'] = {
            "displayName": "Total Outstanding", 
            "amount": {
                "value":billAmount
            }
        }

        return billDict

    @staticmethod
    def receiptGeneratedWithBillTemplate(receiptObject):
        statusMessageTemplate["status"] = OverallStatus.SUCCESS.value
        statusMessageTemplate["success"] = True

        receiptGeneratedResponseTemplate["data"]["billerBillID"] = str(receiptObject.bill.billerBillID)
        receiptGeneratedResponseTemplate["data"]["platformBillID"] = receiptObject.payment.platformBillID
        receiptGeneratedResponseTemplate["data"]["platformTransactionRefID"] = receiptObject.payment.platformTransactionRefID
        receiptGeneratedResponseTemplate["data"]["receipt"] = {
            "id": receiptObject.receiptId,
            "date": receiptObject.generatedOn.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        receiptGeneratedResponse = dict(**statusMessageTemplate,
                                            **receiptGeneratedResponseTemplate)
        return receiptGeneratedResponse
