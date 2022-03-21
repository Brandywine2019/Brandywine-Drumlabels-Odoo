# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class PortalWizard(models.TransientModel):

    _inherit = 'portal.wizard'

    # have to overload this cos it's not very modular :/
    def _default_user_ids(self):
        # for each partner, determine corresponding portal.wizard.user records
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids | partner
            for contact in contact_partners:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal_admin = False
                    in_portal = False
                    if contact.user_ids:
                        in_portal_admin = self.env.ref('bdl_portal.group_portal_admin') in contact.user_ids[0].groups_id
                        in_portal = self.env.ref('base.group_portal') in contact.user_ids[0].groups_id or in_portal_admin
                    user_type = False
                    if in_portal:
                        user_type = 'admin' if in_portal_admin else 'user'
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                        'user_type': user_type,
                    }))
        return user_changes

    # this field must be redefined in order for the new default function to be called
    # this is necessary when the original default function is not called by lambda
    user_ids = fields.One2many('portal.wizard.user', default=_default_user_ids)
    
class PortalWizardUser(models.TransientModel):

    _inherit = 'portal.wizard.user'
    user_type = fields.Selection([('user', 'Client User'), ('admin', 'Client Administrator')], string='Portal User Type')

    @api.onchange('in_portal')
    def _onchange_in_portal(self):
        for user in self:
            if user.in_portal and not user.user_type:
                user.user_type = 'user'
            if not user.in_portal:
                user.user_type = False


    def action_apply(self):
        super(PortalWizardUser, self).action_apply()
        group_portal = self.env.ref('base.group_portal')
        group_portal_admin = self.env.ref('bdl_portal.group_portal_admin')
        for wizard_user in self.sudo().with_context(active_test=False):
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            if wizard_user.in_portal:
                if wizard_user.user_type == 'admin' and wizard_user.user_id and group_portal in wizard_user.user_id.groups_id:
                    # once we make sure that this user is a valid portal user, we can give it admin access now
                    wizard_user.user_id.write({'groups_id': [(4, group_portal_admin.id)]})
                if wizard_user.user_type == 'user' and wizard_user.user_id and group_portal_admin in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'groups_id': [(3, group_portal_admin.id)]})
                    wizard_user.user_id.write({'groups_id': [(4, group_portal.id)]})
            else:
                if user and group_portal_admin in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal_admin.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal_admin.id)]})
                    
