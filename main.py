# limit buy 10 99.00
# limit buy 15 100.00
# limit buy 3 100.50
# limit sell 5 100.00
# limit buy 5 99.50
# stop sell 3 99.49
# cancel na 2 0.00
# market sell 6 0.00
#
# match taker maker volume price
#
# match 4 3 3 100.5
# match 4 2 2 100
# match 8 5 5 99.5
# match 8 1 1 99.0
# match 6 1 3 99.00
import heapq
class Order(object):
    def __init__(self, parameters, id):
        self.typeOfOrder = parameters[0]
        self.action = parameters[1]
        self.number = int(parameters[2])
        self.amount = float(parameters[3])
        self.id = id

class Exchange(object):
    def __init__(self):
        #limit buy_order is max_heap, negative
        self.existing_limit_buy_order = []
        #limit sell order is min_heap, positive
        self.existing_limit_sell_order = []

        #market buy order is just a list ordered by time
        self.existing_market_buy_order = []
        #market sell order is just a list ordered by time
        self.existing_market_sell_order = []

        #stop order is sequential
        self.stop_order = []
        self.stop_order_to_be_triggered = []

    def _try_to_trigger_stop_action(self):
        "trigger buy stop action with price buy higher than stop action price"
        new_stop_order_list = []

        # self.stop_order_to_be_triggered
        for stop_order in self.stop_order_to_be_triggered:
            #because stop order is treated as market order, it could only work with limit order
            if stop_order.action == "buy":
                #market order buy + limit order sell
                # previous_order limit sell + new_order market buy
                while len(self.existing_limit_sell_order) > 0 and stop_order.number > 0:
                    (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_sell_order)
                    self._opposing_stop_order(limit_previous_order, stop_order)

                self._try_to_add_order_to_stop_book(stop_order)
            elif stop_order.action == "sell":
                while len(self.existing_limit_buy_order) > 0 and stop_order.number > 0:
                    (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_buy_order)
                    self._opposing_stop_order(limit_previous_order, stop_order)
                self._try_to_add_order_to_stop_book(stop_order)
    def _opposing_stop_order(self, previous_order, stop_order):
        amount = previous_order.amount
        taker_id = -1
        maker_id = -1
        if new_order.action == "buy":
            taker_id = previous_order.id
            maker_id = stop_order.id
        elif new_order.action == "sell":
            taker_id = stop_order.id
            maker_id = previous_order.id
        if previous_order.number <= stop_order.number:
            # previous_order is completely fulfilled
            print "match " + str(taker_id) + " " + str(maker_id) + \
                  " " + str(previous_order.number) + " " + "{0:.2f}".format(amount)
            stop_order.number -= previous_order.number

        else:
            # stop_order is completely fulfilled
            print "match " + str(taker_id) + " " + str(maker_id) + \
                  " " + str(stop_order.number) + " " + "{0:.2f}".format(amount)
            previous_order.number -= new_order.number
            stop_order.number = 0

            # previous order is not fulfilled completely
            if previous_order.action == "buy":
                heapq.heappush(self.existing_limit_buy_order, (-previous_order.amount, previous_order))
            elif previous_order.action == "sell":
                heapq.heappush(self.existing_limit_sell_order, (previous_order.amount, previous_order))


    def _try_to_add_order_to_stop_book(self, stop_order):
        if stop_order.number == 0:
            return
        else:
            self.stop_order.append(stop_order)

    def process_order(self, new_order):
        if new_order.typeOfOrder == "stop":
            self.stop_order.append(new_order)
        elif new_order.typeOfOrder == "cancel":
            self.existing_limit_buy_order = filter(lambda elem: elem[1].id != new_order.number, self.existing_limit_buy_order)
            heapq.heapify(self.existing_limit_buy_order)
            self.existing_limit_sell_order = filter(lambda elem: elem[1].id != new_order.number, self.existing_limit_sell_order)
            heapq.heapify(self.existing_limit_sell_order)

            self.existing_market_buy_order = filter(lambda elem: elem[1].id != new_order.number,self.existing_market_buy_order)
            self.existing_market_sell_order = filter(lambda elem: elem[1].id != new_order.number,self.existing_market_sell_order)

        else:
            if new_order.action == "buy":
                if new_order.typeOfOrder == "market":
                    #previous_order limit sell + new_order market buy
                    while len(self.existing_limit_sell_order) and new_order.number > 0:
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_sell_order)
                        self._opposing_order_helper(limit_previous_order, new_order)

                    self._try_to_add_order_to_book(new_order, "buy")
                    self._try_to_trigger_stop_action()
                elif new_order.typeOfOrder == "limit":
                    #previous_order limit_sell, previous_order market_sell + new_order limit buy
                    while new_order.number > 0 and len(self.existing_limit_sell_order) > 0 and len(self.existing_market_sell_order) > 0:
                        market_previous_order = self.existing_market_sell_order[0]
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_sell_order)
                        if limit_previous_order.amount > new_order.amount:
                            #fullfill limit price first
                            self._opposing_order_helper(limit_previous_order, new_order)

                        elif limit_previous_order.amount == new_order.amount:
                            if market_previous_order.id < limit_previous_order.id:
                                #fullfill market order first because it comes first in terms of time
                                heapq.heappush(self.existing_limit_sell_order, (limit_price, limit_previous_order))
                                self._opposing_order_helper(market_previous_order, new_order)

                        else:
                            heapq.heappush(self.existing_limit_sell_order, (limit_price, limit_previous_order))
                            #will not fullfill previous limit order but can fullfill any unfullfilled previous market sell order
                            self._opposing_order_helper(market_previous_order, new_order)

                    while new_order.number > 0 and len(self.existing_limit_sell_order) > 0:
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_sell_order)
                        if limit_previous_order.amount >= new_order.amount:
                            self._opposing_order_helper(limit_previous_order, new_order)

                    while new_order.number > 0 and len(self.existing_market_sell_order) > 0:
                        market_previous_order = self.existing_market_sell_order[0]
                        self._opposing_order_helper(market_previous_order, new_order)


                    #try to add the new_order to corresponding existing_order
                    self._try_to_add_order_to_book(new_order, "buy")
                    self._try_to_trigger_stop_action()
            else:
                if new_order.typeOfOrder == "market":
                    # previous_order limit buy + new_order market sell
                    while len(self.existing_limit_buy_order) and new_order.number > 0:
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_buy_order)
                        self._opposing_order_helper(limit_previous_order, new_order)


                    self._try_to_add_order_to_book(new_order, "sell")
                    self._try_to_trigger_stop_action()
                elif new_order.typeOfOrder == "limit":
                    # previous_order limit_buy, previous_order market_buy + new_order limit sell
                    while new_order.number > 0 and len(self.existing_limit_buy_order) > 0 and len(
                            self.existing_market_buy_order) > 0:
                        market_previous_order = self.existing_market_buy_order[0]
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_buy_order)
                        if limit_previous_order.amount < new_order.amount:
                            # fullfill limit price first
                            self._opposing_order_helper(limit_previous_order, new_order)


                        elif limit_previous_order.amount == new_order.amount:
                            if market_previous_order.id < limit_previous_order.id:
                                # fullfill market order first because it comes first in terms of time
                                heapq.heappush(self.existing_limit_buy_order, (limit_price, limit_previous_order))
                                self._opposing_order_helper(market_previous_order, new_order)

                            else:
                                # fullfill limit order first because it comes first in terms of time
                                "don't need to do anything with market_previous_order"
                                self._opposing_order_helper(limit_previous_order, new_order)

                        else:
                            heapq.heappush(self.existing_limit_buy_order, (limit_price, limit_previous_order))
                            # will not fullfill previous limit order but can fullfill any unfullfilled previous market sell order
                            self._opposing_order_helper(market_previous_order, new_order)

                    while new_order.number > 0 and len(self.existing_limit_buy_order) > 0:
                        (limit_price, limit_previous_order) = heapq.heappop(self.existing_limit_buy_order)
                        if limit_previous_order.amount >= new_order.amount:
                            self._opposing_order_helper(limit_previous_order, new_order)

                    while new_order.number > 0 and len(self.existing_market_buy_order) > 0:
                        market_previous_order = self.existing_market_buy_order[0]
                        self._opposing_order_helper(market_previous_order, new_order)

                    # try to add the new_order to corresponding existing_order
                    self._try_to_add_order_to_book(new_order, "sell")
                    self._try_to_trigger_stop_action()


    def _try_to_add_order_to_book(self, new_order, which_book):
        if new_order.number == 0:
            return
        if new_order.typeOfOrder == "market":
            if which_book == "buy":
                self.existing_market_buy_order.append(new_order)
            elif which_book == "sell":
                self.existing_market_sell_order.append(new_order)
        else:
            if which_book == "buy":
                heapq.heappush(self.existing_limit_buy_order, (-new_order.amount, new_order))
            elif which_book == "sell":
                heapq.heappush(self.existing_limit_sell_order, (new_order.amount, new_order))

    def _mark_stop_order_to_be_triggered(self, trigger_price):

        "trigger buy stop action with price buy higher than stop action price"
        stop_order_not_triggered = []
        for stop_order in self.stop_order:
            if stop_order.action == "buy" and stop_order.amount <= trigger_price:
                self.stop_order_to_be_triggered.append(stop_order)
            elif stop_order.action == "sell" and stop_order.amount >= trigger_price:
                self.stop_order_to_be_triggered.append(stop_order)
            else:
                stop_order_not_triggered.append(stop_order)

        self.stop_order = stop_order_not_triggered

    def _opposing_order_helper(self, previous_order, new_order):
        amount = 0
        if previous_order.typeOfOrder == "market" and new_order.typeOfOrder == "market":
            # market order can't trade directly with market order
            return
        if previous_order.typeOfOrder == "market" and new_order.typeOfOrder == "limit":
            # market order sell + limit order buy
            amount = new_order.amount
        elif previous_order.typeOfOrder == "limit" and new_order.typeOfOrder == "market":
            # limit order sell + market order buy
            amount = previous_order.amount
        elif previous_order.typeOfOrder == "limit" and new_order.typeOfOrder == "limit":
            # limit order sell + limit order buy
            amount = max(previous_order.amount, new_order.amount)


        taker_id = -1
        maker_id = -1
        if new_order.action == "buy":
            taker_id = previous_order.id
            maker_id = new_order.id
        elif new_order.action == "sell":

            taker_id = new_order.id
            maker_id = previous_order.id

        if previous_order.number <= new_order.number:
            #previous_order is completely fulfilled
            print "match " + str(taker_id) + " " + str(maker_id) + \
                  " " + str(previous_order.number) + " " + "{0:.2f}".format(amount)
            new_order.number -= previous_order.number

            # previous order is fulfilled completely
            if previous_order.typeOfOrder == "market":
                if previous_order.action == "buy":
                    del self.existing_market_buy_order[0]
                elif previous_order.action == "sell":
                    del self.existing_market_sell_order[0]


        else:
            # new_order is completely fulfilled
            print "match " + str(taker_id) + " " + str(maker_id) + \
                  " " + str(new_order.number) + " " + "{0:.2f}".format(amount)
            previous_order.number -= new_order.number
            new_order.number = 0

            #previous order is not fulfilled completely
            if previous_order.typeOfOrder == "limit":
                if previous_order.action == "buy":
                    heapq.heappush(self.existing_limit_buy_order, (-previous_order.amount, previous_order))
                elif previous_order.action == "sell":
                    heapq.heappush(self.existing_limit_sell_order, (previous_order.amount, previous_order))

        self._mark_stop_order_to_be_triggered(amount)




id = 1
exchangeMachine = Exchange()
# input = [
#     # 'market sell 6 0.0',
#     # 'limit buy 1 33.3',
#     # 'limit buy 1 33.4',
#     # 'limit buy 1 33.5',
#     # 'market buy 3 0.0'
#     'limit buy 10 99.00',
#     'limit buy 15 100.00',
#     'limit buy 3 100.5',
#     'limit sell 5 100.00',
#     'limit buy 5 99.5',
#     'stop sell 3 99.49',
#     'cancel na 2 0.00',
#     'market sell 6 0.00',
#     # 'market buy 5 99.3'
#     # 'limit sell 5 100.2',
#     # 'limit buy 3 100.3',
#
#
#
# ]
# # input = [
# #     'stop sell 3 99.49',
# #     'stop buy 3 99.7',
# #     'limit buy 4 100.1',
# #     'limit sell 5 98.3'
# # ]
# for i in input:
#     words = i.split()
#     new_order = Order(parameters=words, id=id)
#     exchangeMachine.process_order(new_order)
#     id += 1
while True:
    row = raw_input()
    words = row.split()
    new_order = Order(parameters=words, id=id)
    exchangeMachine.process_order(new_order)
    id += 1

