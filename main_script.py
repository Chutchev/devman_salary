import requests
import datetime
from dateutil import parser
import terminaltables
from dotenv import load_dotenv
import os


def get_predict_rub_salary(vacancies):
    salaries = []
    for vacancy in vacancies:
        if vacancy['salary'] is not None:
            if vacancy['salary']['currency'] == 'RUR':
                if vacancy['salary']['to'] is None:
                    salaries.append(vacancy['salary']['from'] * 1.2)
                elif vacancy['salary']['from'] is None:
                    salaries.append(vacancy['salary']['to'] * 0.8)
                elif (vacancy['salary']['from'], vacancy['salary']['to']) is not None:
                    salaries.append((vacancy['salary']['to'] + vacancy['salary']['from']) / 2)
    averages = int(sum(salaries)/(len(salaries)))
    return averages


def predict_rub_salary_from_SuperJob(vacancies):
    salaries = []
    for vacancy in vacancies:
        if vacancy['currency'] == 'rub':
            if vacancy['payment_to'] == 0 and vacancy['payment_from'] > 0:
                salaries.append(vacancy['payment_from'] * 0.8)
            elif vacancy['payment_from'] == 0 and vacancy['payment_to'] > 0:
                salaries.append(vacancy['payment_to'] * 1.2)
            elif vacancy['payment_to'] > 0 and vacancy['payment_from'] > 0:
                salaries.append((vacancy['payment_to'] + vacancy['payment_from']) / 2)
    average = int(sum(salaries)/len(salaries))
    return average, len(salaries)


def get_amount_vacancies(languages):
    need_vacancies = {}
    url = "https://api.hh.ru/vacancies"
    for language in languages:
        vacancies = []
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
                if response.json()['found'] > 100 and vacancy['area']['name'] == 'Москва' \
                        and (today-vacancy_date).days < 30:
                    vacancies.append(vacancy)
                    need_vacancies[language] = {'found': response.json()['found'], 'pages':response.json()['pages'],
                                                'vacancy': vacancies}
    return need_vacancies


def get_vacancies_from_SuperJob(language, secret_key):
    vacancies = []
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id':
                   secret_key}  # .env
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
        data = (language, vacancies[language]['found'], vacancies[language]['processed'],
                vacancies[language]['average_salary'])
        table_data.append(data)
    table = terminaltables.AsciiTable(table_data, title)
    print(table.table)

def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    languages = ['Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'GO', 'JS']
    vacancies_HH = get_amount_vacancies(languages)
    vacancies_SJ = {}
    for language in vacancies_HH:
        average = get_predict_rub_salary(vacancies_HH[language]['vacancy'])
        info_for_language = {'found': vacancies_HH[language]['found'], 'processed': len(vacancies_HH[language]['vacancy']),
                             'average_salary': average}
        vacancies_HH[language] = info_for_language
    total = {}
    for language in languages:
        vacancies_SJ[language], total[language] = get_vacancies_from_SuperJob(language, secret_key)
    for language, vacancies_list in vacancies_SJ.items():
        average, processed = predict_rub_salary_from_SuperJob(vacancies_list)
        info_for_language = {'found': total[language], 'processed': processed,
                             'average_salary': average}
        vacancies_SJ[language] = info_for_language
    print_table(vacancies_SJ, 'SuperJob Moscow')
    print_table(vacancies_HH, 'HeadHunter Moscow')


if __name__ == "__main__":
    main()