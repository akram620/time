import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "API работает! Перейдите на /api/prayer-times"

@app.route('/api/prayer-times')
def get_prayer_times():
    url = "https://takvim.tj/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        # Отключаем предупреждения SSL (полезно для некоторых сайтов)
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        masjid_times = {}
        today_times = {}
        
        # Ищем вообще все строки на странице (тег tr - table row)
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                # Очищаем название и время от переносов и лишних пробелов
                name = " ".join(cols[0].text.split())
                time_val = " ".join(cols[1].text.split())
                
                # Список того, что мы ищем
                valid_names = [
                    "Бомдод", "Пешин", "Аср", "Шом", "Хуфтан", 
                    "Даромадани офтоб, хондани намоз мумкин нест (макрӯҳ)"
                ]
                
                if name in valid_names:
                    # Если во времени есть "аз" или "то" (период для Имрӯз)
                    if "аз" in time_val or "то" in time_val:
                        # Берем только первое совпадение, так как оно относится к "Имрӯз"
                        if name not in today_times:
                            today_times[name] = time_val
                            
                    # Если это точное время для мечети (например 05:06)
                    elif re.match(r'^\d{2}:\d{2}$', time_val):
                        if name not in masjid_times:
                            masjid_times[name] = time_val

        return jsonify({
            "status": "success",
            "masjid_central_times": masjid_times,
            "today_durations": today_times
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
