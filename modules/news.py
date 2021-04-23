import requests
import os
import bs4
from data import db_session
from data.user import User


class News:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, '
                           'like Gecko) Chrome/27.0.1453.93 Safari/537.36'})
        self.db = '\\'.join(os.getcwd().split('\\')[:-1]) + '\\db\\all_data.sqlite'
        self.link = 'https://ru.investing.com/news/cryptocurrency-news'

    def get_all_news(self):
        news = []
        req = self.session.get(self.link)
        soup = bs4.BeautifulSoup(req.text, 'lxml')
        all_news = soup.find_all('article', {
            'class': ['js-article-item articleItem', 'js-external-link-wrapper articleItem']})[6:-8]
        for elem in all_news:
            if 'js-article-item' in elem.get('class'):
                title = elem.img.get('alt')
                link = 'https://ru.investing.com/' + elem.a.get('href')
                news_soup = bs4.BeautifulSoup(
                    self.session.get(link).text, 'lxml')
                date = news_soup.find('div', {'class': 'contentSectionDetails'}).span.text
                if '(' in date:
                    date = date.split('(')[-1][:-1]
                news.append([title, date, link])
            if 'js-external-link-wrapper' in elem.get('class'):
                title = elem.img.get('alt')
                link = elem.a.get('href')
                news_soup = bs4.BeautifulSoup(
                    self.session.get(link).text, 'lxml')
                try:
                    date = news_soup.find('span', {'class': 'article_date'}).text
                except Exception:
                    date = elem.find('span', {'class': 'date'}).text[3:]
                if '(' in date:
                    date = date.split('(')[-1][:-1]
                news.append([title, date, link])
        return news

    async def send_news(self, bot):
        session = db_session.create_session()
        check = session.query(User).filter(User.news_checked == True).all()
        news = self.get_all_news()
        for elem in check:
            await bot.send_message(int(str(elem).split('\n')[1]), 'Ежедневная рассыка')
            await bot.send_message(int(str(elem).split('\n')[1]), '\n'.join(news[0]))
