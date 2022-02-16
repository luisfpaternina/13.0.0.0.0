from odoo import models, fields, api


class ResNeighborhood(models.Model):
    _description = 'Barrio'
    _name = "res.neighborhood"
    _order = "name"

    name = fields.Char(required=True, index=True, help="Nombre del barrio")
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    external_id = fields.Integer(string='id de barrio externo', required=True, index=True,
                                 help="Id de barrio externo a Odoo, usado para importaciones de datos de clientes")

    _sql_constraints = [
        (
            "external_id_unique",
            "UNIQUE(external_id)",
            "Ya existe un barrio con el identificador externo que está intentando ingresar. "
            "El identidicador externo del barrio debe ser único",
        )
    ]

    @api.model
    def create(self, vals):
        vals['external_id'] = self.env['ir.sequence'].next_by_code('res.neighborhood.external_id')
        return super(ResNeighborhood, self).create(vals)
