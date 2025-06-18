from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '1.xlsx')

# Загрузка данных
df = pd.read_excel(file_path)
df['max_vol'] = pd.to_numeric(df['max_vol'].replace('--', 'inf'), errors='coerce').astype(float)
df = df[['service', 'country', 'min_vol', 'max_vol', 'rates']]
df = df.dropna()
df['service'] = df['service'].str.strip().str.replace('"', '')
df['country'] = df['country'].str.strip().str.replace('"', '').str.replace('\n', ' ')

# Получаем уникальные услуги для выпадающего списка service
services = df['service'].unique()

# Функция для получения доступных стран для выбранной услуги
def get_countries_for_service(service):
    return df[df['service'] == service]['country'].unique()

def calc_rates(df, service_name, country_name, traffic_volume):
    fd = df[(df['service'] == service_name) & (df['country'] == country_name)]
    total_cost = 0.0
    remaining_volume = traffic_volume
    fd = fd.sort_values('min_vol').reset_index(drop=True)
    for _, row in fd.iterrows():
        if remaining_volume <= 0:
            break      
        min_vol = row['min_vol']
        max_vol = row['max_vol']
        rate = row['rates']
        band_volume = min(max_vol, traffic_volume) - min_vol
        applicable_volume = min(band_volume, remaining_volume)
        if applicable_volume > 0:
            total_cost += applicable_volume * rate
            remaining_volume -= applicable_volume  
    return round(total_cost / traffic_volume, 5)  # Форматируем до 5 знаков

@app.route('/', methods=['GET', 'POST'])
def index():
    avg_rate = None
    service_selected = "Utility"  # Устанавливаем значение по умолчанию на "Utility"
    country_selected = None
    traffic_volume = None
    countries = get_countries_for_service(service_selected)  # Получаем страны для "Utility"
    
    if request.method == 'POST':
        service_selected = request.form['service']
        country_selected = request.form['country']
        traffic_volume = int(request.form['traffic_volume'])
        countries = get_countries_for_service(service_selected)  # Обновляем страны для выбранной услуги
        
        avg_rate = calc_rates(df, service_selected, country_selected, traffic_volume)
        
    return render_template('index.html', 
                           avg_rate=avg_rate, 
                           services=services, 
                           countries=countries,
                           service_selected=service_selected,
                           country_selected=country_selected,
                           traffic_volume=traffic_volume)

@app.route('/get_countries/<service>', methods=['GET'])
def get_countries(service):
    countries = get_countries_for_service(service)
    return jsonify(countries=list(countries))

if __name__ == '__main__':
    app.run(debug=True)