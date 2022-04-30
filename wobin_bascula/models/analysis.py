from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class BasculaAnalysis(models.Model):
    #Boletas
    _name = 'bascula.analysis'
    _inherit = ['mail.thread']
    _description = 'Analisis'

    @api.model
    def _get_name_analist(self):
        #Obtener analista
        return self.env.user.name

    @api.one
    @api.depends('humidity')
    def _get_humidity_discount(self):
        #Metodo para calcular el descuento de humedad por cada mil kilos
        if self.humidity:
            if self.humidity > 14:
                self.humidity_discount = ((self.humidity-14)*1.16)/100*1000

    @api.one
    @api.depends('impurity')
    def _get_impurity_discount(self):
        #Metodo para calcular el descuento de impureza por cada mil kilos
        if self.impurity:
            if self.impurity > 2:
                self.impurity_discount = (self.impurity-2)/100*1000

    @api.one
    @api.depends('params_id')
    def _get_total_damage(self):
        #Metodo para calcular la suma de daños
        total = 0
        for data in self.params_id:
            if data.quality_params_id.damage:
                total += data.value
        self.sum_damage = total

    
    @api.one
    @api.depends('params_id')
    def _get_total_broken(self):
        #Metodo para calcular la suma de quebrados
        total = 0
        for data in self.params_id:
            if data.quality_params_id.broken:
                total += data.value
        self.sum_broken = total

    #------------------------------------Datos de calidad---------------------------------
    name = fields.Char(string="Folio")
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('bascula.ticket'))
    state = fields.Selection([('draft', 'Borrador'),
    ('accepted', 'Aceptado'),
    ('rejected', 'Rechazado')], default='draft', track_visibility='onchange')
    branch = fields.Selection([('cas','Silos el castillo'),('aca', 'Acatic'),('oli', 'Silos Olivares')], string="Sucursal", required=True)
    user = fields.Char(string="Usuario responsable", track_visibility='onchange', default=_get_name_analist, readonly=True, required=True)
    date = fields.Datetime(string="Fecha y hora", default=lambda self: fields.datetime.now())
    contact = fields.Char(string="Contacto")
    product_id = fields.Many2one('product.product', string="Producto", track_visibility='onchange', required=True)
    quality_id = fields.Many2one('bascula.quality', string="Norma de calidad", track_visibility='onchange', required=True)
    humidity = fields.Float(string="Humedad 14%", track_visibility='onchange', required=True)
    humidity_discount = fields.Float(string="Descuento humedad por tonelada (Kg)", compute='_get_humidity_discount', store=True)
    impurity = fields.Float(string="Impurezas 2%", track_visibility='onchange', required=True)
    impurity_discount = fields.Float(string="Descuento impurezas por tonelada(Kg)", compute='_get_impurity_discount', store=True)
    density = fields.Float(string="Densidad g/L 720-1000", track_visibility='onchange', required=True)
    temperature = fields.Float(string="Temperatura °C", track_visibility='onchange', required=True)
    params_id = fields.One2many('bascula.ticket.params', 'ticket_id', track_visibility='onchange')
    sum_damage = fields.Float(string="Suma daños", compute='_get_total_damage', store=True, track_visibility='onchange')
    sum_broken = fields.Float(string="Suma quebrados", compute='_get_total_broken', store=True, track_visibility='onchange')
    ticket_id = fields.Many2one('bascula.ticket', string="Boleta", readonly=True)
    purchase_id = fields.Many2one(related='ticket_id.purchase_id', string="Orden de compra", readonly=True)
    ticket_asign = fields.Boolean(string="Ticket asignado")

    #-----------------------------------Datos de transportacion---------------------------
    driver = fields.Char(string="Nombre del operador", track_visibility='onchange')
    type_vehicle = fields.Selection([('van','Camioneta'),
    ('torton','Torton'),
    ('trailer', 'Trailer sencillo'),
    ('full','Trailer full')], string="Tipo de vehiculo", default='van', track_visibility='onchange')
    plate_vehicle = fields.Char(string="Placas unidad", track_visibility='onchange')
    plate_trailer = fields.Char(string="Placas remolque", track_visibility='onchange')
    plate_second_trailer = fields.Char(string="Placas segundo remolque", track_visibility='onchange')

    @api.onchange('quality_id')
    def _get_quality_params(self):
        #Metodo para agregar los parametros de calidad a la boleta
        self.params_id = None
        if self.quality_id:
            array_params = []
            for param in self.quality_id.params:
                array_params.append((0,0,{'quality_params_id':param.id, 'name': param.name, }))
            self.params_id = array_params

    
    def acept_analysis(self):
        self.state = 'accepted'
        analysis = self.env['bascula.analysis'].search([('branch','=',self.branch)])
        if analysis:
            self.name = 'AN-'+str(self.branch).upper()+str(len(analysis)).zfill(5)
        else:
            self.name = 'AN-'+str(self.branch).upper()+'00001'

    def reject_analysis(self):
        self.state = 'rejected'
        analysis = self.env['bascula.analysis'].search([('branch','=',self.branch)])
        if analysis:
            self.name = 'AN-'+str(self.branch).upper()+str(len(analysis)).zfill(5)
        else:
            self.name = 'AN-'+str(self.branch).upper()+'00001'


class BasculaTicketParams(models.Model):
    #Parametros de calidad de boleta
    _name = 'bascula.ticket.params'
    _description = 'Boletas'

    ticket_id = fields.Many2one('bascula.analysis')
    quality_params_id = fields.Many2one('bascula.quality.params', 'Parametro de calidad')
    max_value = fields.Float(related='quality_params_id.value', string="Máximo")
    unit = fields.Char(related='quality_params_id.unit', string="Unidad de medida")
    value = fields.Float(string="Valor")

class BasculaQuality(models.Model):
    #Normas de calidad
    _name = 'bascula.quality'
    _description = 'Parametros de calidad'

    name = fields.Char(string="Norma")
    product_id = fields.Many2one('product.product', string="Producto")
    params = fields.One2many('bascula.quality.params', 'quality_id')


class BasculaQualityParams(models.Model):
    #Parametros de calidad
    _name = 'bascula.quality.params'
    _description = 'Parametros de calidad de bascula'

    name = fields.Char(string="Nombre", required=True)
    quality_id = fields.Many2one('bascula.quality')
    value = fields.Float(string="Máximo", required=True)
    unit = fields.Char(string="Unidad de medida", required=True)
    damage = fields.Boolean(string="Sumar daño")
    broken = fields.Boolean(string="Sumar quebrado")