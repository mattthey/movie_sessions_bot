import requests
import schedule
from bs4 import BeautifulSoup

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


def get_films():
    r = requests.get('https://www.e1.ru/afisha/kino/')
    html_body = r.content.decode('windows-1251')
    soup = BeautifulSoup(html_body, 'html.parser')
    films = []
    for td in soup.find_all('td', attrs=ATTRS_SEARCH):
        film = Film()
        film.title, film.genre = [i.contents[0] for i in td.find_all('font')]
        film.description = td.br.next_element.next_element
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
    global FILMS
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
    print(get_pretty_films(0))
