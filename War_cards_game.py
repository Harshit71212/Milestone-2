import cards_war    

player_one = cards_war.Player(input("Player 1 enter you name: "))
player_two = cards_war.Player(input("Player 2 enter you name: "))

new_deck = cards_war.Deck()
new_deck.shuffle()

for x in range(26):
    player_one.add_cards(new_deck.onecard())
    player_two.add_cards(new_deck.onecard())

game_on = True
round_num = 0
while game_on:
    round_num += 1
    print(f"Round number : {round_num}")

    #Check to see if any of players is out of cards:
    if(len(player_one.allcards) == 0):
        print(f"{player_one.name} out of cards! Game over")
        print(f"{player_two.name} wins")
        game_on = False
        break
    if(len(player_two.allcards) == 0):
        print(f"{player_two.name} out of cards! Game over")
        print(f"{player_one.name} wins")
        game_on = False
        break

    #Otherwise the game is still on
    #Start a new round and reset cards "on the table"

    player_one_cards = []
    player_one_cards.append(player_one.remove_one())
    print(f"{player_one_cards[-1]}")

    player_two_cards = []
    player_two_cards.append(player_two.remove_one())
    print(f"{player_two_cards[-1]}")

    at_war = True
    while at_war:
        if player_one_cards[-1].value > player_two_cards[-1].value:
            player_one.add_cards(player_one_cards)
            player_one.add_cards(player_two_cards)

            at_war = False
        
        elif player_one_cards[-1].value < player_two_cards[-1].value:
            player_two.add_cards(player_one_cards)
            player_two.add_cards(player_two_cards)

            at_war = False

        else:
            print("WAR")
            if(len(player_one.allcards)) < 5:
                print(f"{player_one.name} unable to play war! Game over at War")
                print(f"{player_two.name} Wins! {player_one.name} Loses!")
                game_on = False
                break
            elif(len(player_two.allcards)) < 5:
                print(f"{player_two.name} unable to play war! Game over at War")
                print(f"{player_one.name} Wins! {player_two.name} Loses!")
                game_on = False
                break
            else:
                print("We're still at war!")
                for num in range(5):
                    player_one_cards.append(player_one.remove_one())
                    print(f"{player_one_cards[-1]}")
                    player_two_cards.append(player_two.remove_one())
                    print(f"{player_two_cards[-1]}")



















"""
Harshit = Player(name="Harshit")
Harshit.add_cards([Card("Hearts", "Two"),Card("Diamonds", "King")])
print(Harshit)
Harshit.remove()
print(Harshit)

mydeck = Deck()
#mydeck.shuffle()
print(f"{mydeck}\n")
print(f"The card removed is : {mydeck.onecard()}\n")
print(mydeck)
print(len(mydeck))

mycard2 = Card("Hearts","Jack")
print(mycard2)
print(mycard2.value)
print(mycard2.suit)
print(mycard2.rank)

mycard = Card(random.choice(suits), random.choice(ranks))
print(mycard)
print(mycard.value)

"""
