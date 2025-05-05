import datetime

## Values
HISTORIC_CONSTANTS_OTHER_CHAINS_CHANGE_HEALTHCARE_REGULAR_DICT = {
    'contract_name': 'change_healthcare',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2024, 3, 1, 10, 0),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'awp',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'mac',
                                    'base': 'MAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'wac',
                                    'base': 'WAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'nadac',
                                    'base': 'NADAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'awp',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand')",
                                },
                                {
                                    'name': 'wac',
                                    'base': 'WAC',
                                    'condition': "(brand_generic_flag == 'brand')",
                                },
                            ],
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

HISTORIC_CONSTANTS_OTHER_CHAINS_OUT_OF_NETWORK_REGULAR_DICT = {
    'contract_name': 'out_of_network',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': [
                                {
                                    'name': 'awp',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'mac',
                                    'base': 'MAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'wac',
                                    'base': 'WAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                                {
                                    'name': 'nadac',
                                    'base': 'NADAC',
                                    'condition': "(brand_generic_flag == 'generic')",
                                },
                            ],
                            'brands': [
                                {
                                    'name': 'awp',
                                    'base': 'AWP',
                                    'condition': "(brand_generic_flag == 'brand')",
                                },
                                {
                                    'name': 'wac',
                                    'base': 'WAC',
                                    'condition': "(brand_generic_flag == 'brand')",
                                },
                            ],
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
