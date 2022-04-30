from itertools import product
from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class BasculaTicket(models.Model):
    #Boletas
    _name = 'bascula.ticket'
    _inherit = ['mail.thread']
    _description = 'Boletas'

    @api.model
    def _get_name_weigher(self):
        #Obtener analista
        return self.env.user.name

    @api.one
    @api.depends('gross_weight', 'tare_weight')
    def _get_net_weight(self):
        #metodo para calcular peso neto
        if self.type_ticket == 'internal':
            if self.gross_weight and self.tare_weight:
                self.net_weight = self.gross_weight-self.tare_weight
                if self.operation_type == 'in':
                    self.net_weight_analysis = self.net_weight
                elif self.operation_type == 'out':
                    self.net_weight_analysis = self.net_weight*-1
                elif self.operation_type == 'ti':
                    if self.transfer_type == 'in':
                        self.net_weight_analysis = self.net_weight
                    elif self.transfer_type == 'out':
                        self.net_weight_analysis = self.net_weight*-1
            else:
                self.net_weight = 0
                self.net_weight_analysis = 0
        else:
            if self.gross_weight and self.tare_weight:
                self.net_weight = self.gross_weight-self.tare_weight
                self.net_weight_analysis = self.net_weight
            else:
                self.net_weight = 0
                self.net_weight_analysis = 0


    @api.one
    @api.depends('humidity', 'net_weight')
    def _get_humidity_total_discount(self):
        #Metodo para calcular el descuento total por humedad del peso neto 
        if self.humidity:
            if self.humidity > 14:
                self.humidity_total_discount = ((self.humidity-14)*1.16)/100*self.net_weight

    @api.one
    @api.depends('impurity', 'net_weight')
    def _get_impurity_total_discount(self):
        #Metodo para calcular el descuento total por impureza del peso neto
        if self.impurity:
            if self.impurity > 2:
                self.impurity_total_discount = (self.impurity-2)/100*self.net_weight

    @api.one
    @api.depends('humidity_total_discount', 'impurity_total_discount')
    def _get_discount_total(self):
        #Metodo para calcular el descuento total
        self.discount = self.humidity_total_discount+self.impurity_total_discount

    @api.one
    @api.depends('net_weight', 'discount')
    def _get_total_weight(self):
        #Metodo para calcular el peso neto analizado
        self.total_weight = self.net_weight-self.discount

    #===============================================Campos================================================

    state = fields.Selection([('draft', 'Borrador'),
    ('first', 'Primer pesada'),
    ('second', 'Segunda pesada'),
    ('cancel', 'Cancelada')], string="Estado", default='draft', track_visibility='onchange')
    type_ticket= fields.Selection([('internal', 'Interno'),
    ('public', 'Público')], default='internal', string="Tipo de boleta")
    operation_type = fields.Selection([('in','Entrada'),('out','Salida')], string="Tipo de operación")
    transfer_type = fields.Selection([('in','Entrada'),('out','Salida')], string="Tipo de transferencia")
    branch = fields.Selection([('cas','Silos el castillo'),('aca', 'Acatic'),('oli', 'Silos Olivares')], string="Sucursal", required=True)
    user = fields.Char(string="Usuario responsable", track_visibility='onchange', default=_get_name_weigher, readonly=True, required=True)
    date = fields.Datetime(string="Fecha y hora", default=lambda self: fields.datetime.now())
    name = fields.Char(string="Folio", default="Boleta borrador", track_visibility='onchange', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('bascula.ticket'))
    origin_ticket = fields.Many2one('bascula.ticket', string="Documento origen", readonly=True)
    related_ticket = fields.Many2one('bascula.ticket', string="Boleta relacionada", readonly=True)
    analysis_id = fields.Many2one('bascula.analysis', string="Folio de análisis", domain="[('state','=','accepted'),('ticket_asign','=',False)]")

    quality_id = fields.Many2one(related='analysis_id.quality_id', string="Norma de calidad")
    humidity = fields.Float(related='analysis_id.humidity', string="Humedad 14%")
    humidity_discount = fields.Float(related='analysis_id.humidity_discount', string="Descuento humedad por tonelada (Kg)")
    impurity = fields.Float(related='analysis_id.impurity', string="Impurezas 2%")
    impurity_discount = fields.Float(related='analysis_id.impurity_discount', string="Descuento impurezas por tonelada(Kg)")
    density = fields.Float(related='analysis_id.density', string="Densidad g/L 720-1000")
    temperature = fields.Float(related='analysis_id.temperature', string="Temperatura °C")
    params_id = fields.One2many(related='analysis_id.params_id')
    sum_damage = fields.Float(related='analysis_id.sum_damage', string="Suma daños")
    sum_broken = fields.Float(related='analysis_id.sum_broken', string="Suma quebrados")
    document_asign = fields.Boolean(string="Orden asignada", default=False)
    purchase_id = fields.Many2one('purchase.order', string="Orden de compra", readonly=True)
    sale_id = fields.Many2one('sale.order', string="Orden de venta")
    picking_id = fields.Many2one('stock.picking', string="Transferencia relacionada")

    #-----------------------------------Datos de transportacion---------------------------
    driver = fields.Char(string="Nombre del operador")
    type_vehicle = fields.Selection([('van','Camioneta'),
    ('torton','Torton'),
    ('trailer', 'Trailer sencillo'),
    ('full','Trailer full')], string="Tipo de vehiculo", default='van', track_visibility='onchange')
    plate_vehicle = fields.Char(string="Placas unidad", track_visibility='onchange')
    plate_trailer = fields.Char(string="Placas remolque", track_visibility='onchange')
    plate_second_trailer = fields.Char(string="Placas segundo remolque", track_visibility='onchange')
    contact = fields.Char(string="Contacto")
    product = fields.Char(string="Producto")
    product_id = fields.Many2one(related='analysis_id.product_id')
    price = fields.Float(string="Precio")

    #----------------------------------Primer pesada-------------------------------
    folio = fields.Char(string="Folio de báscula")
    first_weight = fields.Float(string="Primer pesada (Kg)", track_visibility='onchange')
    first_date = fields.Datetime(string="Fecha y hora")
    second_weight = fields.Float(string="Segunda pesada (Kg)", track_visibility='onchange')
    second_date = fields.Datetime(string="Fecha y hora")
    
    gross_weight = fields.Float(string="Peso Bruto (Kg)", track_visibility='onchange', readonly=True)
    tare_weight = fields.Float(string="Peso Tara (Kg)", track_visibility='onchange', readonly=True)
    net_weight = fields.Float(string="Peso Neto (Kg)", compute='_get_net_weight', store=True)
    net_weight_analysis = fields.Float(string="Peso Neto (Kg)", compute='_get_net_weight', store=True)

    #-----------------------------------Descuentos------------------------------------
    humidity_total_discount = fields.Float(string="Descuento total de humedad (Kg)", compute='_get_humidity_total_discount', store=True)
    impurity_total_discount = fields.Float(string="Descuento total de impurezas (Kg)", compute='_get_impurity_total_discount', store=True)
    discount = fields.Float(string="Descuento total (kg)", compute='_get_discount_total', store=True)
    total_weight = fields.Float(string="Peso neto analizado", compute='_get_total_weight', store=True)

    @api.onchange('analysis_id')
    def _change_analysis(self):
        if self.analysis_id:
            self.branch = self.analysis_id.branch
            self.driver = self.analysis_id.driver
            self.type_vehicle = self.analysis_id.type_vehicle
            self.plate_vehicle = self.analysis_id.plate_vehicle
            self.plate_trailer = self.analysis_id.plate_trailer
            self.plate_second_trailer = self.analysis_id.plate_second_trailer
            self.product = self.analysis_id.product_id.name
            self.contact = self.analysis_id.contact
        
    @api.model
    def create(self, vals):
        res = super(BasculaTicket, self).create(vals)
        try:
            if vals['analysis_id']:
                ticket = self.env['bascula.analysis'].browse(vals['analysis_id'])
                ticket.write({'ticket_asign':True,
                            'ticket_id': res.id})
        except:
            return res
        
        return res
    
    @api.multi
    def write(self, vals):
        try:
            if vals['analysis_id']:
                if self.analysis_id.id != vals['analysis_id']:
                    self.analysis_id.write({'ticket_asign':False,
                                        'ticket_id': 0})
                    ticket_new = self.env['bascula.analysis'].browse(vals['analysis_id'])
                    ticket_new.write({'ticket_asign':True,
                                    'ticket_id':self.id})
        except:
            return super(BasculaTicket, self).write(vals)
        
        res = super(BasculaTicket, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        if self.analysis_id:
            self.analysis_id.write({'ticket_asign':False,
                                    'ticket_id': 0})
        res = super(BasculaTicket, self).unlink()
        return res


    def save_first(self):
        if self.first_weight > 0:
            self.state = 'first'
            tickets = self.env['bascula.ticket'].search([('branch','=',self.branch),('state','!=','draft'),('company_id','=',self.company_id.id)])
            if tickets:
                self.name = 'BAS-'+str(self.branch).upper()+str(len(tickets)).zfill(5)
            else:
                self.name = 'BAS-'+str(self.branch).upper()+'00001'
            if self.operation_type == 'out':
                self.sale_id.write({
                    'tickets_id': [(0,0,{'ticket_id': self.id,'sale_id':self.sale_id.id})]
                })
        else:
            msg = 'No se ha ingresado la primer pesada'
            raise UserError(msg)

    def save_second(self):
        if self.second_weight > 0:
            self.state = 'second'
            if self.first_weight > self.second_weight:
                self.gross_weight = self.first_weight
                self.tare_weight = self.second_weight
            else:
                self.gross_weight = self.second_weight
                self.tare_weight = self.first_weight
        else:
            msg = 'No se ha ingresado la segunda pesada'
            raise UserError(msg)

    def cancel_ticket(self):
        if self.document_asign:
            if self.purchase_id:
                if self.purchase_id.state != 'cancel':
                    msg = 'La boleta no puede ser cancelada porque está relacionada a una orden de compra activa'
                    raise UserError(msg)
                else:
                    self.state = 'cancel'
                    
                    new_ticket = self.env['bascula.ticket'].create({
                        'type_ticket': self.type_ticket,
                        'operation_type' : self.operation_type,
                        'branch' : self.branch,
                        'contact' : self.contact,
                        'product': self.product,
                        'product_id': self.product_id,
                        'price': self.price,
                        'driver': self.driver,
                        'type_vehicle': self.type_vehicle,
                        'plate_vehicle': self.plate_vehicle,
                        'plate_trailer': self.plate_trailer,
                        'plate_second_trailer': self.plate_second_trailer,
                        'folio': self.folio,
                        'first_weight': self.first_weight,
                        'first_date': self.first_date,
                        'second_weight': self.second_weight,
                        'second_date': self.second_date,
                        'origin_ticket': self.id,
                        'analysis_id': self.analysis_id.id
                    })
                    self.related_ticket = new_ticket.id
                    self.analysis_id.write({'ticket_id': new_ticket.id})
            if self.sale_id:
                self.state = 'cancel'
                new_ticket = self.env['bascula.ticket'].create({
                    'type_ticket': self.type_ticket,
                    'operation_type' : self.operation_type,
                    'branch' : self.branch,
                    'contact' : self.contact,
                    'product': self.product,
                    'product_id': self.product_id,
                    'price': self.price,
                    'driver': self.driver,
                    'type_vehicle': self.type_vehicle,
                    'plate_vehicle': self.plate_vehicle,
                    'plate_trailer': self.plate_trailer,
                    'plate_second_trailer': self.plate_second_trailer,
                    'folio': self.folio,
                    'first_weight': self.first_weight,
                    'first_date': self.first_date,
                    'second_weight': self.second_weight,
                    'second_date': self.second_date,
                    'origin_ticket': self.id,
                    'analysis_id': self.analysis_id.id
                })
                self.related_ticket = new_ticket.id
                self.analysis_id.write({'ticket_id': new_ticket.id})
            if self.picking_id:
                if self.picking_id.state != 'cancel':
                    msg = 'La boleta no puede ser cancelada porque está relacionada a una transferencia activa'
                    raise UserError(msg)
                else:
                    self.state = 'cancel'
                    new_ticket = self.env['bascula.ticket'].create({
                        'type_ticket': self.type_ticket,
                        'operation_type' : self.operation_type,
                        'branch' : self.branch,
                        'contact' : self.contact,
                        'product': self.product,
                        'product_id': self.product_id,
                        'price': self.price,
                        'driver': self.driver,
                        'type_vehicle': self.type_vehicle,
                        'plate_vehicle': self.plate_vehicle,
                        'plate_trailer': self.plate_trailer,
                        'plate_second_trailer': self.plate_second_trailer,
                        'folio': self.folio,
                        'first_weight': self.first_weight,
                        'first_date': self.first_date,
                        'second_weight': self.second_weight,
                        'second_date': self.second_date,
                        'origin_ticket': self.id,
                        'analysis_id': self.analysis_id.id
                    })
                    self.related_ticket = new_ticket.id
                    self.analysis_id.write({'ticket_id': new_ticket.id})
        else:
            self.state = 'cancel'
            new_ticket = self.env['bascula.ticket'].create({
                'type_ticket': self.type_ticket,
                'operation_type' : self.operation_type,
                'branch' : self.branch,
                'contact' : self.contact,
                'product': self.product,
                'product_id': self.product_id,
                'price': self.price,
                'driver': self.driver,
                'type_vehicle': self.type_vehicle,
                'plate_vehicle': self.plate_vehicle,
                'plate_trailer': self.plate_trailer,
                'plate_second_trailer': self.plate_second_trailer,
                'folio': self.folio,
                'first_weight': self.first_weight,
                'first_date': self.first_date,
                'second_weight': self.second_weight,
                'second_date': self.second_date,
                'origin_ticket': self.id,
                'analysis_id': self.analysis_id.id
            })
            self.related_ticket = new_ticket.id
            self.analysis_id.write({'ticket_id': new_ticket.id})

#===============================================Compras=========================================================        

class BasculaPurchaseTicket(models.Model):
    _name = 'bascula.purchase.ticket'

    ticket_id = fields.Many2one('bascula.ticket', string="Folio")
    product_id = fields.Many2one(related='ticket_id.product_id', string="Producto")
    net_weight = fields.Float(related='ticket_id.net_weight', string="Peso neto")
    purchase_id = fields.Many2one('purchase.order')

    @api.model
    def create(self, vals):
        res = super(BasculaPurchaseTicket, self).create(vals)
        if vals['ticket_id']:
            ticket = self.env['bascula.ticket'].browse(vals['ticket_id'])
            ticket.write({'document_asign':True,
                        'purchase_id': vals['purchase_id']})
        return res
    
    @api.multi
    def write(self, vals):
        if vals['ticket_id']:
            if self.ticket_id.id != vals['ticket_id']:
                self.ticket_id.write({'document_asign':False,
                                    'purchase_id': 0})
                ticket_new = self.env['bascula.ticket'].browse(vals['ticket_id'])
                ticket_new.write({'document_asign':True,
                                'purchase_id':self.purchase_id.id})
        res = super(BasculaPurchaseTicket, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        if self.ticket_id:
            self.ticket_id.write({'document_asign':False,
                                    'purchase_id': 0})
        res = super(BasculaPurchaseTicket, self).unlink()
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tickets_id = fields.One2many('bascula.purchase.ticket', 'purchase_id', string="Boletas Relacionadas")

    @api.onchange('tickets_id')
    def _onchange_ticket(self):
        vals = []

        for ticket in self.tickets_id:
            if ticket.product_id:
                uom_id = self.env['uom.uom'].search([('name','=','kg')]).id
                vals.append({'product_id': ticket.ticket_id.product_id.id,
                            'product_qty': ticket.ticket_id.net_weight,
                            'price_unit': ticket.ticket_id.price,
                            'date_planned': datetime.now(),
                            'product_uom': uom_id,
                            'name': ticket.ticket_id.product_id.display_name,
                            'taxes_id': ticket.ticket_id.product_id.supplier_taxes_id})
                if ticket.ticket_id.discount > 0:
                    product_desc = self.env['product.product'].search([('name','ilike','Descuento Sobre Compra')])
                    uom_desc = self.env['uom.uom'].search([('name','=','Servicio(s)')]).id
                    vals.append({'product_id': product_desc.id,
                            'product_qty': ticket.ticket_id.discount,
                            'price_unit': ticket.ticket_id.price*-1,
                            'date_planned': datetime.now(),
                            'product_uom': uom_desc,
                            'name': product_desc.display_name,
                            'taxes_id': product_desc.supplier_taxes_id})
            else:
                vals.append(False)
        
        
        self.order_line = None
        
        for val in vals:
            if val:
                self.order_line = [(0,0,val)]


#===============================================Ventas=========================================================        

class BasculaSaleTicket(models.Model):
    _name = 'bascula.sale.ticket'

    ticket_id = fields.Many2one('bascula.ticket', string="Folio")
    product_id = fields.Many2one(related='ticket_id.product_id', string="Producto")
    net_weight = fields.Float(related='ticket_id.net_weight', string="Peso neto")
    sale_id = fields.Many2one('sale.order')

    @api.model
    def create(self, vals):
        res = super(BasculaSaleTicket, self).create(vals)
        if vals['ticket_id']:
            ticket = self.env['bascula.ticket'].browse(vals['ticket_id'])
            ticket.write({'document_asign':True,
                        'sale_id': vals['sale_id']})
        return res
    
    @api.multi
    def write(self, vals):
        if vals['ticket_id']:
            if self.ticket_id.id != vals['ticket_id']:
                self.ticket_id.write({'document_asign':False,
                                    'sale_id': 0})
                ticket_new = self.env['bascula.ticket'].browse(vals['ticket_id'])
                ticket_new.write({'document_asign':True,
                                'sale_id':self.sale_id.id})
        res = super(BasculaSaleTicket, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        if self.ticket_id:
            self.ticket_id.write({'document_asign':False,
                                    'sale_id': 0})
        res = super(BasculaSaleTicket, self).unlink()
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tickets_id = fields.One2many('bascula.sale.ticket', 'sale_id', string="Boletas Relacionadas")

    @api.onchange('tickets_id')
    def _onchange_ticket(self):
        vals = []

        for ticket in self.tickets_id:
            if ticket.product_id:
                uom_id = self.env['uom.uom'].search([('name','=','kg')]).id
                vals.append({'product_id': ticket.ticket_id.product_id.id,
                            'product_uom_qty': ticket.ticket_id.net_weight,
                            'product_uom': uom_id,
                            'name': ticket.ticket_id.product_id.display_name})
            else:
                vals.append(False)
        
        
        self.order_line = None
        
        for val in vals:
            if val:
                self.order_line = [(0,0,val)]

#===============================================Transferencias=========================================================        

class BasculaPickingTicket(models.Model):
    _name = 'bascula.picking.ticket'

    ticket_id = fields.Many2one('bascula.ticket', string="Folio")
    product_id = fields.Many2one(related='ticket_id.product_id', string="Producto")
    net_weight = fields.Float(related='ticket_id.net_weight', string="Peso neto")
    picking_id = fields.Many2one('stock.picking')

    @api.model
    def create(self, vals):
        res = super(BasculaPickingTicket, self).create(vals)
        if vals['ticket_id']:
            ticket = self.env['bascula.ticket'].browse(vals['ticket_id'])
            ticket.write({'document_asign':True,
                        'picking_id': vals['picking_id']})
        return res
    
    @api.multi
    def write(self, vals):
        if vals['ticket_id']:
            if self.ticket_id.id != vals['ticket_id']:
                self.ticket_id.write({'document_asign':False,
                                    'picking_id': 0})
                ticket_new = self.env['bascula.ticket'].browse(vals['ticket_id'])
                ticket_new.write({'document_asign':True,
                                'picking_id':self.picking_id.id})
        res = super(BasculaPickingTicket, self).write(vals)
        return res 

    @api.multi
    def unlink(self):
        if self.ticket_id:
            self.ticket_id.write({'document_asign':False,
                                    'picking_id': 0})
        res = super(BasculaPickingTicket, self).unlink()
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tickets_id = fields.One2many('bascula.picking.ticket', 'picking_id', string="Boletas Relacionadas")

    @api.onchange('tickets_id')
    def _onchange_ticket(self):
        vals = []

        for ticket in self.tickets_id:
            if ticket.product_id:
                vals.append({'product_uom_qty': ticket.ticket_id.net_weight,
                            'product_uom': ticket.product_id.uom_id.id,
                            'name': ticket.ticket_id.product_id.display_name,
                            'date_expected': datetime.now(),
                            'product_id': ticket.product_id.id,
                            'is_initial_deman_editable': True,
                            'state': 'draft',
                            'location_id': self.location_id.id,
                            'location_dest_id': self.location_dest_id.id})
            else:
                vals.append(False)
        
        
        self.order_line = None
        
        for val in vals:
            if val:
                self.move_ids_without_package = [(0,0,val)]
    