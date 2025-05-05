import datetime

## Values
HISTORIC_CONSTANTS_CVS_TPDT_SPECIALTY_DICT = {
    'contract_name': 'cvs_tpdt',
    'program_name': 'specialty_list',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2024, 1, 1, 10, 0),
            'dict_constants':{
                'sub_programs': [
                    {
                        'specialty': {
                            'generics': {
                                'base': 'AWP',
                                'condition': "(brand_generic_flag == 'generic') & (is_otc == False)",
                                'value': 0.8900,
                                'DISP_FEE': 2.00
                            },
                            'brands': [
                                {
                                    'name': 'days_supply_less_than_90',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand') & (claims['is_otc'] == False) & (claims['days_supply'] < 90)",
                                    'value': 0.1600,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'days_supply_greater_or_equal_to_90',
                                    'base': 'AWP',
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['is_otc'] == False) & (claims['days_supply'] >= 90)",
                                    'value': 0.1800,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'MARGIN': 3.00
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
            'name': 'second_amendment',
            'valid_from': datetime.datetime(2024, 1, 1, 10, 0),
            'valid_to': datetime.datetime(2024, 4, 1, 10, 0),
            'dict_constants':{
                'sub_programs': [
                    {
                        'specialty': {
                            'generics': {
                                'base': 'AWP',
                                'condition': "(claims['brand_generic_flag'] == 'generic')",
                                'value': 0.8800,
                                'DISP_FEE': 2.00
                            },
                            'brands': [
                                {
                                    'name': 'days_supply_less_than_90',
                                    'base': 'AWP',
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] < 90)",
                                    'value': 0.1600,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'days_supply_greater_or_equal_to_90',
                                    'base': 'AWP',
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] >= 90)",
                                    'value': 0.1800,
                                    'DISP_FEE': 2.00
                                },
                            ],
                            'MARGIN': 3.00
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
