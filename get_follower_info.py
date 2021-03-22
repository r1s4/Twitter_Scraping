'''
あるユーザを中心に相互フォロワーを収集するプログラム
（無向グラフ）

長期の収集はできない（dbの問題？）
'''

import json
import config
from requests_oauthlib import OAuth1Session
from time import sleep
from mongo_dao import MongoDAO
import datetime

# APIキー設定
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET

# 認証処理
twitter = OAuth1Session(CK, CS, AT, ATS)  

mongo = MongoDAO("db", "followers_info")

get_friends_url = "https://api.twitter.com/1.1/friends/list.json" # フォローしているアカウントを取得
get_user_info_url = "https://api.twitter.com/1.1/users/show.json" # ユーザー情報を取得する
count = 200
targets = ['hoge'] # このユーザーのフォロワーのうち相互フォローとなるユーザーを求める(これを変える)
registed_list = []
depth = 2 # 潜る深さ
max_friends_count = 10000 # フォローアカウントが多い人が居るので一定数を超えてると除外する

# フォローアカウントが一定数を超えていないか判定する
def judge_friends_count(screen_name):
    params = {'screen_name': screen_name}
    while True:
        res = twitter.get(get_user_info_url, params=params)
        result_json = json.loads(res.text)
        if res.status_code == 200:
            # フォローしている人数は「friends_count」、フォローされている人数は「followers_count」
            if result_json['friends_count'] > max_friends_count:
                return False
            else:
                return True
        elif res.status_code == 429:
            # 15分間で15回しかリクエストを送信出来ないので上限に達していたら待つ
            now = datetime.datetime.now()
            print(now.strftime("%Y/%m/%d %H:%M:%S") + ' 接続上限のため待機')
            sleep(5 * 60) # 15分待機
        else:
            return False

# 指定したscreen_nameのフォロワーを取得する
def get_followers_info(screen_name):
    followers_info = []
    params = {'count': count,'screen_name': screen_name}
    try:
        res = twitter.get(get_friends_url, params=params)
        result_json = json.loads(res.text)

        if res.status_code == 200 and len(result_json['users']) != 0:
                for user in result_json['users']:
                    # APIから取得した情報のうち、必要な情報だけをdict形式で設定　
                    followers_info.append({'screen_name': user['screen_name'], 'id': user['id']})
                # パラメーターに次の取得位置を設定する
                params['cursor'] = result_json['next_cursor']
        # APIの接続上限を超えた場合の処理           
        elif res.status_code == 429:
            now = datetime.datetime.now()
            print(now.strftime("%Y/%m/%d %H:%M:%S") + ' 接続上限のため待機')
            sleep(5 * 60) # 15分待機
    except RemoteDisconnected:
        print("error!!")
        return

    return followers_info

# dictのlistからscreen_nameのみのlistを取得する
def followers_list(followers_info):
    followers_list = []
    for follower in followers_info:
        followers_list.append(follower['screen_name'])
    return followers_list

# 再帰処理
def dive_search(target_list, d):
    for name in target_list:
        if name in registed_list or not judge_friends_count(name):
            continue
        print("user {}".format(name)) 
        # 変数nameで表されるユーザーのフォロワーを取得
        followers_info = get_followers_info(name)
        mongo.insert_one({'screen_name': name, 'followers_info': followers_info})
        registed_list.append(name)
        sleep(2 * 60)
        if depth > d:
            dive_search(followers_list(followers_info), d + 1)
        else:
            return

def main():
    dive_search(targets, 0)

if __name__ == "__main__":
    main()
