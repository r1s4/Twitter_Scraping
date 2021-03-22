'''
edgelistのユーザのツイートをAPIの制限である3200件まで集めるプログラム
入力：edgelist
出力：各ユーザのツイートを出力したcsvファイル*ユーザ数
'''

import csv
import config
from requests_oauthlib import OAuth1Session
from time import sleep
import datetime
import tweepy
import pandas as pd


# APIキー設定
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET

# 認証処理
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)

api = tweepy.API(auth)  


def main():

    with open('test.edgelist', encoding='utf-8') as f:
        text = f.read()
    id_lists = text.split()
    id_lists = list(set(id_lists))

    print(id_lists)
    print(len(id_lists))

    for user_id in id_lists:
        print(user_id)
        tweet_data = []
        next_id_list=[]
        tweet_id_list=[]

        next_max_id=0

        #status_list = api.user_timeline(screen_name=user_id)
        #statuses_count:ツイート数
        user_info=api.get_user(screen_name=user_id)
        tweet_count=user_info.statuses_count

        #limitation:900/15min 60/1min
        #100*32=3200件のツイート収集
        #description:プロフィール
        if tweet_count >= 3200:
            for i in range(32):
                print(i,"回目")
                if next_max_id==0:
                    for tweet in tweepy.Cursor(api.user_timeline, tweet_mode = 'extended', screen_name=user_id).items(100):
                        tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count,tweet.user.description])
                        tweet_id_list.append([tweet.id])

                else:
                    for tweet in tweepy.Cursor(api.user_timeline, tweet_mode = 'extended', screen_name=user_id, max_id=next_max_id-1).items(100):
                        tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count,tweet.user.description])
                        tweet_id_list.append([tweet.id])

                next_max_id = tweet_id_list[-1][-1]
                print(next_max_id)

                
        else:
            for i in range(tweet_count//100):
                print(i,"回目")
                if next_max_id==0:
                    for tweet in tweepy.Cursor(api.user_timeline, tweet_mode = 'extended', screen_name=user_id).items(100):
                        tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count,tweet.user.description])
                        tweet_id_list.append([tweet.id])

                else:
                    for tweet in tweepy.Cursor(api.user_timeline, tweet_mode = 'extended', screen_name=user_id, max_id=next_max_id-1).items(100):
                        tweet_data.append([tweet.id, tweet.user.screen_name, tweet.created_at, tweet.full_text.replace('\n',''), tweet.favorite_count, tweet.retweet_count, tweet.user.followers_count, tweet.user.friends_count,tweet.user.description])
                        tweet_id_list.append([tweet.id])

                next_max_id = tweet_id_list[-1][-1]
                print(next_max_id)

                # CSVに保存
        with open('./data/3/{}_tweets.csv'.format(user_id), 'a',newline='',encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(tweet_data)
            

        sleep(2 * 60)



if __name__ == "__main__":
    main()


