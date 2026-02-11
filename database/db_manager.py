import psycopg2
from psycopg2.extras import DictCursor


class DBManager:
    def __init__(self, db_name, user, password, host="localhost", port=5432):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True

    def __del__(self):
        """Закрываем соединение при уничтожении объекта"""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
        query = """
            SELECT e.name AS company, COUNT(v.id) AS vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancies_count DESC;
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием компании, вакансии, зарплаты и ссылки."""
        query = """
            SELECT e.name AS company,
                   v.title AS vacancy,
                   v.salary_from,
                   v.salary_to,
                   v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            ORDER BY v.salary_from DESC NULLS LAST;
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям (по salary_from и salary_to)."""
        query = """
            SELECT AVG((COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0)) / 
                       NULLIF((CASE WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN 2 ELSE 1 END),0)
                      )::NUMERIC(10,2) AS avg_salary
            FROM vacancies v;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        """Получает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT e.name AS company,
                   v.title AS vacancy,
                   v.salary_from,
                   v.salary_to,
                   v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE (COALESCE(v.salary_from,0) + COALESCE(v.salary_to,0)) /
                  NULLIF((CASE WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN 2 ELSE 1 END),0) > %s
            ORDER BY v.salary_from DESC NULLS LAST;
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Получает вакансии, где в названии встречается ключевое слово."""
        query = """
            SELECT e.name AS company,
                   v.title AS vacancy,
                   v.salary_from,
                   v.salary_to,
                   v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE v.title ILIKE %s
            ORDER BY v.salary_from DESC NULLS LAST;
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (f"%{keyword}%",))
            return cur.fetchall()
