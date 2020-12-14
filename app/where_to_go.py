from argparse import ArgumentParser
import collections
import json
import logging
from typing import List, Dict, Iterator, Generator, Any, Optional, Union
import requests
from requests.structures import CaseInsensitiveDict


JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

logging.getLogger().setLevel(logging.INFO)


_URL_MAPPING = dict(
    users='https://gist.githubusercontent.com/benjambles/ea36b76bc5d8ff09a51def54f6ebd0cb/raw'
          '/ee1d0c16eaf373cccadd3d5604a1e0ea307b2ca0/users.json',
    venues='https://gist.githubusercontent.com/benjambles/ea36b76bc5d8ff09a51def54f6ebd0cb/raw'
           '/ee1d0c16eaf373cccadd3d5604a1e0ea307b2ca0/venues.json',
)


class GoToWhere:

    def __init__(self, *args, **kwargs):

        self.arg_parser = ArgumentParser()
        self.args = self._set_up_args()

        self.mapping = _URL_MAPPING
        self.cache = {}

    def _set_up_args(self):

        self.arg_parser.add_argument(
            '-n', '--list', help="provide list of inputs in delimited format (like: 'a','a b','c','etc')", type=str,
        )

        self.arg_parser.add_argument(
            "-v", "--verbose", help="increase output verbosity",
            action="store_true"
        )

        return self.arg_parser.parse_args()

    @staticmethod
    def _merge_dicts(dicts: List[Dict[str, str]], default_type: Optional[object] = set) -> Dict:
        """

        :rtype: object Python dictionary of merged records
        """
        merged_dicts = collections.defaultdict(default_type)

        items = list()

        for d in dicts:
            for k, v in d.items():
                if default_type == set:
                    merged_dicts[k].add(v)

                elif default_type == list:
                    if (k, v) not in items:
                        merged_dicts[k].append(v)
                        items.append((k, v))

        return dict(merged_dicts)

    @staticmethod
    def _data_entity_iter(list_data: List[dict], lookup_object: str) -> Generator[dict, Any, None]:
        """
        :param list_data: A list of dictionaries
        :param lookup_object: dictionary key (ex. users, venues etc.)
        :return: python iterator object
        """
        return (i for i in list_data if lookup_object in i.keys())

    @staticmethod
    def dict_subset(input_list, dic_data: CaseInsensitiveDict) -> CaseInsensitiveDict:
        for name in input_list:
            if name not in [key.strip().lower() for key in dic_data.keys()]:
                logging.warning(
                    f"provided entry with the name - {name} is not "
                    f"valid The program will disregard this input"
                )
                input_list.remove(name)

        sub_data = {
            key: value for key, value in dic_data.items() if
            key.strip().lower() in [item.strip().lower() for item in input_list]
        }

        return CaseInsensitiveDict(data=sub_data)

    @staticmethod
    def _convert_results(iter_data: Iterator, rearrange_key: Optional[str] = None) -> Union[list, Dict[Any, dict]]:
        """

        :rtype: object List or Dictionary
        """
        if rearrange_key is None: return list(iter_data)

        processed_dict = dict()

        for idx, i in enumerate(iter_data):

            logging.info(
                f"Processing batch N: {idx}.."
            )
            for val in i.values():
                for d in val:
                    if rearrange_key in d.keys():
                        processed_dict[d[rearrange_key]] = {k: v for k, v in d.items() if k != rearrange_key}

            return processed_dict

    @staticmethod
    def _submit_request(url: str, entity: str) -> Dict:

        logging.info(
            f"Getting `{entity}` data from the following url: {url}"
        )

        res = requests.get(url)

        if res.status_code == 200:
            yield {

                entity: json.loads(res.text)
            }

        else:
            logging.error(
                f"An error occurred while fetching data for entity `{entity}` from {url} url "
                f"Skipping `{entity}` Error code - {res.status_code}. Reason: {res.reason}"
            )

    def _process_data_request(self, entity: Optional[str] = None) -> List:

        if entity:
            return list(self._submit_request(url=self.mapping[entity], entity=entity))

        all_data = list()
        for entity, url in self.mapping.items():

            for i in self._submit_request(url=url, entity=entity):
                all_data.append(i)

        return all_data

    def get_data(self, entity: str, rearrange_on: Optional[str] = None) -> Union[list, Dict[Any, dict]]:

        if entity in self.cache.keys():
            iter_data = self.cache[entity]

        else:
            raw_data = self._process_data_request()
            iter_data = self._data_entity_iter(list_data=raw_data, lookup_object=entity)
            self.cache[entity] = iter_data

        return self._convert_results(iter_data=iter_data, rearrange_key=rearrange_on)

    def _user_preferences(self, _users_data: CaseInsensitiveDict) -> Dict:
        food_user_mappings = list()
        user_drinks_mappings = dict()

        for _user, pref in _users_data.items():
            for item, val in pref.items():
                if item == 'wont_eat':
                    food_user_mappings.append({key.strip().lower(): _user.strip() for key in val})
                elif item == 'drinks':
                    user_drinks_mappings[_user.strip()] = set(v.strip().lower() for v in val)

        return {
            'bad_food_user_mappings': self._merge_dicts(food_user_mappings),
            'user_drinks_mappings': user_drinks_mappings
        }

    def _recommendation(self, venues_data: CaseInsensitiveDict, user_pref: Dict) -> Dict:

        logging.info(
            f"Generating a recommendation report to advise which venues should the team members go."
        )

        places_to_avoid = list()

        for bad_food, _users in user_pref['bad_food_user_mappings'].items():
            for u in _users:
                for venue, available_food in venues_data.items():

                    # Assumption: if the venue offers anything else but what the user won't eat, then
                    # it is assumed that the user is comfortable in visiting that place. However,
                    # if the venue only offers the very food that the user won't eat then it is assumed that
                    # that venue should be avoided...

                    list_of_foods_offered_by_venue = list(set(x.strip().lower() for x in available_food['food']))

                    if ([bad_food] == list_of_foods_offered_by_venue) or (len(list_of_foods_offered_by_venue) == 0):
                        # [bad_food] == list_of_foods_offered_by_venue will return true only when the
                        # venue offers one type of dish and that happens to be the one that the user won't eat.

                        # len(list_of_foods_offered_by_venue) == 0 means that venue doesn't offer anything at all,
                        # hence it should be avoided.

                        places_to_avoid.append({venue: f'There is nothing for {u.split()[0]} to eat.'})

        for _user, drinks in user_pref['user_drinks_mappings'].items():
            for _v_name, available_drinks in venues_data.items():

                set_of_drinks_offered_by_venue = set(x.strip().lower() for x in available_drinks['drinks'])

                if len(set(drinks).intersection(set_of_drinks_offered_by_venue)) == 0:

                    # len(set(drinks).intersection(set_of_drinks_offered_by_venue)) == 0 will return True if
                    # the venue offers none of the drinks that are desired by the users; In either case
                    # this suggests that the team cannot go to that venue.

                    places_to_avoid.append({_v_name: f'There is nothing for {_user.split()[0]} to drink.'})

        avoid_dict = self._merge_dicts(places_to_avoid, default_type=list)

        return {
            'places_to_visit': [v for v in venues_data.keys() if v not in [key for key in avoid_dict.keys()]],
            'places_to_avoid': [{'name': key, 'reason': value} for key, value in avoid_dict.items()]
        }

    def _generate_report(self, participants_list: List, rearrange_on: str = 'name') -> Dict:

        users_data = self.get_data(entity='users', rearrange_on=rearrange_on)
        venues_data = self.get_data(entity='venues', rearrange_on=rearrange_on)

        if isinstance(users_data, dict) and (isinstance(venues_data, dict)):

            users_data = CaseInsensitiveDict(data=users_data)
            venues_data = CaseInsensitiveDict(data=venues_data)

            participants = self.dict_subset(input_list=participants_list, dic_data=users_data)

            participant_preferences = self._user_preferences(_users_data=participants)

            return self._recommendation(venues_data=venues_data, user_pref=participant_preferences)

        else:
            raise NotImplementedError("Not implemented to support lists")

    def runner(self):

        if self.args.list is not None:

            participants = [str(item) for item in self.args.list.split(',')]

        else:
            participants = list()

            while True:

                participant = str(
                    input(
                        "Please provide the names of the attendee "
                        "(ex. Gregory Hill, Mathew Brown, Sophia May, etc) : "
                    )
                )

                participants.extend(participant.split(','))
                end = str(input("Are there any other participants? Yes/No ")).lower()

                if end.lower() == "no":
                    break

        if len(participants) == 0:
            raise ValueError("you must provide list of team members")

        logging.info(
            f"Thank you for providing the names of the participants."
            f"Just to confirm, here are the names of the participant "
            f"that you provided {participants}"
        )

        users = [x.strip().lower() for x in participants]

        return json.dumps(
            [self._generate_report(participants_list=users)], indent=4, sort_keys=False,

        )


if __name__ == '__main__':
    ob = GoToWhere()
    data = ob.runner()
    print(data)

