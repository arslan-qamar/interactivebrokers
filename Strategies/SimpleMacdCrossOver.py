import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')
import pandas_datareader.data as web
from IBDataFetcher import IBDataFetcher
from ib_insync import util
from ib_insync.contract import Contract, Stock

def GetSimpleMovingAverageCrossOverStrategyDataFrame(ib, contract, exchange='SMART', currency='USD', start_date = '2020-11-01', end_date = '', 
                               short_window = 9, long_window = 21, moving_avg = 'EMA', 
                               display_table = False, whatToShow='MidPoint', 
                               duration = '7 D', useRTH = 0,
                               barSizeSetting = '15 mins',
                               saveToCsvFile = False                               
                               ):
    '''
    The function takes the contract symbol, time-duration of analysis, 
    look-back periods and the moving-average type(SMA or EMA) as input 
    and returns the respective MA Crossover chart along with the buy/sell signals for the given period.
    '''
    # ib - Client for interactive brokers
    # contract_symbol - (str)contract ticker as on Yahoo finance. Eg: 'ULTRACEMCO.NS' 
    # start_date - (str)start analysis from this date (format: 'YYYY-MM-DD') Eg: '2018-01-01'
    # end_date - (str)end analysis on this date (format: 'YYYY-MM-DD') Eg: '2020-01-01'
    # short_window - (int)lookback period for short-term moving average. Eg: 5, 10, 20 
    # long_window - (int)lookback period for long-term moving average. Eg: 50, 100, 200
    # moving_avg - (str)the type of moving average to use ('SMA' or 'EMA')
    # display_table - (bool)whether to display the date and price table at buy/sell positions(True/False)

    #  the closing price data of the contract for the aforementioned period of time in Pandas dataframe
    
    
    bars = ib.reqHistoricalData(
        contract, endDateTime=end_date, durationStr=duration,
        barSizeSetting=barSizeSetting, whatToShow=whatToShow, useRTH=useRTH)

    # convert to pandas dataframe:
    contract_df = util.df(bars)
    contract_df.dropna(axis = 0, inplace = True) # remove any null rows 
                        
    # column names for long and short moving average columns
    short_window_col = str(short_window) + '_' + moving_avg
    long_window_col = str(long_window) + '_' + moving_avg  

    if moving_avg == 'SMA':
        # Create a short simple moving average column
        contract_df[short_window_col] = contract_df['close'].rolling(window = short_window, min_periods = 1).mean()

        # Create a long simple moving average column
        contract_df[long_window_col] = contract_df['close'].rolling(window = long_window, min_periods = 1).mean()

    elif moving_avg == 'EMA':
        # Create short exponential moving average column
        contract_df[short_window_col] = contract_df['close'].ewm(span = short_window, adjust = True).mean()

        # Create a long exponential moving average column
        contract_df[long_window_col] = contract_df['close'].ewm(span = long_window, adjust = True).mean()

    # create a new column 'Signal' such that if faster moving average is greater than slower moving average 
    # then set Signal as 1 else 0.
    contract_df['Signal'] = 0.0  
    contract_df['Signal'] = np.where(contract_df[short_window_col] > contract_df[long_window_col], 1.0, 0.0) 

    # create a new column 'Position' which is a day-to-day difference of the 'Signal' column. 
    contract_df['Position'] = contract_df['Signal'].diff()

    if display_table == True:
        print(tabulate(contract_df, headers = 'keys', tablefmt = 'csv')) 
    
    signals = contract_df[(contract_df['Position'] == 1) | (contract_df['Position'] == -1)]        
    signals['Position'] = signals['Position'].apply(lambda x: 'Buy' if x == 1 else 'Sell')

    if saveToCsvFile:        
        contract_df.to_csv(f'{contract.symbol} - All Data - BarSize {barSizeSetting} - {datetime.now().strftime("%Y%m%d-%H%M%S")}.csv', index = False)
        signals.to_csv(f'{contract.symbol} - BarSize {barSizeSetting} - {datetime.now().strftime("%Y%m%d-%H%M%S")}.csv', index = False)
    
    if display_table == True:
        print(tabulate(signals, headers = 'keys', tablefmt = 'csv')) 
    
    return contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col
                    

# show chart of the dataframe
def show_chart(contract, contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col, xtickScaleSample = 0):
    
    plt.figure(figsize = (20,10))
    plt.style.use('fivethirtyeight')
    plt.tick_params(axis = 'both', labelsize = 14)
    plt.ylabel('Price in USD', fontsize = 16 )
    plt.xlabel('Date Time', fontsize = 16 )
    

    plt.title(str(contract.symbol) + ' - ' + str(moving_avg) + ' Crossover Period ' + str(barSizeSetting) , fontsize = 20)
    plt.legend()
    plt.grid()      
    
    # plot close price, short-term and long-term moving average    
    dtFmt = mdates.DateFormatter('%d/%m %H:%M:%S') # define the formatting    
    plt.gca().xaxis.set_major_formatter(dtFmt) # apply the format to the desired axis
    if xtickScaleSample > 0:
        plt.xticks(contract_df['date'].values[0::xtickScaleSample], rotation=90)
    contract_df.set_index('date', inplace = True)

    contract_df['close'].plot(color = 'k', lw = 1, label = 'close')  
    contract_df[short_window_col].plot(color = 'b', lw = 1, label = short_window_col)
    contract_df[long_window_col].plot(color = 'g', lw = 1, label = long_window_col) 

    # plot 'buy' signals
    plt.plot(contract_df[contract_df['Position'] == 1].index, 
            contract_df[short_window_col][contract_df['Position'] == 1], 
            '^', markersize = 15, color = 'g', alpha = 0.7, label = 'buy')

    # plot 'sell' signals
    plt.plot(contract_df[contract_df['Position'] == -1].index, 
            contract_df[short_window_col][contract_df['Position'] == -1], 
            'v', markersize = 15, color = 'r', alpha = 0.7, label = 'sell')

    plt.tight_layout()
    plt.pause(0.05)
    input('Press any key to close the chart')

