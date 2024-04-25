from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from library.main import db, app
from library.models import User, token_required
from library.controller import InvoiceController
from library.validatory import InvoiceValidator

# register route
@app.route('/signup', methods=['POST'])
def signup_user(): 
    data = request.get_json() 
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password, admin=False)
        db.session.add(new_user) 
        db.session.commit() 

        return jsonify({'message': 'registered successfully'}), 201
    else:
        return make_response(jsonify({"message": "User already exists!"}), 409)

# user login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = User.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'public_id': user.public_id}, app.config['SECRET_KEY'], 'HS256')
        return make_response(jsonify({'token': token}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})



@app.route('/invoice/<invoice_id>', methods=['POST'])
@token_required
def create_invoice(current_user, invoice_id):
    data = request.get_json()
    
    validator = InvoiceValidator(invoice_id, data)
    try:
        invoice_data = validator.validateInvoiceRequest()
    except KeyError as e:
        return jsonify({"Message": "Bad request, Value missing: {}".format(e) }), 400
    except ValueError as e:
        return jsonify({"Message": "Bad request, {}".format(e)}), 400

    errors = validator.validateInvoice()
    if len(errors):
        return jsonify({"Message" : "Validation errors in Invoice data", "errors": errors}), 400

    return InvoiceController.create(invoice_id, invoice_data)

@app.route('/invoice/<invoice_id>', methods=['PUT'])
@token_required
def update_invoice(current_user, invoice_id):
    data = request.get_json()

    validator = InvoiceValidator(invoice_id, data)
    try:
        invoice_data = validator.validateInvoiceRequest()
    except KeyError as e:
        return jsonify({"Message": "Bad request, Value missing: {}".format(e) }), 400
    except ValueError as e:
        return jsonify({"Message": "Bad request, {}".format(e)}), 400

    errors = validator.validateInvoice()
    if len(errors):
        return jsonify({"Message" : "Validation errors in Invoice data", "errors": errors}), 400
    
    return InvoiceController.put(invoice_id, invoice_data)

@app.route('/invoice/<invoice_id>', methods=['GET'])
@token_required
def get_invoice(current_user, invoice_id):
    return InvoiceController.get(invoice_id)

@app.route('/invoice/<invoice_id>', methods=['DELETE'])
@token_required
def delete_invoice(current_user, invoice_id):
    return InvoiceController.delete(invoice_id)

@app.route('/invoices/', methods=['GET'])
@token_required
def list_all_invoices(current_user):
    return InvoiceController.listall()