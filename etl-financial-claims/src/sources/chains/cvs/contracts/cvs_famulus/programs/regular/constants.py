import datetime

## Values
HISTORIC_CONSTANTS_CVS_FAMULUS_REGULAR_DICT = {
    'contract_name': 'cvs_famulus',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(2024, 10, 31, 10, 30, 0),
            'valid_to': datetime.datetime(2024, 10, 31, 10, 29, 59),
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
                                    'value': 0.17,
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
        }        
    ]
}
