from rest_framework import serializers

# verify Customer Search input for fetchCustomerBills API
class AttributeSerializer(serializers.Serializer):
    attributeName = serializers.CharField(required=True)
    attributeValue = serializers.CharField(required=True)

class CustomerRequestSerializer(serializers.Serializer):
    customerIdentifiers = serializers.ListField(child=AttributeSerializer())


# verify bill payment inputs for fetchReceipt API
class ValueSerializer(serializers.Serializer):
    value = serializers.IntegerField(required=True)

class PaymentSerializer(serializers.Serializer):
    platformTransactionRefID = serializers.CharField(required=True)
    uniquePaymentRefID = serializers.CharField(required=True)
    amountPaid = ValueSerializer()
    billAmount = ValueSerializer()

class RequestReceiptSerializer(serializers.Serializer):
    billerBillID = serializers.CharField(required=True)
    platformBillID = serializers.CharField(required=True)
    paymentDetails = PaymentSerializer()