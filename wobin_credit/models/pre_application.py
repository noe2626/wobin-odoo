from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class CreditPreApplication(models.Model):
    _name = "credit.preapplication"
    _inherit = ['mail.thread']

    @api.depends('crop_type_ids')
    def get_amount(self):
        amount = 0
        insurance = 0
        
        for line in self.crop_type_ids:
            amount += line.calculated_amount
            insurance += line.calculated_insurance

        self.calculated_amount = amount
        self.insurance = insurance

    @api.depends('crop_type_ids')
    def get_insurance(self):
        amount = 0
        
        for line in self.crop_type_ids:
            amount += line.calculated_amount

        self.insurance = amount

    def _get_name(self):
        count = self.env['credit.preapplication'].search([('company_id','=',self.env.user.company_id.id)])
        number = str(len(count)+1).zfill(4)
        return 'PRE-'+number


    state = fields.Selection([('draft', 'Borrador'),
    ('locked', 'Bloqueado')], default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('credit.preapplication'))
    name = fields.Char('Preaplicación', default=_get_name, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Cliente")
    cycle =  fields.Many2one('credit.cycles', string="Ciclo")
    calculated_amount = fields.Float(string="Monto permitido", compute="get_amount", store=True)
    requested_amount = fields.Float(string="Monto solicitado")
    authorized_amount = fields.Float(string="Monto autorizado")
    insurance = fields.Float(string="Seguro Agrícola total", compute="get_amount", store=True)
    credit_type_id = fields.Many2one('credit.types', string="Tipo de crédito")
    payment_terms = fields.Many2one(related='credit_type_id.payment_terms', string="Plazo de pago", readonly='True')
    date_limit_flag = fields.Boolean(default="False")
    date_limit = fields.Date(string="Fecha límite")
    interest = fields.Float(related='credit_type_id.interest', string="Interés", readonly='True')
    interest_mo = fields.Float(related='credit_type_id.interest_mo', string="Interés moratorio", readonly='True')
    crop_type_ids = fields.One2many('credit.crop.type', 'preapplication_id', string="Tipos de cultivo")

    @api.onchange('payment_terms')
    def get_payment_term(self):

        if self.payment_terms and len(self.payment_terms.line_ids) > 1:
            
            if self.payment_terms.line_ids[1].days == 180:
                self.date_limit_flag = True
            else:
                self.date_limit_flag = False
                self.date_limit = ''
        else:
            self.date_limit_flag = False
            self.date_limit = ''

    def lock_credit(self):

        self.state = 'locked'

    def unlock_credit(self):

        self.state = 'draft'


class CreditCropType(models.Model):
    _name = "credit.crop.type"
    #Tipos de cultivo

    @api.one
    @api.depends('crop_type_id','crop_method','hectares')
    def get_amount(self):
        amount = 0
        insurance = 0
        
        if self.crop_type_id and self.crop_method:
            param = self.env['credit.parameters'].search([('crop_type','=',self.crop_type_id.id),('crop_method','=',self.crop_method),('credit_type_id','=',self.preapplication_id.credit_type_id.id)], limit=1)
            if param:
                amount = param.amount*self.hectares
                insurance = param.insurance*self.hectares

        self.calculated_amount = amount
        self.calculated_insurance = insurance

    preapplication_id = fields.Many2one('credit.preapplication')
    crop_method = fields.Selection([('irrigation', 'Riego'),('rainwater', 'Temporal')], string="Metodo de cultivo")
    crop_type_id = fields.Many2one('product.product', string="Tipo de cultivo")
    hectares = fields.Float(string="Hectareas")
    calculated_amount = fields.Float(string="Monto calculado", compute="get_amount", store=True)
    calculated_insurance = fields.Float(string="Seguro agrícola", compute="get_amount", store=True)
    

class AccountPayment(models.Model): 
    #Agregamos los campos para relacionar abonos
    _inherit = 'account.payment'

    is_payment = fields.Boolean(string="Abono")
    payment_credit_id = fields.Many2one('account.payment', string="Prestamo")
    payment_credit_ids = fields.One2many('account.payment', 'payment_credit_id')

class AccountMoveLine(models.Model):
    #Empresa en transferencias internas
    _inherit = 'account.move.line'

    x_studio_field_KXQlu = fields.Many2one(related='payment_id.partner_id')

    @api.model
    def create(self, values):
        if values['partner_id'] == False:
            payment = self.env['account.payment'].search([('id','=',values['payment_id'])],limit=1)
            values['partner_id'] = payment.partner_id.id
        move = super(AccountMoveLine, self).create(values)

        return move
