import json
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, request
from django.views import View
from django.forms.models import model_to_dict

from .biller import Biller
from .models import Customer
from .utils import CustomerUtils, PaymentUtils, AuthorizationUtils, BillUtils
from .responseObjects import ResponseObjects
from .exceptions import ObjectNotPresentException

# Create your views here.
class FetchCustomerBills(View):

    def post(self, request):

        requestHeaders = request.headers
        customerIdentifiers = request.body.decode('utf-8')

        customerUtils = CustomerUtils()
        if (verifyRequestAuth := AuthorizationUtils._validateRequestWithJWT(requestHeaders)) \
            or (validationResult := customerUtils.validateObjectInputReqeust(customerIdentifiers)):
            return verifyRequestAuth if verifyRequestAuth else validationResult

        customerOptional = customerUtils.getObject(customerIdentifiers)
        
        if customerOptional.is_empty():
            return JsonResponse(status=HttpResponseNotFound.status_code, 
                                data=ResponseObjects.customerNotFoundResponseObject(), 
                                safe=False)

        customerObj = customerOptional.get()
        bills = Biller.getBills(customerObj)
        customerWithBillResponseObject = ResponseObjects.customerFoundWithBillObjects(customerObj, bills)
        return JsonResponse(customerWithBillResponseObject, safe=False)


class FetchReceipt(View):
    
    def post(self, request):
        
        requestHeaders = request.headers
        paymentIdentifiers = request.body.decode('utf-8')

        paymentUtils = PaymentUtils()
        if (verifyRequestAuth := AuthorizationUtils._validateRequestWithJWT(requestHeaders)) \
            or (validationResult := paymentUtils.validateObjectInputReqeust(paymentIdentifiers)):
            return verifyRequestAuth if verifyRequestAuth else validationResult

        paymentObject = paymentUtils.createObject(paymentIdentifiers)

        try:
            generatedReceipt = Biller.generateReceipt(paymentObject)
        except ObjectNotPresentException:
            return HttpResponseBadRequest(b'Incorrect bill details. Bill is not present in system')
        return JsonResponse(paymentObject.uniquePaymentRefID, safe=False)