from api.employers_hh_api import EmployersHeadHunterAPI
from api.vacancies_hh_api import VacanciesHeadHunterAPI
from database.db_manager import DBManager
from models.vacancy import Vacancy
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn_params = {
    "host": os.getenv('HOST'),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "port": os.getenv('PORT')
}


def create_database(db_name: str):
    """Создаёт базу данных. Сначала удаляет, если такая уже есть"""
    try:
        conn = psycopg2.connect(dbname='postgres', **conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        drop_db_connections_query = f"""SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
          AND pid <> pg_backend_pid();
          """
        cur.execute(drop_db_connections_query)
        cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
        create_db_query = f"""CREATE DATABASE {db_name}"""
        cur.execute(create_db_query)
        print(f'База данных {db_name} создана')
    except psycopg2.Error as error:
        print(f"Ошибка при создании базы данных: {error}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def create_tables(db_name: str):
    """Создаёт таблицы в БД"""
    try:
        conn = psycopg2.connect(database=f'{db_name}', **conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS public.employers
    (id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    open_vacancies INT,
    alternate_url VARCHAR(255) NOT NULL);""")
        print("Таблица employers создана")

        cur.execute("""CREATE TABLE IF NOT EXISTS public.vacancies
            (id INT PRIMARY KEY,
            title VARCHAR(255),
            url TEXT,
            salary_from INT,
            salary_to INT,
            currency VARCHAR(50),
            employer_id INT,
            FOREIGN KEY (employer_id) REFERENCES public.employers(id),
            description TEXT);""")
        print("Таблица vacancies создана")
        employers, vacancies = get_data()
        for employer in employers:
            cur.execute("INSERT INTO employers VALUES (%s, %s, %s, %s)",
                        (int(employer.get('id')), employer.get('name'), employer.get('open_vacancies'),
                         employer.get('alternate_url')))
        print(f'Данные в таблицу employers внесены ({len(employers)}) значений')
        for vacancy in vacancies:
            cur.execute("INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (int(vacancy.get('id')), vacancy.get('title'), vacancy.get('url'),
                         vacancy.get('salary_from'),
                         vacancy.get('salary_to'),
                         vacancy.get('currency'),
                         vacancy.get('employer_id'),
                         vacancy.get('description')))
        print(f'Данные в таблицу vacancies внесены ({len(vacancies)}) значений')
    except psycopg2.Error as error:
        print(f"Ошибка при создании таблицы: {error}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def get_data() -> list:
    """Получает данные с hh_ru"""
    employer_hh_api = EmployersHeadHunterAPI()
    vacancy_hh_api = VacanciesHeadHunterAPI()
    employers = employer_hh_api.get_employers()
    vacancies = []
    for employer in employers:
        raw = vacancy_hh_api.get_vacancies_by_employer_id(employer.get('id'), per_page=10)
        objs = Vacancy.cast_to_object_list(raw)
        vacancies.extend([v.to_dict() for v in objs])
    return employers, vacancies


def drop_database(db_name: str):
    """Удаляет базу данных"""
    try:
        conn = psycopg2.connect(dbname='postgres', **conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        drop_db_connections_query = f"""SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '{db_name}'
  AND pid <> pg_backend_pid();
  """
        cur.execute(drop_db_connections_query)
        cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
        print("База данных удалена")
    except psycopg2.Error as error:
        print(f"Ошибка при создании базы данных: {error}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def main():
    """Запуск точки входа"""
    database_name = 'hh_api'
    create_database(database_name)
    create_tables(database_name)
    db = DBManager('hh_api', os.getenv('USER'), os.getenv('PASSWORD'))
    while True:
        print("HH Vacancies and Employers console. Выберите действие:")
        print("\n1) Получить список всех компаний и количество вакансий у каждой компании.")
        print(
            "2) Получить список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.")
        print("3) Получить среднюю зарплату по вакансиям.")
        print("4) Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям.")
        print(
            "5) Получить список всех вакансий, в названии которых содержатся переданные в метод слова, например python.")
        print("0) Выход")
        choice = input("Введите номер действия: ").strip()
        if choice == "1":
            print(*db.get_companies_and_vacancies_count(), sep='\n')
        elif choice == "2":
            print(*db.get_all_vacancies(), sep='\n')
        elif choice == "3":
            print(db.get_avg_salary())
        elif choice == "4":
            print(*db.get_vacancies_with_higher_salary(), sep='\n')
        elif choice == "5":
            keyword = input(f'Введите ключевое слово: ')
            print(*db.get_vacancies_with_keyword(keyword), sep='\n')
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор")


if __name__ == '__main__':
    main()
