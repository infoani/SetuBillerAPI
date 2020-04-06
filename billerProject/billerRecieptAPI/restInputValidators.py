from rest_framework import serializers
from .models import Customer
import re

# verify Customer Search input for fetchCustomerBills API
class AttributeSerializer(serializers.Serializer):
    attributeName = serializers.CharField(required=True)
    attributeValue = serializers.CharField(required=True)

    def validate_attributeName(self, attributeName):
        self._hasMobile = False
        choices = [f.name for f in Customer._meta.get_fields() if f.name not in ['accounts', 'password']]
        if attributeName not in choices:
            raise serializers.ValidationError(f"Invalid attributeName <{attributeName}>. Choices are {choices}")
        if attributeName == "mobileNumber": self._hasMobile = True
        return attributeName
             
    def validate_attributeValue(self, attributeValue):
        if self._hasMobile:
            matchObject = re.match(r"^\+?(0|91)?([5-9][0-9]{9})$", attributeValue)
            if matchObject: return matchObject.group(2)
            else: raise serializers.ValidationError("Invalid <mobileNumber>. Only numeric values upto 10 digits, starting [5-9] are accepted. Optional country code +91/91/0 is accepted")
        return attributeValue
            

class CustomerRequestSerializer(serializers.Serializer):
    customerIdentifiers = serializers.ListField(child=AttributeSerializer())


# verify bill payment inputs for fetchReceipt API
class ValueSerializer(serializers.Serializer):
    value = serializers.FloatField(required=True)

class PaymentSerializer(serializers.Serializer):
    platformTransactionRefID = serializers.CharField(required=True)
    uniquePaymentRefID = serializers.CharField(required=True)
    amountPaid = ValueSerializer()
    billAmount = ValueSerializer()

class RequestReceiptSerializer(serializers.Serializer):
    billerBillID = serializers.CharField(required=True)
    platformBillID = serializers.CharField(required=True)
    paymentDetails = PaymentSerializer()