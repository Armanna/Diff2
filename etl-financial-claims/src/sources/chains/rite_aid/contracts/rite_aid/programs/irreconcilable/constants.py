import datetime

## Values
HISTORIC_CONSTANTS_RITE_AID_IRRECONCILABLE_DICT = {
    'contract_name': 'rite_aid',
    'program_name': 'irreconcilable',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2025, 3, 31, 23, 59, 59),
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
        }
    ]
}
