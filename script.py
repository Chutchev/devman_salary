import requests
import datetime
from dateutil import parser


def get_predict_rub_salary(language):
    url = "https://api.hh.ru/vacancies"
    print(language)
    parameters = {'text': f'программист {language}'}
    response = requests.get(url, params=parameters)
    for vacancy in response.json()['items']:
        if vacancy['salary'] is not None:
            if vacancy['salary']['currency'] == 'RUR':
                if vacancy['salary']['to'] is None:
                    print(f"\t{vacancy['salary']['from'] * 1.2}")
                elif vacancy['salary']['from'] is None:
                    print(f"\t{vacancy['salary']['to'] * 0.8}")
                elif (vacancy['salary']['from'], vacancy['salary']['to']) is not None:
                    salary = (vacancy['salary']['to'] + vacancy['salary']['from']) / 2
                    print(f"\t{salary}")
            else:
                print(f"\t{None}")


def get_amount_vacancies(languages):
    need_vacancies = {}
    url = "https://api.hh.ru/vacancies"
    for language in languages:
        parameters = {'text': f'программист {language}'}
        response = requests.get(url, params=parameters)
        if response.json()['found'] > 100:
            need_vacancies[language] = response.json()['found']
    return need_vacancies


def get_programmer_vacancies(languages):
    url = "https://api.hh.ru/vacancies"
    for language in languages:
        parameters = {'text': f'программист {language}'}
        print(language)
        response = requests.get(url, params=parameters)
        for vacancy in response.json()['items']:
            vacancy_datetime = parser.parse(vacancy['published_at'])
            today = datetime.date.today()
            vacancy_date = datetime.date(vacancy_datetime.year, vacancy_datetime.month, vacancy_datetime.day)
            if vacancy['area']['name'] == 'Москва' and (today-vacancy_date).days < 30:
                print(f'\t{vacancy}')


def main():
    languages = ['JavaScipt', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'GO']
    #get_programmer_vacancies(languages)
    vacancies, count = get_amount_vacancies(languages)
    print(vacancies)
    for language in vacancies.keys():
        get_predict_rub_salary(language)


if __name__ == "__main__":
    main()