from odoo import models, fields, api


class ResStreet(models.Model):
    _description = 'Nybble Calle'
    _name = "res.street"
    _order = "name"

    name = fields.Char(string="Nombre de la calle", index=True, required=True, help="Nombre de la calle")
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    external_id = fields.Integer(string='id de calle externo', required=True, index=True,
                                 help="Id de calle externo a Odoo, usado para importaciones de datos de clientes")

    _sql_constraints = [
        (
            "external_id_unique",
            "UNIQUE(external_id)",
            "Ya existe una calle con el identificador externo que está intentando ingresar. "
            "El identidicador externo de la calle debe ser único",
        )
    ]

    @api.model
    def create(self, vals):
        vals['external_id'] = self.env['ir.sequence'].next_by_code('res.street.external_id')
        return super(ResStreet, self).create(vals)
