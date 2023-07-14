import requests
from bs4 import BeautifulSoup


def main():
    url = 'https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_inst=0&p_faculty=8'
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    options = soup.find('tr').find_next_sibling().find_next_sibling().find('option').find_all('option')
    d = {}
    for opt in options:
        value = int(str(opt)[15:str(opt).find('>') - 1])
        text = opt.text
        if ('(бакалавриат)' in text or '(специалитет)' in text) and '(для приема иностранных граждан)' not in text:
            d[text] = value
    print(d)


if __name__ == '__main__':
    main()
