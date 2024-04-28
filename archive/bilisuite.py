import pandas as pd
import requests
import jieba
import time
import copy
import json
import bs4
import re
import os


MAX = 1024
HINT = '''
bls.search.uploader     ->      user-agent
bls.tool.spammer        ->      cookie, csrf
bls.post.report         ->      cookie, csrf
bls.post.reply          ->      cookie, csrf

bls.setting.up(
    usragent = "",
    cookie = "",
    csrf = ""
)
'''


def form(kind:str):
    if kind == 'report':
        return {
            'add_blacklist': False,
            'csrf': setting.csrf,
            'ordering': 'heat',
            'reason': None,
            'rpid': None,
            'type': 1
        }
    elif kind == 'reply':
        return {
            'oid': None,
            'message': None,
            'csrf': setting.csrf,
            'plat': 1,
            'type': 1
        }
    else:
        return {}
    


class setting:
    usragent = None
    cookie = None
    csrf = None

    @staticmethod
    def up(usragent:str=None, cookie:str=None, csrf:str=None):
        if usragent is None and cookie is None and csrf is None:
            print(HINT)
        else:
            setting.usragent = usragent
            setting.cookie = cookie
            setting.csrf = csrf



class loading:
    def __init__(self, content:list):
        self.content = content
    
    @property
    def head(self):
        self.content.insert(0, self.content.pop())
        return self.content[0]
    
    def spin(self, wait:float):
        print(f'Loading: {self.head}\t', end='\r')
        time.sleep(wait)



class url:
    main = 'https://www.bilibili.com/video/{}'
    host = 'https://api.bilibili.com/'
    video = host + 'x/space/wbi/arc/search?mid={}&ps=30&tid=0&pn={}'
    add = host + 'x/v2/reply/add'
    report = host + 'x/v2/reply/report'
    page = host + 'x/v2/reply/main?&mode=3&oid={}&pagination_str=%7B%22offset%22:%22%7B%5C%22type%5C%22:1,%5C%22direction%5C%22:1,%5C%22data%5C%22:%7B%5C%22pn%5C%22:{}%7D%7D%22%7D&plat=1&type=1'
    branch = host + 'x/v2/reply/reply?&oid={}&pn=1&ps={}&root={}&type=1'
    

    
class utils:
    @staticmethod
    def bv2oid(bvid:str):
        try:
            html = requests.get(url=url.main.format(bvid))
            oid = re.search(f'"bvid":"{bvid}","aid":(\d+),', html.text).group(1)
        except Exception as error:
            raise Exception(f'{error} <utils.bv2oid>')
        
        time.sleep(1)
        return oid
    
    @staticmethod
    def code2msg(code:str):
        if code == '0': return '无异常'
        elif code == '12019': return '举报频率过快'
        elif code == '12008': return '重复举报'
        elif code == '-101': return '账号未登录'
        elif code == '-107': return '账号未转正'
        else: return '未知'


class search:
    @staticmethod
    def uploader(mid:str, page:int=MAX):
        def get(mid:str, i:int, headers:str):
            res = requests.get(url=url.video.format(mid, i), headers=headers)
            raw = json.loads(res.text)['data']['list']['vlist']
            data = [i['bvid'] for i in raw]
            time.sleep(1)
            return data

        try:
            headers = {'User-Agent': setting.usragent}
            videos = []
            for i in range(1, page+1):
                data = get(mid, i, headers)
                if len(data):
                    videos += data
                    visualize.spin(0.1)
                else:
                    break
        except Exception as error:
            raise Exception(f'{error} <search.uploader>')
        
        time.sleep(1)
        print(f'[{mid}]: {len(videos)}')
        return videos
        


