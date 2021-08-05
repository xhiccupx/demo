import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy 
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime
import datetime
from functools import wraps
import pytz

app = Flask(__name__)
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
app.config['SECRET_KEY'] = 'thisissecret'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', "sqlite:///loan.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

IST = pytz.timezone('Asia/Kolkata')

# table for users 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    agent = db.Column(db.Boolean)
    customer = db.Column(db.Boolean)

db.create_all()    

# table for loan requests
class loan_request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # .now(IST).strftime('%Y-%m-%d %H:%M:%S'))
    agent_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now(IST))
    updation_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
    tenure = db.Column(db.Numeric)
    ammount = db.Column(db.Numeric)
    interest = db.Column(db.Numeric)
    emi = db.Column(db.Numeric)
    loan_state = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    rejection_date = db.Column(db.DateTime)
    
db.create_all()

# table for backup
class backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_request_id = db.Column(db.Integer)
    # .now(IST).strftime('%Y-%m-%d %H:%M:%S'))
    agent_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime)
    updation_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
    tenure = db.Column(db.Numeric)
    ammount = db.Column(db.Numeric)
    interest = db.Column(db.Numeric)
    emi = db.Column(db.Numeric)
    loan_state = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    rejection_date = db.Column(db.DateTime)
    
db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256', ])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print(e)
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# get list of users
@app.route('/getallusers', methods=['GET'])
@token_required
def get_all_users(current_user):
    if  not current_user.admin and not current_user.agent:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        if user.admin==True:
            user_data['role'] = 'admin'
        elif user.agent==True:
            user_data['role'] = 'agent' 
        elif user.customer==True:
            user_data['role'] = 'customer'        
        output.append(user_data)

    return jsonify({'users' : output})


# filter users by role
@app.route('/getusers/<filter>', methods=['GET'])
@token_required
def get_users(current_user, filter):
    if  not current_user.admin and not current_user.agent:
        return jsonify({'message' : 'Cannot perform that function!'})

    if filter=="admin":
        users = User.query.filter_by(admin=True).all()
    elif filter=="agent":
        users = User.query.filter_by(agent=True).all()
    elif filter=="customer":
        users = User.query.filter_by(customer=True).all()
    else:
        return jsonify({'message' : 'wrong value of filter entered'})  

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        if user.admin==True:
            user_data['role'] = 'admin'
        elif user.agent==True:
            user_data['role'] = 'agent' 
        elif user.customer==True:
            user_data['role'] = 'customer'        
        output.append(user_data)

    return jsonify({'users' : output})  

# filter users by public id 
@app.route('/getoneuser/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if  not current_user.admin and not current_user.agent :
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    if user.admin==True:
        user_data['role'] = 'admin'
    elif user.agent==True:
        user_data['role'] = 'agent' 
    elif user.customer==True:
        user_data['role'] = 'customer' 
    return jsonify({'user' : user_data})


# create new account
@app.route('/createaccount', methods=['POST'])
def create_user():    
    data = request.get_json()
    if not 'name' in data :
        return jsonify({'message' : 'name is not entered!'})
    if not 'password' in data :
        return jsonify({'message' : 'password is not entered!'})
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False ,agent=False,customer=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})

# make user admin using public id 
@app.route('/makeuseradmin/<public_id>', methods=['PUT'])
@token_required
def promote_user_to_admin(current_user, public_id):
    if  not current_user.admin :
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    user.agent = False
    user.customer = False
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted to admin!'})

# make user agent using public id 
@app.route('/makeuseragent/<public_id>', methods=['PUT'])
@token_required
def promote_user_to_agrent(current_user, public_id):
    if  not current_user.admin :
        return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = False
    user.agent = True
    user.customer = False
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted to agent!'})    

# filter by public id 
@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if  not current_user.admin :
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

# login
@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : str(token)})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

