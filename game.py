import numpy as np

class gameComponents:
    def __init__(self, num_rounds, price_history, initial_stock_price, stock_volatility, drift_rate_mean, drift_rate_std, initial_balance, position_limit, player_balance, player_inventory, bot_balance, bot_inventory):
        self.T = num_rounds             # total number of rounds
        self.dt = 1                     # time step in the brownian motion simulation is 1 round
        self.S = price_history          # array of the price history 
        self.S0 = initial_stock_price   # stock price at start of the round
        self.sigma = stock_volatility   # volatility of stock - adjusted for difficulty level of game
        self.mu_mean = drift_rate_mean  # mean of drift rate distribution
        self.mu_std = drift_rate_std    # standard deviation of drift rate distribution
        self.ib = initial_balance
        self.pl = position_limit        # position limit for player/bot's portfolio
        self.pb = player_balance        # player's balance
        self.pi = player_inventory      # player's inventory based on it's current positions (+ve for long and -ve for short)
        self.bb = bot_balance           # bot's balance
        self.bi = bot_inventory         # bot's inventory
    
    def generate_price(self):
        self.S.append(self.S0)
        
        for i in range(self.T):
            # Generate random drift component for each step
            mu = np.random.normal(self.mu_mean, self.mu_std)
            # Generate random normal shock for Brownian motion component
            Z = np.random.normal(0, 1)

            # Generate stock price using the Geometric Brownian Motion formula with random drift
            St = self.S[-1] * np.exp((mu - 0.5 * self.sigma**2) * self.dt + self.sigma * np.sqrt(self.dt) * Z)
        
        return round(St, 2)
    

    def bot_decision(self):
        ## Implement a dynamic spread based on volatility (higher volatility -> greater uncertainty -> wider spread)
        # These base prices will be adjusted later 
        multiplier = 10
        dynamic_spread = multiplier * self.sigma

        base_bid = self.S[-1] - (dynamic_spread / 2)
        base_ask = self.S[-1] + (dynamic_spread / 2)


        ## Implement inventory-based spread adjustment to encourage trades to ensure that the inventory does not go over the limit
        # 2 is the sensitivity of the bot to its inventory limits
        inventory_adjustment_factor = (abs(self.bi) / self.pl) * 2

        ## Implement trend following to encourage trades influenced by trend analysis
        # Using a window to calculate the moving average, the trend strenght is considered
        window_size = 3
        if len(self.S) < window_size:
            moving_av = np.mean(self.S)
        else:
            moving_av = np.mean(self.S[-window_size:])
        # Price change sensitivity will also be considered if there is a rapid change in the price
        if len(self.S) < 2:
            rate_of_change = 0
        else:
            rate_of_change = self.S[-1] - self.S[-2]
        # Calculate trend adjustment factor
        if moving_av != 0:
            trend_adjustment_factor = rate_of_change / moving_av
        else:
            trend_adjustment_factor = 0


        ## Combine adjustment factors
        # Consider if bot is long (positive inventory)
        if self.bi > 0:
            # Upward trend - raise bid and ask to sell more aggressively
            if rate_of_change > 0:
                adjusted_bid = base_bid + inventory_adjustment_factor * trend_adjustment_factor
                adjusted_ask = base_ask + inventory_adjustment_factor * trend_adjustment_factor
            # Downward trend - lower bid and ask to avoid buying too much
            elif rate_of_change < 0:
                adjusted_bid = base_bid - inventory_adjustment_factor * trend_adjustment_factor
                adjusted_ask = base_ask - inventory_adjustment_factor * trend_adjustment_factor
            # Flat trend
            else: 
                adjusted_bid = base_bid
                adjusted_ask = base_ask

        # Consider if bot is short (negative inventory)
        elif self.bi < 0:
            # Upward trend - lower bid and ask to buy more cautiously
            if rate_of_change > 0:
                adjusted_bid = base_bid - inventory_adjustment_factor * trend_adjustment_factor
                adjusted_ask = base_ask - inventory_adjustment_factor * trend_adjustment_factor
            # Downward trend - raise bid and ask to buy back more aggressively 
            elif rate_of_change < 0:
                adjusted_bid = base_bid + inventory_adjustment_factor * trend_adjustment_factor
                adjusted_ask = base_ask + inventory_adjustment_factor * trend_adjustment_factor
            # Flat trend
            else: 
                adjusted_bid = base_bid
                adjusted_ask = base_ask
        
        # Bot has no positions
        else:
            adjusted_bid = base_bid
            adjusted_ask = base_ask

        # If scalars mean bot wants to bid at a higher price or sell at a lower price, change these values to the limits
        if (adjusted_bid >= self.S[-1]):
            adjusted_bid = self.S[-1] - 0.01
        
        if (adjusted_ask <= self.S[-1]):
            adjusted_ask = self.S[-1] + 0.01
        
        bid = round(adjusted_bid, 2)
        ask = round(adjusted_ask, 2)

        return bid, ask
    
    def player_decision(self):
        print(f'The current stock price is £{self.S[-1]:.2f}')
        print()

        while True:
            # Input player's bid price
            bid = float(input('Bid price: £'))
            if (round(bid, 2) == bid) and (bid < self.S[-1]):
                break
            else:
                print('You must enter a bid price less than the current market price with exactly 2 decimal places')
        
        while True:
            # Input player's ask price
            ask = float(input('Ask price: £'))
            if (round(ask, 2) == ask) and (ask > self.S[-1]):
                break
            else:
                print('You must enter a ask price more than the current market price with exactly 2 decimal places')

        return bid, ask

    def check_position_limit(self, character, balance, inventory):
        # Character is 'the player' or 'the bot'
        # Long on too many positions
        if (inventory > self.pl):
            # Sell at an unfavourable price (60% of current market price)
            sale_price = 0.6 * self.S[-1]
            new_balance = balance + sale_price
            new_inventory = inventory - 1
            print(f'Message to {character}')
            print(f'You are long on too many positions. You are forced to sell at 40% under the current market price ({sale_price}).')
            return round(new_balance, 2), round(new_inventory, 2)
        # Short on too many posititons
        if (inventory < (-self.pl)):
            # Buy back at an unfavourable price (40% over current market price)
            buy_price = 1.4 * self.S[-1]
            new_balance = balance - buy_price
            new_inventory = inventory + 1
            print(f'Message to {character}:')
            print(f'You are short on too many positions. You are forced to buy at 40% over the current market price ({buy_price}).')
            print()
            return round(new_balance, 2), round(new_inventory, 2)
        # Not exceeding position limit
        else:
            return balance, inventory
        
    def single_round(self):
        print('Start of round statistics:')
        print(f'Player- Balance: £{self.pb:.2f}, Inventory: {self.pi}')
        print(f'Bot- Balance: £{self.bb:.2f}, Inventory: {self.bi}')
        print()

        player_bid, player_ask = self.player_decision()
        bot_bid, bot_ask = self.bot_decision()

        print()
        print(f'Bid prices - Player: £{player_bid:.2f}, Bot: £{bot_bid:.2f}')
        # Player bids higher than bot
        if (player_bid > bot_bid):
            print('Player has bid higher than the bot and buys a single asset.')
            print(f"Player's inventory increases by 1 and player's balance decreases by £{player_bid:.2f}.")
            self.pb -= player_bid
            self.pi += 1
        # Bot bids higher than player
        elif (bot_bid > player_bid):
            print('Bot has bid higher than the player and buys a single asset.')
            print(f"Bot's inventory increases by 1 and bot's balance decreases by £{bot_bid:.2f}.")
            self.bb -= bot_bid
            self.bi += 1
        # Player and bot bids the same
        else:
            print('Both the player and bot have bid the exact same price. Therefore, no stock is bought this round.')
        print()

        print(f'Ask prices - Player: £{player_ask:.2f}, Bot: £{bot_ask:.2f}')
        # Player asks lower than bot
        if (player_ask < bot_ask):
            print('Player has asked for a lower price than the bot and sells a single asset.')
            print(f"Player's inventory decreases by 1 and player's balance increases by £{player_ask:.2f}")
            self.pb += player_ask
            self.pi -= 1
        # Bot asks lower than player
        elif (bot_ask < player_ask):
            print('Bot has asked for a lower price than the player and sells a single asset.')
            print(f"Bot's inventory decreases by 1 and bot's balance increases by £{bot_ask:.2f}")
            self.bb += bot_ask
            self.bi -= 1
        # Player and bot asks the same
        else:
            print('Both the player and bot have asked the exact same price. Therefore, no stock is sold this round.')
        print()

        self.pb, self.pi = self.check_position_limit("the player", self.pb, self.pi)
        self.bb, self.bi = self.check_position_limit("the bot", self.bb, self.bi)

        print('End of round statistics:')
        print(f'Player- Balance: £{self.pb:.2f}, Inventory: {self.pi}')
        print(f'Bot- Balance: £{self.bb:.2f}, Inventory: {self.bi}')
        
    def game(self):
        for i in range(self.T):
            print(f'---------- Round number {i + 1}/{self.T} ----------')
            current_price = self.generate_price()
            self.S.append(current_price)
            self.single_round()

            print()
            input('Type enter to progress to the next round.')
            print()
        
        print(f'------------ Game Complete ------------')
        print('End of game statistics:')
        print(f'Player- Balance: £{self.pb:.2f}, Inventory: {self.pi}')
        print(f'Bot- Balance: £{self.bb:.2f}, Inventory: {self.bi}')
        print()
        profit = self.pb - self.ib
        if (profit > 0):
            if (self.pb > self.bb):
                print(f'Congratulations! You beat the bot and made a profit of £{profit:.2f}.')
            elif (self.pb < self.bb):
                print(f'You lost to the bot but made a profit of £{profit:.2f}.')
            else:
                print(f'You drew to the bot and you both made a profit of £{profit:.2f}.')
        elif (profit < 0):
            print(f'You made a loss of £{abs(profit):.2f}. Try again to make a profit')
        else:
            print(f'You went neutral. Try again to make a profit')




        

