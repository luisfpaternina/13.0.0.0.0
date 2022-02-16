# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import res_neighborhood, res_street


class ResPartner(models.Model):
    _inherit = 'res.partner'

    street_id = fields.Many2one('res.street', string="Calle")
    neighborhood_id = fields.Many2one('res.neighborhood', string="Barrio")
    address_references = fields.Text(
        string="Referencias",
        help="Referencias de la dirección. Indicaciones adicionales para poder encontrar el domicilio con facilidad")
    piso = fields.Char(string="Piso")
    lote = fields.Char(string="Lote")
    manzana = fields.Char(string="Manzana")
    peatonal = fields.Char(string="Peatonal")
    duplex = fields.Char(string="Duplex")
    tira = fields.Char(string="Tira")
    address_display = fields.Char(
        compute="_compute_address_display", store=True, index=True
    )

    @api.depends("street_id", "neighborhood_id", "street_number", "piso", "lote", "manzana", "peatonal", "duplex",
                 "tira", "city_id", "state_id", "zip_id")
    def _compute_address_display(self):
        for partner in self:
            string_address = []
            if partner.street_id.name:
                string_address.append(partner.street_id.name)
                # partner.street = partner.street_id.name
            if partner.street_number:
                string_address.append(' ' + partner.street_number)
            if partner.neighborhood_id.name:
                string_address.append(', ' + partner.neighborhood_id.name)
            if partner.piso:
                string_address.append(' ' + partner.piso)
            if partner.lote:
                string_address.append(' ' + partner.lote)
            if partner.peatonal:
                string_address.append(' ' + partner.peatonal)
            if partner.duplex:
                string_address.append(' ' + partner.duplex)
            if partner.tira:
                string_address.append(' ' + partner.tira)
            if partner.city_id.name:
                string_address.append(' ' + partner.city_id.name)
            if partner.state_id.name:
                string_address.append(' - ' + partner.state_id.name)
            if partner.zip:
                string_address.append(' - CP:' + partner.zip)
            if partner.country_id.name:
                string_address.append(' - ' + partner.country_id.name)

            self.address_display = ''.join(string_address)

    def geo_localize(self):
        # We need country names in English below
        for partner in self.with_context(lang='en_US'):
            result = self._geo_localize(partner.street_id.name + ' ' + partner.street_number,
                                        partner.zip,
                                        partner.city_id.name,
                                        partner.state_id.name,
                                        partner.country_id.name)

            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner)
                })
        return True