# create loan request
@app.route('/loan_request', methods=['POST'])
@token_required
def loan_req(current_user):
    if not current_user.agent:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.get_json()
    if not 'customer_id' in data :
        return jsonify({'message' : 'customer_id is not entered!'})
    customer = User.query.filter_by(public_id=data['customer_id']).first()
    if not customer :
        return jsonify({'message' : "wrong customer id entered"})
    if not 'ammount' in data :
        return jsonify({'message' : 'ammount is not entered!'})
    if not 'interest' in data :
        return jsonify({'message' : 'interest is not entered!'})
    if not 'tenure' in data :
        return jsonify({'message' : 'tenure is not entered!'})            
    # Reading inputs from user
    p = data['ammount']
    R = data['interest']
    n = data['tenure']

    # Calculating interest rate per month
    r = R/(12*100)

    # Calculating Equated Monthly Installment (EMI)
    emi = p * r * ((1+r)**n)/((1+r)**n - 1)
    
    new_loan_request = loan_request(agent_id=current_user.id, customer_id=customer.id,tenure=data['tenure'], ammount=data['ammount'], interest=data['interest'], emi=emi,loan_state="NEW",customer_name=customer.name)
    db.session.add(new_loan_request)
    db.session.commit()
    last = loan_request.query.order_by(loan_request.id.desc()).first()
    backup_loan_request = backup(loan_request_id=last.id,agent_id=last.agent_id,customer_id=last.customer_id,tenure=last.tenure, ammount=last.ammount, interest=last.interest, emi=last.emi,loan_state=last.loan_state,customer_name=last.customer_name,creation_date=last.creation_date,updation_date=last.updation_date,approval_date=last.approval_date,rejection_date=last.rejection_date)
    db.session.add(backup_loan_request)
    db.session.commit()


    return jsonify({'message' : "Loan Request Created!"})  

# get all loan requests
@app.route('/get_loan_requests', methods=['GET'])  
@token_required
def get_loan_requests(current_user): 
    if current_user.admin:
        loans = loan_request.query.all()
    elif current_user.agent:
        loans = loan_request.query.filter_by(agent_id=current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(customer_id=current_user.id).all() 
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})    
    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output})

# filter by loan state
@app.route('/get_loan_requests_bystatus/<filter>', methods=['GET'])
@token_required
def get_loan_requests_bystatus(current_user, filter):
    if current_user.admin:
        loans = loan_request.query.filter_by(loan_state=filter).all()
    elif current_user.agent:
        loans = loan_request.query.filter_by(loan_state=filter,agent_id=current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(loan_state=filter,customer_id=current_user.id).all()
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})

    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output})          

# filter by creation date
@app.route('/get_loan_requests_bydateofcreation/<yyyy>/<mm>/<dd>', methods=['GET'])
@token_required
def get_loan_requests_bydateofcreation(current_user, yyyy,mm,dd):
    date = datetime.datetime(int(yyyy),int(mm),int(dd))
    nextday = date+datetime.timedelta(days=1)
    if current_user.admin:
        loans = loan_request.query.filter(loan_request.creation_date >= date , loan_request.creation_date < nextday).all()
    elif current_user.agent:
        loans = loan_request.query.filter(loan_request.creation_date >= date , loan_request.creation_date < nextday , loan_request.agent_id==current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(loan_request.creation_date >= date , loan_request.creation_date < nextday , loan_request.customer_id==current_user.id).all()
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})

    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output}) 

# filter by updation date
@app.route('/get_loan_requests_bydateofupdation/<yyyy>/<mm>/<dd>', methods=['GET'])
@token_required
def get_loan_requests_bydateofupdation(current_user, yyyy,mm,dd):
    date = datetime.datetime(int(yyyy),int(mm),int(dd))
    nextday = date+datetime.timedelta(days=1)
    if current_user.admin:
        loans = loan_request.query.filter(loan_request.updation_date >= date , loan_request.updation_date < nextday).all()
    elif current_user.agent:
        loans = loan_request.query.filter(loan_request.updation_date >= date , loan_request.updation_date < nextday , loan_request.agent_id==current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(loan_request.updation_date >= date , loan_request.updation_date < nextday , loan_request.customer_id==current_user.id).all()
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})

    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output})

