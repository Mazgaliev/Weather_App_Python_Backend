"""Weather_App_Python_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.http import JsonResponse
import os
from dotenv import load_dotenv
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import pickle
import pandas as pd

load_dotenv()


api_key = os.getenv('OPENWEATHERMAP_API_KEY')
url = os.getenv("OPENWEATHERMAP_API_URL")

@csrf_exempt   
def scrape_data(request):

    payload = json.loads(request.body)
    stations_payload = payload.get("stations_payload")
    stations = stations_payload.get("Stations")
    number_of_hours = stations_payload.get("NumberOfHours")

    if stations== None:
        return JsonResponse({'Result':[], 'Error':True, 'Message':f'EMPTY stations payload'})
        
    # Simple logic to scrape data
    now = datetime.now()
    start = int((now - timedelta(hours=number_of_hours)).timestamp())
    end = int(now.timestamp())

    final_result = []

    for station in stations:
        longitude = station.get("Longitude") 
        latitude = station.get("Latitude")
        station_id = station.get("Id")
        params = {
            'lat':latitude,
            'lon':longitude,
            'start':start,
            'end':end,
            'type':'hour',
            'appid':api_key}
        
        req = requests.models.PreparedRequest()
        req.prepare_url(url, params)
        
        response = requests.get(req.url)

        data = _parse_data(response, station_id)
        final_result.append(data)
    return JsonResponse({"Result" : final_result})

@csrf_exempt   
def train_models(request):
    # Simple logic to train models
    
    all_data = json.loads(request.body)
    measurements  = all_data.get('measurements_payload')
    
    if measurements == None or measurements == []:
        return JsonResponse({'status': 'fail', 'result':[]})   
    ## transforms it to a dataframe
    measurements_df = pd.DataFrame(measurements)

    
    pm10_model =_fit_model(RandomForestRegressor(n_estimators= 150), measurements)
    pm2_5_model = _fit_model(RandomForestRegressor(n_estimators= 150), measurements)
    co_model = _fit_model(RandomForestRegressor(n_estimators= 150), measurements)
    so2_model = _fit_model(RandomForestRegressor(n_estimators= 150), measurements)

    with open('../models/pm2_5_model.pkl','wb') as f:
        pickle.dump(pm10_model, f)
    
    with open('../models/pm2_5_model.pkl','wb') as f:
        pickle.dump(pm2_5_model, f)

    with open('../models/co_model.pkl','wb') as f:
        pickle.dump(co_model, f)

    with open('../models/so2_model.pkl','wb') as f:
        pickle.dump(so2_model, f)

    model_status = "Models trained successfully"
    return JsonResponse({'status': 'success', 'message': model_status})

@csrf_exempt   
def predict_values(request):

    #small models easy to load them in and predict the needed values
    # Simple logic to predict values

    all_data = json.loads(request.body)
    measurements  = all_data.get('measurements_payload')

    if measurements == None or measurements == []:
        return JsonResponse({"status":'failed', 'result':[]})
    
    measurements_df = pd.DataFrame(measurements)
    
    pm10_model = None
    pm2_5_model = None
    co_model = None
    so2_model = None

    with open('../models/pm10_model.pkl','rb') as f:
        pm10_model = pickle.load(f)
    
    with open('../models/pm2_5_model.pkl','rb') as f:
        pm2_5_model = pickle.load(f)

    with open('../models/co_model.pkl','rb') as f:
        co_model = pickle.load(f)

    with open('../models/so2_model.pkl','rb') as f:
        so2_model = pickle.load(f)

    
    predictions = {"result": "some predicted values"}
    return JsonResponse({'status': 'success', 'predictions': predictions})

def _parse_data(response, station_id):
    final_results = []
    if response.status_code == 200:
        data = json.loads(response.content)
        list_of_results = data.get('list')

        if list_of_results == None or list_of_results == []:
            return {'Result': None, 'Error' : True, 'Message':'Empty Response from OpenWeatherApi'}
        
        else:
            for result in list_of_results:
                parsed_result = {}
                aqi = None
                aqi_obj = result.get('main')
                if aqi_obj != None:
                    aqi = aqi_obj.get('aqi')

                components = result.get('components')
                if components == None:
                    return {'Result' : None, 'Error' : True, 'Message': 'There is no details data for the rest of the parameters'}
                parsed_result['co'] = components.get('co')
                parsed_result['pm2_5'] = components.get('pm2_5')
                parsed_result['pm10'] = components.get('pm10')
                parsed_result['aqi'] = aqi
                parsed_result['so2'] = components.get('so2')
                parsed_result['stationId'] = int(station_id)
                parsed_result['measurementTime'] = result['dt']

                final_results.append(parsed_result)
    else:
        return {'Result':[], 'Error':True, 'Message':f'Problem with response from OpenweatherAPI {response.content}'}
    
    return {'Result': final_results, 'Error': False, 'Message': 'Success'}

def _fit_model(model, data):
    return model

def _transform_data_for_prediction():
    pass
urlpatterns = [
    path('scrape_data/', scrape_data, name='scrape_data'),
    path('train_models/', train_models, name='train_models'),
    path('predict_values/', predict_values, name='predict_values'),
]

