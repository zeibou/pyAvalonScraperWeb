from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import numpy as np
import matplotlib.pyplot as plt
import PIL
import PIL.Image
import io
import base64
import pyAvalonScraper.Scraper

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
    x = np.arange(10)
    y = x
    fig = plt.figure()
    plt.plot(x, y)
    graphic = plot_to_b64(fig)
    apts = pyAvalonScraper.Scraper.avalon_buildings

    return render(request, 'histo/index.html', {'graphic': graphic, 'apts' : apts})


    #return HttpResponse("Hello, world. You're at the Histo index.")
