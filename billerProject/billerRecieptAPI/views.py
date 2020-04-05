import json
from django.views import View
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, request

from .biller import Biller
from .models import Customer
from .utils import CustomerUtils, PaymentUtils, AuthorizationUtils, BillUtils
from .responseObjects import ResponseObjects
from .exceptions import BillExactAmountMismatchException, BillFullyPaidAlreadyException
from .restInputValidators import RequestReceiptSerializer, CustomerRequestSerializer

# Create your views here.
class FetchCustomerBills(View):

    def post(self, request):

        requestHeaders = request.META
        customerIdentifiers = request.body.decode('utf-8')

        customerUtils = CustomerUtils()
        verifyRequestAuth = AuthorizationUtils.validateRequestWithJWT(requestHeaders)
        validateJsonInput = customerUtils.validateObjectInputReqeust(customerIdentifiers)
    
        if verifyRequestAuth: return verifyRequestAuth
        if validateJsonInput: return validateJsonInput

        customerSerializer = CustomerRequestSerializer(data=json.loads(customerIdentifiers))
        if customerSerializer.is_valid():
            customerOptional = customerUtils.getObject(customerSerializer.validated_data)
        else:
            return HttpResponseBadRequest(customerSerializer.errors)
        
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
        
        requestHeaders = request.META
        paymentIdentifiers = request.body.decode('utf-8')

        paymentUtils = PaymentUtils()
        verifyRequestAuth = AuthorizationUtils.validateRequestWithJWT(requestHeaders)
        validateJsonInput = paymentUtils.validateObjectInputReqeust(paymentIdentifiers)
    
        if verifyRequestAuth: return verifyRequestAuth
        if validateJsonInput: return validateJsonInput

        paymentSerializer = RequestReceiptSerializer(data=json.loads(paymentIdentifiers))
        if paymentSerializer.is_valid():
            paymentObject = paymentUtils.createObject(paymentSerializer.validated_data)
        else:
            return HttpResponseBadRequest(json.dumps(paymentSerializer.errors))

        try:
            generatedReceipt = Biller.generateReceipt(paymentObject)
        except (BillExactAmountMismatchException, BillFullyPaidAlreadyException) as e:
            return HttpResponseBadRequest(str(e))

        receiptResponseObject = ResponseObjects.receiptGeneratedWithBillTemplate(generatedReceipt)
        return JsonResponse(receiptResponseObject, safe=False)