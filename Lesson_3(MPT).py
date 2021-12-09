import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import pickle


def modern_portfolio_theory_simulate(num=2, p_num=1, randoms=False):
    # 随机选取股票
    with open('csi_ticker_list.pickle', 'rb') as f:
        all_tickers_list = pickle.load(f)
    # 使用.seed()设置种子，只要种子一样random结果就一样
    # 使用random.sample(list,n)从list中随机获取n只股票
    if not randoms:
        random.seed(10)
        chioce_tickers_list = random.sample(all_tickers_list, num)
    else:
        chioce_tickers_list = random.sample(all_tickers_list, num)
    print(f'选择的股票为:{chioce_tickers_list}')

    # 计算回报率及cov
    df_chioce_tickers_close_price = pd.DataFrame()
    for ticker in chioce_tickers_list:
        df = pd.read_csv(f'csi300_data/{ticker}.csv', parse_dates=True)
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index('trade_date', inplace=True)
        df = df.sort_index(ascending=True)
        df.rename(columns={'close': ticker}, inplace=True)
        df.drop(
            columns=['index', 'ts_code', 'open', 'high', 'low', 'pre_close', 'change',
                     'pct_chg', 'vol', 'amount'], inplace=True
        )
        if df_chioce_tickers_close_price.empty:
            df_chioce_tickers_close_price = df
        else:
            df_chioce_tickers_close_price = df_chioce_tickers_close_price.join(df, how='outer')
    df_chioce_tickers_close_price.dropna(inplace=True)
    daily_pct_change = df_chioce_tickers_close_price.pct_change()
    daily_pct_change.dropna(inplace=True)
    dailt_cov = daily_pct_change.cov()
    # .resample('Y').sum().mean()意为按年采样求和计算年度收益率后再求平均，得出年度平均收益率
    # .apply(func)表示将重新采样的data传入func函数进行运算
    # .pord()用来计算所有元素的乘积，对于有多个维度的数组可以指定轴，默认axis=0指定计算每一行列的乘积，axis=1则指定计算每一行的乘积
    annual_pct_change = daily_pct_change.resample('Y').apply(lambda x:(1+x).prod()-1).mean()
    # 对年度收益率求协方差
    annual_cov = daily_pct_change.resample('Y').apply(lambda x:(1+x).prod()-1).cov()

    # 计算组合的投资回报及volatility（波动）
    p_return = []
    p_voltility = []
    p_weight = []
    for i in range(p_num):
        # 随机生成组合权重
        weights = np.random.random(num)
        weights /= np.sum(weights)  # 利用比例计算，调整组合权重，使权重的合计为1
        returns = np.dot(weights, annual_pct_change)
        voltility = np.sqrt(np.dot(np.dot(weights, annual_cov), weights.T))
        p_return.append(returns)
        p_voltility.append(voltility)
        p_weight.append(weights)

    # 将回报率、波动率及权重组合生成dataframe
    df_p = pd.DataFrame()
    df_p['p_return'] = p_return
    df_p['p_voltility'] = p_voltility
    for count, ticker in enumerate(chioce_tickers_list):
        df_p[f'W_{ticker}'] = [weight[count] for weight in p_weight]
    # df_p.to_csv('portfolio.csv')

    # 生成散点图
    plt.figure(figsize=(10, 8))  # 设置画布尺寸
    plt.scatter(df_p['p_voltility'], df_p['p_return'])
    plt.grid()  # 设置网格线
    plt.style.use("seaborn")
    plt.xlabel('voltility')
    plt.ylabel('return')
    plt.title('Efficient Frontier')
    plt.show()


modern_portfolio_theory_simulate(3, 500000, randoms=False)
