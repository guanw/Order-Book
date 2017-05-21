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
        #buy_order is max_heap, negative
        self.existing_buy_order = []
        #sell order is min_heap, positive
        self.existing_sell_order = []
        self.total_sell = 0
        self.total_buy = 0
        self.stop_order = []
        self.cancel_order = []

    def process_order(self, new_order):
        if new_order.typeOfOrder == "stop":
            self.stop_order.append(new_order)
            #TODO process stop order
        elif new_order.typeOfOrder == "cancel":
            #TODO process cancel order
            self.cancel_ordera.append(new_order)
        else:
            if new_order.action == "buy":

                if new_order.typeOfOrder == "market":

                    while len(self.existing_sell_order) > 0:
                        (price, previous_order) = heapq.heappop(self.existing_sell_order)
                        if self._opposing_order_helper(previous_order, new_order):
                            # the new_order has been opposed completely
                            break
                    self._try_to_add_order_to_book(new_order, "buy")
                elif new_order.typeOfOrder == "limit":
                    while len(self.existing_sell_order) > 0:
                        (price, previous_order) = heapq.heappop(self.existing_sell_order)
                        if previous_order.amount <= new_order.amount:
                            #continue to buy because the sell price is below our limit
                            if self._opposing_order_helper(previous_order, new_order):
                                #the new_order has been opposed completely
                                break
                        else:
                            heapq.heappush(self.existing_sell_order, (price, previous_order))
                            break
                    self._try_to_add_order_to_book(new_order, "buy")
            else:

                if new_order.typeOfOrder == "market":
                    while len(self.existing_buy_order) > 0:
                        (price, previous_order) = heapq.heappop(self.existing_buy_order)
                        if self._opposing_order_helper(previous_order, new_order):
                            break
                elif new_order.typeOfOrder == "limit":
                    while len(self.existing_buy_order) > 0:
                        (price, previous_order) = heapq.heappop(self.existing_buy_order)
                        if previous_order.amount >= new_order.amount:
                            # continue to sell because the buy price is above our limit
                            if self._opposing_order_helper(previous_order, new_order):
                                # the new_order has been opposed completely
                                break
                        else:
                            heapq.heappush(self.existing_buy_order, (price, previous_order))
                            break
                    self._try_to_add_order_to_book(new_order, "sell")



    def _try_to_add_order_to_book(self, new_order, which_book):
        if which_book == "buy" and new_order.number > 0:
            self.total_buy += new_order.number
            heapq.heappush(self.existing_buy_order, (-new_order.amount, new_order))
        elif which_book == "sell" and new_order.number > 0:
            self.total_sell += new_order.number
            heapq.heappush(self.existing_sell_order, (new_order.amount, new_order))

    def _opposing_order_helper(self, previous_order, new_order):
        if new_order.action == "buy":
            if previous_order.number <= new_order.number:
                print "match " + str(previous_order.id) + " " + str(new_order.id) + \
                      " " + str(previous_order.number) + " " + str(previous_order.amount)
                new_order.number -= previous_order.number
                self.total_sell -= previous_order.number
                return False
            else:
                print "match " + str(previous_order.id) + " " + str(new_order.id) + \
                      " " + str(new_order.number) + " " + str(new_order.amount)
                previous_order.number -= new_order.number
                self.total_sell -= new_order.number
                heapq.heappush(self.existing_sell_order, (previous_order.amount, previous_order))
                new_order.number = 0
                return True
        else:
            if previous_order.number <= new_order.number:
                print "match " + str(new_order.id) + " " + str(previous_order.id)+ \
                      " " + str(previous_order.number) + " " + str(previous_order.amount)
                new_order.number -= previous_order.number
                self.total_buy -= previous_order.number
                return False
            else:
                print "match " + str(new_order.id) + " " + str(previous_order.id) + \
                      " " + str(new_order.number) + " " + str(new_order.amount)
                previous_order.number -= new_order.number
                self.total_buy -= new_order.number
                heapq.heappush(self.existing_buy_order, (-previous_order.amount, previous_order))
                new_order.number = 0
                return True



id = 1
exchangeMachine = Exchange()
while True:
    row = raw_input()
    words = row.split()
    new_order = Order(parameters=words, id=id)
    exchangeMachine.process_order(new_order)
    id += 1

