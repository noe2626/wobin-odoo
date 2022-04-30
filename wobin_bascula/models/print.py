from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class PrintBasculaTicket(models.AbstractModel):
    #Impresion de pesada
    _name = 'report.wobin_bascula.print_ticket'

    @api.model
    def _get_report_values(self, docids, data=None):
        tickets = self.env['bascula.ticket'].browse(docids)
        docs=[]
        for ticket in tickets:
            doc={'ticket': ticket,
            'first_weight': f'{ticket.first_weight:,.2f}',
            'first_date': ticket.first_date.strftime("%d/%m/%Y %H:%M:%S"),
            'second_weight': f'{ticket.second_weight:,.2f}',
            'second_date': ticket.second_date.strftime("%d/%m/%Y %H:%M:%S"),
            'gross_weight': f'{ticket.gross_weight:,.2f}',
            'tare_weight': f'{ticket.tare_weight:,.2f}',
            'net_weight': f'{ticket.net_weight:,.2f}',
            }
            docs.append(doc)
        
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs
        }

class ReportRecibaTicketExternal(models.AbstractModel):
    #Impresion de boleta
    _name = 'report.wobin_bascula.print_ticket_external'

    @api.model
    def _get_report_values(self, docids, data=None): 
        tickets = self.env['bascula.ticket'].browse(docids)
        docs=[]
        for ticket in tickets:

            #Sumamos los otros granos
            sum_other=0
            for param in ticket.params_id:
                if param.quality_params_id.damage == False:
                    sum_other += param.value

            #Descuento sumado en porcentaje
            total_discount_p = ticket.humidity + ticket.impurity

            #Damos formato a los datos que se van a mostrar
            doc={
                'ticket': ticket,
                'humidity': f'{ticket.humidity:,.2f}',
                'impurity': f'{ticket.impurity:,.2f}',
                'density': f'{ticket.density:,.2f}',
                'temperature': f'{ticket.temperature:,.2f}',
                'humidity': f'{ticket.humidity:,.2f}',
                'impurity': f'{ticket.impurity:,.2f}',
                'humidity_total_discount': f'{round(ticket.humidity_total_discount):,}',
                'impurity_total_discount': f'{round(ticket.impurity_total_discount):,}',
                'total_discount': f'{round(ticket.discount):,}',
                'total_discount_p': f'{round(total_discount_p):,}',
                'net_weight': f'{round(ticket.net_weight):,}',
                'total_format': f'{round(ticket.total_weight):,}',
                'sum_damage': f'{ticket.sum_damage:,.2f}',
                'sum_other': f'{sum_other:,.2f}',
            }
            docs.append(doc)
            
        
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs
        }

class ReportRecibaTicketExternalWA(models.AbstractModel):
    #Impresion de boleta sin analisis
    _name = 'report.wobin_bascula.print_ticket_external_wa'

    @api.model
    def _get_report_values(self, docids, data=None): 
        tickets = self.env['bascula.ticket'].browse(docids)
        docs=[]
        for ticket in tickets:
            
            doc={'ticket': ticket,
                'total_format': f'{ticket.total_weight:,.2f}'
            }
            docs.append(doc)
            
        
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs
        }