# filter by approval date
@app.route('/get_loan_requests_bydateofapproval/<yyyy>/<mm>/<dd>', methods=['GET'])
@token_required
def get_loan_requests_bydateofapproval(current_user, yyyy,mm,dd):
    date = datetime.datetime(int(yyyy),int(mm),int(dd))
    nextday = date+datetime.timedelta(days=1)
    if current_user.admin:
        loans = loan_request.query.filter(loan_request.approval_date >= date , loan_request.approval_date < nextday).all()
    elif current_user.agent:
        loans = loan_request.query.filter(loan_request.approval_date >= date , loan_request.approval_date < nextday , loan_request.agent_id==current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(loan_request.approval_date >= date , loan_request.approval_date < nextday , loan_request.customer_id==current_user.id).all()
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})

    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output})

# filter by approval date
@app.route('/get_loan_requests_bydateofrejection/<yyyy>/<mm>/<dd>', methods=['GET'])
@token_required
def get_loan_requests_bydateofrejection(current_user, yyyy,mm,dd):
    date = datetime.datetime(int(yyyy),int(mm),int(dd))
    nextday = date+datetime.timedelta(days=1)
    if current_user.admin:
        loans = loan_request.query.filter(loan_request.rejection_date >= date , loan_request.rejection_date < nextday).all()
    elif current_user.agent:
        loans = loan_request.query.filter(loan_request.rejection_date >= date , loan_request.rejection_date < nextday , loan_request.agent_id==current_user.id).all()
    elif current_user.customer:
        loans = loan_request.query.filter_by(loan_request.rejection_date >= date , loan_request.rejection_date < nextday , loan_request.customer_id==current_user.id).all()
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})

    output = []
    for loan in loans:
        loan_data = {}
        loan_data['loan_id'] = loan.id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'loan_requests' : output})    

#get_pirticular_loan_request using loan id 
@app.route('/get_one_loan_request/<loan_id>', methods=['GET'])  
@token_required
def get_one_loan_requests(current_user, loan_id): 
    if current_user.admin:
        loan = loan_request.query.filter_by(id=loan_id).first()
    elif current_user.agent:
        loan = loan_request.query.filter_by(id=loan_id,agent_id=current_user.id).first()
    elif current_user.customer:
        loan = loan_request.query.filter_by(id=loan_id,customer_id=current_user.id).first() 
    if not loan:
        return jsonify({'message' : 'No loan_request found!'})
    loan_data = {}
    loan_data['id'] = loan.id
    loan_data['creation_date'] = loan.creation_date
    if(loan.updation_date != None):
        loan_data['updation_date'] = loan.updation_date
    if(loan.approval_date != None):
        loan_data['approval_date'] = loan.approval_date
    if(loan.rejection_date != None):    
        loan_data['rejection_date'] = loan.rejection_date
    loan_data['customer_name'] = loan.customer_name
    loan_data['ammount'] = str(round(loan.ammount))+"rupees"
    loan_data['interest'] = str(round(loan.interest,2))+"%"
    loan_data['tenure'] = str(round(loan.tenure))+"months"
    loan_data['emi'] = str(round(loan.emi,2))+"rupees"
    loan_data['loan_state'] = loan.loan_state
    
    return jsonify(loan_data)       

