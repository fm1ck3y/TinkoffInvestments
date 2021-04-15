import time
from datetime import datetime
from rich import box
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.measure import Measurement
from tinkoff_api import TinkoffApi
from utils import CurrencyHelper

console = Console()

class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]Tinkoff Investments[/b]",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid)

def make_layout(portfolio):
    layout = Layout(name="Tinkoff")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
    )
    layout['main'].split(
        Layout(name = 'table', ratio = 5),
        Layout(name = 'currencies', ratio = 1.5),
        direction="horizontal",
    )
    layout['header'].update(
       Header()
    )
    layout['table'].update(
        Align.center(
            PortfolioTable(portfolio),
        )
    )
    layout['currencies'].update(
        CurrenciesTable()
    )
    return layout

def live_screen():
    tinkoff = TinkoffApi()
    portfolio = tinkoff.download_portfolio() 
    layout = make_layout(portfolio)
    time_update = 0
    with Live(layout, console = console ,auto_refresh = False, screen=False, vertical_overflow = 'crop') as live:
        while True:
            if time_update == 10:
                portfolio = tinkoff.download_portfolio() 
                time_update = 0
            live.update(make_layout(portfolio),refresh = True)
            time.sleep(1)
            time_update += 1


class PortfolioTable:
    
    def __init__(self,portfolio):
        self.table = Table()
        self.set_table_settings()
        self.update_columns()
        self.update_rows(portfolio)

    def set_table_settings(self):
        original_width = Measurement.get(console, self.table).maximum
        self.table.row_styles = ["none", "dim"]
        self.table.border_style = "bright_yellow"
        self.table.pad_edge = False
        self.table.box = box.SIMPLE_HEAVY

    def __rich__(self) -> Panel:
        return Panel(Align.center(self.table),style="")

    def update_columns(self):
        self.table.add_column("Type",justify = "center",style="rgb(161,161,161)", ratio = 3)
        self.table.add_column("Name",justify = "center",style="rgb(206,206,206)", ratio = 1)
        self.table.add_column("Amount",justify = "center",style="rgb(161,161,161)",ratio = 5)
        self.table.add_column('Ticker',justify = 'center' , style = 'rgb(161,161,161)', ratio = 4)
        self.table.add_column("Avg. buy",justify = "right",style="rgb(161,161,161)",ratio = 3)
        self.table.add_column("Current price",justify = "right",style="rgb(161,161,161)", ratio = 3)
        self.table.add_column("Yield",justify = "right" , ratio = 3)
        self.table.add_column("Yield %",justify = "right", ratio = 4)
    
    def update_rows(self,portfolio):
        format_value = lambda value : ("[green]+" if position.Yield > 0 else "[red]") + str(round(value,2))
        for position in portfolio:
            self.table.add_row(
                position.type,
                position.name,
                str(position.amount),
                position.ticker,
                str(round(position.avg_buy,2)) + ' ' + position.currency,
                str(round(position.current_price,2)) + ' ' + position.currency,
                format_value(position.Yield) +  ' ' + position.currency,
                format_value(position.yield_proc) +  ' ' + "%"
            )

class CurrenciesTable:
    def __init__(self):
        self.currencies = [
            'USD','EUR','UZS','AUD','GBP','CNY'
        ]
        self.table = Table()
        self.set_table_settings()
        self.update_columns()
        self.update_rows()

    def set_table_settings(self):
        self.table.row_styles = ["none", "dim"]
        self.table.border_style = "bright_yellow"
        self.table.pad_edge = False
        self.table.box = box.SIMPLE_HEAVY
    
    def update_columns(self):
        self.table.add_column("Currency",justify = "center",style="rgb(161,161,161)", ratio = 2)
        self.table.add_column("Value",justify = "right",style="rgb(161,161,161)", ratio = 1)
    
    def update_rows(self):
        for currency in self.currencies:
            self.table.add_row(currency,
                               str(CurrencyHelper.get_course_to_rub(currency)) + ' ₽'
                              )

    def __rich__(self):
        return Panel(Align.center(self.table),style="")
