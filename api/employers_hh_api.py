import requests


class EmployersHeadHunterAPI:
    BASE_URL = 'https://api.hh.ru/employers'

    def __init__(self, area=113):
        # area 113 = Россия
        self.area = area

    def get_employers(self, per_page: int = 10) -> list:
        params = {
            'area': self.area,
            'per_page': per_page,
            'page': 0,
            'sort_by': 'by_vacancies_open'
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()['items']
        employers = []
        for employer in data:
            employers.append({"id": employer["id"],
                              'name': employer['name'],
                              'open_vacancies': employer['open_vacancies'],
                              'alternate_url': employer['alternate_url']
                              })
        return employers
