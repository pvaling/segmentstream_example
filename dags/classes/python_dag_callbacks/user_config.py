# Mock Configs
def get_config():

    configs = [
        {
            'user': 'u1',
            'params': {
                'shops': [1,2,3],
                'conversion': True,
                'prediction_depth': 7
            }
        },
        {
            'user': 'u2',
            'params': {
                'shops': [1, 3],
                'conversion': False,
                'prediction_depth': 3
            }
        }
    ]
    return configs