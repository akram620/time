import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "API работает! Перейдите на /api/prayer-times"

@app.route('/api/prayer-times')
def get_prayer_times():
    url = "https://takvim.tj/"
    
    # Маскируем наш запрос под обычный браузер Google Chrome на Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        # Передаем headers в запрос
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        
        masjid_times = {}
        today_times = {}
        
        for table in tables:
            text = table.text
            
            if "Бомдод" in text and "Пешин" in text and not "аз" in text:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        time_val = cols[1].text.strip()
                        if name:
                            masjid_times[name] = time_val
                            
            elif "аз" in text and "то" in text and "Имрӯз" in table.find_previous_sibling('text') or True:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        name = cols[0].text.strip()
                        time_val = cols[1].text.strip()
                        if name and "аз" in time_val:
                            name = name.replace('\r', '').replace('\n', ' ')
                            today_times[name] = time_val
                            
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
