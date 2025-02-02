# UNST計算結果をアニメーションに変換するプログラム

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import multiprocessing
import os
import subprocess

# ファイル名を設定
basin_name = 'asuwa_paddyon_test'  # basin name(use output file name)
hmax_file = f"{basin_name}_hmaxdata.csv"
h_file = f"{basin_name}_h.csv"

# データの読み込みと前処理
print("Loading and preprocessing data...")
hmax_data = pd.read_csv(hmax_file, usecols=['id', 'xmesh', 'ymesh'])
h_data = pd.read_csv(h_file)

# メモリ使用量を削減するためにデータ型を最適化
for col in h_data.columns:
    if h_data[col].dtype == 'float64':
        h_data[col] = h_data[col].astype('float32')

# idをキーにしてデータを結合
merged_data = pd.merge(h_data, hmax_data, on='id', how='left')

# 時間列（0.0s, 600.0s, ...）を取得
time_columns = [col for col in merged_data.columns if col.endswith('s')]

# カスタムカラーマップの作成
colors = ['#FFFFFF', '#E6F3FF', '#CCE7FF', '#B3DBFF', '#99CFFF', '#80C3FF', 
          '#66B7FF', '#4DABFF', '#339FFF', '#1A93FF', '#0087FF', '#0066CC', 
          '#004C99', '#003366', '#001A33', '#000000']
n_bins = len(colors) - 1  # ビンの数
cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)
cmap.set_over('red')  # 10m以上の値に対する色を設定

# 非線形の境界値を設定
boundaries = np.concatenate([
    np.linspace(0, 1, 6),     # 0-1mの範囲を5等分
    np.linspace(1, 3, 5)[1:], # 1-3mの範囲を4等分
    np.linspace(3, 6, 4)[1:], # 3-6mの範囲を3等分
    np.linspace(6, 10, 4)[1:] # 6-10mの範囲を3等分
])
norm = BoundaryNorm(boundaries, cmap.N)

# フレーム生成関数
def generate_frame(frame):
    time_col = time_columns[frame]
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    scatter = ax.scatter(merged_data['xmesh'], merged_data['ymesh'], c=merged_data[time_col], 
                         cmap=cmap, norm=norm, s=1)
    cbar = fig.colorbar(scatter, ax=ax, label='Water Depth (m)', extend='max')
    cbar.set_ticks(list(boundaries) + [10])  # 10を追加して境界値と一致させる
    cbar.set_ticklabels([f'{b:.1f}m' for b in boundaries] + ['>10m'])
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'Water Depth at {time_col}')
    return fig

# フレーム保存関数
def save_frame(frame):
    try:
        fig = generate_frame(frame)
        filename = f'frame_{frame:04d}.png'
        fig.savefig(filename)
        plt.close(fig)  # メモリリークを防ぐために明示的に図を閉じる
        return filename
    except Exception as e:
        print(f"Error generating frame {frame}: {str(e)}")
        return None

# FFmpegコマンドを生成する関数
def get_ffmpeg_command(input_pattern, output_file, framerate):
    # 利用可能なエンコーダーをチェック
    encoders = subprocess.check_output("ffmpeg -encoders", shell=True).decode()
    
    if 'libx264' in encoders:
        return f"ffmpeg -framerate {framerate} -i {input_pattern} -c:v libx264 -pix_fmt yuv420p {output_file}"
    elif 'mpeg4' in encoders:
        return f"ffmpeg -framerate {framerate} -i {input_pattern} -c:v mpeg4 -q:v 1 {output_file}"
    else:
        return f"ffmpeg -framerate {framerate} -i {input_pattern} {output_file}"

if __name__ == '__main__':
    print("Generating frames...")
    pool = multiprocessing.Pool(processes=os.cpu_count() - 1)
    frame_files = pool.map(save_frame, range(len(time_columns)))
    pool.close()
    pool.join()

    # エラーチェックと無効なファイル名の削除
    frame_files = [f for f in frame_files if f is not None]

    if not frame_files:
        print("No frames were generated successfully. Check for errors in frame generation.")
    else:
        # フレームを動画に変換
        print("Creating animation...")
        output_file = f"{basin_name}_water_depth_animation_fixed.mp4"
        ffmpeg_command = get_ffmpeg_command("frame_%04d.png", output_file, 5)
        subprocess.call(ffmpeg_command, shell=True)

        print(f"Animation saved as {output_file}")

    # 一時ファイルの削除
    for file in frame_files:
        if os.path.exists(file):
            os.remove(file)