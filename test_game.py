from game import *

print('The aim of the game is to make more money than a bot through buying and selling the same stock.')
print()
print('You and the bot start on the same balance and each round the stock price changes.')
print('At the start of each round, you will offer a bid and ask price.')
print('You must always bid at a price lower than the market price and ask higher than the market (to make profit).')
print('Each round, whoever offers a more attractive bid price will buy a unit at this price.')
print('Each round, whoever offers a more attractive ask price will sell a unit at this price.')
print('At the end of each round, your balance and inventory will be updated.')
print('Going long on a position increases your inventory by 1. Going short on a position decreases your inventory by 1.')
print('Players must make sure that their inventory does not exceed the maximum number of long or short positions.')
print('If your inventory does exceed the limit, you will be forced to buy/sell a unit at an unfavourable price.')
print('At the end of the game, you will be forced to buy/sell so that you have a neutral inventory.')
print()
print('The price is modelled using geometric brownian motion (a Gaussian distribution) with random drift.')
print('The price of a single unit starts at £10.00.')
print('The stock price also incorporates volatility, simulating the real world. The amount of volatility determines how difficult the game is.')
print()
input('Type enter to start the game.')
print()

print('------------ Game Settings ------------')
print('To select your level of difficulty enter 1 (easiest), 2 or 3 (hardest).')
while True:
    try:
        difficulty = int(input('Difficulty: '))
        if difficulty == 1:
            stock_volatility = 0.1
            break
        elif difficulty == 2:
            stock_volatility = 0.25
            break
        elif difficulty == 3:
            stock_volatility = 0.5
            break
        else:
            print('You must enter one of the integer values 1, 2 or 3.')      
    except:
        print('You must enter one of the integer values 1, 2 or 3.')

while True:
    try:
        num_rounds = int(input('Number of rounds: '))
        break
    except ValueError:
        print('You must enter an integer.')

price_history = []
initial_stock_price = 10
drift_rate_mean = 0.02
drift_rate_std = 0.01
position_limit = num_rounds - 2
initial_balance = initial_stock_price * (num_rounds)
player_balance = initial_balance
bot_balance = initial_balance
player_inventory = 0
bot_inventory = 0

print(f'The inventory limit for this game is {position_limit}.')
print()

game = gameComponents(num_rounds, price_history, initial_stock_price, stock_volatility, drift_rate_mean, drift_rate_std, initial_balance, position_limit, player_balance, player_inventory, bot_balance, bot_inventory)

game.game()
