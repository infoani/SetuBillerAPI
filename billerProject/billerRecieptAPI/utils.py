from abc import ABC, abstractmethod
import json, yaml, jwt, datetime
import typing, optional
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist

from .models import Customer, Bill, Payment

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

# Common methods
class Utils(ABC):

    objectOfDBModel = models.Model
    setOfParamsToBePresent: set

    def getObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
        searchParameters = self.getObjectSearchParameters(objectIdentifiers)
        try:
            objectOfModel = self.objectOfDBModel.objects.get(**searchParameters)
        except ObjectDoesNotExist:
            objectOfModel = None

        return optional.Optional.of(objectOfModel)

    def validateObjectInputReqeust(self, requestBody:str) -> typing.Optional[HttpResponse]:

        if not requestBody: return HttpResponseBadRequest(b'No request body is provided')
        try:
            requestParameterDict = json.loads(requestBody)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(b'Invalid request body. Unable to parse')

        if set(requestParameterDict) != self.setOfParamsToBePresent:
            return HttpResponseBadRequest(b'Incorrect request body parameters')

    @abstractmethod
    def getObjectSearchParameters(self, objectIdentifiers):
        pass


class CustomerUtils(Utils):

    objectOfDBModel = Customer
    setOfParamsToBePresent = {"customerIdentifiers", }

    def getObjectSearchParameters(self, requestBody: str) -> dict:
        requestParameterDict = json.loads(requestBody)
        return {attr['attributeName']:attr['attributeValue'] 
                for attr in requestParameterDict.get("customerIdentifiers")}


class BillUtils(Utils):

    objectOfDBModel = Bill
    setOfParamsToBePresent = {"billerBillID", }

    def getObjectSearchParameters(self, requestBody: str) -> dict:
        return json.loads(requestBody)

class PaymentUtils(Utils):

    objectOfDBModel = Payment
    setOfParamsToBePresent = {"billerBillID", "platformBillID", "paymentDetails",}
    # setOfParamsToBePresent = {"platformTransactionRefID", "uniquePaymentRefID", "amountPaid",}

    def createObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
        objectIdentifierDict = json.loads(objectIdentifiers)
        paymentIdentifier = objectIdentifierDict.get("paymentDetails")
        bill = Bill.objects.get(billerBillID=objectIdentifierDict['billerBillID'])
        platformBillID = objectIdentifierDict.get("platformBillID")

        objectOfModel, created = self.objectOfDBModel.objects.get_or_create(bill=bill, 
                platformBillID=platformBillID, **self.flattenPaymentDetailsParameter(paymentIdentifier))
        return objectOfModel

    def flattenPaymentDetailsParameter(self, paymentDetailsObject: dict) -> dict:
        paymentDetailsObject["amountPaid"] = paymentDetailsObject["amountPaid"].get("value")
        paymentDetailsObject["billAmount"] = paymentDetailsObject["billAmount"].get("value")
        return paymentDetailsObject

    def getObjectSearchParameters(self, objectIdentifiers):
        return json.loads(objectIdentifiers)

# class PaymentUtilsj(Utils):

#     setOfParamsToBePresent = {"billerBillID", "platformBillID", "paymentDetails",}
#     setOfPaymentDetailsObject = {"platformTransactionRefID", "uniquePaymentRefID", "amountPaid", "billAmount"}

#     def __init__(self, **kwargs):
#         self.billerBillID = kwargs.get("billerBillID")
#         self.platformBillID = kwargs.get("platformBillID")
#         self.paymentDetails = kwargs.get("paymentDetails")

#     @classmethod
#     def getPaymentObject(cls, searchParameters):
#         return cls(**searchParameters)

#     def getObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
#         searchParameters = self.getObjectSearchParameters(objectIdentifiers)
#         try:
#             objectOfModel = PaymentUtils.getPaymentObject(searchParameters)
#         except ObjectDoesNotExist:
#             objectOfModel = None

#         return optional.Optional.of(objectOfModel)

#     def getObjectSearchParameters(self, requestBody: str) -> dict:
#         requestParameterDict = json.loads(requestBody)
#         return requestParameterDict

#     def validateObjectInputReqeust(self, requestBody:str) -> typing.Optional[HttpResponse]:
#         super().validateObjectInputReqeust(requestBody)

#         # extra efforts to validate paymentDetails object   
#         paymentDetails = json.loads(requestBody)
#         paymentDetailsObject = paymentDetails.get("paymentDetails")
#         if not (paymentDetailsObject \
#             and set(paymentDetailsObject) == self.setOfPaymentDetailsObject):
#             return HttpResponseBadRequest(b'Incorrect request body parameters in paymentDetails')


class AuthorizationUtils:
    authorizationConfigFile = "config.yml"

    @staticmethod
    def _validateRequestWithJWT(requestHeaders):
        if not (token := requestHeaders.get("Authorization")):
            return HttpResponseUnauthorized(b'No Authorization header is provided')
        
        credentialOptional = AuthorizationUtils._getJWTCredentials("setu")
        if credentialOptional.is_empty():
            return HttpResponseBadRequest(b'Internal Server Error')

        creds = credentialOptional.get()
        try:
            payloadData =  jwt.decode(token.replace("Bearer ", ""), 
                                        creds.get('secretKey'), audience=creds.get('aud'))
        except jwt.PyJWTError:
            return HttpResponseUnauthorized(b'Authorization token in invalid')

        tokenGeneratedOn = datetime.datetime.utcfromtimestamp(payloadData.get('iat'))
        if ((datetime.datetime.utcnow() - tokenGeneratedOn).total_seconds() // 60) >= 20:
            return HttpResponseUnauthorized(b'Authorization token has expired')

    @staticmethod
    def _getJWTCredentials(customerName: str) -> dict:
        with open(AuthorizationUtils.authorizationConfigFile, 'r') as stream:
            try:
                content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

        return optional.Optional.of(content.get(customerName))