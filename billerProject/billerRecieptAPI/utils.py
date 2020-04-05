import typing, optional
import json, yaml, jwt, datetime

from abc import ABC, abstractmethod
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

    @abstractmethod
    def getObjectSearchParameters(self, objectIdentifiers):
        pass


class CustomerUtils(Utils):

    objectOfDBModel = Customer

    def getObjectSearchParameters(self, requestBody: str) -> dict:
        requestParameterDict = requestBody
        return {attr['attributeName']:attr['attributeValue'] 
                for attr in requestParameterDict.get("customerIdentifiers")}


class BillUtils(Utils):

    objectOfDBModel = Bill

    def getObjectSearchParameters(self, requestBody: str) -> dict:
        return json.loads(requestBody)

class PaymentUtils(Utils):

    objectOfDBModel = Payment

    def createObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
        paymentIdentifier = objectIdentifiers.get("paymentDetails")
        bill = Bill.objects.get(billerBillID=objectIdentifiers['billerBillID'])
        platformBillID = objectIdentifiers.get("platformBillID")

        paymentParameters = self.flattenPaymentDetailsParameter(paymentIdentifier)
        try:
            objectOfModel = self.objectOfDBModel.objects.get(
                uniquePaymentRefID=paymentParameters.get('uniquePaymentRefID'))
        except ObjectDoesNotExist:
            objectOfModel = self.objectOfDBModel.objects.create(bill=bill, 
                platformBillID=platformBillID, **paymentParameters)

        return objectOfModel

    def flattenPaymentDetailsParameter(self, paymentDetailsObject: dict) -> dict:
        paymentDetailsObject["amountPaid"] = paymentDetailsObject["amountPaid"]['value']
        paymentDetailsObject["billAmount"] = paymentDetailsObject["billAmount"]['value']
        return paymentDetailsObject

    def getObjectSearchParameters(self, objectIdentifiers):
        return json.loads(objectIdentifiers)
        

class AuthorizationUtils:
    authorizationConfigFile = "config.yml"

    @staticmethod
    def validateRequestWithJWT(requestHeaders):
        token = requestHeaders.get("HTTP_AUTHORIZATION")
        if not token:
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
        if ((datetime.datetime.utcnow() - tokenGeneratedOn).total_seconds() // 60) >= 200:
            return HttpResponseUnauthorized(b'Authorization token has expired')

    @staticmethod
    def _getJWTCredentials(customerName: str) -> dict:
        with open(AuthorizationUtils.authorizationConfigFile, 'r') as stream:
            try:
                content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

        return optional.Optional.of(content.get(customerName))