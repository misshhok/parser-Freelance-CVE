import requests
import datetime
import re
import csv
from bs4 import BeautifulSoup, element
HOST = 'https://www.huawei.com'
URL = 'https://www.huawei.com/en/psirt/all-bulletins'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'accept': '/'}


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('div', class_='page-list-box')

    for page in pages:
        number = int(page.find_all('li')[-1].get_text())

    i = 1
    elements = []
    while i <= number:
        # print('time: {} ; iteration: {}'.format(
        #     datetime.datetime.now(tz=None), i))
        url = 'https://www.huawei.com/en/psirt/all-bulletins?page={}'
        r = requests.get(url.format(i), headers=HEADERS, params='')

        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find('ul', class_='result-list').findAll('li')

        for item in items:
            spantag = item.find('span', class_='iconfont icon-20200528-SA-02')

            if spantag is not None:
                title = item.find('h4').get_text().lstrip().rstrip()
                link = item.find('a').get('href')
                paragraph = item.find('p').get_text()

                r = requests.get(HOST+link, headers=HEADERS, params='')
                soup = BeautifulSoup(r.text, 'html.parser')

                cve_block = soup.find(
                    'div', class_='moreinfo active')

                if cve_block is not None:
                    cve_block = cve_block.get_text()

                    cve_replace = re.sub(r'[^\w\s-]', '', cve_block)
                    cve = ', '.join(re.findall(r'(CVE\-\S{1,})', cve_replace))
                else:
                    cve = 'none'

                year = int(paragraph.split('|')[1].split(',')[1])

                if(year >= 2017):
                    elements.append(
                        {
                            'title': title,
                            'link': HOST+link,
                            'paragraph': paragraph,
                            'cve': cve
                        }
                    )
                else:
                    break
        # print('time: {} ; iteration: {}'.format(
        #     datetime.datetime.now(tz=None), i))
        i += 1
    return elements


html = get_html(URL)

result = get_content(html.text)

FILENAME = 'result.csv'
with open(FILENAME, 'w', newline="") as file:
    columns = ['title', 'link', 'paragraph', 'cve']
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(result)
