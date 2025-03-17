from pykiwoom.kiwoom import *
import pandas as pd
import numpy as np
import time
import os


def transform_dataframe(df):
    df['cp'] = df['현재가'].astype('float32').abs()
    df['op'] = df['시가'].astype('float32').abs()
    df['hp'] = df['고가'].astype('float32').abs()
    df['lp'] = df['저가'].astype('float32').abs()
    df['vol'] = df['거래량'].astype('float32')
    df['date'] = df['체결시간'].str[2:8].astype('uint32')
    df['time'] = df['체결시간'].str[8:12].astype('uint32')
    df = df[['date', 'time', 'cp', 'op', 'hp', 'lp', 'vol']]
    df.index = (df['date'] * 10000 + df['time']).astype('uint32')
    return df


def download_full(kiwoom, fname, optcode, stockcode):
    next = 0
    df_list = []
    while True:
        df = kiwoom.block_request(
            optcode,
            종목코드=stockcode,
            시간단위=1,
            output='',
            next=next)
        if len(df) == 0:
            break
        df_list.append(df)
        if len(df) < 900:
            break
        next = 2
        time.sleep(0.5)
    df = transform_dataframe(pd.concat(df_list))
    df.to_parquet(fname)
    return df


def download_partial(kiwoom, fname, optcode, stockcode):
    df_total = pd.read_parquet(fname)
    next = 0
    df_list = []
    last_index = df_total.index.max()
    last_index_str = str((last_index + 200000000000) * 100)
    while True:
        df = kiwoom.block_request(
            optcode,
            종목코드=stockcode,
            시간단위=1,
            output='',
            next=next)
        if len(df) == 0:
            break
        df = df[df['체결시간'] >= last_index_str]
        df_list.append(df)
        if len(df) < 900:
            break
        next = 2
        time.sleep(0.5)
    if len(df_list) > 0:
        df = transform_dataframe(pd.concat(df_list))
        df = pd.concat((df, df_total[df_total.index != last_index]), axis=0)
        df.to_parquet(fname)
    else:
        df = df_total
    return df


if __name__=='__main__':
    kiwoom = Kiwoom()
    kiwoom.CommConnect(block=True)

    optcode = 'opt50029'
    stockcode = '10100000'
    fname = '../data/kospi.parquet'
    download = download_partial if os.path.exists(fname) else download_full
    
    download(kiwoom, fname, optcode, stockcode)
