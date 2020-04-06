import django
from django.conf import settings
import os, random
from faker import Faker
from faker.providers import bank, date_time
from datetime import tzinfo

os.environ['DJANGO_SETTINGS_MODULE'] = 'billerProject.settings'
django.setup()

from billerRecieptAPI.models import Customer, CustomerAccount, Bill, Receipt
from django.utils import timezone

fake = Faker()
fake.add_provider(bank)
fake.add_provider(date_time)

for i in range(50):
    customer = Customer(name=fake.name(), 
                        mobileNumber=fake.random_int(5000000000, 9999999999), 
                        email=fake.email(),
                        userName=fake.user_name(),
                        password=fake.password(length=40, special_chars=False, upper_case=False))

    customer.save()
    
    for i in range(5):
        account = CustomerAccount(customer=customer,
                                id=fake.bban(),
                                accountDesc=fake.text())

        account.save()

        bill = Bill(billerBillID=fake.random_int(100000000000, 999999999999),
                    generatedOn=fake.date_time_this_month(tzinfo=timezone.get_current_timezone()),
                    recurrence=random.choice(["ONE_TIME",]),
                    amountExactness=random.choice(["EXACT",]),
                    customerAccount=account,
                    billAmount=fake.random_int(10, 1000000))

        bill.save()
        