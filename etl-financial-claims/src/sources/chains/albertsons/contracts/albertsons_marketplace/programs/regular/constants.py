import datetime

## Values
HISTORIC_CONSTANTS_ALBERTSONS_MARKETPLACE_REGULAR_DICT = {
    'contract_name': 'albertsons_marketplace',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(2025, 4, 1, 10, 30, 0),
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
                                    'DISP_FEE': 10.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'generic')",
                                    'value': 0.82, # meaning AWP -82%
                                    'DISP_FEE': 2.50
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'nadac',
                                    'base': "NADAC",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0,
                                    'DISP_FEE': 10.00
                                },
                                {
                                    'name': 'awp',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand')",
                                    'value': 0.14,
                                    'DISP_FEE': 2.50
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
