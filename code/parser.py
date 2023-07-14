import json
import os
import random
import time

import requests
from bs4 import BeautifulSoup

from fake_useragent import UserAgent

ua = UserAgent()


def get_request(p_inst=0, p_faculty=47, p_speciality=1416, p_typeofstudy=1, p_category=1):
    headers = {'User-Agent': ua.random}
    time.sleep(random.uniform(1, 3))
    req = f'https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_inst={p_inst}&p_faculty={p_faculty}&p_speciality={p_speciality}&p_typeofstudy={p_typeofstudy}&p_category={p_category}'
    res = requests.get(req, headers=headers)
    return res.text


def get_new_site(speciality=1416, faculty=47) -> None:
    html_doc = get_request(p_speciality=speciality, p_faculty=faculty)
    save_site(speciality, html_doc)


def save_site(speciality, html_doc) -> None:
    with open(f'../sites/site_{speciality}.html', 'w', encoding='utf-8') as f:
        f.write(html_doc)


def save_to_json(speciality=1416) -> None:
    with open(f'../sites/site_{speciality}.html', 'r', encoding='utf-8') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    kcp = soup.find(id='t_common')
    if kcp:
        kcp = kcp.find_all('tr')
        res = {}
        for index, tr in enumerate(kcp[2:]):
            tds = tr.find('td').find_next_siblings()
            snils, ege, priority = tds[0].text.strip(), tds[-7].text.strip(), tds[
                -4].text.strip()
            res[snils] = {
                'index': index + 1,
                'priority': priority,
                'ege': ege
            }
        with open(f'../jsons/res_{speciality}.json', 'w') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)


def get_all() -> None:
    with open('../../../Desktop/code/data/specialities.json', encoding='utf-8') as f:
        res: dict = json.load(f)
    for institute, info in res.items():
        print(institute)
        faculty: int = info['faculty_code']
        profiles: dict = info['profiles']
        for profile, profile_code in profiles.items():
            print(profile)
            get_new_site(profile_code, faculty)
            save_to_json(profile_code)


def find_by_snils(snils, speciality=1416) -> dict:
    with open(f'../jsons/res_{speciality}.json', encoding='utf-8') as f:
        res = json.load(f)
    return res[snils]


def get_for_snils(snils: str) -> list:
    with open('../../../Desktop/code/data/specialities.json', encoding='utf-8') as f:
        res = json.load(f)
    ans = []
    for institute, info in res.items():
        faculty: int = info['faculty_code']
        profiles: dict = info['profiles']
        for profile, profile_code in profiles.items():
            if os.path.exists(os.path.dirname(__file__) + f'/../jsons/res_{profile_code}.json'):
                with open(f'../jsons/res_{profile_code}.json') as f:
                    spec: dict = json.load(f)
                if snils in spec.keys():
                    spec[snils]['profile'] = f'{institute}.{profile}'
                    ans.append(spec[snils])
    return ans


def pretty_results(data: list):
    data.sort(key=lambda x: x['priority'])
    s = ''
    for row in data:
        s += f'Приоритет: {row["priority"]}\n'
        s += f'Профиль: {row["profile"]}\n'
        s += f'Место в списке: {row["index"]}\n'
        s += '--------------------\n'
    return s


if __name__ == '__main__':
    # snils = input('Введите Ваш СНИЛС')
    # snils = '154-922-757-86'
    # res = pretty_results(get_for_snils(snils))
    # print(res)
    get_all()