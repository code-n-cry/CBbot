import matplotlib.pyplot as plt
import datetime
import json
from currency_converter import CurrencyConverter
from calendar import monthrange
from cryptocmd import CmcScraper


def str_periods_to_machine(period):
    date_lst = []
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    previous_month = current_month - 1
    if current_month == 1:
        previous_month = 12
    current_day = datetime.date.today().day
    month_length = monthrange(current_year, previous_month)[1]
    if previous_month == 12:
        month_length = monthrange(current_year - 1, previous_month)[1]
    dates_for_month = []
    for day in range(month_length):
        if current_day + day < month_length + 1:
            if previous_month != 12:
                dates_for_month.append((current_day + day, previous_month, current_year))
            else:
                dates_for_month.append((current_day + day, previous_month, current_year - 1))
        else:
            dates_for_month.append((current_day + day - month_length, current_month, current_year))
    period_dct = {
        'Пять лет': [current_year - i for i in range(4, -1, -1)],
        'Год': [(current_month + i, current_year - 1) if current_month + i <= 12 else
                (current_month + i - 12, current_year) for i in range(0, 13)],
        'Месяц': dates_for_month

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
    if period == 'Месяц':
        for date in period_dct['Месяц']:
            date_lst.append(datetime.date(date[2], date[1], date[0]).strftime('%d-%m-%Y'))
    return date_lst


def convert_fiat_currency(usd_amount: int, currency_code: str):
    converter = CurrencyConverter()
    return converter.convert(usd_amount, 'USD', currency_code)


def process_month_period(date_lst: list, crypto: str):
    price_lst = []
    for date in date_lst:
        scraper = CmcScraper(crypto, date, date)
        price_lst.append(scraper.get_data()[1][0][1])
    return date_lst, price_lst


def process_five_year_period(date_lst: list, crypto: str):
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
    return year_lst, price_lst


def process_year_period(date_lst, crypto):
    price_lst = []
    with open('data/month_names.json', encoding='utf-8') as json_names:
        month_names = json.load(json_names)['Months']
    for date in date_lst:
        scraper = CmcScraper(crypto, date, date)
        price_lst.append(scraper.get_data()[1][0][1])
    first_date_year = date_lst[0].split('-')[-1]
    year_changed = False
    for date_ind in range(len(date_lst)):
        month_name = month_names[date_lst[date_ind].split('-')[1]]
        if date_ind == 0:
            date_lst[date_ind] = f"{month_name}\n{date_lst[date_ind].split('-')[-1]}"
        elif date_lst[date_ind].split('-')[-1] == first_date_year or year_changed:
            date_lst[date_ind] = f"{month_name}"
        elif date_lst[date_ind].split('-')[-1] != first_date_year:
            year_changed = True
            date_lst[date_ind] = f"{month_name}\n{date_lst[date_ind].split('-')[-1]}"
    return date_lst, price_lst


def set_size(pixel_size: tuple):
    return pixel_size[0] * 0.0104166667, pixel_size[1] * 0.0104166667


def build_plot(x_axis: list, y_axis: list, name_x: str, name_y: str, title: str):
    plt.rcParams.update({'font.size': 8})
    fig = plt.figure(figsize=set_size((950, 700)))
    plot = fig.add_subplot(111)
    plot.plot(x_axis, y_axis)
    plot.set_xlabel(name_x)
    plot.set_ylabel(name_y)
    plot.set_title(title)
    fig.savefig('static/img/plot.png')


def main(crypto, fiat, period):
    need_period = str_periods_to_machine(period)
    x, y = None, None
    if period == 'Пять лет':
        x, y = process_five_year_period(need_period, crypto)
    elif period == 'Год':
        x, y = process_year_period(need_period, crypto)
    elif period == 'Месяц':
        x, y = process_month_period(need_period, crypto)
    if fiat != 'USD':
        for amount in range(len(x)):
            y[amount] = convert_fiat_currency(y[amount], fiat)
    name_x = f'Дата'
    name_y = f'Курс {crypto} к {fiat}'
    title = f'Изменения цены {crypto} к {fiat} за {period.lower()}'
    build_plot(x, y, name_x, name_y, title)
