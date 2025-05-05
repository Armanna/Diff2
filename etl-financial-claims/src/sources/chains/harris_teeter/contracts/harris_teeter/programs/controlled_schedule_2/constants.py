import datetime

## Values

HISTORIC_CONSTANTS_HARRIS_TEETER_CONTROLLED_SCHEDULE_2_DICT = {
    'contract_name': 'harris_teeter',
    'program_name': 'controlled_schedule_2',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from':  datetime.datetime(2024, 5, 15, 10, 0, 0),
            'valid_to': datetime.datetime(2025, 1, 3, 10, 29, 59),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac_days_supply_less_than_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] < 84)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 20.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_or_equal_to_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] >= 84)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 25.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.2,
                                    'DISP_FEE': 5
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'nadac_days_supply_less_than_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] < 84)",
                                    'value': 0,
                                    'DISP_FEE': 25.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_or_equal_to_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] >= 84)",
                                    'value': 0,
                                    'DISP_FEE': 35.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.13,
                                    'DISP_FEE': 5
                                },
                            ],
                            'MARGIN': 4.00
                        }
                    },
                    {
                        'unc': {
                            'generics': {
                                'base': 'UNC',
                                'condition': "(claims['brand_generic_flag'] == 'generic')",
                            },
                            'brands': {
                                'base': 'UNC',
                                'condition': "(claims['brand_generic_flag'] == 'brand')",
                            },
                        }
                    }      
                ]
            },
        },
        {
            'name': 'first amendment',
            'valid_from':  datetime.datetime(2025, 1, 3, 10, 30, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'mac_days_supply_less_than_84',
                                    'base': "MAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] < 84)",
                                    'value': 0, # meaning MAC - 0%
                                    'DISP_FEE': 20.00
                                },
                                {
                                    'name': 'mac_days_supply_more_or_equal_to_84',
                                    'base': "MAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] >= 84)",
                                    'value': 0, # meaning MAC - 0%
                                    'DISP_FEE': 25.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.2,
                                    'DISP_FEE': 5
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'mac_days_supply_less_than_84',
                                    'base': "MAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] < 84)",
                                    'value': 0,
                                    'DISP_FEE': 25.00
                                },
                                {
                                    'name': 'mac_days_supply_more_or_equal_to_84',
                                    'base': "MAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] >= 84)",
                                    'value': 0,
                                    'DISP_FEE': 35.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.13,
                                    'DISP_FEE': 5
                                },
                            ],
                            'MARGIN': 4.00
                        }
                    },
                    {
                        'unc': {
                            'generics': {
                                'base': 'UNC',
                                'condition': "(claims['brand_generic_flag'] == 'generic')",
                            },
                            'brands': {
                                'base': 'UNC',
                                'condition': "(claims['brand_generic_flag'] == 'brand')",
                            },
                        }
                    }      
                ]
            },
        }
    ]
}
