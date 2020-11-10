from IBDataFetcher import IBDataFetcher
from Strategies.SimpleMacdCrossOver import *
import csv
from ib_insync.order import MarketOrder
from ib_insync.contract import Forex
from asyncio.tasks import sleep
import logging
import coloredlogs
coloredlogs.install()

amount_To_Invest_Per_Signal = 1000
max_Amount_To_Invest_Per_Stock = 5000
max_Stop_Loss_Percentage = 1
minimum_Profit_To_Take = 0.5

def executeNewSignals(stock, previousSignals, currentSignals):
    if currentSignals.size >= previousSignals.size:     
        newSignal = currentSignals.tail(1)       
        executeSignal(stock, newSignal)

def isSellSignal(signal):
    return signal['Position'].iloc[0] == 'Sell'

def isBuySignal(signal):
    return signal['Position'].iloc[0] == 'Buy'


def getQuantity(amount_To_Invest_Per_Signal, currentPrice):
    return round(amount_To_Invest_Per_Signal / currentPrice)

def getPortfolioPosition(stock):
    positions = ib.positions()
    for position in positions:
        if position.contract.symbol == stock.symbol:
            return position 

def getPortfolioItem(stock):
    portfolioItems = ib.portfolio()
    for portfolioItem in portfolioItems:
        if portfolioItem.contract.symbol == stock.symbol:
            return portfolioItem 

def getPortfolioQuantity(stock):
    position = getPortfolioPosition(stock)
    if position:
        return position.position

def shouldSell(stock, signal):
    position = getPortfolioPosition(stock)
    if position:
        if reachedMinimumProfit(stock,  minimum_Profit_To_Take):  
            logging.warning(f'Selling on SELL signal as reached minimum profit of {minimum_Profit_To_Take}')         
            return True
        elif reachedMaximumStopLoss(stock, position, max_Stop_Loss_Percentage):
            logging.error(f'Selling on SELL signal as reached MAXIMUM STOP LOSS of {max_Stop_Loss_Percentage} %')         
            return True
    return False

def sellStock(stock, signal, quantity):    
    trade = None
    if shouldSell(stock, signal):
        order = MarketOrder('SELL', quantity)
        trade = ib.placeOrder(stock, order)
        while not trade.isDone():
            ib.waitOnUpdate()        
    else:
        logging.warning(f'Skipped selling : {trade}')
    return trade

    

def maxInvestedLimitReached(stock, max_Amount_To_Invest_Per_Stock):
    position = getPortfolioPosition(stock)
    if position:
            return position.position * position.avgCost >= max_Amount_To_Invest_Per_Stock
    return False

def buyStock(stock, quantity):
    if not maxInvestedLimitReached(stock, max_Amount_To_Invest_Per_Stock):
        order = MarketOrder('BUY', quantity, outsideRth=True)
        trade = ib.placeOrder(stock, order)
        while not trade.isDone():
            ib.waitOnUpdate()
        return trade
    else:
        logging.warning(f'SKIPPED BUY SIGNAL as Max Invested amount {max_Amount_To_Invest_Per_Stock} reached.')

def reachedMinimumProfit(stock, minimum_Profit_To_Take):
    portfolioItem = getPortfolioItem(stock)
    if portfolioItem:
        return portfolioItem.unrealizedPNL >= (portfolioItem.averageCost * portfolioItem.position) * (minimum_Profit_To_Take / 100)
    return False

def reachedMaximumStopLoss(stock, position, max_Stop_Loss_Percentage):
    portfolioItem = getPortfolioItem(stock)
    if portfolioItem:
        return portfolioItem.unrealizedPNL <= -1 * (position.position * position.avgCost) * (max_Stop_Loss_Percentage/100)
    return False

def executeSignal(stock, signal):
    if isSellSignal(signal):
        logging.warning(f'New SELL signal : {signal}')
        logging.warning(f'current price should be around : {signal["high"].iloc[0]}')
        trade = sellStock(stock, signal, getPortfolioQuantity(stock))
        logging.warning(f'Sold : {trade}')
    
    elif isBuySignal(signal):
        logging.warning(f'New BUY signal : {signal}')
        logging.warning(f'current price should be around : {signal["high"].iloc[0]}')   
        trade = buyStock(stock, getQuantity(amount_To_Invest_Per_Signal, signal["high"].iloc[0]))
        logging.warning(f'Bought : {trade}')


contract = input("Enter your Stock/Forex symbol : ")
contractType = input("Enter Sec Type (Stock / Forex): ")
barSizeSetting = input("Enter Bar Size (15 mins ~> 1 hour) : ")
amount_To_Invest_Per_Signal = int(input("Enter amount to invest per buy signal : "))
max_Amount_To_Invest_Per_Stock = int(input("Enter MAX amount to invest in this contract : "))


logging.basicConfig(filename=f'{contract}.log', level=logging.INFO)
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# # add the handler to the root logger
# logging.getLogger('').addHandler(console)

logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

ib = IBDataFetcher().get_IBClient() 

# Multiple stocks to trade

combined_calculations = pd.DataFrame() 
previousSignals = {}

if(contractType == "Forex"):
    logging.warning('Selected Forex as contract type')
    contract = Forex(symbol=contract, exchange='IdealPro', currency='USD')
else:
    logging.warning('Selected Stock as contract type')
    contract = Stock(symbol=contract, exchange='SMART', currency='USD')

last_HeartBeat_Log = datetime.now()
while(True):
   
    try:
        contract_df, signals, barSizeSetting, moving_avg, short_window_col, long_window_col = GetSimpleMovingAverageCrossOverStrategyDataFrame(ib, contract=contract, display_table=False, 
        saveToCsvFile=True, duration='7 D', barSizeSetting = barSizeSetting)

        if not contract.symbol in previousSignals:
            previousSignals[contract.symbol] = signals

        executeNewSignals(contract, previousSignals[contract.symbol] , signals)
        previousSignals[contract.symbol] = signals

        
        ib.sleep(10.0)
        if (last_HeartBeat_Log - datetime.utcnow()).seconds > 60:
            last_HeartBeat_Log = datetime.utcnow()
            logging.info(f'No New Signal found for {contract.symbol}. Previous signals : {previousSignals[contract.symbol].size}, current signals : {signals.size} ')
            logging.info(f'Last known signal for {contract.symbol}: {signals.tail(1)}')

    except Exception as ex:
        print(ex)
        ib.sleep(10.0)


 