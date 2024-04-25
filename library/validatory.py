from datetime import datetime

class InvoiceValidator():
    def __init__(self, invoice_id, invoice_data):
        self.invoice_data = invoice_data
        self.invoice_id = invoice_id

    def validateInvoiceItem(self, item_data):
        errors = []
        if item_data["amount"] != item_data["quantity"] * item_data["price"]:
            errors.append("Amount mismatch in Invoice Item Id: {}".format(item_data["id"]))
        
        if item_data["amount"] <= 0:
            errors.append("Amount is zero for Invoice Item Id: {}".format(item_data["id"]))

        if item_data["price"] <= 0:
            errors.append("price is zero for Invoice Item Id: {}".format(item_data["id"]))

        if item_data["quantity"] <= 0:
            errors.append("quantity is zero for Invoice Item Id: {}".format(item_data["id"]))

        return errors
    
    def validateInvoice(self):
        invoice_data = self.invoice_data
        invoice_items = invoice_data["invoiceItems"]
        errors = []
        invoices_amount = 0
        for item in invoice_items:
            errors.extend(self.validateInvoiceItem(item))
            invoices_amount += item["amount"]

        bill_sandry_amount = 0
        for bill in invoice_data["billSundry"]:
            bill_sandry_amount+=bill["amount"]

        if invoice_data["totalAmount"] != invoices_amount+bill_sandry_amount:
            errors.append("Total invoice amount and invoice items amount and bill sandry amount is not adding up.")

        return errors

    def validateInvoiceRequest(self):
        data = self.invoice_data
        try:
            datetime_object = datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')
        except:
            raise ValueError("datetime format issue")

        invoice_data = {
            "id" : self.invoice_id,
            "date" : datetime_object,
            "invoiceNumber" : data["invoiceNumber"], 
            "customerName" : data["customerName"],
            "billingAddress" : data["billingAddress"], 
            "shippingAddress" : data["shippingAddress"],
            "gstIn" : data["gstIn"], 
            "totalAmount" : data["totalAmount"],
        }
        
        items_data = data.get("invoiceItems")
        invoice_items = []
        if items_data:
            for item in items_data:
                invoice_items.append({
                    "id" : item["id"],
                    "itemName" : item["itemName"],
                    "quantity" : item["quantity"],
                    "price" : item["price"],
                    "amount" : item["amount"]
                })
        invoice_data["invoiceItems"] = invoice_items

        bill_data = data.get("billSundry")
        bill_sundry = []
        if bill_data:
            for bill in bill_data:
                bill_sundry.append({
                    "id" : bill["id"],
                    "billSundryName" : bill["billSundryName"],
                    "amount" : bill["amount"]
                })
        invoice_data["billSundry"] = bill_sundry

        return invoice_data
