import json
from django.views import View
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, request
from django.forms.models import model_to_dict

from .biller import Biller, ExactBiller, ExactUpBiller
from .models import Customer
from .utils import CustomerUtils, PaymentUtils, AuthorizationUtils, BillUtils, Utils
from .responseObjects import ResponseObjects
from .exceptions import BillExactAmountMismatchException, BillFullyPaidAlreadyException, PaymentRefIdAlreadyExists, BillWithBillerIdDoesNotExist
from .restInputValidators import RequestReceiptSerializer, CustomerRequestSerializer
from .billerFactory import BillerFactory

class FetchCustomerBills(View):

    def post(self, request):

        requestHeaders = request.META
        verifyRequestAuth = AuthorizationUtils.validateRequestWithJWT(requestHeaders)
        if verifyRequestAuth: return verifyRequestAuth

        objectIdentifiers = request.body.decode('utf-8')
        if not objectIdentifiers: return HttpResponseBadRequest(b'Reqeust Body is expected to fetch Customer Bills')

        validateJsonInput = Utils.validateObjectInputReqeust(objectIdentifiers)
        if validateJsonInput: return validateJsonInput

        customerSerializer = CustomerRequestSerializer(data=json.loads(objectIdentifiers))
        if customerSerializer.is_valid():
            customerOptional = CustomerUtils().getObject(customerSerializer.validated_data)
        else:
            return HttpResponseBadRequest(json.dumps(customerSerializer.errors))
        
        if customerOptional.is_empty():
            return JsonResponse(status=HttpResponseNotFound.status_code, 
                                data=ResponseObjects.customerNotFoundResponseObject(), 
                                safe=False)

        customerObj = customerOptional.get()
        bills = ExactBiller.getBills(customerObj)
        customerWithBillResponseObject = ResponseObjects.customerFoundWithBillObjects(customerObj, bills)
        return JsonResponse(customerWithBillResponseObject, safe=False)


class FetchReceipt(View):
    
    def post(self, request):

        requestHeaders = request.META
        verifyRequestAuth = AuthorizationUtils.validateRequestWithJWT(requestHeaders)
        if verifyRequestAuth: return verifyRequestAuth

        objectIdentifiers = request.body.decode('utf-8')
        if not objectIdentifiers: return HttpResponseBadRequest(b'Reqeust Body is expected to generate receipt')

        validateJsonInput = Utils.validateObjectInputReqeust(objectIdentifiers)
        if validateJsonInput: return validateJsonInput

        paymentSerializer = RequestReceiptSerializer(data=json.loads(objectIdentifiers))
        if paymentSerializer.is_valid():
            try: paymentObject = PaymentUtils().createObject(paymentSerializer.validated_data)
            except (BillWithBillerIdDoesNotExist, PaymentRefIdAlreadyExists) as e: 
                return HttpResponseBadRequest(e)        
        else:
            return HttpResponseBadRequest(json.dumps(paymentSerializer.errors))

        biller = BillerFactory.getBiller(paymentObject.bill)
        try:
            generatedReceipt = biller.generateReceipt(paymentObject)
        except (BillExactAmountMismatchException, BillFullyPaidAlreadyException) as e:
            return HttpResponse(e)

        receiptResponseObject = ResponseObjects.receiptGeneratedWithBillTemplate(generatedReceipt)
        return JsonResponse(receiptResponseObject, safe=False)

class FetchCustomerDetails(View):

    def get(self, request):

        requestHeaders = request.META
        verifyRequestAuth = AuthorizationUtils.validateRequestWithJWT(requestHeaders)
        if verifyRequestAuth: 
            return verifyRequestAuth

        allCustomerDictObjects = map(lambda c: model_to_dict(c, exclude=["password"]), Customer.objects.all())
        return JsonResponse(list(allCustomerDictObjects), safe=False)