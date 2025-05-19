# Importing the package with important classes like card, player, deck etc.
import cards_blackjack 

if __name__ == "__main__":
    print("WELCOME TO BLACKJACK!!")
    round_num = 1
    game_on = True
    players = []

    # Taking inputs on number of players and there names and saving it in the players list.
    while True:
        try:
            players_num = int(input("\nHow many players are there? [1-5]"))
        except ValueError:
            print("Invalid input, please try again!")
            continue
        if players_num > 0 and players_num < 6:
            for i in range(players_num):
                name = input(f"Player {i+1}, enter your name: ")
                players.append(cards_blackjack.Player(name))
            break
        print("Sorry, number of players can be from 1 player minimum to 5 players maximum, please try again!")

    while game_on:

        # Checking if the game is still on after round number 1
        if round_num != 1:
            replay = input("Game ended, do you want to continue playing (Y or N)")
            if replay != 'Y':
                game_on = False
                print("Thank you for playing, come back later!")
                break
        

        print(f"Round number: {round_num}")

        # Creating new deck of cards and shuffling it
        new_deck = cards_blackjack.Deck()
        new_deck.shuffle()
        
        players_blackjack = []
        
        # For all the players, getting their bet amount and providing them with the first 2 cards.
        for i,player in enumerate(players):
            player.mycards = []
            player.bet()
            player.add_cards(new_deck.selectOne())
            player.add_cards(new_deck.selectOne())
            if player.show_cards():
                players_blackjack.append(i)
        
        # Creating the dealer object and give dealer his first 2 cards.
        dealer = cards_blackjack.Dealer()
        dealer.add_cards(new_deck.selectOne())
        dealer.add_cards(new_deck.selectOne())

        if dealer.mypoints == 21:
            if len(players_blackjack) == 0:
                print("Only dealer has a blackjack")
                round_num += 1
                continue
            else:
                for index in players_blackjack:
                    players[index].balance += players[index].bet_amount
                    print(f"Dealer also has a blackjack, {player.name} has pushed back")
                round_num += 1
                continue

        players_lost = []

        for i,player in enumerate(players):
            if i not in players_blackjack:
                if player.game_action(new_deck):
                    players_lost.append(i)
        
        if len(players_lost) > 0:
            for i in sorted(players_lost, reverse=True):
                players.pop(i)
        
        #if all the players have busted, game over!
        if len(players) == 0:
            print("All players busted!")
            round_num += 1
            continue
        
        dealer.show_cards()
        
        players_can_win = 0
        for player in players:
            if(dealer.mypoints <= player.mypoints):
                players_can_win+= 1
        if players_can_win > 0:
            dealer.game_action(new_deck)
        else:
            print("Dealer has won, all other players lost!")
            round_num += 1
            continue
        
        if dealer.total_points() > 21:
            for player in players:
                player.balance += (player.bet_amount * 2)
            round_num += 1
            continue
                
        for player in sorted(players, key=lambda x: x.mypoints):
            if (player.mypoint == 21):
                player.balance += (player.bet_amount * 2.5)
                print(f"{player.name} has a blackjack and they won 2.5 times of the bet amount!")
            elif (dealer.mypoints > player.mypoints):
                print(f"{player.name} has lost as your points are less than dealer's points.")
            elif (dealer.mypoints == player.mypoints):
                print(f"{player.name} has pushed back as your points matches the dealer's points.")
                player.balance += (player.bet_amount)
            else:
                print(f"{player.name} has won as your points are more than dealer's points.")
                player.balance += (player.bet_amount * 2)
        round_num += 1