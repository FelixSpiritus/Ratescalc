from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '2.xlsx')

# Загрузка данных
df = pd.read_excel(file_path)
df['max_vol'] = pd.to_numeric(df['max_vol'].replace('--', 'inf'), errors='coerce').astype(float)
df.rename(columns={'Currency': 'currency'}, inplace=True)
df = df[['service', 'currency', 'country', 'min_vol', 'max_vol', 'rates']]
df = df.dropna()
df['service'] = df['service'].str.strip().str.replace('"', '')
df['country'] = df['country'].str.strip().str.replace('"', '').str.replace('\n', ' ')

# Получаем уникальные услуги и валюты для выпадающего списка
services = df['service'].unique()
currencies = df['currency'].unique()

# Функция для получения доступных стран для выбранной услуги
def get_countries_for_service(service):
    return df[df['service'] == service]['country'].unique()

# Функция для расчета средней ставки
def calc_rates(df, service_name, country_name, traffic_volume, currency):
    # Фильтруем по выбранной валюте
    fd = df[(df['service'] == service_name) & (df['country'] == country_name) & (df['currency'] == currency)]
    total_cost = 0.0
    remaining_volume = float(traffic_volume)  # Преобразуем в float для корректных вычислений
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
    return round(total_cost / traffic_volume, 5), currency

@app.route('/', methods=['GET', 'POST'])
def index():
    avg_rate = None  # По умолчанию нет средней ставки
    service_selected = request.form.get('service', 'Utility')  # Устанавливаем значение по умолчанию
    country_selected = request.form.get('country', None)
    currency_selected = request.form.get('currency', 'USD')  # Валюта по умолчанию
    traffic_volume = request.form.get('traffic_volume', None)
    
    # Преобразуем traffic_volume в целое число (если оно не пустое)
    if traffic_volume:
        try:
            traffic_volume = int(traffic_volume)
        except ValueError:
            traffic_volume = None  # Если преобразование не удалось, установим значение в None

    countries = get_countries_for_service(service_selected)  # Получаем страны для выбранной услуги

    currency = currency_selected

    if request.method == 'POST' and traffic_volume is not None:
        avg_rate, currency = calc_rates(df, service_selected, country_selected, traffic_volume, currency_selected)
        
    return render_template('index.html', 
                           avg_rate=avg_rate, 
                           currency_selected=currency_selected,
                           services=services, 
                           currencies=currencies,
                           countries=countries,
                           service_selected=service_selected,
                           country_selected=country_selected,
                           traffic_volume=traffic_volume)


@app.route('/get_countries/<service>', methods=['GET'])
def get_countries(service):
    countries = get_countries_for_service(service)
    return jsonify(countries=list(countries))

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=False)
