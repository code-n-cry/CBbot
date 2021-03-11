import matplotlib.pyplot as plt
import datetime
from os import remove
from currency_converter import currency_converter
from calendar import monthrange
from cryptocmd import CmcScraper


def str_periods_to_machine(period):
    date_lst = []
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    current_day = datetime.date.today().day
    month_length = monthrange(current_year, current_month)
    period_dct = {
        'Пять лет': [current_year - i for i in range(4, -1, -1)],
        'Год': [(current_month + i, current_year - 1) if current_month + i <= 12 else
                (current_month + i - 12, current_year) for i in range(0, 13)],
        'Месяц': []

    }
    if period == 'Пять лет':
        for year in period_dct['Пять лет']:
            date_lst.append([])
            if year != datetime.date.today().year:
                for month in range(1, 13):
                    date_lst[-1].append(datetime.date(year, month, 1).strftime('%d-%m-%Y'))
            else:
                for month in range(1, datetime.date.today().month + 1):
                    date_lst[-1].append(datetime.date(year, month, 1).strftime('%d-%m-%Y'))
    if period == 'Год':
        for month_and_year in period_dct['Год']:
            date_lst.append(
                datetime.date(month_and_year[1], month_and_year[0], 1).strftime('%d-%m-%Y'))
    return date_lst


def process_five_year_period(date_lst, crypto):
    price_lst = []
    for year in date_lst:
        average_for_year = 0
        for date in year:
            scraper = CmcScraper(crypto, date, date)
            average_for_year += scraper.get_data()[1][0][1]
        if year != date_lst[-1]:
            average_for_year = round(average_for_year / 12, 2)
        else:
            average_for_year = round(average_for_year / datetime.date.today().month, 2)
        price_lst.append(str(average_for_year))
    year_lst = [i[0].split('-')[-1] for i in date_lst]
    return price_lst, year_lst


def process_year_period(date_lst, crypto):
    price_lst = []
    for date in date_lst:
        scraper = CmcScraper(crypto, date, date)
        price_lst.append(scraper.get_data()[1][0][1])
    return price_lst, date_lst


def build_plot(x_axis: list, y_axis: list, name_x: str, name_y: str, title: str):
    plt.plot(x_axis, y_axis)
    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(title)
    plt.savefig('static/img/plot.png')


def main(crypto, fiat, period):
    need_period = str_periods_to_machine(period)
    x, y = None, None
    if period == 'Пять лет':
        x, y = process_five_year_period(need_period, crypto)
    elif period == 'Год':
        x, y = process_year_period(need_period, crypto)
    name_x = f'Курс {crypto} к {fiat}'
    name_y = f'Дата'
    title = f'Изменения цена {crypto} к {fiat} за {period.lower()}'
    build_plot(x, y, name_x, name_y, title)
