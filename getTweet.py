'''
キーワードに当てはまるツイートを長期的に収集するプログラム
'''

# -*- coding: utf-8 -*-

import tweepy
import config
import csv
import time
import schedule
import pandas as pd

# OAuth認証部分
CK      = config.CONSUMER_KEY
CS      = config.CONSUMER_SECRET
AT      = config.ACCESS_TOKEN
ATS     = config.ACCESS_TOKEN_SECRET
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)

api = tweepy.API(auth)

# 検索内容
keyword = 'コロナ　min_retweets:100'
''' 
使えそうなもの　
min_faves:500 （いいね数が500以上）
min_retweets:500 （リツイート数が500以上）
min_replies:10
exclude:retweets　（検索結果にRT含まない）
'''
tweet_data = []
user_id_list=[]
tweet_id_list=[]
next_id_list=[]

def job():
    #検索
    '''
    tweet.id ツイートIDの取得
    tweet.user.screen_name ユーザーネームの取得
    tweet.created_at ツイート日時の取得
    tweet.full_text.replace('\n','') ツイート本文を改行を取り除いた上で取得
    tweet.favorite_count いいね数の取得
    tweet.retweet_count リツイート数の取得
    tweet.user.followers_count フォロワー数の取得
    tweet.user.friends_count フォロー数の取得
    '''

    with open('next_id.csv', 'r', newline='') as f:
        reader = csv.reader(f,lineterminator='\n')
        for r in reader:
            next_max_id=int(r[-1])
    
    print(next_max_id)


    if next_max_id == 0:
        for tweet in api.search(q=keyword, tweet_mode = 'extended', count=100):  #tweet_mode='extended' ツイート本文が途切れないようにする
            try:
                tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count])
                user_id_list.append([tweet.user.id]) 
                tweet_id_list.append([tweet.id])    #例：1225785463845163010
            except Exception as e:
                print(e)
        #ツイートは新しいほどidが大きくなる
        next_max_id = tweet_id_list[-1][-1]
        
        for i in range(170):
            for tweet in api.search(q=keyword, tweet_mode = 'extended', count=100, max_id=next_max_id):  #max_id->next_max_id（集めた中で1番古いツイートid）以下のツイートのみ検索
                try:
                    tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count])
                    user_id_list.append([tweet.user.id]) 
                    tweet_id_list.append([tweet.id])
                except Exception as e:
                    print(e)
            next_max_id = tweet_id_list[-1][-1]
            
        
        
    else:
        for i in range(180):
            for tweet in api.search(q=keyword, tweet_mode = 'extended', count=100, max_id=next_max_id):  #max_id->next_max_id（集めた中で1番古いツイートid）以下のツイートのみ検索
                try:
                    tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count])
                    user_id_list.append([tweet.user.id]) 
                    tweet_id_list.append([tweet.id])
                except Exception as e:
                    print(e)
            next_max_id = tweet_id_list[-1][-1]

    #for n in next_max_id:
    #    next_max_id = int(n)
    
    print(next_max_id)
    
    next_max_id_list=[]
    next_max_id_list.append(next_max_id)

    # CSVに保存
    with open('coronavirus.csv', 'a',newline='',encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(tweet_data)
    pass

    with open('user_id.csv', 'a', newline='') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerows(user_id_list)

    with open('next_id.csv', 'a', newline='') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(next_max_id_list)    


job()

# 15分ごとに実行 
schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)