import random

suits = ('Hearts','Diamonds','Spades','Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8, 'Nine':9, 'Ten':10, 'Jack':11, 'Queen':12, 'King':13, 'Ace':14}

class Card:
    def __init__(self,suit,rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]
    def __str__(self):
        return self.rank +" of "+self.suit

class Deck:
    def __init__(self):
        self.allcard = []
        for suit in suits:
            for rank in ranks:
                self.allcard.append(Card(suit,rank))
    def shuffle(self):
        random.shuffle(self.allcard)
    def onecard(self):
        return self.allcard.pop()
    def __str__(self):
        cards = ""
        for card in self.allcard:
            cards = cards + card.rank +" of "+card.suit+" \n"
        return cards
    def __len__(self):
        return len(self.allcard)

class Player:
    def __init__(self,name):
        self.name = name
        self.allcards = []
    def remove_one(self):
        return self.allcards.pop(0)
    def add_cards(self,newcard):
        if type(newcard) == type([]):
            self.allcards.extend(newcard)
        else:
            self.allcards.append(newcard)
    def __str__(self):
        return f"{self.name} has {len(self.allcards)} cards."