"""Module to calculate trading strategy results"""

import trading_rules as tr
import numpy as np
import math
from date_manip import DateManip

class PnL(tr.RSquareTr):

    def __init__(self):
        super().__init__()

    def pnl_(self):
        super().__call__()
        self.start_date_ = self.series.iloc[0, self.series.columns.get_loc(self.date_name)]
        self.end_date_ = self.series.iloc[-1, self.series.columns.get_loc(self.date_name)]
        self.calcul_pnl()

    def calcul_pnl(self):
        self.diff_ = ((self.end_date_ - self.start_date_).days / 365) #diff in term of year with decimal
        self.pnl_dict[self.range_date_] = self.range_date()
        self.pnl_dict[self.ann_return_] = self.ann_return()
        self.pnl_dict[self.ann_vol_] = self.ann_vol()
        self.pnl_dict[self.sharpe_ratio_] = self.sharpe_ratio()
        self.pnl_dict[self.max_draw_] = self.max_draw()
        self.pnl_dict[self.pour_win_] = self.pour_win()
        self.pnl_dict[self.nb_trades_] = self.nb_trades()

        if (self.pnl_dict[self.nb_trades_] != None):
            if (self.pnl_dict[self.nb_trades_] >= 2):
                if self.pnl_dict[self.sharpe_ratio_] == None:
                    raise Exception("Error in Sharpe Ratio calculation...")
                if math.isnan(self.pnl_dict[self.sharpe_ratio_]):
                    raise Exception("Error in Sharpe Ratio calculation...")



    def annualized_(func):
        """Decorator to return annualized value"""
        def wrap_diff(self):
            return ((1+func(self))**(1/self.diff_)-1)
        return wrap_diff

    @annualized_
    def ann_return(self):
        """Calculate the annualized return"""
        return_ = 0
        for index_ in self.trades_track.index:
            return_ = (1+return_)*(1+self.trades_track.loc[index_,self.trade_return]) - 1
        return return_

    def ann_vol(self):
        """Calculate annualized vol
        """

        vol_ = self.trades_track[self.trade_return].std()
        if not np.isnan(vol_):
            return (vol_ *  math.sqrt(1/self.diff_))
        else :
            return None

    def sharpe_ratio(self):
        """Sharpe ratio

        Not using the risk-free rate has it doesn't change the final result
        """
        if not bool(self.pnl_dict):
            return None

        if self.pnl_dict[self.ann_vol_] == None:
            return None

        elif ((self.pnl_dict[self.ann_vol_] == 0) | np.isnan(self.pnl_dict[self.ann_vol_])):
            return None
        else :
            return (self.pnl_dict[self.ann_return_] /self.pnl_dict[self.ann_vol_])

    def max_draw(self):
        """Return lowest value """

        return self.trades_track[self.trade_return].min()

    def nb_trades(self):
        """Return the number of trades"""
        return self.trades_track.shape[0]

    def range_date(self):
        """ Return the range date tested in a desired format

        Using "%Y-%m-%d" as Timestamp format
        """
        dm_begin_ = DateManip(self.date_debut).end_format(self.end_format_)
        dm_end_ = DateManip(self.date_fin).end_format(self.end_format_)
        return f"{dm_begin_} to {dm_end_}"

    def pour_win(self):
        """Return the pourcentage of winning trades
        """

        total_trade = self.nb_trades()
        pour_win_ = self.trades_track[self.trades_track[self.trade_return] >= 0].shape[0]
        return 0 if total_trade == 0 else (pour_win_ / total_trade)