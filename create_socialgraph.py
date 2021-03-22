'''
get_follower_info.py
で集めたデータから，グラフを出力（可視化）
'''

import json
import networkx as nx
import matplotlib.pyplot as plt
from requests_oauthlib import OAuth1Session
from mongo_dao import MongoDAO

mongo = MongoDAO("db", "followers_info")
start_screen_name = 'hoge' # このユーザーのフォロワーのうち相互フォローとなるユーザーに関するソーシャルグラフを出力，可視化する(これを変える)
#DENEBU7

# 新規グラフを作成
G = nx.Graph()
# ノードを追加
G.add_node(start_screen_name)

depth = 3
processed_list = []

def get_followers_list(screen_name):
    result = mongo.find(filter={"screen_name": screen_name})
    followers_list = []
    try:
        doc = result.next()
        if doc != None:
            for user in doc['followers_info']:
                followers_list.append(user['screen_name'])
        return followers_list
    except StopIteration:
        return followers_list

def dive(screen_name, d):
    if depth > 0:
        if screen_name in processed_list:
            return
        followers_list = get_followers_list(screen_name)
        for follower in followers_list:
            f = get_followers_list(follower)
            if start_screen_name in f:
                G.add_edge(screen_name, follower)
                processed_list.append(screen_name)
                dive(follower, d + 1)
    else:
        return

def main():
    # あるユーザーと相互フォローになっているフォロワーを求める
    dive(start_screen_name, 0)

    # ユーザー間のつながりを表したテキストファイルを書き込む
    nx.write_edgelist(G, "test.edgelist", data=False)

    #図の作成。figsizeは図の大きさ
    plt.figure(figsize=(10, 8))

    #図のレイアウトを決める。kの値が小さい程図が密集する
    pos = nx.spring_layout(G, k=0.8)

    #ノードとエッジの描画
    # _color: 色の指定
    # alpha: 透明度の指定
    nx.draw_networkx_edges(G, pos, edge_color='y')
    nx.draw_networkx_nodes(G, pos, node_color='r', alpha=0.5)

    #ノード名を付加
    nx.draw_networkx_labels(G, pos, font_size=10)

    #X軸Y軸を表示しない設定
    plt.axis('off')

    plt.savefig("mutual_follow.png")
    #図を描画
    #plt.show()

if __name__ == "__main__":
    main()
