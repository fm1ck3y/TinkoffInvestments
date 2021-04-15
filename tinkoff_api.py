from datetime import datetime
import tinvest
import os
from utils import *
from decimal import Decimal
from pydantic import BaseModel,validator
from typing import Optional
from rich import print

class Position(BaseModel):
    type: str
    name: str
    amount: int = 0
    ticker : str = ''
    avg_buy : Optional[Decimal] = 0.0
    currency : str = ""
    current_price : Optional[Decimal] = 0.0
    Yield: Optional[Decimal] = 0.0
    yield_proc: float = 0.0
    
    @validator('currency')
    def currency_name_format(cls,v):
        return CurrencyHelper.get_char_by_currency(v)

TINKOFF_TOKEN = os.getenv('TINKOFF_INVEST_TOKEN')
TINKOFF_BROCKER_ACCOUNT_ID = os.getenv('TINKOFF_BROCKER_ACCOUNT_ID')
TINKOFF_START_DATE = datetime.strptime(os.getenv('TINKOFF_START_DATE'), '%d.%m.%Y')


class TinkoffApi:

    def __init__(self):
        self.client = tinvest.SyncClient(TINKOFF_TOKEN)
        

    def download_portfolio(self):
        portfolio = self.client.get_portfolio()  # tinvest.PortfolioResponse
        positions_array = []
        for position in portfolio.payload.positions:
            # (balance * avg_buy_price + expected_yield) / balance
            current_price = (Decimal(position.average_position_price.value)*\
                     position.balance +\
                     Decimal(position.expected_yield.value)) / position.balance
            
            # expected_yield / (avg_buy_price * balance) * 100
            yield_procent = Decimal(position.expected_yield.value) / \
                                    (Decimal(position.average_position_price.value) * position.balance) \
                                    * 100

            positions_array.append(Position(
                **{
                    'type'    : str(position.instrument_type.value),
                    'name'    : position.name,
                    'amount'  : position.balance,
                    'ticker'  : position.ticker,
                    'avg_buy' : Decimal(position.average_position_price.value),
                    'currency' : str(position.average_position_price.currency.value),
                    'current_price' : current_price, 
                    'Yield':  Decimal(position.expected_yield.value),
                    'yield_proc':  yield_procent
                }
            ))
        return positions_array
TinkoffApi()
