# Twitter_Scraping
Twitterのデータ収集に関するもの

- 大量収集用：
下記を組み合わせることで，あるツイートをRTしたユーザのみに関するフォロー・フォロワー関係のグラフを作成できる．
  - getTweet.py
  キーワードに当てはまるツイートを長期的に収集するプログラム
  - get_follower_para.py
  複数ユーザのフォロワーを大量に収集するプログラム．フォロー・フォロワーの有向グラフ．


- あるユーザのツイートを収集する：
  - get_tweet.py
  edgelistのユーザのツイートをAPIの制限である3200件まで集めるプログラム
  
  
- 相互フォローの関係のグラフを作る．（長期向けではない）:
  - get_follower_info.py
  あるユーザを中心に相互フォロワーを収集するプログラム．
  - mongo_dao.py
  MongoDBを使うためのプログラム.get_follower.pyと一緒に使用
  - create_socialgraph.py
  get_follower_info.pyで集めたデータからグラフを出力する
