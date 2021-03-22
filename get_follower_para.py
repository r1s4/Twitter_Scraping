'''
入力の複数ユーザのフォロワーを大量に収集するプログラム
（各ユーザのフォロワーを集める＝フォロー・フォロワー関係になるため有向グラフ）
入力：ユーザリスト（csv形式）
出力：ユーザのフォロワー情報から作成したグラフ（gml形式）
'''

from joblib import Parallel, delayed
from collections import defaultdict
from time import sleep, time
import tweepy
import networkx as nx
import config
import dask.dataframe as dd
import pandas as pd
import os

def authenticate_api_key():
	"""
	twitter api keyを読み込む関数
	"""
	CK	  = config.CONSUMER_KEY
	CS	  = config.CONSUMER_SECRET
	AT	  = config.ACCESS_TOKEN
	ATS	 = config.ACCESS_TOKEN_SECRET
	return CK, CS, AT, ATS


def divide_and_read_csv():
	"""
	フォロワーを調べる対象のユーザー(center_id)のidを分割する関数
	"""
	ddf = dd.read_csv("user_id.csv",blocksize=6400) # blocksizeの数を指定することで，csvファイルの分割数を決定できる
	#print("the number of divided csvs: {}".format(ddf.npartitions)) # 分割したcsvファイルの数を表示 今回の例だと 6つ
	csv_filepathes = ddf.to_csv("./user_ids/user_id_*.csv", index=False)
	divided_user_ids = [pd.read_csv("{}".format(csv_filepath),header=None) for csv_filepath in csv_filepathes] # 分割したcsvをそれぞれ読み込む
	print(divided_user_ids)

	return divided_user_ids

# フォロワー取得
def getFollowers_ids(api, id):
	# Get Id list of followers
	followers_ids = tweepy.Cursor(api.followers_ids, id=id, cursor=-1).items()
	followers_ids_list = []
	try:
		followers_ids_list = [followers_id for followers_id in followers_ids]
	except tweepy.error.TweepError as e:
		print(e.reason)
	return followers_ids_list
 
def get_network_relationship(all_user_ids, center_ids, api, G, center_to_followers, node_attributes, follower_id_list):

	for center_id in center_ids:
		try:
			center_info = api.get_user(center_id) 
		except Exception as e:
			print(e)
		else:
			print("center_id:")
			print(center_id)
			G.add_node(center_id)

			node_attributes[center_id]['screenName'] = center_info.screen_name
			node_attributes[center_id]['followersNum'] = center_info.followers_count
			node_attributes[center_id]['followNum'] = center_info.friends_count
			# フォロワー一覧取得
			# たぶん15回/15分　→1回/1分なので1分sleepすればいい？
			center_to_followers[center_id] = getFollowers_ids(api=api, id=center_id)

			tmp = []
			print("getting target")
			# set empty value to account attribute that is not center
			for follower_id in center_to_followers[center_id]:
				# 分割前のユーザーリスト(all_user_ids)の中にcenter_idのユーザーのフォロワーがいるか調べる．
				"""
				all_user_idsを使う理由
				例えばuser_id 1〜100が読み込まれているcsvファイルに対して，user_id=1のフォロワーが101だったとき
				user_id=1のフォロワーがいないという判定になることを防ぐため
				"""
				if (follower_id in all_user_ids) == True: 
					print("follower id {} of center id {}".format(follower_id, center_id))
					G.add_node(follower_id)
					G.add_edge(center_id,follower_id)
					node_attributes.setdefault(follower_id, {'screenName': '', 'followersNum': '', 'followNum': ''})
					tmp.append(follower_id)
			
			follower_id_list[center_id] = tmp
			print("follower list is")
			print(follower_id_list[center_id] )
			print("of center id {}".format(center_id))

		sleep(1 * 60)
		print("end sleep")

	return follower_id_list, node_attributes, G

def main():
	os.makedirs("./user_ids/", exist_ok=True)
	divided_user_ids = divide_and_read_csv()
	all_user_ids = pd.read_csv("./user_id.csv")
	all_user_ids.columns= ['user_id']
	for i in range(len(divided_user_ids)):
		divided_user_ids[i].columns = ['user_id']
		

	CK, CS, AT, ATS = authenticate_api_key()

	#API認証
	auth = tweepy.OAuthHandler(CK, CS)
	auth.set_access_token(AT, ATS)
	api = tweepy.API(auth, wait_on_rate_limit=True)
	
	print("start")
	start = time()
	# result[i][0]: 分割したi番目のcsvファイル(user_id_i.csv)を使って求めたフォロワーid (get_network_relationship中の follower_id_list)の実行結果
	# result[i][1]: 分割したi番目のcsvファイル(user_id_i.csv)を使って求めたフォロワーの属性 (get_network_relationship中 の node_attributes)の実行結果
	# result[i][2]: 分割したi番目のcsvファイル(user_id_i.csv)を使って求めたフォロワーのソーシャルグラフ ( get_network_relationship中の G)の実行結果
	result = Parallel(n_jobs=-1,verbose=10)([delayed(get_network_relationship) 
											(all_user_ids=all_user_ids.loc[:, "user_id"].tolist(), center_ids=divided_user_ids[i].loc[:, "user_id"], 
											api=api, G=nx.DiGraph(), center_to_followers={}, node_attributes=defaultdict(dict), follower_id_list={})
											for i in range(len(divided_user_ids))																			   
											])
	"""
	テスト用
	result = Parallel(n_jobs=-1,verbose=10)([delayed(get_network_relationship) 
											(all_user_ids=all_user_ids.loc[:, "user_id"].tolist(), center_ids=divided_user_ids[1].loc[1:2, "user_id"], 
											api=api, G=nx.DiGraph(), center_to_followers={}, node_attributes=defaultdict(dict), follower_id_list={})
											for i in range(2)																			   
											])
	"""
	merged_follower_id_list = {}
	merged_node_attributes = defaultdict(dict)
	merged_graph = nx.DiGraph()

	# 分割した(フォロワーのid,フォロワーの属性,ソーシャルグラフ)を結合
	for i in range(divide_and_read_csv):
		merged_follower_id_list.update(result[i][0])
	graph = nx.from_dict_of_lists(merged_follower_id_list)

	for i in range(divided_user_ids):
		for key, value in result[i][1].items():
			merged_node_attributes[key].update(value)
	nx.set_node_attributes(graph, merged_node_attributes)

	for i in range(len(divided_user_ids)):
		merged_graph = nx.compose(merged_graph,result[i][2])
	nx.write_gml(merged_graph, 'Graph.gml')
	nx.write_gml(graph, 'twitter.gml')# ソーシャルグラフの作成 
	
	print("all finish {}".format(time.time() - start))
	

if __name__ == "__main__":
	main()

