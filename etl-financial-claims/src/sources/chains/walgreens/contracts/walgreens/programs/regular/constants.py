import datetime
from decimal import Decimal

## Conditions
IS_GENERIC_CONDITION_STR = "global IS_GENERIC_CONDITION; IS_GENERIC_CONDITION = (claims['brand_generic_flag'] == 'generic')"
IS_BRAND_MA_STATE_CONDITION_STR = "global IS_BRAND_MA_STATE_CONDITION; IS_BRAND_MA_STATE_CONDITION = (claims['brand_generic_flag'] == 'brand') & (claims['state_abbreviation'] == 'MA')"
IS_BRAND_OTHER_STATES_CONDITION_STR = "global IS_BRAND_OTHER_STATES_CONDITION; IS_BRAND_OTHER_STATES_CONDITION = (claims['brand_generic_flag'] == 'brand') & (claims['state_abbreviation'].isin(['AK', 'HI', 'AS', 'FM', 'GU', 'MH', 'MP', 'PR', 'PW', 'VI']))"

## Values

HISTORIC_CONSTANTS_WALGREENS_REGULAR_DICT = {
    'contract_name': 'walgreens',
    'program_name': 'regular',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from': datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2023, 10, 1, 10, 0),
            'dict_constants': {
                'sub_programs': [
                    {
                        'regular': {
                            'generics': {
                                'base': "AWP",
                                'condition': "(claims['brand_generic_flag'] == 'generic')",
                                'value': 0.72,
                                'DISP_FEE': 2.00
                            },
                            'brands': [
                                {
                                    'name': 'all_but_ma_and_us_territories',
                                    'base': "AWP",
                                    'condition': "(claims['brand_generic_flag'] == 'brand') & (~claims['state_abbreviation'].isin(['AK', 'HI', 'AS', 'FM', 'GU', 'MH', 'MP', 'PR', 'PW', 'VI', 'MA']))",
                                    'value': 0.13,
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
        {
            'name': 'second_amendment',
            'valid_from': datetime.datetime(2023, 10, 1, 10, 0),
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
                            'MARGIN': 8.00
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
            }            
        }
    ]
}
