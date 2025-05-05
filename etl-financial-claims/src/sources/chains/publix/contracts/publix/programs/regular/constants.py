import datetime

## Values
HISTORIC_CONSTANTS_PUBLIX_REGULAR_DICT = {
    'contract_name': 'publix',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(2024, 8, 1, 10, 30, 0),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'nadac',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0,
                                    'DISP_FEE': 12.00
                                },
                                {
                                    'name': 'wac',
                                    'base': "WAC",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0,
                                    'DISP_FEE': 12.00
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.13,
                                    'DISP_FEE': 2.50
                                },
                            ],
                            'MARGIN': 7.00
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
