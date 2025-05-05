import datetime
from decimal import Decimal

CVS_TPDM_PROCESSING_FEE = Decimal('0.50') # 50 cents PER CLAIM FEE

## Values
HISTORIC_CONSTANTS_CVS_TPDM_REGULAR_DICT = {
    'contract_name': 'cvs_tpdm',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(2024, 11, 1),
            'valid_to': datetime.datetime(2025, 1, 1, 10, 29, 59),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'mac_days_supply_less_than_84',
                                    'base': "MAC",
                                    'condition': "(brand_generic_flag == 'generic') & (days_supply < 84)",
                                    'value': 0, # meaning MAC - 0%
                                    'DISP_FEE': 17.00
                                },
                                {
                                    'name': 'mac_days_supply_greater_or_equal_to_84',
                                    'base': "MAC",
                                    'condition': "(brand_generic_flag == 'generic') & (days_supply >= 84)",
                                    'value': 0, # meaning MAC - 0%
                                    'DISP_FEE': 21.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'generic')",
                                    'value': 0.18,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'wac_days_supply_less_than_84',
                                    'base': "WAC",
                                    'condition': "(brand_generic_flag == 'brand') & (days_supply < 84)",
                                    'value': -0.01325, # Meaning WAC + 1.325%
                                    'DISP_FEE': 17.00
                                },
                                {
                                    'name': 'wac_days_supply_greater_or_equal_to_84',
                                    'base': "WAC",
                                    'condition': "(brand_generic_flag == 'brand') & (days_supply >= 84)",
                                    'value': -0.01325, # Meaning WAC + 1.325%
                                    'DISP_FEE': 21.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'brand')",
                                    'value': 0.18,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'MARGIN': 6.50
                        }
                    },
                    {
                        'unc': {
                            'generics': {
                                'base': 'UNC',
                                'condition': "(brand_generic_flag == 'generic')",
                            },
                            'brands': {
                                'base': 'UNC',
                                'condition': "(brand_generic_flag == 'brand')",
                            },
                        }
                    },
                ]
            },
        },
        {
            'name': 'tpdm_amendment',
            'valid_from': datetime.datetime(2025, 1, 1, 10, 30, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'mac_days_supply_less_than_84',
                                    'base': "MAC",
                                    'condition': "(brand_generic_flag == 'generic') & (days_supply < 84)",
                                    'value': 0,  # meaning MAC - 0%
                                    'DISP_FEE': 18.00
                                },
                                {
                                    'name': 'mac_days_supply_greater_or_equal_to_84',
                                    'base': "MAC",
                                    'condition': "(brand_generic_flag == 'generic') & (days_supply >= 84)",
                                    'value': 0,  # meaning MAC - 0%
                                    'DISP_FEE': 26.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'generic')",
                                    'value': 0.18,
                                    'DISP_FEE': 18.00
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'wac_days_supply_less_than_84',
                                    'base': "WAC",
                                    'condition': "(brand_generic_flag == 'brand') & (days_supply < 84)",
                                    'value': -0.01325,  # Meaning WAC + 1.325%
                                    'DISP_FEE': 18.00
                                },
                                {
                                    'name': 'wac_days_supply_greater_or_equal_to_84',
                                    'base': "WAC",
                                    'condition': "(brand_generic_flag == 'brand') & (days_supply >= 84)",
                                    'value': -0.01325,  # Meaning WAC + 1.325%
                                    'DISP_FEE': 26.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'brand')",
                                    'value': 0.18,
                                    'DISP_FEE': 18.00
                                },
                            ],
                            'MARGIN': 6.50
                        }
                    },
                    {
                        'unc': {
                            'generics': {
                                'base': 'UNC',
                                'condition': "(brand_generic_flag == 'generic')",
                            },
                            'brands': {
                                'base': 'UNC',
                                'condition': "(brand_generic_flag == 'brand')",
                            },
                        }
                    },
                ]
            },
        }
    ]
}
