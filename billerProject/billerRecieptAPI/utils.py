import typing, optional
import json, yaml, jwt, datetime

from abc import ABC, abstractmethod
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from .models import Customer, Bill, Payment
from .exceptions import PaymentRefIdAlreadyExists, BillWithBillerIdDoesNotExist

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

# Common methods
class Utils(ABC):

    objectOfDBModel = models.Model
    setOfParamsToBePresent: set

    def getObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
        searchParameters = self.getObjectSearchParameters(objectIdentifiers)
        try: objectOfModel = self.objectOfDBModel.objects.get(**searchParameters)
        except ObjectDoesNotExist: return optional.Optional.empty()

        return optional.Optional.of(objectOfModel)

    @staticmethod
    def validateObjectInputReqeust(requestBody:str) -> typing.Optional[HttpResponse]:

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
        return requestBody

class PaymentUtils(Utils):

    objectOfDBModel = Payment

    def createObject(self, objectIdentifiers: str) -> typing.Optional[models.Model]:
        paymentIdentifier = objectIdentifiers.get("paymentDetails")

        bill = BillUtils().getObject({"billerBillID":objectIdentifiers['billerBillID']}).get_or_raise(BillWithBillerIdDoesNotExist("Invalid Bill Id provided"))
        platformBillID = objectIdentifiers.get("platformBillID")

        paymentParameters = self.flattenPaymentDetailsParameter(paymentIdentifier)
        try:
            objectOfModel = self.objectOfDBModel.objects.create(bill=bill, 
                    platformBillID=platformBillID, **paymentParameters)
        except IntegrityError:
            raise PaymentRefIdAlreadyExists(
                        f"payment ref {paymentParameters.get('uniquePaymentRefID')} already exists")

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
        token = requestHeaders.get("HTTP_X_AUTHORIZATION")
        if not token:
            return HttpResponseUnauthorized(b'X-Authorization header is expected')
        
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
        if ((datetime.datetime.utcnow() - tokenGeneratedOn).total_seconds() // 60) >= creds.get('keyTimeOut'):
            return HttpResponseUnauthorized(b'Authorization token has expired')

    @staticmethod
    def _getJWTCredentials(customerName: str) -> dict:
        with open(AuthorizationUtils.authorizationConfigFile, 'r') as stream:
            try:
                content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

        return optional.Optional.of(content.get(customerName))