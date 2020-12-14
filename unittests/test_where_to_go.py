import unittest
from requests.structures import CaseInsensitiveDict

from app.where_to_go import GoToWhere


class GoToWhereTest(unittest.TestCase):

    def setUp(self):
        self.ob = GoToWhere()

    def test_init(self):

        raise NotImplementedError()

    def test_set_up_args(self):

        raise NotImplementedError()

    def test_merge_dicts(self):
        # Test with default type equals to set

        input_data_1 = [
            {'fish': 'Danielle Ren'},
            {'eggs': 'Cristiana Lusitano', 'pasta': 'Cristiana Lusitano'},
            {'bread': 'Karol Drewno', 'pasta': 'Karol Drewno'},
            {'mexican': 'Rosie Curran'}
        ]

        expected_1 = {
            'fish': {'Danielle Ren'},
            'eggs': {'Cristiana Lusitano'},
            'pasta': {'Karol Drewno', 'Cristiana Lusitano'},
            'bread': {'Karol Drewno'},
            'mexican': {'Rosie Curran'}
        }

        got_1 = self.ob._merge_dicts(input_data_1, default_type=set)

        self.assertEqual(expected_1, got_1)

        # Test with default type equals to list

        input_data_2 = [
            {'Twin Dynasty': 'There is nothing for Wen to eat.'},
            {'Spirit House': 'There is nothing for Tom to drink.'},
            {'Spirit House': 'There is nothing for Tom to drink.'},
            {'Spirit House': 'There is nothing for Tom to drink.'},
            {'Spirit House': 'There is nothing for Paul to drink.'},
            {'Arms Gardens': 'There is nothing for Paul to drink.'},
            {'Fabrique': 'There is nothing for Wen to drink.'}
        ]

        expected_2 = {
            'Fabrique': [
                'There is nothing for Wen to drink.'
            ],
            'Spirit House': [
                'There is nothing for Tom to drink.',
                'There is nothing for Paul to drink.'
            ],
            'Twin Dynasty': [
                'There is nothing for Wen to eat.'
            ],

            'Arms Gardens': [
                'There is nothing for Paul to drink.'
            ]
        }
        got_2 = self.ob._merge_dicts(input_data_2, default_type=list)

        self.assertEqual(expected_2, got_2)

    def test_data_entity_iter(self):

        raise NotImplementedError()

    def test_dict_subset(self):
        input_list = ['danielle ren', 'tom mullen', 'cristiana lusitano', 'wen li']
        all_data = CaseInsensitiveDict(data={
            'Danielle Ren': {'wont_eat': ['Fish'], 'drinks': ['Cider', 'Rum', 'Soft drinks']},
            'Cristiana Lusitano': {'wont_eat': ['Eggs', 'Pasta'],
                                   'drinks': ['Tequila', 'Soft drinks', 'beer', 'Coffee']},
            'Name1 Surname': {'wont_eat': ['Bread', 'Pasta'], 'drinks': ['Vodka', 'Gin', 'Whisky', 'Rum']},
            'Name2 Surname': {'wont_eat': [], 'drinks': ['Cider', 'Beer', 'Rum', 'Soft drinks']},
            'Tom Mullen': {'wont_eat': ['Meat', 'Fish'], 'drinks': ['Soft drinks', 'Tea']},
            'Name3 Surname': {'wont_eat': ['Mexican'],
                              'drinks': ['Vodka', 'Gin', 'whisky', 'Rum', 'Cider', 'Beer', 'Soft drinks']},
            'Wen Li': {'wont_eat': ['Chinese'], 'drinks': ['Beer', 'cider', 'Rum']}
        }
        )

        expected = CaseInsensitiveDict(data={
            'Danielle Ren': {'wont_eat': ['Fish'], 'drinks': ['Cider', 'Rum', 'Soft drinks']},
            'Cristiana Lusitano': {'wont_eat': ['Eggs', 'Pasta'],
                                   'drinks': ['Tequila', 'Soft drinks', 'beer', 'Coffee']},
            'Tom Mullen': {'wont_eat': ['Meat', 'Fish'], 'drinks': ['Soft drinks', 'Tea']},
            'Wen Li': {'wont_eat': ['Chinese'], 'drinks': ['Beer', 'cider', 'Rum']}
        }
        )

        got = self.ob.dict_subset(input_list=input_list, dic_data=all_data)

        self.assertEqual(expected, got)

    def test_convert_results(self):

        raise NotImplementedError()

    def test_submit_request(self):

        raise NotImplementedError()

    def test_process_data_request(self):

        raise NotImplementedError()

    def test_get_data(self):

        raise NotImplementedError()

    def test_user_preferences(self):

        input_data = CaseInsensitiveDict(data={
            'Danielle Ren': {'wont_eat': ['Fish'], 'drinks': ['Cider', 'Rum', 'Soft drinks']},
            'Cristiana Lusitano': {'wont_eat': ['Eggs', 'Pasta'],
                                   'drinks': ['Tequila', 'Soft drinks', 'beer', 'Coffee']},
            'Tom Mullen': {'wont_eat': ['Meat', 'Fish'], 'drinks': ['Soft drinks', 'Tea']},
            'Wen Li': {'wont_eat': ['Chinese'], 'drinks': ['Beer', 'cider', 'Rum']},
            'foo': {'wont_eat': ['Chinese', 'Meat', 'Fish', 'Eggs', 'Pasta'],
                    'drinks': ['Beer', 'cider', 'Rum', 'Tequila', 'Soft drinks', 'beer', 'Coffee']}
        }
        )

        expected = {
            'bad_food_user_mappings': {
                'fish': {'foo', 'Tom Mullen', 'Danielle Ren'},
                'eggs': {'foo', 'Cristiana Lusitano'},
                'pasta': {'foo', 'Cristiana Lusitano'},
                'meat': {'foo', 'Tom Mullen'},
                'chinese': {'foo', 'Wen Li'}
            },
            'user_drinks_mappings': {
                'Danielle Ren': {'rum', 'cider', 'soft drinks'},
                'Cristiana Lusitano': {'coffee', 'tequila', 'beer', 'soft drinks'},
                'Tom Mullen': {'tea', 'soft drinks'},
                'Wen Li': {'rum', 'cider', 'beer'},
                'foo': {'beer', 'cider', 'coffee', 'rum', 'soft drinks', 'tequila'}
            }

        }

        got = self.ob._user_preferences(input_data)

        self.assertEqual(expected, got)

    def test_recommendation(self):

        input_venues = CaseInsensitiveDict(

            data={
                'El Cantina': {
                    'food': ['Mexican'],
                    'drinks': ['Soft drinks', 'Tequila', 'Beer']
                },
                'Fabrique': {
                    'food': ['Bread', 'Cheese', 'Deli'],
                    'drinks': ['Soft Drinks', 'Tea', 'Coffee']
                },
                "Bad_Food_Place": {
                    'food': ['honey cake'],
                    'drinks': ['Vodka', 'Gin', 'whisky', 'Rum', 'Cider', 'Beer', 'Soft drinks']
                },
                "Bad_Drink_Place": {
                    'food': ['good food'],
                    'drinks': []
                }
            }
        )

        user_pref = {
            'bad_food_user_mappings': {
                    'fish': {'Danielle Ren', 'Tom Mullen'},
                    'eggs': {'Cristiana Lusitano'},
                    'pasta': {'Cristiana Lusitano'},
                    'meat': {'Tom Mullen'},
                    'chinese': {'Wen Li'},
                    'honey cake': {'Danielle Ren', 'Tom Mullen', 'Wen Li', 'Cristiana Lusitano'}
            },
            'user_drinks_mappings': {
                    'Danielle Ren': {'cider', 'rum', 'soft drinks'},
                    'Cristiana Lusitano': {'tequila', 'beer', 'coffee', 'soft drinks', 'cider', 'beer', 'rum'},
                    'Tom Mullen': {'soft drinks', 'tea'},
                    'Wen Li': {'cider', 'beer', 'rum'}
            }
        }

        expected = {
            'places_to_avoid': [
                            {
                                'name': 'Bad_Food_Place',
                                'reason': [
                                         'There is nothing for Cristiana to eat.',
                                         'There is nothing for Wen to eat.',
                                         'There is nothing for Danielle to eat.',
                                         'There is nothing for Tom to eat.'
                                ]
                            },
                            {
                                'name': 'Bad_Drink_Place',
                                'reason': [
                                        'There is nothing for Danielle to drink.',
                                        'There is nothing for Cristiana to drink.',
                                        'There is nothing for Tom to drink.'
                                ]
                            },
                            {
                                'name': 'Fabrique',
                                'reason': [
                                    'There is nothing for Wen to drink.'
                                ]
                            }
                ],
             'places_to_visit': ['El Cantina']
        }

        got = self.ob._recommendation(input_venues, user_pref=user_pref)

        self.assertCountEqual(got, expected)

    def test_generate_report(self):

        raise NotImplementedError()

    def test_runner(self):

        raise NotImplementedError()


if __name__ == '__main__':
    GoToWhereTest()
