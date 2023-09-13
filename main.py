from typing import List

take_profit = 0.02 # percent
stop_loss = 0.02 # percent
start_capital = 50.0 # dollars
# minimal_volume = 5.0 # minimal volume for trade on exchange
# tax = 0.0 # tax for trade on exchange

class Deal:
    time: int
    type: int
    quantity: float
    price: float

    def get_price(self) -> float:
        return self.price

    def volume(self) -> float:
        return self.price * self.quantity

    def is_buy(self) -> bool:
        return self.type == 1

    def is_sell(self) -> bool:
        return self.type == 2

class Position:
    type: int = 1 # buy = 1, sell = 2
    quantity: float
    price: float
    loss_accumulator: float
    count_of_trade: int
    capital: int
    take_profit: float
    stop_loss: float

    def set_capital(self, capital):
        self.capital = capital
    def set_take_profit(self, take_profit):
        self.take_profit = take_profit
    def set_stop_loss(self, stop_loss):
        self.stop_loss = stop_loss

    def volume(self) -> float:
        return self.price * self.quantity

    def is_buy(self) -> bool:
        return self.type == 1

    def is_sell(self) -> bool:
        return self.type == 2

    def buy(self, deal: Deal):
        if self.volume() < deal.volume():
            return

        self.type = 2
        self.count_of_trade += 1
        self.price = deal.get_price()
        self.quantity = self.capital/self.price

    def sell(self,deal: Deal):
        if (self.price*self.take_profit < deal.get_price() or
            self.price*self.stop_loss > deal.get_price()):
            return

        self.type = 1
        self.count_of_trade += 1
        self.capital = deal.get_price() * self.quantity
        self.price = 0
        self.quantity = 0
        return

    def summary(self):
        print("count of deals: %d, volume: %f", self.count_of_trade, self.volume())

position = Position
position.set_capital(capital=start_capital)
position.set_take_profit(take_profit=take_profit)
position.set_stop_loss(stop_loss=stop_loss)

volumes:List[float] = list()
deals:List[Deal] = list()
for deal in deals:
    if deal.is_buy() and position.is_buy():
        position.buy()
        continue
    if deal.is_sell() and position.is_sell():
        position.sell()
        volumes.append(position.volume())

position.summary()
