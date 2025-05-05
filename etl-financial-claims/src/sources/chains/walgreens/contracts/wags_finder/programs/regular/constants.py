import datetime

## Values

HISTORIC_CONSTANTS_WAGS_FINDER_REGULAR_DICT = {
    'contract_name': 'wags_finder',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants':{
                'sub_programs': [
                    {
                        'regular': {
                            'generics': {
                                'base': "AWP",
                                'condition': "(claims['brand_generic_flag'] == 'generic')",
                                'value': 0.74,
                                'DISP_FEE': 2.00
                            },
                            'brands': [
                                {
                                    'name': 'all_but_ma_and_us_territories',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (~claims['state_abbreviation'].isin(['AK', 'HI', 'AS', 'FM', 'GU', 'MH', 'MP', 'PR', 'PW', 'VI', 'MA']))",
                                    'value': 0.135,
                                    'DISP_FEE': 2.00
                                },
                                {
                                    'name': 'ma',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['state_abbreviation'] == 'MA')",
                                    'value': 0.125,
                                    'DISP_FEE': 2.25
                                },
                                {
                                    'name': 'us_territories',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (claims['state_abbreviation'].isin(['AK', 'HI', 'AS', 'FM', 'GU', 'MH', 'MP', 'PR', 'PW', 'VI']))",
                                    'value': 0.10,
                                    'DISP_FEE': 3.00
                                },
                            ],
                            'MARGIN': 1.50
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
