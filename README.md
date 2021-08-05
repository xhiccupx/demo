# loan-api
# steps to run the code
1.	command : docker build -t flask-loan-api .
2.	command : docker run -d -p 5000:5000 flask-loan-api
3.	Now api is hosted on loaclhost port 5000 you can run the following test cases on postman.
This api is developed using flask as back-end and SQlite database.
listed below are test cases for loan api. Run all the test cases in postman.
# Account creation
*	request type : POST
*	route : /createaccount
*	url: http://localhost:5000/createaccount 
*	following are test cases for account creation.
1.	body(JSON):  {"name":"jef","password":"12345"}
2.	body(JSON):  {"password":"12345"}
3.	body(JSON):  {"name":"jef"}
4.	body(JSON):  {}
note : The passwords will be encrypted and then stored in database. For every account a publc id will be generated using uuid and stored in database.The account created will by default be customer account. Only Admin can promote a user to agent or admin.
# Login
*	request type : GET
*	route : /login
*	url: http://localhost:5000/login
*	In Authorization choose Basic Auth and enter login details.
1.	Username : admin , Password : 12345 
2.	Username : enter wrong user name 
3.	Password : enter wrong password
After logging in successfully a token will be generated which has expiration of 30 minutes.copy the token and create a KEY in headers with name x-access-token and paste the token in the value section of created key. You will be logged in for 30 mins. 
for generating token fwt was used.
there are some accounts i have added you can use it for testing purpose.
# login credentials for admin:
Username : admin , Password : 12345 
# login credentials for agent:
Username : agent1 , Password : 12345 
# login credentials for agent:
Username : customer1 , Password : 12345 
#To get  list of all users
*	 request type : GET
*	route : /getallusers
*	test case
1.	url: http://localhost:5000/getallusers
only admin and agent can get list of users.
login in into all types of accounts(admin,agent and customer) and try this above testcase.
# To get  list of all users filter by role :
*	request type : GET
*	route : /getusers/<filter>
*	testcase
1.	url : http://localhost:5000/getusers/admin
2.	url : http://localhost:5000/getusers/agent
3.	url : http://localhost:5000/getusers/customer
4.	url : http://localhost:5000/getusers/wrongfilter
test all four cases for to filter_by admin, agent, customer and final test case is for wrong filter value.
# To get  one user filter by public id of user :
*	request type : GET
*	route : /getoneuser/<public_id>
*	testcase
*	url : http://localhost:5000/getoneuser/17ddbdb4-0623-45ea-ac20-b47809950b27
*	url : http://localhost:5000/getoneuser/1111111111wrongpublicid1111111111111
try the above test case with correct public id and also with a wrong public id 
# Create loan request : 
*	request type : POST
*	route : /loan_request
*	url : http://localhost:5000/loan_request
*	testcases
1.	body(JSON):  {"customer_id":"17b495b2-efe5-4a92-9bda-b897020c92b1","tenure":12, "ammount":10000, "interest":10} 
2.	body(JSON):  {"customer_id":"6e65ae81-02e9-4944-93ec-95c8d90014e2","tenure":12, "ammount":10000, "interest":10}
3.	body(JSON):  {"customer_id":"6e65ae81-02e9-4944-93ec-95c8d90014e2","tenure":12, "ammount":10000}
4.	body(JSON):  {"tenure":12, "ammount":10000}
5.	body(JSON):  {"tenure":12}
6.	body(JSON):  {}
Note: creation of loan request can only be done by agent . If you try creating loan request by customer or admin account it will give a message called cannot perform that function.
# Modify loan request :
*	request type : POST
*	route : /modify_loan_request/<loan_id>
*	url : http://localhost:5000/modify_loan_request/2
*	testcases
1.	body(JSON):  {"tenure":40, "ammount":300000, "interest":9.8} 
2.	body(JSON):  {"tenure":40, "ammount":300000} 
3.	body(JSON):  {"tenure":40}
4.	body(JSON):  {}
Note : modification of loan request can only be done by agent .If the loan is approved it cannot be modified. If you try modifying loan request by customer or admin account it will give a message called cannot perform that function.
Note : there is a secound table where back up will be stored in case of emergency the past data can be fetched from the backup table. It also helps in tracking the history.
# Approve loan request :
*	request type : PUT
*	route : /approve_loan_request/<loan_id>
*	url : http://localhost:5000/approve_loan_request/1
# Reject loan request :
*	request type : PUT
*	route : /reject_loan_request/<loan_id>
*	url : http://localhost:5000/reject_loan_request/3
Note : This can be done only by admin and if you try to approve or reject already approved or rejected loan request you will get a message saying "already approved" or "already rejected". If you try to approve using agent or customers it output a message saying "Cannot perform that function!".
Try the above test case with wrong loan request id also.
# Get list of all loan requests :
*	request type : GET
*	rounte : /get_loan_requests
*	http://localhost:5000//get_loan_requests
Note : admin can get all loan requests, agent can get requests which only he has created and customer gets loan requests which agent has created for him in particular.
# get loan request filter by loan id :
*	request type : GET
*	route : /get_one_loan_request/<loan_id>
*	http://localhost:5000//get_one_loan_request/1
*	http://localhost:5000//get_one_loan_request/2
*	http://localhost:5000//get_one_loan_request/5
# Get loan request filter by loan status "NEW" or "APPROVED" or"REJECTED":
*	request type : GET
*	route : /get_loan_requests_bystatus/<filter>
*	http://localhost:5000/get_loan_requests_bystatus/NEW
*	http://localhost:5000/get_loan_requests_bystatus/APPROVED
*	http://localhost:5000/get_loan_requests_bystatus/REJECTED
*	http://localhost:5000/get_loan_requests_bystatus/WRONGVALUE
# Get loan request filter by date of creation :
*	request type : GET
*	route : /get_loan_requests_bydateofcreation/<yyyy>/<mm>/<dd>
*	http://localhost:5000/get_loan_requests_bydateofcreation/2021/08/05
*	http://localhost:5000/get_loan_requests_bydateofcreation/2021/08/06
*	http://localhost:5000/get_loan_requests_bydateofcreation/2021/08/07
# Get loan request filter by date of updation :
*	request type : GET
*	route : /get_loan_requests_bydateofupdation/<yyyy>/<mm>/<dd>
*	http://localhost:5000/get_loan_requests_bydateofupdation/2021/08/06
*	http://localhost:5000/get_loan_requests_bydateofupdation/2021/08/07
# Get loan request filter by date of approval :
*	request type : GET
*	route : /get_loan_requests_bydateofapproval/<yyyy>/<mm>/<dd>
*	http://localhost:5000/get_loan_requests_bydateofapproval/2021/08/06
*	http://localhost:5000/get_loan_requests_bydateofapproval/2021/08/07
# Get loan request filter by date of rejection :
*	request type : GET
*	route : /get_loan_requests_bydateofrejection/<yyyy>/<mm>/<dd>
*	http://localhost:5000/get_loan_requests_bydateofrejection/2021/08/05
*	http://localhost:5000/get_loan_requests_bydateofrejection/2021/08/06
# To view back up data or history of a loan request :
*	request type : GET
*	route : /get_backup/<loan_id>
*	url : http://localhost:5000/get_backup/1
*	url : http://localhost:5000/get_backup/3
*	url : http://localhost:5000/get_backup/100
Note: In case the agent has update the loan request and wants to get back the data which was previously stored . He can use restore method .
# To restore :
*	request type : PUT
*	route : /restore/<loan_id>
*	http://localhost:5000/restore/1
*	http://localhost:5000/restore/2
*	http://localhost:5000/restore/3
Note : Approved and Rejected loan requests cannot be restored. 