# modify_loan_request using loan id 
@app.route('/modify_loan_request/<loan_id>', methods=['POST'])
@token_required
def mod_loan_req(current_user, loan_id):
    if not current_user.agent:
        return jsonify({'message' : 'Cannot perform that function!'})
    loan = loan_request.query.filter_by(id=loan_id,agent_id=current_user.id).first()
    if not loan:
        return jsonify({'message' : 'No loan_request found!'}) 
    if loan.loan_state == "REJECTED" :
        return jsonify({'message' : 'Rejected loan requests cannot be modified'})  
    if loan.loan_state == "APPROVED" :
        return jsonify({'message' : 'Approved loan requests cannot be modified'})  
             
    data = request.get_json()
    # Reading inputs from user
    if 'ammount' in data:
        p = float(data['ammount'])
        loan.ammount = p
    else:    
        p = float(loan.ammount)
        
    if 'interest' in data:
        R = float(data['interest'])
        loan.interest = R
    else:    
        R = float(loan.interest)

    if 'tenure' in data:
        n = float(data['tenure'])
        loan.tenure = n
    else:    
        n = float(loan.tenure)       
    print("R=",R)
    print("p=",p)
    print("n=",n)
    # Calculating interest rate per month
    r = R/(12*100)

    # Calculating Equated Monthly Installment (EMI)
    emi = p * r * ((1+r)**n)/((1+r)**n - 1)
    loan.emi = emi
    loan.updation_date = datetime.datetime.now(IST)
    db.session.commit()
    last = loan_request.query.filter_by(id=loan_id).first()
    backup_loan_request = backup(loan_request_id=last.id,agent_id=last.agent_id,customer_id=last.customer_id,tenure=last.tenure, ammount=last.ammount, interest=last.interest, emi=last.emi,loan_state=last.loan_state,customer_name=last.customer_name,creation_date=last.creation_date,updation_date=last.updation_date,approval_date=last.approval_date,rejection_date=last.rejection_date)
    db.session.add(backup_loan_request)
    db.session.commit()
    return jsonify({'message' : "Loan Request Modified!"})  

