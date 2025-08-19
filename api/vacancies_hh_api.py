import requests


class VacanciesHeadHunterAPI:
    BASE_URL = 'https://api.hh.ru/vacancies'

    def __init__(self, area=113):
        # area 113 = Россия
        self.area = area

    def get_vacancies_by_employer_id(self, employer_id: str, per_page: int = 20) -> list:
        params = {
            'employer_id': employer_id,
            'area': self.area,
            'per_page': per_page,
            'page': 0
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # return list of items
        return data.get('items', [])

if __name__ == '__main__':
    f = VacanciesHeadHunterAPI()
    print(f.get_vacancies_by_employer_id('1942330'))