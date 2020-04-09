from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    mobileNumber = models.IntegerField(
        validators=[
            RegexValidator(
                regex=r"(0|91)?[5-9][0-9]{9}",
                message=_("The phone number is not valid")
            ),
        ]
    )
    email = models.CharField(max_length=150)
    userName = models.CharField(max_length=100, primary_key=True, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f"Customer(username:{self.name}, mobile:{self.mobileNumber})"

class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    id = models.CharField(max_length=50, primary_key=True, db_column="accountId")
    accountDesc = models.CharField(max_length=250)

    def __str__(self):
        return f"Account(id:{self.id})"

class Bill(models.Model):
    billerBillID = models.BigIntegerField(primary_key=True)
    generatedOn = models.DateTimeField()
    recurrence = models.CharField(
        max_length=20, 
        choices=[
            ('ONE_TIME', 'ONE_TIME'),
            ('MONTHLY', 'MONTHLY'),
            ('QUARTERLY', 'QUARTERLY'),
            ('ANNUALLY', "ANNUALLY")
        ],
        default='ONE_TIME'
    )
    amountExactness = models.CharField(
        max_length=20,
        choices=[
            ('EXACT', 'EXACT'),
            ('INEXACT', 'INEXACT')
        ],
        default='EXACT'
    )
    customerAccount = models.ForeignKey(CustomerAccount, on_delete=models.DO_NOTHING, related_name='bills')
    billAmount = models.IntegerField(default=0)
    paidAmount = models.IntegerField(default=0)
    billPaidFully = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill(id:{self.billerBillID})"

class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.DO_NOTHING, related_name='bills')
    platformBillID = models.CharField(max_length=100)
    platformTransactionRefID = models.CharField(max_length=100)
    uniquePaymentRefID = models.CharField(primary_key=True, max_length=100)
    amountPaid = models.IntegerField(null=False)
    billAmount = models.IntegerField(default=0)
    receiptGenerated = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment(id:{self.uniquePaymentRefID})"

class Receipt(models.Model):
    receiptId = models.AutoField(primary_key=True)
    generatedOn = models.DateTimeField(default=timezone.now)
    bill = models.ForeignKey(Bill, on_delete=models.DO_NOTHING)
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING)
    receiptAmount = models.IntegerField(null=True)

    def __str__(self):
        return f"Receipt(id:{self.receiptId})"