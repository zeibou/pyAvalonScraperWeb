from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import matplotlib.pyplot as plt
import PIL
import PIL.Image
import io
import base64
from dataclasses import dataclass
import sys
sys.path.insert(0, '/home/zeibou/web/pyAvalonScraper') # for pythonanywhere
sys.path.insert(0, '/Users/nicolas.seibert/Documents/Projects/pyAvalonScraperWeb/pyAvalonScraper') # for pycharm
import Scraper
import Historizer
import ApartmentFilter
import Alerter
from pyAvalonScraper.Scraper import Building
from pyAvalonScraper.ApartmentFilter import Filter
import matplotlib.dates as mdates
import datetime
from datetime import timedelta
import pytz


@dataclass
class GraphicItem:
    building : Scraper.Building
    apt : Scraper.Apartment
    graphic_b64: str

@dataclass
class UpdateItem:
    building : Scraper.Building
    updateLog : Alerter.UpdateLog


def plot_to_b64(figure):
    canvas = figure.canvas
    buf, size = canvas.print_to_buffer()
    image = PIL.Image.frombuffer('RGBA', size, buf, 'raw', 'RGBA', 0, 1)
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    graphic = buffer.getvalue()
    graphic = base64.b64encode(graphic)
    buffer.close()
    return str(graphic)[2:-1]


def index(request):
    return render(request, 'histo/index.html')

'''
def get_update_logs(building : Building, filter : Filter):
    apts_now = Scraper.get_apartments(building)
    histos = list(Historizer.load_building(building))
    histos.append(HistoEntry(datetime.datetime.now(), apts_now))
    for i in range(1, len(histos)):
        yield UpdateLog(histos[i-1].date, histos[i].date, compare(histos[i-1].apartments, histos[i].apartments, filter))
        
        '''


def logs(request):
    updates = []
    filter = Filter(3000, 10000, 750)
    for building in Scraper.avalon_buildings:
        for log in Alerter.get_update_logs(building, filter):
            if log.updates and (log.updates.added or log.updates.removed or log.updates.changed):
                updates.append(UpdateItem(building, log))

    return render(request, 'histo/logs.html', {'updates' : sorted(updates, key=lambda x : x.updateLog.date_after.replace(tzinfo=pytz.UTC) , reverse=True)})


def graphs(request):
    items = []
    filterGr = Filter(3500, 5000, 750)
    for building in Scraper.avalon_buildings:
        histos = list(Historizer.load_building(building))
        apts_ids = set()
        for da in histos:
            for id in ApartmentFilter.filter_apartments_get_ids(da.apartments, filterGr):
                apts_ids.add(id)
        x = [h.date for h in histos]
        #print(x)
        for id in sorted(apts_ids, key=lambda id: int(id.split('-')[-1][:-1])):
            #print(id)
            fig = plt.figure()
            y = list()
            apt = None
            for da in histos:
                for a in da.apartments:
                    if a.id == id:
                        apt = a
                        y.append(a.price)
                        break
                else:
                    y.append(None)
            #print(y)
            fig, ax = plt.subplots()
            plt.plot(x, y)
            #ax.xaxis_date()
            #ax.xaxis.set_major_locator(mdates.DayLocator())
            #ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30], interval=30))
            #yearsFmt = mdates.DateFormatter('%Y')
            #ax.xaxis.set_major_formatter(yearsFmt)
            #ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.set_xlim([datetime.date(2019, 1, 20), datetime.datetime.today() + timedelta(days=1)])
            plt.subplots_adjust(top = 0.95, bottom = 0.05)
            items.append(GraphicItem(building, apt, plot_to_b64(fig)))

    return render(request, 'histo/graphs.html', {'items': items})