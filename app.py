import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "API для получения времени намаза работает! Перейдите на /api/prayer-times"

@app.route('/api/prayer-times')
def get_prayer_times():
    url = "https://takvim.tj/"
    
    try:
        # Делаем запрос к сайту
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим все таблицы на странице
        tables = soup.find_all('table')
        
        masjid_times = {}
        today_times = {}
        
        for table in tables:
            text = table.text
            
            # Парсим блок: Вақтҳои намоз дар масҷиди Марказии шаҳри Душанбе
            if "Бомдод" in text and "Пешин" in text and not "аз" in text:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        time_val = cols[1].text.strip()
                        if name:
                            masjid_times[name] = time_val
                            
            # Парсим блок: Вақтҳои намоз барои шаҳри Душанбе, Имрӯз
            elif "аз" in text and "то" in text and "Имрӯз" in table.find_previous_sibling('text') or True:
                # Так как на сайте несколько таблиц с "аз" и "то" (имруз, пагох), 
                # берем первую подходящую для "Имруз"
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        time_val = cols[1].text.strip()
                        if name and "аз" in time_val:
                            # Убираем лишние переносы строк
                            name = name.replace('\r', '').replace('\n', ' ')
                            today_times[name] = time_val
                            
                # Если нашли сегодняшнее время, прерываем поиск остальных дней (пагох, рузи)
                if today_times:
                    break

        return jsonify({
            "status": "success",
            "masjid_central_times": masjid_times,
            "today_durations": today_times
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
