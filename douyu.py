# 获取斗鱼直播间的真实流媒体地址，默认最高画质
# 使用 https://github.com/wbt5/real-url/issues/185 中两位大佬@wjxgzz @4bbu6j5885o3gpv6ss8找到的的CDN，在此感谢！

import hashlib
import re
import time

import js2py
import requests


class DouYu:
    """
    可用来替换返回链接中的主机部分
    两个阿里的CDN：
    dyscdnali1.douyucdn.cn
    dyscdnali3.douyucdn.cn
    墙外不用带尾巴的akm cdn：
    hls3-akm.douyucdn.cn
    hlsa-akm.douyucdn.cn
    hls1a-akm.douyucdn.cn
    """

    def __init__(self, rid):
        """
        房间号通常为1~8位纯数字，浏览器地址栏中看到的房间号不一定是真实rid.
        Args:
            rid:
        """
        self.did = '10000000000000000000000000001501'
        self.t10 = str(int(time.time()))
        self.t13 = str(int((time.time() * 1000)))

        self.s = requests.Session()
        self.rid = rid
        if self.rid.isdigit() == False:
            self.res = self.s.get('https://m.douyu.com/' + str(rid)).text
            result = re.search(r'rid":(\d{1,8}),"vipId', self.res)
            if result:
                self.rid = result.group(1)
            else:
                #raise Exception('房间号错误')
                self.rid = 0

    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_pre(self):
        url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + self.rid
        data = {
            'rid': self.rid,
            'did': self.did
        }
        auth = DouYu.md5(self.rid + self.t13)
        headers = {
            'rid': self.rid,
            'time': self.t13,
            'auth': auth
        }
        res = self.s.post(url, headers=headers, data=data).json()
        error = res['error']
        data = res['data']
        key = ''
        if data:
            rtmp_live = data['rtmp_live']
            key = re.search(
                r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}(/playlist|.m3u8)', rtmp_live).group(1)
        return error, key, data, res

    def get_js(self):
        result = re.search(
            r'(function ub98484234.*)\s(var.*)', self.res).group()
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result)
        #js = execjs.compile(func_ub9)
        context = js2py.EvalJs()
        context.execute(func_ub9)

        #res = js.call('ub98484234')
        res = context.ub98484234()

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace(
            'CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        #js = execjs.compile(func_sign)
        #params = js.call('sign', self.rid, self.did, self.t10)

        context = js2py.EvalJs()
        context.execute(func_sign)

        #res = js.call('ub98484234')
        params = context.sign(self.rid, self.did, self.t10)
        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        url = 'https://m.douyu.com/api/room/ratestream'
        res = self.s.post(url, params=params).text
        key = re.search(
            r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}(.m3u8|/playlist)', res).group(1)

        return key

    def get_pc_js(self, cdn='ws-h5', rate=0):
        """
        通过PC网页端的接口获取完整直播源。
        :param cdn: 主线路ws-h5、备用线路tct-h5
        :param rate: 1流畅；2高清；3超清；4蓝光4M；0蓝光8M或10M
        :return: JSON格式
        """
        res = self.s.get('https://www.douyu.com/' + str(self.rid)).text
        result = re.search(
            r'(vdwdae325w_64we[\s\S]*function ub98484234[\s\S]*?)function', res).group(1)
        func_ub9 = re.sub(r'eval.*?;}', 'strc;}', result)
        #js = execjs.compile(func_ub9)
        context = js2py.EvalJs()
        context.execute(func_ub9)

        #res = js.call('ub98484234')
        res = context.ub98484234()

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace(
            'CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        context = js2py.EvalJs()
        context.execute(func_sign)

        #res = js.call('ub98484234')
        params = context.sign(self.rid, self.did, self.t10)
        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        params += '&cdn={}&rate={}'.format(cdn, rate)
        url = 'https://www.douyu.com/lapi/live/getH5Play/{}'.format(self.rid)
        res = self.s.post(url, params=params).json()['data']
        supported_reso = res['multirates']
        key = res['rtmp_live'].split('.')[0]
        if '_' in key:
            key = key.split('_')[0]
        real_url = {
            'hw': {},
            'ws': {},
        }
        #real_url['raw'] = res
        for cdn in real_url:
            for reso in supported_reso:
                bitrate = reso['bit']
                type = reso['name']
                print(key)
                if reso['rate'] == 0:
                    real_url[cdn][type] = f'http://{cdn}-tct.douyucdn.cn/live/{key}.flv?uuid='
                else:
                    real_url[cdn][type] = f'http://{cdn}-tct.douyucdn.cn/live/{key}_{bitrate}.flv?uuid='
                # real_url[cdn]['xs']=f'http://{cdn}-tct.douyucdn.cn/live/{key}.xs?uuid='

        return real_url, res

    def get_real_url(self):
        error, key, data, diagnostic = self.get_pre()
        real_url = {
            'hw': {},
            'ws': {},
            'akm': {}
        }
        if error == 0:
            pass
        elif error == 102:
            raise Exception('房间不存在')
        elif error == 104:
            raise Exception('房间未开播')
        elif error == 742017:
            return real_url, data, diagnostic
        else:
            key = self.get_pre()

        for cdn in real_url:
            real_url[cdn]['原画'] = f'https://{cdn}-tct.douyucdn.cn/live/{key}.flv?uuid='
            # real_url[cdn]['xs']=f'http://{cdn}-tct.douyucdn.cn/live/{key}.xs?uuid='
        return real_url, data, diagnostic

    def get_room_info(self):
        url = f'https://open.douyucdn.cn/api/RoomApi/room/{self.rid}'
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            json['data']['gift'] = []
            return json
        else:
            return f'Error :{response.text}'

    def douyu(self, full='enable', details='enable'):
        
        if self.rid == 0:
            return{
                "message": "Room id is invalid",
                "status": 400
            }, 400
        else:
            live_info = self.get_room_info()
            if 'Error' not in live_info:
                basic_data = {
                    "avatar": live_info['data']['avatar'],
                    "cover": live_info['data']['room_thumb'],
                    "nick": live_info['data']['owner_name'],
                    "roomId": live_info['data']['room_id'],
                    "title": live_info['data']['room_name']
                }
                if live_info['data']['room_status'] == '2':
                    basic_data['liveStatus'] = 'OFF'
                    return {
                        "data": basic_data,
                        "message": "Room is offline!",
                        "status": 200
                    }
                else:
                    basic_data['liveStatus'] = 'ON'
                    if details == 'enable':
                        if full == 'enable':
                            data, res = self.get_pc_js()
                        else:
                            data, res,dia = self.get_real_url()

                            #TODO fix args
                        basic_data['links'] = data
                        print(res)
                        if 'data' in res and res['data'] == '':
                            basic_data['liveStatus'] = 'OFF'
                        return{
                            "data": basic_data, "status": 200, "diagnostic": res
                        }
                    else:
                        return{
                            "data": basic_data, "status": 200
                        }
            else:
                self.res = self.s.get(
                    'https://m.douyu.com/' + str(self.rid)).text
                result = re.search(r'rid":(\d{1,8}),"vipId', self.res)
                if result:
                    self.rid = result.group(1)
                    return self.douyu(full, details)
                return{
                    "message": f"Room id is invalid or not found,the id is {self.rid} and here is the info:{live_info}",
                    "status": 404
                }, 404
