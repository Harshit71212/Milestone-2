import random

suits = ('Hearts','Diamonds','Spades','Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8, 'Nine':9, 'Ten':10, 'Jack':10, 'Queen':10, 'King':10, 'Ace':11}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = values[rank]
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
class Deck:
    def __init__(self):
        self.allcards = []
        for suit in suits:
            for rank in ranks:
                self.allcards.append(Card(rank,suit))
    def __len__(self):
        return len(self.allcards)
    def __str__(self):
        cards = ''
        for card in self.allcards:
            cards = cards + str(card) + '\n'
        return cards
    def shuffle(self):
        random.shuffle(self.allcards)
    def selectOne(self):
        return self.allcards.pop()

class Player:
    def __init__(self,name):
        self.name = name
        self.balance = 10000.00
        self.mycards = []
        self.mypoints = 0
        self.bet_amount = 0
    def bet(self):
        print(f"{self.name}, your available balance is {self.balance} rupees.")
        if self.balance > 0.00:
            while True:
                try:
                    self.bet_amount = float(input("How much amount would you like to bet now: "))
                except ValueError:
                    print("Invalid bet amount, please try again!")
                    continue
                if (self.bet_amount > 0 and self.bet_amount <= self.balance):
                    self.balance = self.balance - self.bet_amount
                    return self.bet_amount
                elif (self.bet_amount > self.balance):
                    print(f"You entered more than you current available balance, you can only bet less than or equal to {self.balance} rupees.")
                    continue
                else:
                    print("Invalid bet amount, please try again!")
                    continue
        print(f"Sorry {self.name}, you are out of balance!, please add money to your balance.")
        choice = input("Do you want to add money to your balance now (Y or N): ")
        if choice == 'Y':
            self.add_money()
        if choice == 'N':
            print("Thank you for playing, please come back later!")

    def add_cards(self,newcard):
        self.mycards.append(newcard)


    def add_money(self):
        while True:
            try:
                self.money = float(input("How much money you would like to add to your game wallet: "))
            except ValueError:
                print("Invalid amount, please try again!")
            if (self.money > 0):
                self.balance = self.balance + self.money
                print(f"Great, your balance is increased to {self.balance} rupees.")
                break
            else:
                print("Invalid amount, please try again!")
        
    def total_points(self):
        self.mypoints = 0
        self.mycards.sort(key=lambda card: card.value)
        for card in self.mycards:
            if(card.rank != 'Ace'):
                self.mypoints += card.value
            elif(self.mypoints<=10):
                self.mypoints += 11
            else:
                self.mypoints+=1
        return self.mypoints

    def show_cards(self):
        x = self.total_points()
        print(f"{self.name} has:", *self.mycards, sep='\n')
        print(f"Total point: {x}")
        if x == 21:
            return True
        
    def game_action(self,deck):
        while True:
            action_choice = input(f"{self.name}, do you want to hit or stand? (Enter H for Hit and S for Stand) ")
            if action_choice == 'H':
                new_card = deck.selectOne()
                self.add_cards(new_card)
                print(f"{new_card} added to {self.name}")
                if self.total_points() > 21:
                    print(f"{self.name} has busted")
                    return True
            elif action_choice == 'S':
                break
            else:
                print("Invalid input, please try again!")

class Dealer(Player):
    def __init__(self):
        self.name = "Dealer"
        self.mypoints = 0
        self.mycards = []
    def add_cards(self,newcard):
        self.mycards.append(newcard)
        if len(self.mycards)==1:
            print(f"Dealer has: {self.mycards[0]}")
    def game_action(self,deck):
        while True:
            if self.mypoints < 17:
                new_card = deck.selectOne()
                self.add_cards(new_card)
                print(f"{new_card} added to {self.name}")
                if self.total_points() > 21:
                    print(f"{self.name} has busted")
            else:
                break