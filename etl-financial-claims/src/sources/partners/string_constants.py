PARTNER_GROUPS_EXCLUDED_FROM_OTHER = ['Dr First', 'Rcopia', 'GoodRx', 'cvs_tpdt', 'webmd', 'famulus', 'caprx', 'rxpartner', 'waltz', 'fam_cvs_tpdt', 'direct', 'smart', 'wags_finder', 'rxlink', 'direct-mail', 'buzzrx', 'buzzrx_tpdt'] # partners excluded from Other based on the Partner Financials logic
DR_FIRST_PARTNERS = ['Rcopia', 'Dr First'] # Dr First partners
IS_IN_NETWORK_PARTNERS = ['other', 'Dr First', 'Rcopia', 'rxlink'] # partners that use is_in_network flag
DIRECT_PARTNER = ['platform','hippo','web','twilio','*.hippo.engineering','test','Account not found','google web flow',
                                'tester','hippo-H','friend referral','coronavirus','warrior'] # list of the partners grouped under the partner name Direct

def get_partner_group(partner):
    if partner in DIRECT_PARTNER:
        return 'direct'
    if partner in PARTNER_GROUPS_EXCLUDED_FROM_OTHER:
        if partner in ['fam_cvs_tpdt', 'buzzrx_tpdt']:
            return 'cvs_tpdt'
        if partner == 'buzzrx':
            return 'cvs_tpdm'
        if partner in ['smart', 'direct-mail']:
            return 'Save.Health'
        return partner
    return 'other'
