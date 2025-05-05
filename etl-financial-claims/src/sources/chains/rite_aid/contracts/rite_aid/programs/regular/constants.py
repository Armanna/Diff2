import datetime

## Values
HISTORIC_CONSTANTS_RITE_AID_REGULAR_DICT = {
    'contract_name': 'rite_aid',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2025, 4, 1,  10, 29, 59),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 8.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.60,
                                    'DISP_FEE': 1.75
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'nadac',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 8.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.16,
                                    'DISP_FEE': 1.75
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
            'name': 'first_amendment',
            'valid_from': datetime.datetime(2025, 4, 1, 10, 30, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac_days_supply_equal_or_less_than_60',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (days_supply <= 60)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 8.50
                                },
                                {
                                    'name': 'nadac_days_supply_greater_than_60',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic') & (days_supply > 60)",
                                    'value': 0, # meaning NADAC - 0%
                                    'DISP_FEE': 14.50
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.30,
                                    'DISP_FEE': 1.01
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.17,
                                    'DISP_FEE': 1.01
                                },
                            ],
                            'MARGIN': 6.00
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
    ]
}
