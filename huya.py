import json

import requests
from bs4 import BeautifulSoup


def huya(room_id: str) -> map:
    try:
        if not room_id.isdigit():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
                htmlDoc = requests.get(
                    f'https://m.huya.com/{room_id}', headers=headers)
                soup = BeautifulSoup(htmlDoc.text, 'html.parser')
                a = soup.body.contents[8]
                b = str(a).replace('<script> window.HNF_GLOBAL_INIT = ', '')
                c = str(b).replace('</script>', '')
                jsonContent = json.loads(c)
                room_id = str(jsonContent['roomInfo']['tProfileInfo']['lProfileRoom'])
                print(
                    f'Your room id is invalid! The real room id is: {room_id}')
            except:
                print('Room id is invalid!')
                return {'status': 404, 'message': 'Room id is invalid!'},404
        api_url = 'https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid='
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
        html = requests.get(api_url + room_id, headers=headers)
        data = json.loads(html.text)['data']

        nick = data['profileInfo']['nick']
        room_name = data['liveData']['introduction']
        liveStatus = data['liveStatus']
        avatar = data['profileInfo']['avatar180']
    except:
        print('Room id is invalid!')
        return {'status': 404, 'message': 'Room id is invalid!'},404
    

    if liveStatus == "OFF" or liveStatus == "REPLAY":
        return {
            'status': 200,
            'message': 'Room is offline!',
            'data': {
                'nick': nick,
                'title': room_name,
                'roomId': room_id,
                'liveStatus': liveStatus,
                'avatar': avatar,
            }
        }
    else:
        cover=data['liveData']['screenshot']
        stream_dict = data['stream']
        flv = stream_dict['flv']  
        cdn = flv['multiLine']  
        rate = flv['rateArray']  
        supportable_resolution = {'原画': '', }
        for b in rate:
            supportable_resolution[b['sDisplayName']] = f'_{b["iBitRate"]}'
        sort_dict = {}
        for cdn_type in cdn:
            cdn_name = cdn_type['cdnType']
            sort_dict[cdn_name] = {}
            for resolution, bitrate in supportable_resolution.items():
                url = cdn_type['url'].replace('http://', 'https://')
                url = url.replace(
                    'imgplus.flv', f'imgplus{bitrate}.flv')
                sort_dict[cdn_name][resolution] = url


    return {
        'status': 200,
        'message': 'success',
        'data': {
            'nick': nick,
            'title': room_name,
            'liveStatus': liveStatus,
            'links': sort_dict,
            'roomId': room_id,
            'avatar': avatar,
            'cover': cover,
        }
    }