# this method calculates the profit based on signal column in the dataframe
def back_test(signals_df, barSizeSetting):
    amount_to_invest = 5000
    #Remove the last row if it is a buy as the position is still open and should not be used to calculate profits
    signals_df = remove_last_buy_position(signals_df)
    
    #Remove the first row if it is a sell as we should start from buy entry
    signals_df = remove_first_sell_position(signals_df)

    signals_df['Close Price Units Traded'] = 0
    signals_df['Close Price Units Traded'][signals_df['Position'] == "Buy"] = amount_to_invest / signals_df['close']
    signals_df['Close Price Units Traded'][signals_df['Position'] == "Sell"] = signals_df['Close Price Units Traded'].shift()
    
    signals_df['Buy Sell At Close Price'] = signals_df['close']
    signals_df['Buy Sell At Close Price'][signals_df['Position'] == "Buy"] =  -1*signals_df['close']*signals_df['Close Price Units Traded']
    signals_df['Buy Sell At Close Price'][signals_df['Position'] == "Sell"] =  signals_df['close']*signals_df['Close Price Units Traded']
    
    signals_df['Close Price Rolling Sum Profit'] = 0
    signals_df['Close Price Rolling Sum Profit'][signals_df['Position'] == "Sell"] = signals_df['Buy Sell At Close Price'].rolling(2).sum()
    signals_df['Close Price Successful Trade'] = signals_df.apply(calculate_success, column_Name='Close Price Rolling Sum Profit', axis=1)
    
    signals_df['Open Price Units Traded'] = 0
    signals_df['Open Price Units Traded'][signals_df['Position'] == "Buy"] = amount_to_invest / signals_df['open']
    signals_df['Open Price Units Traded'][signals_df['Position'] == "Sell"] = signals_df['Open Price Units Traded'].shift()


    signals_df['Buy Sell At Open Price'] = signals_df['open']
    signals_df['Buy Sell At Open Price'][signals_df['Position'] == "Buy"] =  -1*signals_df['open']*signals_df['Open Price Units Traded']
    signals_df['Buy Sell At Open Price'][signals_df['Position'] == "Sell"] =  signals_df['open']*signals_df['Open Price Units Traded']

    signals_df['Open Price Rolling Sum Profit'] = 0
    signals_df['Open Price Rolling Sum Profit'][signals_df['Position'] == "Sell"] = signals_df['Buy Sell At Open Price'].rolling(2).sum()
    signals_df['Open Price Successful Trade'] = signals_df.apply(calculate_success, column_Name='Open Price Rolling Sum Profit', axis=1)

    signals_df['Close Price vs Open Price'] = signals_df['Close Price Rolling Sum Profit'] - signals_df['Open Price Rolling Sum Profit']

    print(f"BarSize : {barSizeSetting}, Total Trade : {signals_df.index.size/2},  Close Price Profit : {signals_df['Close Price Rolling Sum Profit'].sum()},  Profit Loss Percentage : {calculate_ProfitLoss_Percentage(signals_df,'Close Price Rolling Sum Profit',amount_to_invest)},  Win Rate : {calculate_winrate(signals_df, 'Close Price Successful Trade')}")
    print(f"BarSize : {barSizeSetting}, Total Trade : {signals_df.index.size/2}, Open Price Profit : {signals_df['Open Price Rolling Sum Profit'].sum()} , Profit Loss Percentage : {calculate_ProfitLoss_Percentage(signals_df,'Open Price Rolling Sum Profit',amount_to_invest)}, Win Rate : {calculate_winrate(signals_df, 'Open Price Successful Trade')}")
    print('====================================================')


# Remove the first row if it is a sell position as it should not be used to calculate profits as we are trading long positions only
def remove_first_sell_position(signals_df):
    if signals_df.size > 0 and signals_df.iloc[[0]].iloc[0].Position == "Sell":
        signals_df = signals_df[:1]
    return signals_df

# Remove the last row if it is a buy as the position is still open and should not be used to calculate profits
def remove_last_buy_position(signals_df):    
    if signals_df.size > 0 and signals_df.iloc[[-1]].iloc[0].Position == "Buy":
        signals_df = signals_df[:-1]
    return signals_df

# Calculate the profit loss percentage for trades
def calculate_ProfitLoss_Percentage(signals_df, column_Name, amount_to_invest):
    return signals_df[column_Name].sum()/amount_to_invest * 100

# Calculate the winrate for trades
def calculate_winrate(signals_df, column_Name):
    if signals_df.index.size == 0:
        return 0
    return np.count_nonzero(signals_df[column_Name])/(signals_df.index.size/2) * 100
    
# Calculate success helper method
def calculate_success(signals_df, column_Name):
    if signals_df.index.size == 0 or signals_df['Position'] == "Buy":
        return ""
    elif signals_df['Position'] == "Sell" and signals_df[column_Name] > 0:
        return True
    elif signals_df['Position'] == "Sell" and signals_df[column_Name] <= 0:
        return False
