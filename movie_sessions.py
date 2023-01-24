from typing import List
import requests
import schedule
from bs4 import BeautifulSoup
import os
import shutil
from bs4.element import Tag

ATTRS_SEARCH = {
    'valign': 'top',
    'height': '40'
}


class Session:
    def __init__(self):
        self.place = ''
        self.times = []

    def __str__(self) -> str:
        return f"place={self.place}, times={self.times}"


class Film:
    def __init__(self):
        self.title = ''
        self.genre = ''
        self.description = ''
        self.sessions = []

    def __str__(self) -> str:
        return f"title : {self.title}\n" \
               f"genre : {self.genre}\n" \
               f"description :{self.description}\n" \
               f"session : {[str(i) for i in self.sessions]}\n"


MEDIA_DIR_NAME = 'media'


def download_img(url: str, file_name: str) -> None:
    """Скачать картинку с файлом в файл с указанным именем
        :param url адрем для скачивания картинки
        :param file_name имя файла
    """
    if not os.path.exists(MEDIA_DIR_NAME):
        os.mkdir(MEDIA_DIR_NAME)
    response = requests.get(url)
    with open(MEDIA_DIR_NAME + '/' + file_name, 'wb') as f:
        f.write(response.content)


def find_description(element: Tag, wrong_str: List[str]) -> str:
    """Найти описание фильма

    Args:
        element (Tag): элемент от которого надо искать описание фильма
        wrong_str (List[str]): список строк, которые не являются описанием фильма

    Returns:
        str: описание фильма
    """
    cur_element = element
    cur_text = cur_element.text.strip()
    while cur_text == '' or cur_text in wrong_str:
        cur_element = cur_element.next_element
        cur_text = cur_element.text.strip()
    return cur_text


def get_films():
    r = requests.get('https://www.e1.ru/afisha/kino/')
    html_body = r.content.decode('windows-1251')
    soup = BeautifulSoup(html_body, 'html.parser')
    films = []
    for table in soup.find_all('table', attrs={'style': 'padding-bottom: 10px;', 'width': '100%', 'cellspacing': '0', 'border': '0'}):
        url_img = table.find('img').attrs['src']
        download_img(url_img, str(len(films)))
        td = table.find('td', attrs=ATTRS_SEARCH)
        film = Film()
        film.title, film.genre = [i.contents[0].strip()
                                  for i in td.find_all('font')]
        film.description = find_description(td.br, [film.title, film.genre])
        for tr in td.find('table', attrs={'width': '100%'}).find_all('tr'):
            table = tr.find('table')
            if not table:
                continue
            session = Session()
            session.place = table.a.text
            for b in tr.find_all('button'):
                session.times.append(b.text)
            film.sessions.append(session)
        films.append(film)
    return films


FILMS = get_films()


def update_films():
    """Обновить фильмы"""
    global FILMS
    shutil.rmtree(MEDIA_DIR_NAME, ignore_errors=True)
    FILMS = get_films()


schedule.every(1).hour.do(update_films)


def get_pretty_films(id: int = 0) -> str:
    if id < 0 or id >= len(FILMS):
        id = 0
    f = FILMS[id]
    result = f"<b>{f.title}</b>\n" \
             f"Жанры: {f.genre}\n" \
             f"Описание: {f.description}\n" \
             f"Расписание: \n"
    for s in f.sessions:
        result += s.place + f": {', '.join(s.times)}\n"
    return result


if __name__ == '__main__':
    update_films()
    print(get_pretty_films(0))
