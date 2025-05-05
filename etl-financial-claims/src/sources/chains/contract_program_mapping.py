import datetime

from sources.chains.cvs.contracts.cvs.programs.regular import cvs_regular
from sources.chains.cvs.contracts.cvs_tpdt.programs.regular import cvs_tpdt_regular
from sources.chains.cvs.contracts.cvs_tpdm.programs.regular import cvs_tpdm_regular
from sources.chains.cvs.contracts.cvs_tpdt.programs.specialty_list import cvs_tpdt_specialty_list
from sources.chains.cvs.contracts.cvs_webmd.programs.regular import cvs_webmd_regular
from sources.chains.cvs.contracts.cvs_famulus.programs.regular import cvs_famulus_regular
from sources.chains.cvs.contracts.cvs_integration_card.programs.regular import cvs_integration_card_regular
from sources.chains.rite_aid.contracts.rite_aid.programs.irreconcilable import rite_aid_irreconcilable
from sources.chains.rite_aid.contracts.rite_aid.programs.regular import rite_aid_regular
from sources.chains.walgreens.contracts.walgreens.programs.regular import walgreens_regular
from sources.chains.walgreens.contracts.wags_finder.programs.regular import wags_finder_regular
from sources.chains.publix.contracts.publix.programs.regular import publix_regular
from sources.chains.walmart.contracts.walmart.programs.regular import walmart_regular
from sources.chains.walmart.contracts.walmart.programs.walmart_4_dollar_list import walmart_4_dollar_list
from sources.chains.kroger.contracts.kroger.programs.regular import kroger_regular
from sources.chains.kroger.contracts.kroger.programs.controlled_schedule_2 import kroger_controlled_schedule_2
from sources.chains.kroger.contracts.kroger.programs.controlled_schedule_3_4_5 import kroger_controlled_schedule_3_4_5
from sources.chains.harris_teeter.contracts.harris_teeter.programs.regular import harris_teeter_regular
from sources.chains.harris_teeter.contracts.harris_teeter.programs.controlled_schedule_2 import harris_teeter_controlled_schedule_2
from sources.chains.harris_teeter.contracts.harris_teeter.programs.controlled_schedule_3_4_5 import harris_teeter_controlled_schedule_3_4_5
from sources.chains.meijer.contracts.meijer.programs.regular import meijer_regular
from sources.chains.health_mart_atlas.contracts.health_mart_atlas.programs.regular import health_mart_atlas_regular

from sources.chains.cvs.contracts.cvs.programs.regular import constants as cvs_regular_constants
from sources.chains.cvs.contracts.cvs_tpdt.programs.regular import constants as cvs_tpdt_regular_constants
from sources.chains.cvs.contracts.cvs_tpdm.programs.regular import constants as cvs_tpdm_regular_constants
from sources.chains.cvs.contracts.cvs_tpdt.programs.specialty_list import constants as cvs_tpdt_specialty_list_constants
from sources.chains.cvs.contracts.cvs_webmd.programs.regular import constants as cvs_webmd_constants
from sources.chains.cvs.contracts.cvs_famulus.programs.regular import constants as cvs_famulus_constants
from sources.chains.cvs.contracts.cvs_integration_card.programs.regular import constants as cvs_integration_card_constants
from sources.chains.rite_aid.contracts.rite_aid.programs.regular import constants as rite_aid_regular_constants
from sources.chains.rite_aid.contracts.rite_aid.programs.irreconcilable import constants as rite_aid_irreconcilable_constants
from sources.chains.walgreens.contracts.walgreens.programs.regular import constants as walgreens_regular_constants
from sources.chains.publix.contracts.publix.programs.regular import constants as publix_regular_constants
from sources.chains.walgreens.contracts.wags_finder.programs.regular import constants as wags_finder_constants
from sources.chains.walmart.contracts.walmart.programs.regular import constants as walmart_regular_constants
from sources.chains.walmart.contracts.walmart.programs.walmart_4_dollar_list import constants as walmart_4_dollar_list_constants
from sources.chains.kroger.contracts.kroger.programs.regular import constants as kroger_regular_constants
from sources.chains.kroger.contracts.kroger.programs.controlled_schedule_2 import constants as kroger_controlled_schedule_2_constants
from sources.chains.kroger.contracts.kroger.programs.controlled_schedule_3_4_5 import constants as kroger_controlled_schedule_3_4_5_constants
from sources.chains.harris_teeter.contracts.harris_teeter.programs.regular import constants as harris_teeter_regular_constants
from sources.chains.harris_teeter.contracts.harris_teeter.programs.controlled_schedule_2 import constants as harris_teeter_controlled_schedule_2_constants
from sources.chains.harris_teeter.contracts.harris_teeter.programs.controlled_schedule_3_4_5 import constants as harris_teeter_controlled_schedule_3_4_5_constants
from sources.chains.meijer.contracts.meijer.programs.regular import constants as meijer_regular_constants
from sources.chains.health_mart_atlas.contracts.health_mart_atlas.programs.regular import constants as health_mart_atlas_constants

