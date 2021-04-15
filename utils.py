from datetime import datetime
from pytz import timezone
from pydantic import ValidationError
from pycbrf.toolbox import ExchangeRates
from decimal import Decimal 

class CurrencyHelper:
    __currency_to_char = {
        'RUB' : '₽',
        'USD' : '$',
        'EUR' : '€',
        'UZS' : 'сўм',
        'AUD' : '$',
        'GBP' : '£',
        'CNY' : '¥',
    }

    @staticmethod    
    def get_char_by_currency(currency):
        try:
            return CurrencyHelper.__currency_to_char[currency]
        except KeyError:
            raise ValidationError

    @staticmethod
    def get_course_to_rub(currency):
        rates = ExchangeRates(get_now())
        rate_currency = rates[currency]
        if rate_currency != None:
            return round(Decimal(rate_currency.value),2)
        return -1

def localize(d: datetime) -> datetime:
    return timezone('Europe/Moscow').localize(d)


def get_now() -> datetime:
    return localize(datetime.now())

