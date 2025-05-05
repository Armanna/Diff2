import datetime

## Values
HISTORIC_CONSTANTS_CVS_INTEGRATION_CARD_REGULAR_DICT = {
    'contract_name': 'cvs_integration_card',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(2024, 7, 1, 10, 30, 0),
            'valid_to': datetime.datetime(2025, 1, 1, 10, 29, 59),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'regular_generic',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic')",
                                    'value': 0.7600,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'brand_overriden_by_daw_code',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand') & (dispense_as_written == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                    'value': 0.7600,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'awp_days_supply_less_than_90',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'brand') & (dispense_as_written != 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC') & (days_supply < 90)",
                                    'value': 0.15,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'awp_days_supply_more_or_equal_to_90',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'brand') & (dispense_as_written != 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC') & (days_supply >= 90)",
                                    'value': 0.18,
                                    'DISP_FEE': 2.00
                                }
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
            'name': 'fourth_amendment',
            'valid_from': datetime.datetime(2025, 1, 1, 10, 30, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants': {
                'sub_programs': [
                    {
                        'integration_card': {
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
                                    'DISP_FEE': 27.00
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
                                    'DISP_FEE': 27.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(brand_generic_flag == 'brand')",
                                    'value': 0.18,
                                    'DISP_FEE': 18.00
                                },
                            ],
                            'MARGIN': 5.50
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
