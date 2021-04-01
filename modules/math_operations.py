import matplotlib.pyplot as plt
import datetime
import json
import os
from currency_converter import CurrencyConverter
from calendar import monthrange
import pymorphy2
from cryptocmd import CmcScraper


class MathOperations:
    def __init__(self, period: str, crypto: str, fiat: str, plot_img_name: str):
        self.morph = pymorphy2.MorphAnalyzer()
        self.converter = CurrencyConverter()
        with open('static/json/month_names.json',
                  encoding='utf-8') as json_names:
            self.month_names = json.load(json_names)['Months']
        self.date_lst = []
        self.period = period
        self.crypto = crypto
        self.fiat = fiat
        self.img_name = plot_img_name

    def str_periods_to_machine(self):
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        previous_month = current_month - 1
        if previous_month == 0:
            previous_month = 12
        current_day = datetime.date.today().day
        previous_month_length = monthrange(current_year, previous_month)[1]
        if previous_month == 12:
            previous_month_length = monthrange(current_year - 1, previous_month)[1]
        if self.period == 'Пять лет':
            date_for_five_years = [current_year - i for i in range(4, -1, -1)]
            for year in date_for_five_years:
                self.date_lst.append([])
                if year != datetime.date.today().year:
                    for month in range(1, 13):
                        self.date_lst[-1].append(datetime.date(year, month, 1).strftime('%d-%m-%Y'))
                else:
                    for month in range(1, datetime.date.today().month + 1):
                        self.date_lst[-1].append(datetime.date(year, month, 1).strftime('%d-%m-%Y'))
        if self.period == 'Год':
            date_for_year = [(current_month + i, current_year - 1) if current_month + i <= 12 else
                             (current_month + i - 12, current_year) for i in range(0, 13)]
            for month_and_year in date_for_year:
                self.date_lst.append(
                    datetime.date(month_and_year[1], month_and_year[0], 1).strftime('%d-%m-%Y'))
        if self.period == 'Месяц':
            dates_for_month = []
            for day in range(previous_month_length):
                if current_day + day < previous_month_length + 1:
                    if previous_month != 12:
                        dates_for_month.append((current_day + day, previous_month, current_year))
                    else:
                        dates_for_month.append((current_day + day, previous_month, current_year - 1))
                else:
                    dates_for_month.append(
                        (current_day + day - previous_month_length, current_month, current_year))
            for date in dates_for_month:
                self.date_lst.append(datetime.date(date[2], date[1], date[0]).strftime('%d-%m-%Y'))
        if self.period == 'Неделя':
            dates_for_week = []
            date = current_day - 7
            if date > 0:
                for day in range(date, current_day):
                    dates_for_week.append((day, current_month, current_year))
            if date < 0:
                begin_date = previous_month_length + date
                for day in range(begin_date, begin_date + 7):
                    year = current_year
                    if previous_month == 12:
                        year = current_year - 1
                    if day <= previous_month_length:
                        dates_for_week.append((day, previous_month, year))
                    else:
                        dates_for_week.append(
                            (day - previous_month_length, current_month, current_year))
            for date in dates_for_week:
                self.date_lst.append(datetime.date(date[2], date[1], date[0]).strftime('%d-%m-%Y'))

    def convert_fiat_currency(self, usd_amount):
        return self.converter.convert(usd_amount, 'USD', self.fiat)

    def process_five_year_period(self):
        price_lst = []
        for year in self.date_lst:
            average_for_year = 0
            for date in year:
                scraper = CmcScraper(self.crypto, date, date)
                average_for_year += scraper.get_data()[1][0][1]
            if year != self.date_lst[-1]:
                average_for_year = round(average_for_year / 12, 2)
            else:
                average_for_year = round(average_for_year / datetime.date.today().month, 2)
            price_lst.append(str(average_for_year))
        year_lst = [i[0].split('-')[-1] for i in self.date_lst]
        return year_lst, price_lst

    def process_year_period(self):
        price_lst = []
        year_changed = False
        first_date_year = self.date_lst[0].split('-')[-1]
        print(self.date_lst)
        for date in self.date_lst:
            scraper = CmcScraper(self.crypto, date, date)
            price_lst.append(scraper.get_data()[1][0][1])
        for date_ind in range(len(self.date_lst)):
            month_name = self.month_names[self.date_lst[date_ind].split('-')[1]]
            if date_ind == 0:
                self.date_lst[date_ind] = f"{month_name}\n{self.date_lst[date_ind].split('-')[-1]}"
            elif self.date_lst[date_ind].split('-')[-1] == first_date_year or year_changed:
                self.date_lst[date_ind] = f"{month_name}"
            elif self.date_lst[date_ind].split('-')[-1] != first_date_year:
                year_changed = True
                self.date_lst[date_ind] = f"{month_name}\n{self.date_lst[date_ind].split('-')[-1]}"
        return self.date_lst, price_lst

    def process_month_period(self):
        price_lst = []
        month_changed = False
        first_date_month = self.date_lst[0].split('-')[1]
        for date in self.date_lst:
            scraper = CmcScraper(self.crypto, date, date)
            price_lst.append(scraper.get_data()[1][0][1])
        for date_ind in range(len(self.date_lst)):
            month_name = self.month_names[self.date_lst[date_ind].split('-')[1]]
            need_case = self.morph.parse(month_name)[0].inflect({'gent'}).word.capitalize()
            year = self.date_lst[date_ind].split('-')[2]
            day = self.date_lst[date_ind].split('-')[0]
            if date_ind == 0:
                self.date_lst[date_ind] = f"{day}\n{need_case}\n{year}"
            elif self.date_lst[date_ind].split('-')[1] == first_date_month or month_changed:
                self.date_lst[date_ind] = f"{day}"
            elif self.date_lst[date_ind].split('-')[1] != first_date_month:
                month_changed = True
                self.date_lst[date_ind] = f"{day}\n{need_case}\n{year}"
        return self.date_lst, price_lst

    def process_week_period(self):
        price_lst = []
        month_changed = False
        first_date_month = self.date_lst[0].split('-')[1]
        for date in self.date_lst:
            scraper = CmcScraper(self.crypto, date, date)
            price_lst.append(scraper.get_data()[1][0][1])
        for date_ind in range(len(self.date_lst)):
            month_name = self.month_names[self.date_lst[date_ind].split('-')[1]]
            need_case = self.morph.parse(month_name)[0].inflect({'gent'}).word.capitalize()
            year = self.date_lst[date_ind].split('-')[2]
            day = self.date_lst[date_ind].split('-')[0]
            if date_ind == 0:
                self.date_lst[date_ind] = f"{day}\n{need_case}\n{year}"
            elif self.date_lst[date_ind].split('-')[1] == first_date_month or month_changed:
                self.date_lst[date_ind] = f"{day}"
            elif self.date_lst[date_ind].split('-')[1] != first_date_month:
                month_changed = True
                self.date_lst[date_ind] = f"{day}\n{need_case}\n{year}"
        return self.date_lst, price_lst

    def set_size(self, pixel_size: tuple):
        return pixel_size[0] * 0.0104166667, pixel_size[1] * 0.0104166667

    def build_plot(self, x_axis: list, y_axis: list, name_x: str, name_y: str, title: str,
                   font_size: int):
        plt.rcParams.update({'font.size': font_size})
        fig = plt.figure(figsize=self.set_size((950, 700)))
        plot = fig.add_subplot(111)
        plot.plot(x_axis, y_axis)
        plot.set_xlabel(name_x)
        plot.set_ylabel(name_y)
        plot.set_title(title)
        fig.savefig(f'{self.img_name}.png')

    def main(self):
        self.str_periods_to_machine()
        x, y = None, None
        font_size = 8
        if self.period == 'Пять лет':
            x, y = self.process_five_year_period()
        elif self.period == 'Год':
            x, y = self.process_year_period()
        elif self.period == 'Месяц':
            font_size = 7
            x, y = self.process_month_period()
        elif self.period == 'Неделя':
            self.period = 'неделю'
            x, y = self.process_week_period()
        if self.fiat != 'USD':
            for amount in range(len(x)):
                y[amount] = self.convert_fiat_currency(y[amount])
        name_x = f'Дата'
        name_y = f'Курс {self.crypto} к {self.fiat}'
        title = f'Изменения цены {self.crypto} к {self.fiat} за {self.period.lower()}'
        self.build_plot(x, y, name_x, name_y, title, font_size)
        self.date_lst.clear()

    def set_new_data(self, period: str, crypto: str, fiat: str, plot_img_name: str):
        self.period = period
        self.crypto = crypto
        self.fiat = fiat
        self.img_name = plot_img_name
