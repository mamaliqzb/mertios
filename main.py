import os, re, requests, pyzipper
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from itertools import zip_longest
from datetime import datetime

# تنظیمات اصلی از گیت‌هاب
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']
ZIP_PASS = os.environ['ZIP_PASSWORD'].encode()
BALE_TOKEN = os.environ['BALE_TOKEN']
BALE_CHAT_ID = os.environ['BALE_CHAT_ID']

def get_env_list(key):
    return [c.strip() for c in os.environ.get(key, '').split(',') if c.strip()]

def fetch_configs(client, target, limit):
    configs = []
    try:
        # تشخیص آیدی عددی یا نام کاربری
        entity = int(target) if str(target).replace('-', '').isdigit() else target
        for msg in client.iter_messages(entity, limit=limit*3):
            if msg.text:
                found = re.findall(r"(?:vless|vmess|ss|trojan|hysteria|tuic)://[^\s<]+", msg.text)
                for l in found:
                    if l not in configs: configs.append(l)
            if len(configs) >= limit: break
    except: return None
    return configs[:limit]

def send_to_bale(file_path):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': BALE_CHAT_ID, 'caption': f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
    try:
        requests.post(url, files=files, data=data)
    except: print("Error sending to Bale")

def main():
    all_res = []
    with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        # گروه‌بندی سکرت‌ها و سهمیه‌ها
        tasks = [(('IDS_500', 'CHANNELS_500'), 500), (('IDS_50', 'CHANNELS_50'), 50)]
        for keys, limit in tasks:
            ids, names = get_env_list(keys[0]), get_env_list(keys[1])
            for i_id, i_name in zip_longest(ids, names):
                res = fetch_configs(client, i_id, limit) if i_id else None
                if (not res) and i_name: # اگر آیدی کار نکرد، تلاش با نام
                    res = fetch_configs(client, i_name, limit)
                if res: all_res.extend(res)

    if not all_res: return

    # ۱. ذخیره با نام مستعار (پنهان‌کاری)
    internal_name = "system.log"
    with open(internal_name, 'w', encoding='utf-8') as f:
        f.write('\n'.join(list(dict.fromkeys(all_res))))

    # ۲. ایجاد زیپ رمزدار با نام غیرمرتبط
    zip_name = "Data_Backup_82.zip"
    with pyzipper.AESZipFile(zip_name, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(ZIP_PASS)
        zf.write(internal_name)

    # ۳. ارسال و پاکسازی
    send_to_bale(zip_name)
    os.remove(internal_name)
    os.remove(zip_name)

if __name__ == "__main__":
    main()
