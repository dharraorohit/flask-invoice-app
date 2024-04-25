from library.models import InvoiceItem, Invoice, InvoiceBillSundry
from library.main import db
from flask import jsonify

class InvoiceController():
    def create(invoice_id, data):
        invoice = Invoice.query.filter_by(id=invoice_id).first()
        if invoice:
            return jsonify({"Message": "Invoice already exists"}), 400
        
        invoice = Invoice(id=invoice_id, invoiceNumber = data["invoiceNumber"], customerName = data["customerName"],\
                          billingAddress = data["billingAddress"], shippingAddress=data["shippingAddress"],\
                            gstIn=data["gstIn"], totalAmount=data["totalAmount"])
        db.session.add(invoice)
        db.session.commit()

        invoice_items = data["invoiceItems"]
        for item in invoice_items:
            invoice_item = InvoiceItem(id = item["id"], itemName = item["itemName"], quantity = item["quantity"],\
                                       price = item["price"], amount = item["amount"], invoice=invoice)
            db.session.add(invoice_item)
            db.session.commit()
        
        for bill in data["billSundry"]:
            bill_sundry = InvoiceBillSundry(id=bill["id"], billSundryName=bill["billSundryName"],\
                                            Amount=bill["amount"], invoice=invoice)
            db.session.add(bill_sundry)
            db.session.commit()

        return jsonify({"Message":"Invoice Creation Success"}), 201
    
    def put(invoice_id, data):
        invoice = Invoice.query.filter_by(id=invoice_id).first()
        if not invoice:
            return jsonify({"Message": "Invoice not found"}), 404
        invoice.invoiceNumber = data["invoiceNumber"]
        invoice.customerName = data["customerName"]
        invoice.billingAddress = data["billingAddress"]
        invoice.shippingAddress= data["shippingAddress"]
        invoice.gstIn= data["gstIn"]
        invoice.totalAmount= data["totalAmount"]

        db.session.commit()

        invoice_items = data["invoiceItems"]
        for item in invoice_items:
            invoice_item = InvoiceItem.query.filter_by(id=item['id']).first()
            if not invoice:
                return jsonify({"Message": "InvoiceItem not found"}), 404
            
            invoice_item.itemName = item["itemName"]
            invoice_item.price = item["price"]
            invoice_item.amount = item["amount"]

            db.session.commit()

        for bill in data["billSundry"]:
            bill_sundry = InvoiceBillSundry.query.filter_by(id=item['id']).first()
            if not invoice:
                return jsonify({"Message": "InvoiceItem not found"}), 404
            
            bill_sundry.billSundryName=bill["billSundryName"]
            bill_sundry.Amount=bill["amount"]

            db.session.commit()

        return jsonify({"Message":"Invoice Updation Success"}), 200

    def get(invoice_id):
        invoice = Invoice.query.filter_by(id=invoice_id).first()

        if not invoice:
            return jsonify({"Message": "Invoice not found"}), 404
        
        return jsonify(get_invoice_dict(invoice)), 200
    
    def delete(invoice_id):
        invoice = Invoice.query.filter_by(id=invoice_id).first()

        if not invoice:
            return jsonify({"Message": "Invoice not found"}), 404

        db.session.delete(invoice)
        db.session.commit()

        return jsonify({"Message": "Invoice delete success"}), 200
    
    def listall():
        invoices = Invoice.query.all()
        invoices_list_data = []
        for invoice in invoices:
            invoices_list_data.append(get_invoice_dict(invoice))

        invoices_data = {
            "invoices_list": invoices_list_data
        }
        return jsonify(invoices_data), 200
    
def get_invoice_dict(invoice):
    invoice_data = {
        "id": invoice.id,
        "invoiceNumber" : invoice.invoiceNumber,
        "customerName" : invoice.customerName,
        "billingAddress" : invoice.billingAddress,
        "shippingAddress" : invoice.shippingAddress,
        "gstIn" : invoice.gstIn,
        "totalAmount" : invoice.totalAmount
    }

    items_data = []
    for invoice_item in invoice.items:
        items_data.append({
            "id": invoice_item.id,
            "itemName" : invoice_item.itemName,
            "price" : invoice_item.price,
            "amount" : invoice_item.amount
        })
    invoice_data["items"] = items_data

    bill_data = []
    for bill in invoice.billSundry:
        bill_data.append({
            "id": bill.id,
            "itemName" : bill.billSundryName,
            "amount" : bill.Amount
        })
    invoice_data["billSundry"] = bill_data
    return invoice_data
