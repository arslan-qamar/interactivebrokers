from IBDataFetcher import IBDataFetcher
from Strategies.SimpleMacdCrossOver import *
import csv


stock = input("Enter your stock symbol : ")

stock = 'AAPL'
stocks = ['AAPL', 'NIO', 'XPEV', 'PLTR', 'AMD', 'SNAP', 'LI', 'SQ', 'BABA', 'MSFT', 'PTON', 'TSLA', 'CCL', 'FVRR', 'PINS', 'ETSY', 'DDOG', 'ADBE', 'UPWK' ]

#stocks = ['NIO', 'XPEV', 'PLTR', 'FVRR', 'SQ']

barSizeSettings = ['5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours']
barSizeSettings = ['1 min']#, '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours']


ib = IBDataFetcher().get_IBClient() 

# Multiple time frames

combined_calculations = pd.DataFrame() 
all_Signals_Csv =  f'All Tickers - BackTested Signals - {datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'

with open(all_Signals_Csv, mode='w') as all_Signals_File:
    all_Signals_File_Writer = csv.writer(all_Signals_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    all_Signals_File_Writer.writerow(["symbol" , "barSizeSetting", "total_trades", "amount_to_invest", "close_price_profit", "close_price_profitloss_percentage" , "close_price_winrate" , "open_price_profit" , "open_price_profitloss_percentage", "open_price_winrate"])
    all_Signals_File.close()

for stock in stocks:
    stock = Stock(symbol=stock, exchange='SMART', currency='USD')
    for barSizeSetting in barSizeSettings:
        contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col = GetSimpleMovingAverageCrossOverStrategyDataFrame(ib, contract=stock, display_table=False, 
        saveToCsvFile=True, duration='2 D', barSizeSetting = barSizeSetting)

        show_chart(stock, contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col, saveImageToFile=True, displayChart=False)

        #input('Press any key to close the chart')
        
        symbol , barSizeSetting, total_trades, amount_to_invest, close_price_profit, close_price_profitloss_percentage , close_price_winrate , open_price_profit , open_price_profitloss_percentage, open_price_winrate = back_test(stock, signals, barSizeSetting, saveToCsvFile=True, displayTable=False)

        
        with open(all_Signals_Csv, mode='a') as all_Signals_File:
            all_Signals_File_Writer = csv.writer(all_Signals_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            all_Signals_File_Writer.writerow([symbol , barSizeSetting, total_trades, amount_to_invest, close_price_profit, close_price_profitloss_percentage , close_price_winrate , open_price_profit , open_price_profitloss_percentage, open_price_winrate])
            all_Signals_File.close()