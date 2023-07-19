import pandas as pd
import matplotlib.pyplot as plt
import datetime

class Data:
    """ This class wraps one data point
    """
    def __init__(self, symbol : str, date : datetime.datetime, price : float, indicators : list):

        self.Symbol = symbol
        self.Price = price
        self.Indicators = indicators
        self.Date = date

    def __str__(self) -> str:
        return f'Date: {self.Date}, Symbol: {self.Symbol}, Price: {self.Price}'
        

    
class OHLCV:
    """This class wraps OHLCV dataframe
    """
    def __init__(self, ohlcv : pd.DataFrame, symbol : str, price_column : str = 'Adj Close' ,indicator_columns : list = []):
        self.ohlcv = ohlcv
        self.price_column = price_column
        self.size = self.ohlcv.shape[0]
        self.symbol = symbol
        self.indicator_columns = indicator_columns

    def __iter__(self):
        return OHLCVIter(self)
    
class OHLCVIter:    
    """ This class defines iterator for the OHLCV class
    """
    def __init__(self, OHLCV : OHLCV):
        self._ohlcv = OHLCV.ohlcv
        self._ohlcv_size = OHLCV.size
        self._symbol = OHLCV.symbol
        self._price_column = OHLCV.price_column
        self._indicator_columns = OHLCV.indicator_columns
        self._current_index = 0

    def __iter__(self):
        return self    
    
    def __next__(self):
        if self._current_index < self._ohlcv_size:
            row = self._ohlcv[self._current_index:self._current_index + 1:]
            indicators = {}
            for i in self._indicator_columns:
                indicators[i] = row[i].item()
            data = Data(self._symbol,row['Date'].item(), row[self._price_column].item(),indicators)         
            self._current_index += 1
            return data        
        raise StopIteration
    
class Algorithm():
    def __init__(self):
        pass

    def onData(self,data : Data) -> None:
        pass 

class Portfolio:
    def __init__(self,cash_amount):
        self.initial_amount = cash_amount
        self.current_cash = cash_amount
        self.cum_return = 1
        self.buy_price = 0
        self.in_position = False
        self.trades_curve =  []

        self.return_curve = []

        self.last_price = 0

        self.curr_return = 1

        self.ath = 0

        self.dds = []

    
    def update_return_curve(self,data : Data) -> None:
        if self.in_position:
            self.curr_return *= data.Price/self.last_price

            self.return_curve.append(self.curr_return)
            self.current_cash = self.current_cash*self.curr_return
            self.last_price = data.Price
        else:
            self.return_curve.append(self.curr_return)

        if self.curr_return > self.ath:
            self.ath = self.curr_return

        self.dds.append(-(1-self.curr_return/self.ath))

    def max_drawdown(self,) -> float:
        return max(self.dds)
    
    def CAR(self, num_of_years : float) -> float:
        return self.return_curve[-1] ** 1/num_of_years
    
    def buy(self, price : float) -> None:
        if self.in_position: return
        self.buy_price = price
        self.last_price = price
        self.in_position = True
    
    def sell(self,price : float) -> None:
        if not self.in_position: return
        
        self.cum_return *= price / self.buy_price
        self.trades_curve.append(self.cum_return)
        # self.current_cash = self.initial_amount *  self.cum_return
        self.in_position = False

class Engine:


    def __init__(self,algorithm : Algorithm, ohlcv,symbol, price_column = 'Adj Close', indicator_columns = []):
        self.algorithm = algorithm
        self.df = ohlcv
        self.ohlcv = OHLCV(ohlcv=ohlcv,symbol = symbol, price_column=price_column,indicator_columns=indicator_columns)

    def run(self,verbose : bool = False, plot : bool = False) -> float:
        """Runs the engine calling the algorithm on each data point

        Args:
            verbose (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        for data in self.ohlcv:
            self.algorithm.portfolio.update_return_curve(data)
            self.algorithm.onData(data)
        
        if verbose:
            print('Return: {:.2f} %'.format((self.algorithm.portfolio.cum_return - 1) * 100))
            print('Max drawdown: {:.2f} %'.format(self.algorithm.portfolio.max_drawdown()* 100))
            first_price = [x.Price for x in self.ohlcv][0]
            last_price = [x.Price for x in self.ohlcv][-1]
            print('Buy and hold return: {:.2f} %'.format((last_price/first_price - 1) * 100))
        
        if plot:
            fig, ax1 = plt.subplots()

            ax2 = ax1.twinx()
            ax1.plot(self.df['Date'].to_list(), self.algorithm.portfolio.return_curve, 'g-')
            # ax2.plot(df_spy['Date'].to_list(), df_spy['Adj Close'], 'b-')

            plt.show()
        return self.algorithm.portfolio.cum_return - 1
    




def run_algorithm(algorithm,ohlcv, symbol, indicator_columns = [],verbose = False, plot = False):
    
    engine = Engine(algorithm, ohlcv, symbol,indicator_columns=indicator_columns)
    engine.run(verbose=verbose, plot = plot)
