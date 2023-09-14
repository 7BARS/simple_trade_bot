import psycopg2
from typing import List


take_profit = 0.01  # percent
stop_loss = 0.01  # percent
start_capital = 50.0  # dollars
# minimal_volume = 5.0 # minimal volume for trade on exchange
# tax = 0.0 # tax for trade on exchange


class Deal:
    time: int
    type: int
    quantity: float
    price: float

    def __init__(self, time: int, type: int, quantity: float, price: float):
        self.time = time
        self.type = type
        self.quantity = float(quantity)
        self.price = float(price)

    def get_price(self) -> float:
        return self.price

    def volume(self) -> float:
        return self.price * self.quantity

    def is_buy(self) -> bool:
        return self.type == 1

    def is_sell(self) -> bool:
        return self.type == 2


class Position:
    type: int = 1  # buy = 1, sell = 2
    quantity: float = 0
    price: float = 0
    loss_accumulator: float = 0
    count_of_trade: int = 0
    capital: int
    take_profit: float
    stop_loss: float
    trade_volume: int = 0

    def set_capital(self, capital):
        self.capital = capital

    def set_take_profit(self, take_profit):
        self.take_profit = take_profit

    def set_stop_loss(self, stop_loss):
        self.stop_loss = stop_loss

    def volume(self) -> float:
        return self.price * self.quantity

    def price_take_profit(self) -> float:
        # print("price_take_profit: ", self.price + self.price * self.take_profit)
        return self.price + self.price * self.take_profit

    def price_stop_loss(self) -> float:
        # print("price_stop_loss: ", self.price + self.price * self.stop_loss)
        return self.price - self.price * self.stop_loss

    def is_buy(self) -> bool:
        return self.type == 1

    def is_sell(self) -> bool:
        return self.type == 2

    def buy(self, deal: Deal):
        if self.volume() > deal.volume():
            return

        self.type = 2
        self.count_of_trade += 1
        self.price = deal.get_price()
        self.quantity = self.capital / self.price
        self.trade_volume += self.volume()

    def sell(self, deal: Deal):
        deal_price = deal.get_price()
        # print("deal_price: ", deal_price)
        if self.price_take_profit() < deal_price or self.price_stop_loss() > deal_price:
            return

        self.type = 1
        self.count_of_trade += 1
        self.capital = deal_price * self.quantity
        self.price = 0
        self.quantity = 0
        self.trade_volume += self.capital
        return

    def summary(self):
        print(
            "count of deals: %d, finished capital: %f, generated volume: %d $"
            % (self.count_of_trade, self.volume(), self.trade_volume)
        )


conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="127.0.0.1",
    port="5432",
)
cursor = conn.cursor()
query = "SELECT type,time,price,volume FROM DEALS;"
cursor.execute(query)
results = cursor.fetchall()

deals: List[Deal] = list()
for result in results:
    deals.append(
        Deal(type=result[0], time=result[1], price=result[2], quantity=result[3])
    )
conn.close()

position = Position()
position.set_capital(capital=start_capital)
position.set_take_profit(take_profit=take_profit)
position.set_stop_loss(stop_loss=stop_loss)

for deal in deals:
    if deal.is_buy() and position.is_buy():
        position.buy(deal)
        continue
    if deal.is_sell() and position.is_sell():
        position.sell(deal)

position.summary()
