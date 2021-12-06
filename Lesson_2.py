import os

import numpy as np
import requests
import pandas as pd
import pickle
import tushare as ts
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


def find_and_save_csi300_history():
    response = requests.get('https://en.jinzhao.wiki/wiki/CSI_300_Index')
    # 是固体不过lxml对网页进行解析
    wiki_soup = BeautifulSoup(response.text, 'lxml')
    # 使用find_all找出所有属性中class为wikitable sortable的对象，并获取第2个
    table = wiki_soup.find_all(attrs={'class': 'wikitable sortable'})[1]
    stock_code = []
    # find_all用于在获取的网页中的html格式匹配
    # findall用于在字符串中匹配内容
    for n in table.findAll('tr')[1:]:
        stockcode = n.findAll('td')[0].text[0:6]
        stock_code.append(stockcode)
    # 以下代码为创建一个csi_stockcode.pickle的文件将stock_code以二进制方法存入，方便调用
    # with语句实现自动close文件，省略了f.close()的操作
    # wb为使用二进制写入文件
    with open('csi_stockcode.pickle', 'wb') as f:
        pickle.dump(stock_code, f)  # 将stock_code写入f
    print(stock_code)
    return stock_code


def find_and_save_csi300():
    df = pd.read_excel('000300cons.xls', dtype={'成分券代码Constituent Code': str})  # 指定某列的格式
    # ticker_list = df.iloc[:, 4].values  使用.values将股票代码直接生成list
    # 列表推导式的应用
    # df.iloc[:,4]用来表示df的第5列
    ticker_list_sz = [ticker + '.SZ' for ticker in df.iloc[:, 4] if ticker[0] == '0' or ticker[0] == '3']
    ticker_list_sh = [ticker + '.SH' for ticker in df.iloc[:, 4] if ticker[0] == '6']
    ticker_list = ticker_list_sz + ticker_list_sh
    with open('csi_ticker_list.pickle', 'wb') as f:
        pickle.dump(ticker_list, f)
    return ticker_list


def get_csi300data_from_tushare(reload=False):
    if reload:
        find_and_save_csi300()
    else:
        # 载入find_and_save_csi300()生成的pickle文件
        with open('csi_ticker_list.pickle', 'rb') as f:
            ticker_list = pickle.load(f)
            # 使用os库.path.exists()判断是否存在csi300_data路径，如果不存在则使用.mkdir()进行创建
        if not os.path.exists('csi300_data'):
            os.mkdir('csi300_data')
        else:
            for ticker in ticker_list:
                # 判断是否已获取数据
                if not os.path.exists(f'csi300_data/{ticker}.csv'):
                    pro = ts.pro_api('63b6038d68dd853d09b4652260647332328e6434c37a41d90facbcda')
                    df = pro.daily(ts_code=ticker, start_date='20160101', end_date='20201231')
                    # 重置索引
                    df.reset_index(inplace=True)
                    # 将'trade_date'列设置为索引
                    df.set_index('trade_date', inplace=True)
                    df.to_csv(f'csi300_data/{ticker}.csv')  # 保存文件
                    print(f'{ticker}已采集')
                else:
                    print(f'{ticker}.csv已存在')


def summary_csi300_close_price():
    df_summary_csi300_close_price = pd.DataFrame()
    with open('csi_ticker_list.pickle', 'rb') as f:
        tickers_list = pickle.load(f)
    # 使用enumerate（）函数为for loop制作计数器
    for count, ticker in enumerate(tickers_list):
        df = pd.read_csv(f'csi300_data/{ticker}.csv')
        # 删除不需要的列
        # inplace=True时，直接修改源数据；inplace=False时，生成副本数据
        df.drop(
            columns=['index', 'ts_code', 'open', 'high', 'low', 'pre_close', 'change',
                     'pct_chg', 'vol', 'amount'], inplace=True)
        # 将colse列重命名
        df.rename(columns={'close': ticker}, inplace=True)
        # 设置索引
        df.set_index('trade_date', inplace=True)
        if df_summary_csi300_close_price.empty:  # .empty方法判断df是否为空
            df_summary_csi300_close_price = df
        else:
            # 使用join函数将两个df进行合并，how='outer'表示合并方法为outer
            df_summary_csi300_close_price = df_summary_csi300_close_price.join(df, how='outer')
        print(f'正在处理第{count+1}个文件')
    df_summary_csi300_close_price.to_csv('df_summary_csi300_close_price.csv')


def get_csi300_pearson_correlation_heatmap():
    df = pd.read_csv('df_summary_csi300_close_price.csv')
    # .pct_change()用于计算百分比变化
    # .corr()用于计算相关性，默认为计算皮尔逊相关性（线性相关）
    df_corr = df.pct_change().corr()
    df_corr.drop(index=['trade_date'], inplace=True)
    df_corr.drop(columns=['trade_date'], inplace=True)
    df_corr.to_csv('csi300_pearson_correlation.csv')
    data = df_corr.values  # .values函数生成一个不带index和columns的arrary
    # 生成画布及绘图区
    fig = plt.figure()
    ax = fig.add_subplot(111)  # 向画布中添加一个绘图区，与plt.subplot不同此方法必须先创建一个figure实例
    # 生成主体图
    heatmap = ax.pcolor(data, cmap=plt.cm.YlOrBr)
    # 设置坐标轴
    ax.set_xticks(np.arange(0.5, df_corr.shape[0] + 0.5, 1))  # 设置刻度线位置，np.arange()可在指定区间内按指定步长生成数列
    ax.set_yticks(np.arange(0.5, df_corr.shape[1] + 0.5, 1))  # .shape返回的结果为row*col，x轴坐标对应col，y轴坐标对应row
    ax.set_xticklabels(df_corr.columns)  # 将x轴坐标标签替换为df_corr.columns
    ax.set_yticklabels(df_corr.index)  # 将y轴坐标标签替换为df_corr.index
    ax.invert_yaxis()  # 翻转Y轴坐标
    ax.xaxis.tick_top()  # 将x轴调整到顶部显示
    plt.xticks(rotation=90)  # 将x坐标轴标签旋转90度
    # 设置colorbar
    fig.colorbar(heatmap)  # 在fig画布上为heatmap设置colorbar
    heatmap.set_clim(-1, 1)  # 设置颜色范围为（-1，1）
    # 调整子图参数，填充整个图像区
    plt.tight_layout()
    plt.show()




get_csi300_pearson_correlation_heatmap()