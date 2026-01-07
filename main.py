import os, re
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from itertools import zip_longest

# تنظیمات اصلی
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']

def get_env_list(key):
    return [c.strip() for c in os.environ.get(key, '').split(',') if c.strip()]

def fetch(client, target, limit):
    configs = []
    try:
        # اگر ورودی عدد باشد، آن را تبدیل می‌کند
        entity = int(target) if str(target).replace('-', '').isdigit() else target
        for msg in client.iter_messages(entity, limit=limit*3):
            if msg.text:
                found = re.findall(r"(?:vless|vmess|ss|trojan|hysteria|tuic)://[^\s<]+", msg.text)
                for l in found:
                    if l not in configs: configs.append(l)
            if len(configs) >= limit: break
    except: return None # اگر خطا داد
    return configs[:limit]

def main():
    all_configs = []
    with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        # پردازش گروه‌های ۵۰۰ تایی و ۵۰ تایی
        for group, limit in [ (('IDS_500', 'CHANNELS_500'), 500), (('IDS_50', 'CHANNELS_50'), 50) ]:
            ids = get_env_list(group[0])
            names = get_env_list(group[1])
            
            for i_id, i_name in zip_longest(ids, names):
                res = None
                if i_id: # اول تلاش با آیدی عددی
                    print(f"🔍 تلاش با آیدی: {i_id}")
                    res = fetch(client, i_id, limit)
                
                if (res is None or len(res) == 0) and i_name: # اگر نشد، تلاش با نام
                    print(f"⚠️ آیدی نشد، تلاش با نام: {i_name}")
                    res = fetch(client, i_name, limit)
                
                if res: all_configs.extend(res)

    # ذخیره نهایی بدون تکراری
    final = list(dict.fromkeys(all_configs))
    with open('configs.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final))
    print(f"✅ پایان. مجموع: {len(final)}")

if __name__ == "__main__":
    main()