# approval using loan id
@app.route('/approve_loan_request/<loan_id>', methods=['PUT'])
@token_required
def approve_loan(current_user, loan_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    loan = loan_request.query.filter_by(id=loan_id).first()
    if not loan:
        return jsonify({'message' : 'No loan_request found!'})  
    if loan.loan_state == "APPROVED" :
        return jsonify({'message' : 'Loan Was Already Approved!'})      

    loan.loan_state = "APPROVED"
    loan.approval_date = datetime.datetime.now(IST)
    db.session.commit()
    last = loan_request.query.filter_by(id=loan_id).first()
    backup_loan_request = backup(loan_request_id=last.id,agent_id=last.agent_id,customer_id=last.customer_id,tenure=last.tenure, ammount=last.ammount, interest=last.interest, emi=last.emi,loan_state=last.loan_state,customer_name=last.customer_name,creation_date=last.creation_date,updation_date=last.updation_date,approval_date=last.approval_date,rejection_date=last.rejection_date)
    db.session.add(backup_loan_request)
    db.session.commit()

    return jsonify({'message' : 'Loan Request Approved!'})    

# reject using loan id 
@app.route('/reject_loan_request/<loan_id>', methods=['PUT'])
@token_required
def reject_loan(current_user, loan_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    loan = loan_request.query.filter_by(id=loan_id).first()
    if not loan:
        return jsonify({'message' : 'No loan_request found!'})  
    if loan.loan_state == "REJECTED" :
        return jsonify({'message' : 'Loan Was Already Rejected!'})  
     
    loan.loan_state = "REJECTED"
    loan.rejection_date = datetime.datetime.now(IST)
    db.session.commit()
    last = loan_request.query.filter_by(id=loan_id).first()
    backup_loan_request = backup(loan_request_id=last.id,agent_id=last.agent_id,customer_id=last.customer_id,tenure=last.tenure, ammount=last.ammount, interest=last.interest, emi=last.emi,loan_state=last.loan_state,customer_name=last.customer_name,creation_date=last.creation_date,updation_date=last.updation_date,approval_date=last.approval_date,rejection_date=last.rejection_date)
    db.session.add(backup_loan_request)
    db.session.commit()

    return jsonify({'message' : 'Loan Request Rejected!'})   

# dalete a loan request using loan id 
@app.route('/loan_request/<loan_id>', methods=['DELETE'])
@token_required
def delete_loan(current_user, loan_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    loan = loan_request.query.filter_by(id=loan_id).first()

    if not loan:
        return jsonify({'message' : 'No loan_request found!'})

    db.session.delete(loan)
    db.session.commit()

    return jsonify({'message' : 'Loan Request Deleted!'}) 

# get_backup using loan id 
@app.route('/get_backup/<loan_id>', methods=['GET'])  
@token_required
def get_backup(current_user, loan_id): 
    if current_user.admin:
        loans = backup.query.filter_by(loan_request_id=loan_id).all()
    elif current_user.agent:
        loans = backup.query.filter_by(loan_request_id=loan_id,agent_id=current_user.id).all()
    elif current_user.customer:
        loans = backup.query.filter_by(loan_request_id=loan_id,customer_id=current_user.id).all() 
    if not loans:
        return jsonify({'message' : 'No loan_request found!'})    
    output = []
    for loan in loans:
        loan_data = {}
        loan_data["backup_id"] = loan.id
        loan_data['loan_id'] = loan.loan_request_id
        loan_data['creation_date'] = loan.creation_date
        if(loan.updation_date != None):
            loan_data['updation_date'] = loan.updation_date
        if(loan.approval_date != None):
            loan_data['approval_date'] = loan.approval_date
        if(loan.rejection_date != None):    
            loan_data['rejection_date'] = loan.rejection_date
        loan_data['customer_name'] = loan.customer_name
        loan_data['ammount'] = str(round(loan.ammount))+"rupees"
        loan_data['interest'] = str(round(loan.interest,2))+"%"
        loan_data['tenure'] = str(round(loan.tenure))+"months"
        loan_data['emi'] = str(round(loan.emi,2))+"rupees"
        loan_data['loan_state'] = loan.loan_state
        output.append(loan_data)

    return jsonify({'backup' : output})

# restore from backup using loan id 
@app.route('/restore/<loan_id>', methods=['PUT'])
@token_required
def restore(current_user,loan_id):
    if not current_user.agent:
        return jsonify({'message' : 'Cannot perform that function!'})
    back = backup.query.filter_by(loan_request_id=loan_id).first()
    if not back:
        return jsonify({'message' : 'No loan_request found!'}) 
    loan = loan_request.query.filter_by(id=loan_id).first()
    if loan.loan_state == 'APPROVED':
        return jsonify({'message' : 'cannot be restored because loan has been Approved!'})
    if loan.loan_state == 'REJECTED':
        return jsonify({'message' : 'cannot be restored because loan has been Rejected!'})
    loan.agent_id=back.agent_id
    loan.customer_id=back.customer_id
    loan.tenure=back.tenure
    loan.ammount=back.ammount
    loan.interest=back.interest
    loan.emi=back.emi
    loan.loan_state=back.loan_state
    loan.customer_name=back.customer_name
    loan.creation_date=back.creation_date
    loan.updation_date=back.updation_date
    loan.approval_date=back.approval_date
    loan.rejection_date=back.rejection_date
    db.session.commit()  
    last = loan_request.query.filter_by(id=back.loan_request_id).first()
    backup_loan_request = backup(loan_request_id=last.id,agent_id=last.agent_id,customer_id=last.customer_id,tenure=last.tenure, ammount=last.ammount, interest=last.interest, emi=last.emi,loan_state=last.loan_state,customer_name=last.customer_name,creation_date=last.creation_date,updation_date=last.updation_date,approval_date=last.approval_date,rejection_date=last.rejection_date)
    db.session.add(backup_loan_request)
    db.session.commit()

    return jsonify({'message' : 'Restored form Backup!'})

if __name__ == '__main__':
    app.run(debug=True)