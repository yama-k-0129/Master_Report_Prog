# UNSTの計算実行〜csvで出力するまで実行するプログラム

# macの場合 ターミナルで環境変数を下記で設定
# export GMAIL_APP_PASSWORD="生成したアプリパスワード"


import pandas as pd
import numpy as np
import csv
from collections import defaultdict
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def send_email(subject, body):
    sender_email = "kouki0129kouki0129@gmail.com"
    receiver_email = "kouki0129kouki0129@gmail.com"
    
    # メールの設定
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    # メール本文の追加
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Gmailのサーバーに接続
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        # ログイン
        # 注意: 実際に使用する際は、Googleアカウントでアプリパスワードを生成して使用してください
        app_password = os.environ.get("GMAIL_APP_PASSWORD")  # 環境変数からアプリパスワードを取得
        server.login(sender_email, app_password)
        
        # メール送信
        server.send_message(message)
        print(f"Email sent successfully: {subject}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
    finally:
        server.quit()

# プログラム開始時のメール送信
start_time = datetime.now()
send_email(
    "プログラム開始通知",
    f"プログラムが開始されました。\n開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
)

# main control program
# coded by d.baba, k.yamamura

# unst run
result = subprocess.run(['./unst.exe'], text=True)

basin_name = 'asuwa_paddyon_test'  # basin name(use output file name)
input_hmaxpath = 'out/hmax.dat'  # hmax.dat path
input_hpath = 'out/h.dat'  # h.dat path
mesh_data = 'data/mesh.dat'  # mesh data
hmax_file = f"{basin_name}_hmaxdata.csv"
h_file = f"{basin_name}_h.csv"

# output control[hmax, h]
control = [1, 1]  # active is 1

# function definitions (unchanged)
def parse_fortran_output(file_path):
    data = defaultdict(list)
    current_time = None
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip().startswith('time='):
                current_time = float(line.split('=')[1].split('(')[0].strip())
            elif current_time is not None:
                values = [float(x) for x in line.split()]
                data[current_time].extend(values)
    
    return data

def write_csv(data, output_file):
    times = sorted(data.keys())
    max_length = max(len(values) for values in data.values())
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['id'] + [f'{t}s' for t in times]
        writer.writerow(header)
        
        for i in range(max_length):
            row = [i+1]
            for time in times:
                value = data[time][i] if i < len(data[time]) else ''
                row.append(value)
            writer.writerow(row)

try:
    ## hmax ## 
    if control[0] == 1:
        # read hmax.dat
        data = pd.read_fwf(input_hmaxpath, header=None)
        # pick data area
        data = data.iloc[1:, 1:]
        print(data)  # check

        # meshdata read
        with open(mesh_data, 'r') as f:
            line = f.readline().strip()
            mesh = int(line)  # meshの数　ver.2
            
            max_ko = 10
            ko = np.zeros(mesh, dtype=np.int32)
            menode = np.full((mesh, max_ko), -1, dtype=np.int32)
            melink = np.full((mesh, max_ko), -1, dtype=np.int32)
            smesh = np.zeros(mesh, dtype=np.float32)
            xmesh = np.zeros(mesh, dtype=np.float32)
            ymesh = np.zeros(mesh, dtype=np.float32)
            rtuv = np.full((mesh, max_ko), 0.0, dtype=np.float32)

            for me in range(mesh):
                line = f.readline().split()
                ko[me] = int(line[1])
                menode[me, :ko[me]] = list(map(int, line[2:2 + ko[me]]))
                line = f.readline().split()
                melink[me, :ko[me]] = list(map(int, line[:ko[me]]))
                line = f.readline().split()
                smesh[me], xmesh[me], ymesh[me] = map(float, line)
                line = f.readline().split()
                rtuv[me, :ko[me]] = list(map(float, line[:ko[me]]))
                
        # change numpy array
        np_data = np.array(data, dtype=float)
        # drop NaN(include NaN in end index)
        clean_data = np_data[~np.isnan(np_data)]
        # reshape A row data
        row_data = clean_data.reshape((-1, 1))

        # change pandas DataFrame
        df = pd.DataFrame(row_data, columns=['depth'])
        # Add meshid row
        df['id'] = df.index + 1
        df = df.assign(xmesh=xmesh, ymesh=ymesh)
        
        # output csv
        df.to_csv(f'{basin_name}_hmaxdata.csv', index=False)

    ## h ##
    if control[1] == 1:
        data = parse_fortran_output(input_hpath)
        write_csv(data, f'{basin_name}_h.csv')

    # プログラム終了時のメール送信
    end_time = datetime.now()
    duration = end_time - start_time
    send_email(
        "プログラム終了通知",
        f"プログラムが正常に終了しました。\n"
        f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"処理時間: {duration}"
    )

except Exception as e:
    # エラーが発生した場合のメール送信
    error_time = datetime.now()
    send_email(
        "プログラムエラー通知",
        f"プログラムでエラーが発生しました。\n"
        f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"エラー発生時刻: {error_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"エラー内容: {str(e)}"
    )
    raise  # エラーを再度発生させて処理を終了