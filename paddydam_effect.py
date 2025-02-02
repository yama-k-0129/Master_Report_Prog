# 水田貯留効果を時系列で算出

import pandas as pd
import numpy as np

# CSVファイル読み込み
input2_df = pd.read_csv('asuwa_paddyon_effect_h.csv')
smesh_df = pd.read_csv('output.csv')

# 各セルを処理
for idx in input2_df.index:
   for col in input2_df.columns[1:]:  # id列以外
       value = input2_df.loc[idx, col]
       id_val = input2_df.loc[idx, 'id']
       smesh_sum = smesh_df.loc[smesh_df['id'] == id_val, 'sum_smesh'].values[0]
       
       if value <= 0.3:
           input2_df.loc[idx, col] = value * smesh_sum
       else:
           input2_df.loc[idx, col] = 0.3 * smesh_sum

# 結果を出力
input2_df.to_csv('result_paddyon.csv', index=False)