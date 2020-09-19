from django.shortcuts import render

import requests
import json
from datetime import datetime
import os

lurl = 'https://us1.locationiq.com/v1/search.php?key=e329d0577c126d&format=json&q='
key = 'f5d3e696f6c590a25f1de6811d30d390/'

def home(request):
    json_data = {}
    loc_data = []
    if not request.method == 'POST':
        resp = requests.get('http://ip-api.com/json/')
        jd = json.loads(resp.text)
        lat = str(jd['lat'])
        lon = str(jd['lon'])
        loc_data.append(jd['city'])
        loc_data.append(jd['country'])
        response = requests.get('https://api.darksky.net/forecast/'+key+lat+','+lon+'?units=si')
        json_data = json.loads(response.text)
        # with open(os.getcwd()+'\\data.json', 'r') as file:
        #     json_data = json.load(file)

    if request.method == 'POST':
        print(request.POST['input'])
        location = request.POST['input']
        loc_data = requests.get(lurl+location)
        loc_data = json.loads(loc_data.text)
        if 'error' in loc_data:
            return render(request, 'location_404.html')
        lon = loc_data[0]['lon']
        lat = loc_data[0]['lat']
        loc_data = loc_data[0]['display_name'].split(',')
        response = requests.get('https://api.darksky.net/forecast/'+key+lat+','+lon+'?units=si')
        json_data = json.loads(response.text)

    c = json_data['currently']
    d = json_data['daily']['data']
    h = json_data['hourly']['data'][2:24:3]
    
    current = {
        "city": loc_data[0],
        "country": loc_data[-1],
        "time": datetime.fromtimestamp(c['time']).strftime('%a %d %B %H:%M %p'),
        "summary": c['summary'],
        "icon": c['icon'],
        "visibility": round(c['visibility']),
        "temperature": round(c['temperature']),
        "preasure": round(c['pressure']/3386, 1),
        "dewPoint": round(c['dewPoint']),
        "humidity": round(c['humidity']),
        "precipProbability": round(c['precipProbability']),
        "cloudCover": round(c['cloudCover']),
        "wind_speed": c['windSpeed'],
        "sunrise": datetime.fromtimestamp(d[0]['sunriseTime']).strftime('%H:%M %p'),
        "sunset": datetime.fromtimestamp(d[0]['sunsetTime']).strftime('%H:%M %p')
    }

    hourly = []
    for hour in h:
        hdic = {
            "time": datetime.fromtimestamp(hour['time']).strftime('%I%p'),
            "icon": hour['icon'],
            "temperature": round(hour['temperature'])
        }
        hourly.append(hdic)
    
    daily = []
    for today in d:
        tdic = {
            "day": datetime.fromtimestamp(today['time']).strftime('%a'),
            "date": datetime.fromtimestamp(today['time']).strftime('%d/%m'),
            "icon": today['icon'],
            "temperatureHigh": round(today['temperatureHigh']),
            "temperatureLow": round(today['temperatureLow']),
            "precipProbability": round(today['precipProbability']),
            "windSpeed": today['windSpeed'],
        }
        daily.append(tdic)

    context = {
        "background": c['icon'],
        "current": current,
        "hourly": hourly,
        "daily": daily,
    }
    return render(request, 'home.html', context)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request, exception):
    return render(request, '500.html', status=500)
