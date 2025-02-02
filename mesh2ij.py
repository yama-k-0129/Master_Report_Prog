# !
# ! unst用メッシュに降雨ij番号を付与する
# !

import numpy as np
import pandas as pd
import pyproj

mesh_data = 'data/mesh.dat'  # mesh data


# 入力座標系と出力座標系のEPSGコードを指定
# 入力座標系指定（JGD2000）
#input_epsg = "EPSG:2443" # 長崎県・鹿児島県ののうち北方北緯32度南方北緯27度西方東経128度18分東方東経130度を境界線とする区域内（奄美群島は東経130度13分までを含む。)にあるすべての島・小島、環礁及び岩礁／Japan Plane Rectangular CS I
#input_epsg = "EPSG:2444" # 福岡県・佐賀県・熊本県・大分県・宮崎県・鹿児島県（I系に規定する区域を除く。)／Japan Plane Rectangular CS II
#input_epsg = "EPSG:2445" # 山口県・島根県・広島県／Japan Plane Rectangular CS III
#input_epsg = "EPSG:2446" # 香川県・愛媛県・徳島県・高知県／Japan Plane Rectangular CS IV
#input_epsg = "EPSG:2447" # 兵庫県・鳥取県・岡山県／Japan Plane Rectangular CS V
input_epsg = "EPSG:2448" # 京都府・大阪府・福井県・滋賀県・三重県・奈良県・和歌山県／Japan Plane Rectangular CS VI
#input_epsg = "EPSG:2449" # 石川県・富山県・岐阜県・愛知県／Japan Plane Rectangular CS VII
#input_epsg = "EPSG:2450" # 新潟県・長野県・山梨県・静岡県／Japan Plane Rectangular CS VIII
#input_epsg = "EPSG:2451" # 東京都（XIV系、XVIII系及びXIX系に規定する区域を除く。)・福島県・栃木県・茨城県・埼玉県・千葉県・群馬県・神奈川県／Japan Plane Rectangular CS IX
#input_epsg = "EPSG:2452" # 青森県・秋田県・山形県・岩手県／Japan Plane Rectangular CS X
#input_epsg = "EPSG:2453" # 小樽市・函館市・伊達市・北斗市・北海道後志総合振興局の所感区域・北海道胆振総合振興局の所管区域のうち豊浦町・壮瞥町及び洞爺湖町・北海道渡島総合振興局の所管区域・北海道檜山振興局の所管区域／Japan Plane Rectangular CS XI
#input_epsg = "EPSG:2454" # 北海道（XI系及びXIII系に規定する区域を除く。）／Japan Plane Rectangular CS I
#input_epsg = "EPSG:2455" # 北見市・帯広市・釧路市・網走市・根室市・北海道オホーツク総合振興局の所管区域のうち美幌町・津別町・斜里町・清里町・小清水町・訓子府町・置戸町・佐呂間町及び大空町・北海道十勝総合振興局の所管区域・北海道釧路総合振興局の所管区域・北海道根室振興局の所管区域／Japan Plane Rectangular CS XII
#input_epsg = "EPSG:2456" # 東京都のうち北緯28度から南であり、かつ東経140度30分から東であり東経143度から西である区域／Japan Plane Rectangular CS XIII
#input_epsg = "EPSG:2457" # 沖縄県のうち東経126度から東であり、かつ東経130度から西である区域／Japan Plane Rectangular CS XV
#input_epsg = "EPSG:2458" # 沖縄県のうち東経126度から西である区域／Japan Plane Rectangular CS XVI
#input_epsg = "EPSG:2459" # 沖縄県のうち東経130度から東である区域／Japan Plane Rectangular CS XVII
#input_epsg = "EPSG:2460" # 東京都のうち北緯28度から南であり、かつ東経140度30分から西である区域／Japan Plane Rectangular CS XVIII
#input_epsg = "EPSG:2461" # 東京都のうち北緯28度から南であり、かつ東経143度から東である区域／Japan Plane Rectangular CS XIX
# output_epsg = "EPSG:4612" # JGD2000
output_epsg = "EPSG:4326" # 世界測地系

# 座標変換オブジェクトの作成
bef = pyproj.Proj(init = input_epsg)
aft = pyproj.Proj(init = output_epsg)
transformer = pyproj.Transformer.from_proj(bef, aft)

with open(mesh_data, 'r') as f:
    # Read the mesh
    line = f.readline().strip()
    # mesh = int(line.split('=')[1])  # meshの数
    mesh = int(line) # meshの数
    max_ko = 10  # Initialize variables with maximum array sizes
    ko = np.zeros(mesh, dtype=np.int32)
    menode = np.full((mesh, max_ko), -1, dtype=np.int32)
    melink = np.full((mesh, max_ko), -1, dtype=np.int32)
    smesh = np.zeros(mesh, dtype=np.float32)
    xmesh = np.zeros(mesh, dtype=np.float32)
    ymesh = np.zeros(mesh, dtype=np.float32)
    rri_xmesh = np.zeros(mesh, dtype=np.float32)
    rri_ymesh = np.zeros(mesh, dtype=np.float32)
    
    rtuv = np.full((mesh, max_ko), 0.0, dtype=np.float32)

    for me in range(mesh):
        line = f.readline().split()
        ko[me] = int(line[1])  # 格子の頂点の数
        # Fill in only the first ko[me] values
        menode[me, :ko[me]] = list(map(int, line[2:2 + ko[me]]))
        line = f.readline().split()
        melink[me, :ko[me]] = list(map(int, line[:ko[me]]))
        line = f.readline().split()
        smesh[me], xmesh[me], ymesh[me] = map(float, line)

        # 座標変換の実行
        rri_xmesh[me], rri_ymesh[me] = transformer.transform(xmesh[me], ymesh[me])

        line = f.readline().split()
        rtuv[me, :ko[me]] = list(map(float, line[:ko[me]]))

# rri_xmeshとrri_ymeshを空白区切りのテキストファイルに出力
with open('data/mesh2ij.dat', 'w') as f:
    for i in range(mesh):
        f.write(f"{rri_xmesh[i]} {rri_ymesh[i]}\n")