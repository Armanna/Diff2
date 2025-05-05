import datetime

## Values

HISTORIC_CONSTANTS_KROGER_REGULAR_DICT = {
    'contract_name': 'kroger',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from':  datetime.datetime(2024, 5, 15, 10, 0, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
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
                                    'DISP_FEE': 12.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_or_equal_to_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (claims['days_supply'] >= 84)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 15.00
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
                                    'DISP_FEE': 15.00
                                },
                                {
                                    'name': 'nadac_days_supply_more_or_equal_to_84',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['days_supply'] >= 84)",
                                    'value': 0,
                                    'DISP_FEE': 22.50
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
