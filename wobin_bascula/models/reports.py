from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class BasculaQualityAvgHumidity(models.TransientModel):
    #Promedio ponderado de humedad    
    _name='bascula.quality.avg.humidity'
    
    product = fields.Many2one('product.product', string="Producto")
    branch = fields.Selection([('cas','Silos el castillo'),('aca', 'Acatic'),('oli', 'Silos Olivares')], string="Sucursal")
    init_date = fields.Datetime(string="Fecha inicio")
    end_date = fields.Datetime(string="Fecha fin")

class ReportBasculaAvgHumidity(models.AbstractModel):
    #Reporte promedio ponderado de humedad
    _name = 'report.wobin_bascula.report_bascula_avg_humidity'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['bascula.quality.avg.humidity'].browse(docids)
        tickets_receipt = self.env['bascula.ticket'].search([('type_ticket','=','internal'),('operation_type','=','in'),('date','>',report.init_date),('date','<',report.end_date),('product_id','=',report.product.id),('branch','=',report.branch),('company_id','=',self.env.user.company_id.id),('state','=','second')])
        tickets_receipt_transfer = self.env['bascula.ticket'].search([('type_ticket','=','internal'),('operation_type','=','ti'),('transfer_type','=','in'),('date','>',report.init_date),('date','<',report.end_date),('product_id','=',report.product.id),('branch','=',report.branch),('company_id','=',self.env.user.company_id.id),('state','=','second')])
        tickets_delivery = self.env['bascula.ticket'].search([('type_ticket','=','internal'),('operation_type','=','out'),('date','>',report.init_date),('date','<',report.end_date),('product_id','=',report.product.id),('branch','=',report.branch),('company_id','=',self.env.user.company_id.id),('state','=','second')])
        tickets_delivery_transfer = self.env['bascula.ticket'].search([('type_ticket','=','internal'),('operation_type','=','ti'),('transfer_type','=','out'),('date','>',report.init_date),('date','<',report.end_date),('product_id','=',report.product.id),('branch','=',report.branch),('company_id','=',self.env.user.company_id.id),('state','=','second')])

        sum_net_receipt = 0
        sum_humidity_receipt = 0
        avg_humidity_receipt = 0
        sum_humidity = 0
        sum_net_delivery = 0
        sum_humidity_delivery = 0
        avg_humidity_delivery = 0

        receipts = []
        for receipt in tickets_receipt:
            receipts.append({
                'name' : receipt.name,
                'date' : receipt.date.strftime("%d/%m/%Y %H:%M:%S"),
                'net_weight' : "{:,.0f}".format(receipt.net_weight),
                'humidity' : "{:.2f}".format(receipt.humidity)
            })
            sum_net_receipt += receipt.net_weight
            sum_humidity_receipt += receipt.net_weight * receipt.humidity
            sum_humidity += receipt.humidity_total_discount

        receipts_transfer = []
        for receipt_transfer in tickets_receipt_transfer:
            receipts_transfer.append({
                'name' : receipt_transfer.name,
                'date' : receipt_transfer.date.strftime("%d/%m/%Y %H:%M:%S"),
                'net_weight' : "{:,.0f}".format(receipt_transfer.net_weight),
                'humidity' : "{:.2f}".format(receipt_transfer.humidity)
            })
            sum_net_receipt += receipt_transfer.net_weight
            sum_humidity_receipt += receipt_transfer.net_weight * receipt_transfer.humidity
            sum_humidity += receipt.humidity_total_discount

        if sum_net_receipt > 0:
            avg_humidity_receipt = sum_humidity_receipt/sum_net_receipt

        deliveries = []
        for delivery in tickets_delivery:
            deliveries.append({
                'name' : delivery.name,
                'date' : delivery.date.strftime("%d/%m/%Y %H:%M:%S"),
                'net_weight' : "{:,.0f}".format(delivery.net_weight),
                'humidity' : "{:.2f}".format(delivery.humidity)
            })
            sum_net_delivery += delivery.net_weight
            sum_humidity_delivery += delivery.net_weight * delivery.humidity
        
        deliveries_transfer = []
        for delivery_transfer in tickets_delivery_transfer:
            deliveries_transfer.append({
                'name' : delivery_transfer.name,
                'date' : delivery_transfer.date.strftime("%d/%m/%Y %H:%M:%S"),
                'net_weight' : "{:,.0f}".format(delivery_transfer.net_weight),
                'humidity' : "{:.2f}".format(delivery_transfer.humidity)
            })
            sum_net_delivery += delivery_transfer.net_weight
            sum_humidity_delivery += delivery_transfer.net_weight * delivery_transfer.humidity
        
        if sum_net_delivery > 0:
            avg_humidity_delivery = sum_humidity_delivery/sum_net_delivery
        
        dif_net = sum_net_receipt - sum_net_delivery
        dif_avg = avg_humidity_receipt - avg_humidity_delivery
        dif_merma = dif_net - sum_humidity
        avg_merma = (dif_merma / sum_net_receipt)*100

        report_data = {
            'i_date' : report.init_date.strftime("%d/%m/%Y"),
            'e_date': report.end_date.strftime("%d/%m/%Y"),
            'today' : datetime.today().strftime("%d/%m/%Y %H:%M:%S"),
            'product' : report.product.name,
            'branch' : report.branch,
            'sum_net_receipt' : "{:,.0f}".format(sum_net_receipt),
            'sum_humidity_receipt' : sum_humidity_receipt,
            'avg_humidity_receipt' : "{:.2f}".format(avg_humidity_receipt),
            'sum_net_delivery' : "{:,.0f}".format(sum_net_delivery),
            'sum_humidity_delivery' : sum_humidity_delivery,
            'avg_humidity_delivery' : "{:.2f}".format(avg_humidity_delivery),
            'dif_net' : "{:,.0f}".format(dif_net),
            'dif_avg' : "{:.2f}".format(dif_avg),
            'sum_humidity': "{:,.0f}".format(sum_humidity),
            'dif_merma' : "{:,.0f}".format(dif_merma),
            'avg_merma' : "{:,.2f}".format(avg_merma),
        }

        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'report_data' : report_data,
            'receipts' : receipts,
            'receipts_transfer' : receipts_transfer,
            'deliveries' : deliveries,
            'deliveries_transfer' : deliveries_transfer
        }