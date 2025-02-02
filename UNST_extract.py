import pandas as pd

df = pd.read_csv('../paddyon_out_ver2/asuwa_paddyon_test_q.csv')
extract_df = pd.read_csv('../extract_id.csv')

# 'id'列から抽出したいIDのリストを取得する
ids_to_extract = extract_df['id'].tolist()

# 指定したIDを持つ行を抽出する
extracted_rows = df[df['id'].isin(ids_to_extract)]

# 最初の列を除いて、数字が3600で割り切れる数字の列のみを抽出する
# 's'を除去してから数値に変換する
columns_to_keep = ['id'] + [col for col in extracted_rows.columns if col != 'id' and float(col[:-1]) % 3600 == 0]
extracted_rows = extracted_rows[columns_to_keep]

# 列名から's'を除去する
extracted_rows.columns = [col[:-1] if col != 'id' else col for col in extracted_rows.columns]

# 行と列を入れ替える
extracted_rows_transposed = extracted_rows.set_index('id').T

# インデックス名を'time'に設定し、値を数値に変換する
extracted_rows_transposed.index = pd.to_numeric(extracted_rows_transposed.index)
extracted_rows_transposed.index.name = 'time'

# 抽出した行を新しいCSVファイルに保存する
extracted_rows_transposed.to_csv('../paddyon_out_ver2/extract_paddyonq_test.csv')