## Connection Details
uri: setuBiller.eba-zrcj9xr2.us-west-2.elasticbeanstalk.com
schemeId: 79d338d8-7504-11ea-ab9f-a483e70125e7
secret: e6ffdca7-1744-48c4-a71f-0edcc05839e6
git: https://github.com/infoani/SetuBillerAPI

## Mock Data
Random data has been generated and stored in DB for 100 customers for testing purpose.
*/bills/fetchCustomers* end point has been implemented with auth just to get any customer details for testing purpose.

**Due to shortage of time I have only implemented "ONE_TIME" and "EXACT" type of bills as mentioned in https://docs.setu.co/biller-quickstart. Having said that I've kept the provision to extend them further with any other billing implimentations.**

## Design Decision: 
1. Payments are accepted as is since they come from an another system. Only parameter validation is performed.
2. For exact payment the receipt is only generated if the payment amount exactly matches the bill amount. 
3. Although the receipt is not generated but the payment is recorded into the system. So another payment with the same id would fail even if the earlier payment didn't generate a receipt.
4. Payment if registered but receipt is not generated, these cases can be tracked from the database to process refunds.

I have run my code against the test cases from Postman collection. They are passing as expected.