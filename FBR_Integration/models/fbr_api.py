from odoo import api, fields, models
import requests
import json
import datetime

from odoo.exceptions import UserError


class FbrIntegration(models.Model):
    _inherit = 'sale.order'
    fbr_invoice_number = fields.Char(string="FBR Invoice Number")
    partner_id = fields.Many2one('res.partner', string='Customer')

    @api.model
    def push_sale_data_to_fbr(self, id):

        current_sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        current_sale_order.fbr_invoice_number = "123456789"

        #date_time_obj = datetime.datetime.strptime(current_sale_order.date_order, "%Y-%m-%dT%H:%M:%S")

        #raise UserError(self.env['sale.order'].date_order)
        #Convert the datetime object to the desired format
        #formatted_datetime = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        formatted_datetime = current_sale_order.date_order.isoformat() + "+05:00"

        data = {
            "FBRInvoiceNumber": "",  # Replace with the actual FBR invoice number
            "POSID": 910943,  # Replace with the actual POS ID
            "REFUSIN": 10,  # Replace with the actual REFUSIN value
            "DATETIME": current_sale_order.date_order.isoformat() + "+05:00",
            "BUYERNAME": current_sale_order.partner_id.name,
            "BUYERPHONENUMBER": current_sale_order.partner_id.phone,
            "TOTALQUANTITY": sum(line.product_uom_qty for line in current_sale_order.order_line),
            "TOTALBILLAMOUNT": current_sale_order.amount_total,
            "TOTALSALEVALUE": current_sale_order.amount_total,
            "TOTALTAXCHARGED": current_sale_order.amount_tax,
            "DISCOUNT": 0, #current_sale_order.amount_discount,
            "PAYMENTMODE": 1,  # Replace with the actual payment mode
            "USIN": 1,  # Replace with the actual USIN value
            "INVOICETYPE": 3,  # Replace with the actual invoice type
            "Items": [
                {
                    "ITEMCODE": line.product_id.default_code,
                    "ITEMNAME": line.product_id.name,
                    "PCTCODE": "12345678",  # Replace with the actual PCTCODE
                    "QUANTITY": line.product_uom_qty,
                    "TAXRATE": line.price_unit - line.price_subtotal,
                    "DISCOUNT": line.discount,
                    "TAXCHARGED": 0, #line.price_subtotal *
                                  #line.tax_ids.compute_all(price=line.price_subtotal)[0]['taxes'][0]['amount'],
                    "SALEVALUE": line.price_subtotal,
                    "TOTALAMOUNT": line.price_total,
                    "INVOICETYPE": 3,  # Replace with the actual invoice type
                    "REFUSIN": 10  # Replace with the actual REFUSIN value
                }
                for line in current_sale_order.order_line
            ]
        }

        json.dumps(data)

        # Send the POST request to the API
        url = "http://localhost:8524/api/IMSFiscal/GetInvoiceNumberByModel"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)

        # Handle the response and save the FBR invoice number
        if response.status_code == 200:
            fbr_invoice_number = response.json().get('InvoiceNumber')
            self.fbr_invoice_number = fbr_invoice_number
            #current_sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
            #current_sale_order.fbr_invoice_number = fbr_invoice_number
            #raise UserError(current_sale_order.date_order)
            #raise UserError(response.text)
            #self.fbr_invoice_number = fbr_invoice_number
        else:
            # Handle errors or unexpected responses
            raise ValueError("Error pushing data to FBR API: %s" % response.text)

    @api.model
    def check_functions(self, id):
        if 1 < 2:
            url = "http://localhost:8524/api/IMSFiscal/get"
            response = requests.get(url)
            self.fbr_invoice_number = '123456789'
            raise UserError(response.text)
