import requests
from datetime import datetime
import os

API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

def get_weather(city):
  url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
  response = requests.get(url).json()  
  # Jika API mengembalikan error
  if response.get('cod') != '200':
    # Ambil pesan error dari API jika ada
    error_message = response.get('message', 'Terjadi kesalahan saat mengambil data cuaca.')
    return {'error': f"Gagal mengambil data cuaca: {error_message}"}  
  forecast = []
  try:
    # print(f"{response}")
    for i in [0, 8, 16]:  # hari ini, besok, lusa
      day_data = response['list'][i]
      date = datetime.fromtimestamp(day_data['dt'])
      forecast.append({
        'day': date.strftime('%A, %d %B %Y'),
        'temp_day': day_data['main']['temp_max'],
        'temp_night': day_data['main']['temp_min']
      })
    return {'data': forecast}
  except (KeyError, IndexError):
    return {'error': 'Format data cuaca tidak sesuai. Coba lagi nanti.'}