import requests
import datetime
from dateutil import parser
import terminaltables
from dotenv import load_dotenv
import os


def predict_rub_salary(currency, salary_from, salary_to):
    if currency != 'RUR' and currency != 'rub':
        return None
    if (salary_to is None or salary_to == 0) and salary_from > 0:
        return salary_from * 1.2
    elif (salary_from is None or salary_from == 0) and salary_to > 0:
        return salary_to * 0.8
    elif salary_to > 0 and salary_from > 0:
        return (salary_to + salary_from) / 2


def get_required_vacancy_from_HH(language):
    selected_vacancies = {}
    vacancies = []
    url = "https://api.hh.ru/vacancies"
    parameters = {'text': f'программист {language}'}
    pages = requests.get(url, params=parameters).json()['pages']
    for page in range(pages):
        parameters = {'text': f'программист {language}',
                      'per_page': 20, 'page': page}
        response = requests.get(url, params=parameters)
        for vacancy in response.json()['items']:
            vacancy_datetime = parser.parse(vacancy['published_at'])
            today = datetime.date.today()
            vacancy_date = datetime.date(vacancy_datetime.year, vacancy_datetime.month, vacancy_datetime.day)
            if response.json()['found'] > 100:
                if vacancy['area']['name'] == 'Москва' and (today-vacancy_date).days < 30:
                    vacancies.append(vacancy)
                    selected_vacancies[language] = {'found': response.json()['found'], 'pages':response.json()['pages'],
                                                'vacancy': vacancies}
            else:
                break
    if len(vacancies):
        return selected_vacancies[language]
    else:
        return None


def get_vacancies_from_SuperJob(language, secret_key):
    vacancies = []
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id':
                   secret_key}
    page = 0
    pages = 100
    total = 0
    while page != pages:
        params = {'keyword': f'Программист {language}', 'catalogues': 48, 'town': 4, 'page': page, 'count': 100}
        response = requests.get(url, params=params, headers=headers)
        pages = response.json()['total']//100 + 1
        for vacancy in response.json()['objects']:
            vacancies.append(vacancy)
        page += 1
        total = response.json()['total']
    return vacancies, total


def print_table(vacancies, title):
    table_data = [
        ('Language', 'Found', 'Processed', 'Average salary')
    ]
    for language in vacancies:
        if vacancies[language] is not None:
            data = (language, vacancies[language]['found'], vacancies[language]['processed'],
                    vacancies[language]['average_salary'])
            table_data.append(data)
    table = terminaltables.AsciiTable(table_data, title)
    print(table.table)


def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    languages = ['Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'GO', 'JS']
    vacancies_HH = {}
    vacancies_SJ = {}
    total = {}
    print('Сбор необходимых вакансий')
    for language in languages:
        print(language)
        vacancies_HH[language] = get_required_vacancy_from_HH(language)
        vacancies_SJ[language], total[language] = get_vacancies_from_SuperJob(language, secret_key)
    for language, vacancies in vacancies_SJ.items():
        salaries = []
        for vacancy in vacancies:
            currency = vacancy['currency']
            salary_to = vacancy['payment_to']
            salary_from = vacancy['payment_from']
            salary = predict_rub_salary(currency, salary_from, salary_to)
            if salary is not None:
                salaries.append(salary)
        average = int(sum(salaries)/len(salaries))
        info_for_language = {'found': total[language], 'processed': len(salaries),
                                 'average_salary': average}
        vacancies_SJ[language] = info_for_language
    for language, vacancies in vacancies_HH.items():
        salaries = []
        for vacancy in vacancies['vacancy']:
            if vacancy['salary'] is not None:
                salary_to = vacancy['salary']['to']
                salary_from = vacancy['salary']['from']
                currency = vacancy['salary']['currency']
                salary = predict_rub_salary(currency, salary_from, salary_to)
                if salary is not None:
                    salaries.append(salary)
        average = int(sum(salaries)/len(salaries))
        info_for_language = {'found': vacancies_HH[language]['found'],
                             'processed': len(vacancies_HH[language]['vacancy']),
                                     'average_salary': average}
        vacancies_HH[language] = info_for_language
    print_table(vacancies_HH, "HeadHunter Moscow")
    print_table(vacancies_SJ, 'SuperJob Moscow')


if __name__ == "__main__":
    main()