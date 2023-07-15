import json
import os
import random
import time
import db

import requests
from bs4 import BeautifulSoup

from fake_useragent import UserAgent
import asyncio
import aiohttp

ua = UserAgent()


async def get_page(session, p_faculty, p_speciality):
    headers = {'User-Agent': ua.random}
    url = get_url(p_faculty=p_faculty, p_speciality=p_speciality)
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        save_site(p_speciality, response_text)
        save_to_json(p_speciality, response_text)


def get_url(p_inst=0, p_faculty=47, p_speciality=1416, p_typeofstudy=1, p_category=1):
    req = f'https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_inst={p_inst}&p_faculty={p_faculty}&p_speciality={p_speciality}&p_typeofstudy={p_typeofstudy}&p_category={p_category}'
    return req


async def gather_data():
    async with aiohttp.ClientSession() as session:
        with open('data/specialities.json', encoding='utf-8') as f:
            res: dict = json.load(f)
        tasks = []
        for institute, info in res.items():
            faculty: int = info['faculty_code']
            profiles: dict = info['profiles']
            for profile, profile_info in profiles.items():
                profile_code = profile_info['code']
                task = asyncio.create_task(get_page(session, p_faculty=faculty, p_speciality=profile_code))
                tasks.append(task)

        await asyncio.gather(*tasks)


def save_to_json(speciality, html_doc) -> None:
    soup = BeautifulSoup(html_doc, 'html.parser')
    kcp = soup.find(id='t_common')
    if kcp:
        kcp = kcp.find_all('tr')
        res = {}
        for index, tr in enumerate(kcp[2:]):
            tds = tr.find('td').find_next_siblings()
            snils, ege, priority, original = tds[0].text.strip(), tds[-7].text.strip(), tds[-4].text.strip(), tds[
                -3].text.strip()
            res[snils] = {
                'index': index + 1,
                'priority': priority,
                'ege': ege,
                'original': True if original == 'да' else False
            }
        with open(f'../jsons/res_{speciality}.json', 'w') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)


def get_for_snils(snils: str) -> list:
    with open('data/specialities.json', encoding='utf-8') as f:
        res = json.load(f)
    ans = []
    for institute, info in res.items():
        faculty: int = info['faculty_code']
        profiles: dict = info['profiles']
        for profile, profile_info in profiles.items():
            profile_code = profiles[profile]['code']
            profile_count_places = profiles[profile]['count']
            if not os.path.exists(os.path.dirname(__file__) + f'/../jsons/res_{profile_code}.json'):
                continue
            with open(f'../jsons/res_{profile_code}.json') as f:
                spec: dict = json.load(f)
            if not snils in spec.keys():
                continue
            count1 = 0
            count2 = 0
            place1 = 0
            place2 = 0
            originals_count = 0
            originals_place = 0
            for _snils, inform in spec.items():
                if inform['priority'] == '1':
                    count1 += 1
                    count2 += 1
                    if _snils == snils:
                        place2 = count2
                        place1 = count1
                elif inform['priority'] == '2':
                    count2 += 1
                    if _snils == snils:
                        place2 = count2
                if inform['original']:
                    originals_count += 1
                    if _snils == snils:
                        originals_place = originals_count
            if spec[snils]['priority'] == '1':
                spec[snils]['place1'] = place1
                spec[snils]['place2'] = place2
            elif spec[snils]['priority'] == '2':
                spec[snils]['place2'] = place2

            if spec[snils]['original']:
                spec[snils]['original_place'] = originals_place
            spec[snils]['profile'] = f'{institute}.{profile}'
            spec[snils]['count_places'] = profile_count_places
            ans.append(spec[snils])
    return ans


def pretty_results(data: list):
    data.sort(key=lambda x: int(x['priority']))
    s = ''
    for row in data:
        s += f'Приоритет: {row["priority"]}\n'
        s += f'Профиль: {row["profile"]}\n'
        s += f'Место в списке: {row["index"]}\n'
        if row['original']:
            s += f'Место по оригиналам: {row["original_place"]}\n'
        if row['priority'] == '1':
            s += f'Место среди приоритетов `1`: {row["place1"]}\n'
            s += f'Место среди приоритетов `1` и `2`: {row["place2"]}\n'
        if row['priority'] == '2':
            s += f'Место среди приоритетов `1` и `2`: {row["place2"]}\n'
        if row['count_places']:
            s += f'Бюджетных мест: {row["count_places"]}\n'
        s += '--------------------\n'
    return s


def add_count_places():
    with open('data/specialities.json', encoding='utf-8') as f:
        data: dict = json.load(f)
    for institute, info in data.items():
        for profile_name, code in info['profiles'].items():
            info['profiles'][profile_name] = {
                                   "code": code,
                                   "count": None
                               }
    with open('data/specialities.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_site(speciality, html_doc) -> None:
    with open(f'../sites/site_{speciality}.html', 'w', encoding='utf-8') as f:
        f.write(html_doc)


def main():
    asyncio.run(gather_data())


if __name__ == '__main__':
    start_time = time.time()
    # main()
    print(pretty_results(get_for_snils('154-922-757-86')))
    finish_time = time.time() - start_time
    print('Затраченное время: ' + str(finish_time))
