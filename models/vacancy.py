import uuid
from typing import List

class Vacancy:
    def __init__(self, title: str, url: str, salary_from=None, salary_to=None, currency=None, description='', employer_id='', vacancy_id=None):
        self.title = title or 'No title'
        self.url = url or ''
        # Salary fields normalized to numbers or None
        self.salary_from = self._validate_salary(salary_from)
        self.salary_to = self._validate_salary(salary_to)
        self.currency = currency or 'RUB'
        self.description = description or ''
        self.employer_id = employer_id or ''
        # unique id
        self.id = vacancy_id or str(uuid.uuid4())

    def _validate_salary(self, val):
        try:
            if val is None or val == '':
                return None
            # if string like "100000" or "100000-150000"
            if isinstance(val, str):
                v = val.replace('\xa0', '').replace(' ', '')
                if '-' in v:
                    parts = v.split('-')
                    return int(parts[0]) if parts[0].isdigit() else None
                if v.isdigit():
                    return int(v)
                return None
            if isinstance(val, (int, float)):
                return int(val)
        except Exception:
            return None

    @property
    def avg_salary(self):
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        if self.salary_from:
            return self.salary_from
        if self.salary_to:
            return self.salary_to
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'salary_from': self.salary_from,
            'salary_to': self.salary_to,
            'currency': self.currency,
            'description': self.description,
            'employer_id': self.employer_id
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            title=d.get('title'),
            url=d.get('url'),
            salary_from=d.get('salary_from'),
            salary_to=d.get('salary_to'),
            currency=d.get('currency'),
            description=d.get('description'),
            employer_id=d.get('employer_id'),
            vacancy_id=d.get('id')
        )

    def __lt__(self, other):
        return self.avg_salary < other.avg_salary

    def __repr__(self):
        sal = f"{self.salary_from or '—'}-{self.salary_to or '—'} {self.currency}" if (self.salary_from or self.salary_to) else "Зарплата не указана"
        return f"[{self.id}] {self.title} | {sal} | {self.employer_id} | {self.url}"

    @staticmethod
    def cast_to_object_list(items: List[dict]):
        res = []
        for it in items:
            # hh.ru structure: 'name', 'alternate_url', 'salary' dict
            name = it.get('name')
            url = it.get('alternate_url')
            salary = it.get('salary') or {}
            employer = it.get('employer') or {}
            sal_from = salary.get('from') if isinstance(salary, dict) else None
            sal_to = salary.get('to') if isinstance(salary, dict) else None
            cur = salary.get('currency') if isinstance(salary, dict) else None
            descr = it.get('snippet', {}).get('responsibility') or it.get('snippet', {}).get('requirement') or ''
            employer_id = employer.get('id') if isinstance(employer, dict) else None
            v = Vacancy(title=name, url=url, salary_from=sal_from, salary_to=sal_to, currency=cur, description=descr, employer_id=employer_id, vacancy_id=str(it.get('id')))
            res.append(v)
        return res
