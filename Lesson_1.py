import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import mpl_finance
import matplotlib.dates as mdates
from candlestick import william_edu_candlestick
from matplotlib import style  # 美化图表


style.use('ggplot')  # 使用ggplot样式，对图表进行美化


# 生成指定股票的指定日均线
def stock_ma(stock, n):
    # 调用tushare接口获取股票数据
    stock_data = ts.get_hist_data(stock)
    stock_data = stock_data.sort_index(ascending=True)  # 调整表格顺序，使用日期升序
    # .rolling(window=n)表示每n个求和，.mean()为求平均值
    stock_data['ma_n'] = stock_data['close'].rolling(window=n).mean()
    stock_data.dropna(inplace=True)  # 清洗包含Nan的行
    stock_data['ma_n'].plot()  # 该语句调用的是pandas的画图工具
    plt.show()
    return


# 使用matplotlib画图
def stock_ma_use_plt(stock, n):
    stock_data = ts.get_hist_data(stock)
    stock_data = stock_data.sort_index(ascending=True)
    stock_data.index = stock_data.index.astype('datetime64[ns]')  # 将index类型转变为datetime
    stock_data['ma_n'] = stock_data['close'].rolling(window=n).mean()
    stock_data.dropna(inplace=True)
    # plt.plot(stock_data['ma_n'])
    # 使用plt.subplot2grid(shape,loc,rowspan,colspan)设置画布(大小，起始位置，行数，列数），实现多子图
    ax1 = plt.subplot2grid((15, 10), (0, 0), rowspan=9, colspan=10)
    ax2 = plt.subplot2grid((15, 10), (10, 0), rowspan=5, colspan=10, sharex=ax1)  # 参数sharex=ax1表示与ax1共用x轴
    ax1.xaxis_date()  # 将设置x轴时间格式
    # 将收盘价、均价生成在ax1画布，交易量生成在ax2画布
    ax1.plot(stock_data.index, stock_data['close'])
    ax1.plot(stock_data.index, stock_data['ma_n'])
    ax2.bar(stock_data.index, stock_data['volume'])
    plt.legend()
    plt.show()
    return
# 读取csv文件，parse_dates=True参数将csv中的时间字符串转换成日期格式
# df = pd.read_csv('000001.csv',parse_dates=True,index_col='date')


# 绘制K线,以下代码调用william_edu_candlestick函数
# 使用mpl_finance中candlestick()函数，x轴坐标有问题
# 使用mplfinance中plot(stock_data,type='candle')函数，是更好的解决办法
def candlestick(stock):
    ax1 = plt.subplot2grid((15, 10), (0, 0), rowspan=9, colspan=10)
    ax2 = plt.subplot2grid((15, 10), (10, 0), rowspan=5, colspan=10, sharex=ax1)
    stock_data = ts.get_hist_data(stock)
    stock_data = stock_data.sort_index(ascending=True)
    stock_data = stock_data[['open', 'close', 'high', 'low', 'volume']]
    # 重置索引，并通过map(mdates.date2num)解决.date列时间格式问题
    stock_data = stock_data.reset_index()
    stock_data['date'] = stock_data['date'].astype('datetime64[ns]')  # 将date列格式统一为datetime64[ns]
    stock_data['date'] = stock_data['date'].map(mdates.date2num)  # 将date转换为mpl下的日期格式
    ax1.xaxis_date()  # 将设置x轴时间格式
    # mpf.plot(stock_data,type='candle')
    william_edu_candlestick(ax1, stock_data.values, width=1, colordown='green', colorup='red', alpha=0.75)
    ax2.bar(stock_data['date'],stock_data['volume'])
    plt.show()


candlestick('600916')
