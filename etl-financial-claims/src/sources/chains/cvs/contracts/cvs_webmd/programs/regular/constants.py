import datetime

## Values
HISTORIC_CONSTANTS_CVS_WEBMD_REGULAR_DICT = {
    'contract_name': 'cvs_webmd',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'second_amendment',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2024, 1, 1, 10, 0),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'regular_generic',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic') & (is_otc == False)",
                                    'value': 0.7500,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'brand_overriden_by_daw_code',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand') & (is_otc == False) & (dispense_as_written == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                    'value': 0.7500,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'brands': {
                                'base': 'AWP',
                                'condition': "(brand_generic_flag == 'brand') & (is_otc == False) & (dispense_as_written != 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                'value': 0.1255,
                                'DISP_FEE': 2.00
                            },
                            'MARGIN': 6.50
                        }
                    },
                    {
                        'otc': {
                            'generics': [
                                {
                                    'name': 'regular_generic',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic') & (is_otc == True)",
                                    'value': 0.6300,
                                    'DISP_FEE': 3.00
                                },
                                {
                                    'name': 'brand_overriden_by_daw_code',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand') & (is_otc == True) & (dispense_as_written == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                    'value': 0.6300,
                                    'DISP_FEE': 3.00
                                }
                            ],
                            'brands': {
                                'base': 'AWP',
                                'condition': "(brand_generic_flag == 'brand') & (is_otc == True) & (dispense_as_written != 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                'value': 0.1255,
                                'DISP_FEE': 3.00
                            },
                            'MARGIN': 4.00
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
            'name': 'third_amendment',
            'valid_from': datetime.datetime(2024, 1, 1, 10, 0),
            'valid_to': datetime.datetime(2024, 7, 1, 10, 29, 59),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'regular_generic',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic')",
                                    'value': 0.7500,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'brand_overriden_by_daw_code',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand') & (dispense_as_written == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                    'value': 0.7500,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'brands': {
                                'base': 'AWP',
                                'condition': "(brand_generic_flag == 'brand') & (dispense_as_written != 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')",
                                'value': 0.1255,
                                'DISP_FEE': 2.00
                            },
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

