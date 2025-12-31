import requests
import re
import os

# زانیارییەکانت کە پێشتر ناردت
MAC_ADDRESS = "12d7087e0000630d-0" 
USER_AGENT = "iStarMedia/1.0 (Android)"

def get_new_token(cmd, base_url):
    params = {'type': 'itv', 'action': 'create_link', 'cmd': cmd}
    headers = {
        'User-Agent': USER_AGENT,
        'Cookie': f'mac={MAC_ADDRESS}',
        'X-User-Agent': USER_AGENT
    }
    try:
        api_url = f"{base_url}/server/load.php"
        res = requests.get(api_url, params=params, headers=headers, timeout=15)
        data = res.json()
        if 'js' in data and 'cmd' in data['js']:
            return data['js']['cmd']
    except:
        return None
    return None

def main():
    if not os.path.exists("channels.m3u"):
        return
    
    with open("channels.m3u", "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_list = ["#EXTM3U", "#EXTVLCOPT:http-user-agent=iStarMedia/1.0 (Android)"]
    
    for line in lines:
        line = line.strip()
        if line.startswith("http"):
            base_match = re.search(r'(http://.*?:\d+)', line)
            cmd_match = re.search(r':8085/(.*?)/mono\.m3u8', line)
            
            if base_match and cmd_match:
                new_link = get_new_token(cmd_match.group(1), base_match.group(1))
                if new_link:
                    new_list.append(new_link)
                else:
                    new_list.append(line)
            else:
                new_list.append(line)
        elif line.startswith("#EXTINF"):
            new_list.append(line)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(new_list))

if name == "main":
    main()
