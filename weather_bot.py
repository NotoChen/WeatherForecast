import requests
import yaml
import os
from datetime import datetime, timedelta

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

HEFENG_KEY = os.getenv('HEFENG_API_KEY')
DINGTALK_WEBHOOK = os.getenv('DINGTALK_WEBHOOK')

def get_location_id(location_name):
    """获取城市区域LocationID"""
    url = f"https://qm3yfqrqux.re.qweatherapi.com/geo/v2/city/lookup?location={location_name}&key={HEFENG_KEY}"
    res = requests.get(url).json()
    print(res)
    if res['code'] == '200':
        return res['location'][0]['id']
    raise Exception(f"位置查询失败: {res}")

def get_weather_report(location_id, days=1):
    """获取天气预报"""
    url = f"https://qm3yfqrqux.re.qweatherapi.com/v7/weather/{days}d?location={location_id}&key={HEFENG_KEY}"
    res = requests.get(url).json()
    print(res)
    if res['code'] != '200':
        raise Exception(f"天气查询失败: {res}")
    
    reports = []
    for day in res['daily']:
        date = datetime.strptime(day['fxDate'], '%Y-%m-%d')
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        report = (
            f"📅 **{date.month}月{date.day}日 ({weekday})**\n\n"
            f"☀️ 白天: {day['textDay']} | 🌙 夜间: {day['textNight']}\n\n"
            f"🌡️ 温度: {day['tempMin']}℃ ~ {day['tempMax']}℃\n\n"
            f"💨 风力: {day['windDirDay']}{day['windScaleDay']}级\n\n"
            f"💧 湿度: {day['humidity']}% | ☔ 降水: {day['precip']}mm\n\n"
            f"🌅 日出: {day['sunrise']} | 🌇 日落: {day['sunset']}\n\n"
            "──────────\n\n"
        )
        reports.append(report)
    return "\n".join(reports)

def send_dingtalk(content):
    """发送钉钉消息"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "每日天气播报",
            "text": f"### ⏰ 晨间天气预报 {datetime.now().strftime('%m/%d')}\n\n{content}"
        }
    }
    requests.post(DINGTALK_WEBHOOK, json=payload)

if __name__ == "__main__":
    all_reports = []
    for area in config['areas']:
        try:
            loc_id = get_location_id(area['name'])
            report = get_weather_report(loc_id, area.get('days', 1))
            print(report)
            all_reports.append(f"## 🌍 **{area['name']}**\n{report}")
        except Exception as e:
            all_reports.append(f"❌ {area['name']}播报失败: {str(e)}")
    
    final_report = "\n\n".join(all_reports)
    print(final_report)
    send_dingtalk(final_report)
    print("天气播报发送成功!")
