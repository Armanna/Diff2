import datetime

## Values

HISTORIC_CONSTANTS_WALMART_REGULAR_DICT = {
    'contract_name': 'walmart',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from':  datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2024, 9, 2, 23, 59, 59),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac_days_supply_less_or_equal_to_60',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] <= 60)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 8.50
                                },
                                {
                                    'name': 'nadac_days_supply_more_than_60_less_or_equal_to_120',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] > 60) & (claims['days_supply'] <= 120)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 15.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_than_120',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] > 120)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 40.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.2,
                                    'DISP_FEE': 1.01
                                },
                            ],
                            'brands': {
                                'base': "AWP",
                                'condition': "(claims['brand_generic_flag'] == 'brand')",
                                'value': 0.135,
                                'DISP_FEE': 1.01
                            },
                            'MARGIN': 6.00
                        }
                    },
                    {
                        'unc': {
                            'generics': [
                                {
                                    'name': 'regular_unc',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') and (claims['usual_and_customary_charge'] > 400)",
                                },
                                {
                                    'name': 'less_or_equal_to_$4',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') and (claims['usual_and_customary_charge'] <= 400)",
                                }
                            ],
                            'brands': [
                                {
                                    'name': 'regular_unc',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') and (claims['usual_and_customary_charge'] > 400)",
                                },
                                {
                                    'name': 'less_or_equal_to_$4',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') and (claims['usual_and_customary_charge'] <= 400)",
                                }
                            ]
                        }
                    }      
                ]
            },
        },
        {
            'name': 'second_original',
            'valid_from': datetime.datetime(2024, 9, 3, 0, 0, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac_days_supply_less_or_equal_to_60',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] <= 60)",
                                    'value': 0,
                                    'DISP_FEE': 9.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_than_60',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] > 60)",
                                    'value': 0,
                                    'DISP_FEE': 16.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.2,
                                    'DISP_FEE': 1.01
                                },
                            ],
                            'brands': {
                                'base': "AWP",
                                'condition': "(claims['brand_generic_flag'] == 'brand')",
                                'value': 0.135,
                                'DISP_FEE': 1.01
                            },
                            'MARGIN': 4.50
                        }
                    },
                    {
                        'unc': {
                            'generics': [
                                {
                                    'name': 'regular_unc',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') and (claims['usual_and_customary_charge'] > 400)",
                                },
                                {
                                    'name': 'less_or_equal_to_$4',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') and (claims['usual_and_customary_charge'] <= 400)",
                                }
                            ],
                            'brands': [
                                {
                                    'name': 'regular_unc',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') and (claims['usual_and_customary_charge'] > 400)",
                                },
                                {
                                    'name': 'less_or_equal_to_$4',
                                    'base': "UNC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') and (claims['usual_and_customary_charge'] <= 400)",
                                }
                            ]
                        }
                    }      
                ]
            },
        }
    ]
}
