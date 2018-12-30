import requests
import datetime
from dateutil import parser


def get_predict_rub_salary(language, pages:int):
    url = "https://api.hh.ru/vacancies"
    salaries = []
    for page in range(pages):
        print(language, page)
        parameters = {'text': f'программист {language}',
                      'per_page': 100, 'page': page}
        response = requests.get(url, params=parameters)
        for vacancy in response.json()['items']:
            if vacancy['salary'] is not None:
                if vacancy['salary']['currency'] == 'RUR':
                    if vacancy['salary']['to'] is None:
                        salaries.append(vacancy['salary']['from'] * 1.2)
                    elif vacancy['salary']['from'] is None:
                        salaries.append(vacancy['salary']['to'] * 0.8)
                    elif (vacancy['salary']['from'], vacancy['salary']['to']) is not None:
                        salaries.append((vacancy['salary']['to'] + vacancy['salary']['from']) / 2)
    averages = int(sum(salaries)/(len(salaries)))
    return averages, len(salaries)


def get_amount_vacancies(languages):
    need_vacancies = {}
    url = "https://api.hh.ru/vacancies"
    for language in languages:
        parameters = {'text': f'программист {language}'}
        print(language)
        pages = requests.get(url, params=parameters).json()['pages']
        for page in range(pages):
            parameters = {'text': f'программист {language}',
                           'per_page': 5, 'page': page}
            response = requests.get(url, params=parameters)
            for vacancy in response.json()['items']:
                vacancy_datetime = parser.parse(vacancy['published_at'])
                today = datetime.date.today()
                vacancy_date = datetime.date(vacancy_datetime.year, vacancy_datetime.month, vacancy_datetime.day)
                if response.json()['found'] > 100 and vacancy['area']['name'] == 'Москва' \
                        and (today-vacancy_date).days < 30:
                    need_vacancies[language] = [response.json()['found'], response.json()['pages']]
    return need_vacancies


def main():
    languages = ['JavaScipt', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'GO']
    vacancies = get_amount_vacancies(languages)
    print(vacancies)
    for language in vacancies.keys():
        average, processed = get_predict_rub_salary(language, vacancies[language][1])
        info_for_language = {'found': vacancies[language][0], 'vacancies_processed': processed, 'average_salary': average}
        vacancies[language] = info_for_language
    print(vacancies)


if __name__ == "__main__":
    main()