from sources.chains.albertsons.contracts.albertsons.programs.regular import constants as albertsons_constants
from sources.chains.albertsons.contracts.albertsons.programs.regular import albertsons_regular
from sources.chains.albertsons.contracts.albertsons_marketplace.programs.regular import constants as albertsons_marketplace_constants
from sources.chains.albertsons.contracts.albertsons_marketplace.programs.regular import albertsons_marketplace_regular

from sources.chains.other_chains import other_chains
from sources.chains.other_chains import constants as other_chains_constants

SOURCE_DICT_CURRENT_CONTRACTS = {  ## Same structure we currently got in etl-pbm-hippo

    ## contract: {programs list}
    'cvs': {
        'regular': {
            'drug_type': cvs_regular.brand_generic_indicator_cvs_regular_vectorized,
            'formulas': cvs_regular_constants.HISTORIC_CONSTANTS_CVS_REGULAR_DICT
        }
    },
    'cvs_tpdt': {
        'regular': {
            'drug_type': cvs_tpdt_regular.brand_generic_indicator_cvs_tpdt_regular_vectorized,
            'formulas': cvs_tpdt_regular_constants.HISTORIC_CONSTANTS_CVS_TPDT_REGULAR_DICT
        },
        'specialty_list': {
            'drug_type': cvs_tpdt_specialty_list.brand_generic_indicator_cvs_tpdt_specialty_vectorized,
            'formulas': cvs_tpdt_specialty_list_constants.HISTORIC_CONSTANTS_CVS_TPDT_SPECIALTY_DICT
        }
    },
    'cvs_tpdm': {
        'regular': {
            'drug_type': cvs_tpdm_regular.brand_generic_indicator_cvs_tpdm_regular_vectorized,
            'formulas': cvs_tpdm_regular_constants.HISTORIC_CONSTANTS_CVS_TPDM_REGULAR_DICT
        }
    },
    'cvs_famulus': {
        'regular': {
            'drug_type': cvs_famulus_regular.brand_generic_indicator_cvs_famulus_regular_vectorized,
            'formulas': cvs_famulus_constants.HISTORIC_CONSTANTS_CVS_FAMULUS_REGULAR_DICT
        }
    },
    'cvs_integration_card': {
        'regular': {
            'drug_type': cvs_integration_card_regular.brand_generic_indicator_cvs_integration_card_regular_vectorized,
            'formulas': cvs_integration_card_constants.HISTORIC_CONSTANTS_CVS_INTEGRATION_CARD_REGULAR_DICT
        }
    },
    'cvs_webmd': {
        'regular': {
            'drug_type': cvs_webmd_regular.brand_generic_indicator_cvs_webmd_regular_vectorized,
            'formulas': cvs_webmd_constants.HISTORIC_CONSTANTS_CVS_WEBMD_REGULAR_DICT
        }
    },
    'rite_aid': {
        'regular': {
            'drug_type': rite_aid_regular.brand_generic_indicator_rite_aid_regular_vectorized,
            'formulas': rite_aid_regular_constants.HISTORIC_CONSTANTS_RITE_AID_REGULAR_DICT
        },
        'irreconcilable':{
            'drug_type': rite_aid_irreconcilable.brand_generic_indicator_rite_aid_irreconcilable_vectorized,
            'formulas': rite_aid_irreconcilable_constants.HISTORIC_CONSTANTS_RITE_AID_IRRECONCILABLE_DICT
        }
    },
    'wags_finder': {
        'regular': {
            'drug_type': wags_finder_regular.brand_generic_indicator_wags_finder_regular_vectorized,
            'formulas': wags_finder_constants.HISTORIC_CONSTANTS_WAGS_FINDER_REGULAR_DICT
        }
    },
    'walgreens': {
        'regular': {
            'drug_type': walgreens_regular.brand_generic_indicator_walgreens_regular_vectorized,
            'formulas': walgreens_regular_constants.HISTORIC_CONSTANTS_WALGREENS_REGULAR_DICT
        }
    },
    'publix': {
        'regular': {
            'drug_type': publix_regular.brand_generic_indicator_publix_regular_vectorized,
            'formulas': publix_regular_constants.HISTORIC_CONSTANTS_PUBLIX_REGULAR_DICT
        }
    },
    'walmart': {
        'regular': {
            'drug_type': walmart_regular.brand_generic_indicator_walmart_regular_vectorized,
            'formulas': walmart_regular_constants.HISTORIC_CONSTANTS_WALMART_REGULAR_DICT
        },
        'four_dollar_list': {
            'drug_type': walmart_4_dollar_list.brand_generic_indicator_walmart_4_dollars_list_vectorized,
            'formulas': walmart_4_dollar_list_constants.HISTORIC_CONSTANTS_WALMART_DICT
        }
    },
    'kroger': {
        'regular': {
            'drug_type': kroger_regular.brand_generic_indicator_kroger_regular_vectorized,
            'formulas': kroger_regular_constants.HISTORIC_CONSTANTS_KROGER_REGULAR_DICT
        },
        'controlled_schedule_2': {
            'drug_type': kroger_controlled_schedule_2.brand_generic_indicator_kroger_controlled_schedule_2_vectorized,
            'formulas': kroger_controlled_schedule_2_constants.HISTORIC_CONSTANTS_KROGER_CONTROLLED_SCHEDULE_2_DICT,
        },
        'controlled_schedule_3_4_5': {
            'drug_type': kroger_controlled_schedule_3_4_5.brand_generic_indicator_kroger_controlled_schedule_3_4_5_vectorized,
            'formulas': kroger_controlled_schedule_3_4_5_constants.HISTORIC_CONSTANTS_KROGER_CONTROLLED_SCHEDULE_3_4_5_DICT
        }
    },
    'harris_teeter': {
        'regular': {
            'drug_type': harris_teeter_regular.brand_generic_indicator_harris_teeter_regular_vectorized,
            'formulas': harris_teeter_regular_constants.HISTORIC_CONSTANTS_HARRIS_TEETER_REGULAR_DICT
        },
        'controlled_schedule_2': {
            'drug_type': harris_teeter_controlled_schedule_2.brand_generic_indicator_harris_teeter_controlled_schedule_2_vectorized,
            'formulas': harris_teeter_controlled_schedule_2_constants.HISTORIC_CONSTANTS_HARRIS_TEETER_CONTROLLED_SCHEDULE_2_DICT
        },
        'controlled_schedule_3_4_5': {
            'drug_type': harris_teeter_controlled_schedule_3_4_5.brand_generic_indicator_harris_teeter_controlled_schedule_3_4_5_vectorized,
            'formulas': harris_teeter_controlled_schedule_3_4_5_constants.HISTORIC_CONSTANTS_HARRIS_TEETER_CONTROLLED_SCHEDULE_3_4_5_DICT
        }
    },
    'meijer': {
        'regular': {
            'drug_type': meijer_regular.brand_generic_indicator_meijer_regular_vectorized,
            'formulas': meijer_regular_constants.HISTORIC_CONSTANTS_MEIJER_REGULAR_DICT
        }
    },
    'health_mart_atlas': {
        'regular': {
            'drug_type': health_mart_atlas_regular.brand_generic_indicator_health_mart_atlas_regular_vectorized,
            'formulas': health_mart_atlas_constants.HISTORIC_CONSTANTS_HEALTH_MART_ATLAS_REGULAR_DICT
        }
    },
    # To uncomment once marketplace is live for albertsons
    # 'albertsons_marketplace': {
    #     'regular': {
    #         'drug_type': albertsons_marketplace_regular.brand_generic_indicator_albertsons_marketplace_regular_vectorized,
    #         'formulas': albertsons_marketplace_constants.HISTORIC_CONSTANTS_ALBERTSONS_MARKETPLACE_REGULAR_DICT
    #     }
    # },
    'albertsons': {
        'regular': {
            'drug_type': albertsons_regular.brand_generic_indicator_albertsons_regular_vectorized,
            'formulas': albertsons_constants.HISTORIC_CONSTANTS_ALBERTSONS_REGULAR_DICT
        }
    },
    'change_healthcare': {
        'regular': {
            'drug_type': other_chains.brand_generic_indicator_other_chains_vectorized,
            'formulas': other_chains_constants.HISTORIC_CONSTANTS_OTHER_CHAINS_CHANGE_HEALTHCARE_REGULAR_DICT
        }
    },
    'out_of_network': {
        'regular': {
            'drug_type': other_chains.brand_generic_indicator_other_chains_vectorized,
            'formulas': other_chains_constants.HISTORIC_CONSTANTS_OTHER_CHAINS_OUT_OF_NETWORK_REGULAR_DICT
        }
    }
}

def extract_start_end_contract_dates(historic_formulas):
    historical_sets = historic_formulas['formulas']['historical_sets']
    earliest_valid_from = min(item['valid_from'] for item in historical_sets)
    latest_valid_to = max(item['valid_to'] for item in historical_sets)
    adjusted_valid_to = latest_valid_to - datetime.timedelta(days=1) # we need to remove one day as valid_to is usual till 10am
    return earliest_valid_from, adjusted_valid_to
