class Employer:
    def __init__(self, id: str, name: str, open_vacancy: int, url: str):
        self.id = id,
        self.name = name,
        self.open_vacancy = open_vacancy,
        self.url = url

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.title,
            'open_vacancy': self.salary_from,
            'url': self.url
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            name=d.get('name'),
            open_vacancy=d.get('open_vacancy'),
            url=d.get('url')
        )

    def __repr__(self):
        return f"[{self.id}] {self.name} | {self.url} | {self.open_vacancy}"

