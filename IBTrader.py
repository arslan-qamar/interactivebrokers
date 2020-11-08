from IBDataFetcher import IBDataFetcher
from Strategies.SimpleMacdCrossOver import *


stock = input("Enter your stock symbol : ")

stock = 'AAPL'

stock = Stock(symbol=stock, exchange='SMART', currency='USD')



barSizeSettings = [ '30 secs', '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours', '3 hours', '4 hours' ],

ib = IBDataFetcher().get_IBClient()                    
contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col = GetSimpleMovingAverageCrossOverStrategyDataFrame(ib, contract=stock, display_table=True, 
saveToCsvFile=True, duration='7 D')

show_chart(stock, contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col)

   



