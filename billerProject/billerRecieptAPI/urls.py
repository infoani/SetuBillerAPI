from django.urls import path
from .views import FetchCustomerBills, FetchReceipt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('fetchCustomerBills', csrf_exempt(FetchCustomerBills.as_view()), name='fetchCustomerBills'),
    path('fetchReceipt', csrf_exempt(FetchReceipt.as_view()), name='fetchReceipt')
]