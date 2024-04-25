from flask import request, jsonify, make_response
from library.main import app, db
from functools import wraps
import jwt


# users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Invoice(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    date = db.Column(db.DateTime)
    invoiceNumber = db.Column(db.Integer, nullable=False)
    customerName = db.Column(db.String(64), nullable=False)
    billingAddress = db.Column(db.String(128), nullable=False)
    shippingAddress = db.Column(db.String(128), nullable=False)
    gstIn = db.Column(db.String(128))
    totalAmount = db.Column(db.Float, nullable=False)
    items = db.relationship("InvoiceItem", backref="invoice", lazy=True, cascade="all, delete-orphan")
    billSundry = db.relationship("InvoiceBillSundry", backref="invoice", lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    itemName = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.String(64), db.ForeignKey("invoice.id"), nullable=False)

class InvoiceBillSundry(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    billSundryName = db.Column(db.String(64), nullable=False)
    Amount = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.String(64), db.ForeignKey("invoice.id"), nullable=False)




# token decorator 
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # pass jwt-token in headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: # throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return make_response(jsonify({"message": "Invalid token!"}), 401)

        return f(current_user, *args, **kwargs)
    return decorator