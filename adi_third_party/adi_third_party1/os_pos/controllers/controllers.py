# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http, tools, models, _
from odoo import models, fields, api

import json
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_customers_by_user_id(self, user_id):
        customers = self.search([('user_id', '=', user_id), ('customer', '=', True)])
        return customers


class CustomerSalesInfo(models.Model):
    _name = 'customer.sales.info'

    def get_customer_sales_info(self, mobile):
        # Find the customer by their phone number
        customer = self.env['res.partner'].sudo().search([('phone', '=', mobile)], limit=1)

        if not customer:
            return {}

        # Get total sales for the customer
        total_sales = 0
        for order in customer.sale_order_ids:
            total_sales += order.amount_total

        # Get the most purchased product and its amount
        most_purchased_product = None
        most_purchased_amount = 0
        for order_line in customer.sale_order_ids.mapped('order_line'):
            if order_line.product_uom_qty > most_purchased_amount:
                most_purchased_product = order_line.product_id.name
                most_purchased_amount = order_line.product_uom_qty

        # Get the customer's creation date
        customer_since_date = customer.create_date.date()

        # Get the latest transactions
        latest_transactions = []
        for order in customer.sale_order_ids.sorted(key=lambda x: x.date_order, reverse=True)[:50]:
            latest_transactions.append({
                'date': order.date_order,
                'amount': order.amount_total,
            })

        # Calculate the years since the customer started buying
        today = datetime.now().date()
        years_since_start = (today - customer_since_date).days // 365

        return {
            'total_sales': total_sales,
            'most_purchased_product': most_purchased_product,
            'most_purchased_amount': most_purchased_amount,
            'customer_since_date': customer_since_date,
            'latest_transactions': latest_transactions,
            'years_since_start': years_since_start,
            'years_dict': customer.get_customer_sales_report()

        }


class namaa_api_sales(http.Controller):

    @http.route('/generic_api/query', type='json', auth='public', methods=['POST'])
    def query_data(self, **kwargs):
        model = kwargs.get('model')
        domain = kwargs.get('domain') if kwargs.get('domain') else []
        fields = kwargs.get('fields')if kwargs.get('fields') else []
        limit = kwargs.get('limit')

        # Validate and sanitize the inputs as needed

        # Query the data based on the provided parameters
        records = request.env[model].sudo().search(domain, limit=limit)
        data = records.read(fields)

        return {
            'status': 200,
            'response': data
        }


    @http.route('/get_customer_sales_info', type='json', auth='api_key')
    def get_customer_sales_info(
            self):  # , Card_NO=None, User_Name='', filter="", app_version=5, Kind_Distribution_Title_id=-1):
        request_data = json.loads(request.httprequest.data)
        result = CustomerSalesInfo.get_customer_sales_info(request, request_data["mobile"])
        # result = no
        return {'success': True, 'message': 'successfully found', 'dict': result}

    @http.route('/CreateSalesOrder', type='json', auth='api_key')
    def CreateSalesOrder(
            self):
        # , Card_NO=None, User_Name='', filter="", app_version=5, Kind_Distribution_Title_id=-1):
        # Access the request's JSON data
        request_data = json.loads(request.httprequest.data)
        # Sample request body
        # {
        #     "customerName": "tester",
        #     "customerMobile": "0541",
        #     "User_Name": "tarek",
        #     "filter": "وصف 1444",
        #     "app_version": 5,
        #     "Kind_Distribution_Title_id": -1
        # }

        # Customer
        # search for the customer if he exits
        customerMobile = request_data["customerMobile"]
        customer = request.env['res.partner'].sudo().search([('phone', '=', customerMobile)])
        if customer:
            customer = customer[0]
        if not customer:  # Create
            customer = request.env['res.partner'].create({
                'name': request_data['customerName'] if request_data['customerName'] != "" else request_data[
                    'customerMobile'],
                'phone': request_data['customerMobile']
            })

        lines = []
        for l in request_data["lines"]:
            ol = (0, 0, {
                'product_id': l["product_id"],  # ID of the product
                'product_uom_qty': l["qty"],  # Quantity of the product
                'price_unit': l["price"],  # Price of the product
                #'line_amountxxx': l["line_amount"],  # Price of the product
            })
            lines.append(ol)

        if request_data:
            # Create a new sales order object
            sale_order = request.env['sale.order'].sudo().create({
                'partner_id': 1,  # customer.id
                'employee_sales_person_id': 1,
                'commission_parent_id': 2,
                'pricelist_id': 1,  # ID of the pricelist
                'date_order': request_data['date_order'],  # ID of the pricelist
                'order_line': lines
                #[
                    # (0, 0, {
                    #     'product_id': 832,  # ID of the product
                    #     'product_uom_qty': 1,  # Quantity of the product
                    #     'price_unit': 100,  # Price of the product
                    # })
                  #  ,
              # ],
            })

            # Save the sales order
            # sale_order.save()
            do_invoice = False
            do_pay = False

            if do_invoice:
                invoices = sale_order._create_invoices(final=True)
                temp_date_order = sale_order.date_order
                sale_order.date_order = temp_date_order

                for inv in invoices:
                    inv.action_post()
                    # my_list = [{'date': order_vals.date_order, **obj} for obj in inv.invoice_line_ids]
                    for line in inv.invoice_line_ids:
                        line.date = temp_date_order
                    inv.invoice_date_due = temp_date_order
                    inv.date = temp_date_order
                    if do_pay:
                        request.pay_invoice(inv.id, sale_order.date_order)
            return {'success': True, 'message': 'successfully Found: ', ' dict ': request_data}
        else:
            return {'success': False, 'message': 'data not found', 'qty': "0"}








