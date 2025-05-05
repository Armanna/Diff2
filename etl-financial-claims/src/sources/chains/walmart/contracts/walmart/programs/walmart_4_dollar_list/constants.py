import datetime


# Conditionts

## Values

HISTORIC_CONSTANTS_WALMART_DICT = {
    'contract_name': 'walmart',
    'program_name': 'walmart_4_dollar_list',
    'historical_sets': [
        {
            'name': 'original',
            'valid_from':  datetime.datetime(1900, 1, 1),
            'valid_to': datetime.datetime(2050, 1, 1),
            'dict_constants': {
                'sub_programs': [
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