class load:
    @staticmethod
    def data(bvid:str):
        try:
            html = requests.get(url=url.main.format(bvid))
            soup = bs4.BeautifulSoup(html.text, 'html.parser')

            cls = ['video-like-info', 'video-coin-info', 'video-fav-info', 'video-share-info']
            top = [soup.find('span', class_=i).contents[1] for i in ['view', 'dm']]
            bottom = [soup.find('span', class_=i).contents[0] for i in cls]
            reply = [re.search(r'"reply":(\d+)', html.text).group(1)]

            raw = list(map(lambda x: re.sub('[^万0-9]', '', x), top+bottom+reply))
            data = list(map(lambda x: int(re.sub('万', '000', x)), raw))
        except Exception as error:
            raise Exception(f'{error} <load.data>')
        
        time.sleep(1)
        return data
    

    @staticmethod
    def comment(bvid:str, page:int=MAX, branch:int=MAX):        
        def get(oid:str, i:int):
            res = requests.get(url=url.page.format(oid, i))
            raw = json.loads(res.text)['data']['replies']
            rpid = [str(i['rpid']) for i in raw]
            time.sleep(1)
            return rpid
        
        def more(oid:str, branch:int, rpid:str):
            res = requests.get(url=url.branch.format(oid, branch, rpid))
            raw = json.loads(res.text)['data']
            replies = raw['replies'] if raw['replies'] is not None else []
            replies.append(raw['root'])
            data = {i['rpid']:[i['mid'], i['content']['message']] for i in replies}
            return data

        try:
            comment = {}
            oid = utils.bv2oid(bvid)
            for i in range(1, page+1):
                rpid = get(oid, i)
                if len(rpid):
                    for each in rpid:
                        data = more(oid, branch, each)
                        comment.update(data)
                        visualize.spin(0.1)
                else:
                    break
            df = pd.DataFrame(comment, index=['mid', 'comment']).transpose()
            comment = df.reset_index().rename(columns={'index':'rpid'})
        except Exception as error:
            raise Exception(f'{error} <load.comment>')
        
        time.sleep(1)
        print(f'<{bvid}>: {len(comment)}')
        return comment



class tool:
    @staticmethod
    def observer(bvid:list, folder:str, page:int=MAX, branch:int=MAX):
        if folder not in os.listdir():
            os.mkdir(folder)
        for each in bvid:
            try:
                meta = load.comment(each, page=page, branch=branch)
                data = process.std(meta)
                data.to_csv(f'{folder}/{each}.csv', index=False)
            except Exception as error:
                print(f'{each} -> {error}')
                
        fullset = []
        for file in os.listdir(folder):
            if len(file)>4 and file[-4:]=='.csv':
                fullset.append(pd.read_csv(f'{folder}/{file}'))

        pd.concat(fullset).to_csv(f'{folder}.csv', index=False)


    @staticmethod
    def tracer(bvid:str, run:int):
        for i in range(run):
            prev = time.time()

            try:
                data = load.data(bvid)
                content = ','.join([str(i) for i in data])
            except Exception as error:
                print(error)
                content = ','*6
            finally:
                with open(f'{bvid}.csv', 'a') as file:
                    file.write(f'{int(prev)},' + content + '\n')

            print(f'Progress: {i+1}/{run}', end='\r')
            now = time.time()
            time.sleep(75-(now-prev))


    @staticmethod
    def spammer(oid:str, message:str):
        bvid = search.uploader(oid)
        for each in bvid:
            try:
                code = post.reply(each, message)
                print(f'{each}: {utils.code2msg(code)}')
            except Exception as error:
                print(f'{each}: {error}')
            finally:
                time.sleep(1)



class post:
    @staticmethod
    def report(rpid:str, reason:int=4):
        try:
            headers = {'Cookie': setting.cookie}
            data = form('report')
            data['rpid'] = rpid
            data['reason'] = reason
            res = requests.post(url=url.report, headers=headers, data=data)
            code = re.search('"code":([-\d]+),', res.text).group(1)
        except Exception as error:
            raise Exception(f'{error} <post.report>')
        
        time.sleep(1)
        return code
    

    @staticmethod
    def reply(bvid:str, message:str):
        try:
            headers = {'Cookie': setting.cookie}
            data = form('reply')
            data['oid'] = utils.bv2oid(bvid)
            data['message'] = message
            res = requests.post(url=url.add, headers=headers, data=data)
            code = re.search('"code":([-\d]+),', res.text).group(1)
        except Exception as error:
            raise Exception(f'{error} <post.reply>')
        
        time.sleep(1)
        return code



class process:
    @staticmethod
    def std(data:pd.DataFrame):
        try:
            df = copy.deepcopy(data)
            if len(df):
                df['comment'] = df['comment'].str.replace('回[复復覆] @(.+?) :', '', regex=True)
                df['comment'] = df['comment'].str.replace('[^\u4e00-\u9fa5]', '', regex=True)
                df = df[df['comment']!='']
                df.dropna(subset=['comment'], inplace=True)
                df.drop_duplicates(inplace=True)
                df['comment'] = df['comment'].apply(lambda x: ' '.join(jieba.lcut(x)))
            if 'rating' not in list(df.columns):
                df['rating'] = 0
        except Exception as error:
            raise Exception(f'{error} <process.std>')
        
        return df
    


visualize = loading(['-', '/', '|', '\\'])
jieba.lcut('preload')