class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_customer_segmentation(self):
        analytic_account = self.env['account.analytic.account']
        segment_thresholds = {
            'High Sales': 1000,  # Adjust the thresholds based on your criteria
            'Medium Sales': 500,
            'Low Sales': 0
        }

        for order in self:
            total_sales = sum(order.order_line.mapped('price_total'))

            for segment, threshold in segment_thresholds.items():
                if total_sales > threshold:
                    order.partner_id.analytic_account_id = analytic_account.search([('name', '=', segment)], limit=1)
                    break

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')






class CustomerSalesReport(models.Model):
    _name = 'customer.sales.report'
    _description = 'Customer Sales Report'

    customer_id = fields.Many2one('res.partner', string='Customer')
    sales_amount = fields.Float(string='Total Sales Amount')
    sales_count = fields.Integer(string='Sales Count')
    year = fields.Integer(string='Year')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_customer_sales_report(self):
        report_data = []
        sales = self.env['sale.order'].search([
            ('partner_id', 'in', self.ids),
            ('state', 'in', ['sale', 'done'])
        ])

        for partner in self:
            sales_by_year = {}
            for sale in sales.filtered(lambda s: s.partner_id == partner):
                year = sale.date_order.year
                if year not in sales_by_year:
                    sales_by_year[year] = {'amount': 0.0, 'count': 0}

                sales_by_year[year]['amount'] += sale.amount_total
                sales_by_year[year]['count'] += 1

            for year, sales_data in sales_by_year.items():
                report_data.append({
                    'customer_id': partner.id,
                    'sales_amount': sales_data['amount'],
                    'sales_count': sales_data['count'],
                    'year': year
                })
        return report_data


class CustomLoginAPIController(http.Controller):
    @http.route('/login', type='json' , csrf=False , auth='public', methods=['POST'])

    def user_login(self, db,username, password):
        if db!= "" :
            user_id = request.session.authenticate(db,username, password)
        if db == "" :
            user_id = request.session.authenticate( username, password)
        user = request.env['res.users'].browse(user_id)
        return  user.name or user.login





    # @http.route('/read_products_with_tax_discount'  ,   auth='public', methods=['POST'])
    # http://localhost:9016/read_products_with_tax_discount/
    @http.route('/read_products_with_tax_discount', type='json', auth='public', methods=['POST'])

    def read_products_with_tax_discount(self):
        # Retrieve products with their taxes and discounts
        products = request.env['product.product'].sudo().search([])
        #user = request.env['res.users'].search([('login', '=', username)])


        result = []
        for product in products:
            # Retrieve taxes applied to the product
            taxes = product.taxes_id.mapped('name')

            # Retrieve available discounts for the product
            discounts = product.discount_ids.mapped('name')

            # Prepare the result dictionary
            product_data = {
                'name': product.name,
                'taxes': taxes,
                'discounts': discounts,
            }
            result.append(product_data)

        return result