# 水田ごとの面積を算出するプログラム

import pandas as pd

# CSVファイルを読み込み
df = pd.read_csv('asuwa_paddyoffeffect_hmaxdata.csv')

# paddyidごとにsmeshを合計
result = df.groupby('paddyid')['smesh'].sum().reset_index()

# カラム名を変更
result.columns = ['id', 'sum_smesh']

# CSVファイルとして出力
result.to_csv('output.csv', index=False)