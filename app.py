from flask import Flask, request, jsonify, send_from_directory
import cards_blackjack
import random

app = Flask(__name__, static_folder='static')

# Store game state in memory
game_state = {
    "deck": None,
    "players": [],
    "dealer": None,
    "round_num": 1,
    "players_blackjack": [],
    "players_lost": [],
    "current_player_index": 0,
    "game_phase": "setup"  # setup, betting, player_turns, dealer_turn, round_end
}

@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.json
    player_names = data.get("players", [])
    
    # Reset game state
    game_state["round_num"] = 1
    game_state["players"] = [cards_blackjack.Player(name) for name in player_names]
    game_state["game_phase"] = "betting"
    
    return jsonify({"status": "started", "message": "Game started! Place your bets."})

@app.route('/api/bet', methods=['POST'])
def place_bet():
    data = request.json
    player_index = data.get("player_index", 0)
    amount = data.get("amount", 0)
    
    # Check if player index is valid before accessing
    if player_index < 0 or player_index >= len(game_state["players"]):
        return jsonify({
            "status": "error", 
            "message": f"Invalid player index: {player_index}. There are {len(game_state['players'])} players."
        })
    
    player = game_state["players"][player_index]
    if amount <= 0 or amount > player.balance:
        return jsonify({"status": "error", "message": "Invalid bet amount"})
        
    player.balance -= amount
    player.bet_amount = amount
    
    # Check if all players have bet
    all_bet = all(hasattr(p, 'bet_amount') and p.bet_amount > 0 for p in game_state["players"])
    
    if all_bet:
        # Start the round
        game_state["game_phase"] = "player_turns"
        game_state["current_player_index"] = 0
        game_state["deck"] = cards_blackjack.Deck()
        game_state["deck"].shuffle()
        game_state["dealer"] = cards_blackjack.Dealer()
        game_state["players_blackjack"] = []
        game_state["players_lost"] = []
        
        # Deal initial cards
        for player in game_state["players"]:
            player.mycards = []
            player.add_cards(game_state["deck"].selectOne())
            player.add_cards(game_state["deck"].selectOne())
            if player.total_points() == 21:
                game_state["players_blackjack"].append(game_state["players"].index(player))
        
        game_state["dealer"].add_cards(game_state["deck"].selectOne())
        game_state["dealer"].add_cards(game_state["deck"].selectOne())
        
        # Check for dealer blackjack
        dealer_blackjack = game_state["dealer"].total_points() == 21 and len(game_state["dealer"].mycards) == 2
        
        if dealer_blackjack:
            game_state["game_phase"] = "round_end"
            return handle_dealer_turn()
            
        # Skip players with blackjack - advance to the first player who doesn't have blackjack
        while (game_state["current_player_index"] < len(game_state["players"]) and game_state["current_player_index"] in game_state["players_blackjack"]):
            game_state["current_player_index"] += 1
            
        # If all players have blackjack, go to dealer's turn
        if game_state["current_player_index"] >= len(game_state["players"]):
            return handle_dealer_turn()
    
    return jsonify({
        "status": "bet_placed",
        "message": f"Bet of {amount} placed for {game_state['players'][player_index].name}",
        "balance": player.balance,
        "all_bet": all_bet
    })

@app.route('/api/hit', methods=['POST'])
def player_hit():
    if game_state["current_player_index"] >= len(game_state["players"]):
        return jsonify({"status": "error", "message": "No active player"})
    
    player = game_state["players"][game_state["current_player_index"]]
    card = game_state["deck"].selectOne()
    player.add_cards(card)
    
    points = player.total_points()
    busted = points > 21
    
    if busted:
        game_state["players_lost"].append(game_state["current_player_index"])
        game_state["current_player_index"] += 1
        
        if game_state["current_player_index"] >= len(game_state["players"]):
            return handle_dealer_turn()
    
    return jsonify({
        "status": "hit",
        "card": str(card),
        "player_name": player.name,
        "points": points,
        "busted": busted,
        "next_player": game_state["current_player_index"] if busted else None
    })

@app.route('/api/stand', methods=['POST'])
def player_stand():
    game_state["current_player_index"] += 1
    
    if game_state["current_player_index"] >= len(game_state["players"]):
        return handle_dealer_turn()
    
    return jsonify({
        "status": "stand",
        "next_player": game_state["current_player_index"]
    })

def handle_dealer_turn():
    game_state["game_phase"] = "dealer_turn"
    
    # Remove busted players and blackjack players
    active_players = [
        p for i, p in enumerate(game_state["players"]) 
        if i not in game_state["players_lost"] and i not in game_state["players_blackjack"]
    ]
    
    dealer = game_state["dealer"]
    dealer_cards = [str(card) for card in dealer.mycards]
    dealer_points = dealer.total_points()
    
    # Dealer plays if there are active players
    if active_players:
        while dealer.total_points() < 17:
            new_card = game_state["deck"].selectOne()
            dealer.add_cards(new_card)
            dealer_cards.append(str(new_card))
            dealer_points = dealer.total_points()
    
    # Process results
    game_state["game_phase"] = "round_end"
    results = []
    
    # Handle blackjack players first
    for i in game_state["players_blackjack"]:
        player = game_state["players"][i]
        if dealer_points == 21 and len(dealer.mycards) == 2:
            # Push - dealer also has blackjack
            player.balance += player.bet_amount
            results.append({
                "player": player.name, 
                "result": "push",
                "winnings": player.bet_amount,
                "balance": player.balance
            })
        else:
            # Blackjack pays 3:2
            winnings = player.bet_amount * 2.5
            player.balance += winnings
            results.append({
                "player": player.name, 
                "result": "blackjack",
                "winnings": winnings,
                "balance": player.balance
            })
    
    # Handle busted players
    for i in game_state["players_lost"]:
        player = game_state["players"][i]
        results.append({
            "player": player.name, 
            "result": "bust",
            "winnings": 0,
            "balance": player.balance
        })
    
    # Handle remaining active players
    dealer_busted = dealer_points > 21
    for i, player in enumerate(game_state["players"]):
        if i in game_state["players_blackjack"] or i in game_state["players_lost"]:
            continue  # Already handled
            
        player_points = player.total_points()
        
        if dealer_busted:
            # Dealer busted, player wins
            winnings = player.bet_amount * 2
            player.balance += winnings
            results.append({
                "player": player.name, 
                "result": "win",
                "winnings": winnings,
                "balance": player.balance
            })
        elif player_points > dealer_points:
            # Player beats dealer
            winnings = player.bet_amount * 2
            player.balance += winnings
            results.append({
                "player": player.name, 
                "result": "win",
                "winnings": winnings,
                "balance": player.balance
            })
        elif player_points < dealer_points:
            # Dealer beats player
            results.append({
                "player": player.name, 
                "result": "lose",
                "winnings": 0,
                "balance": player.balance
            })
        else:
            # Push - same points
            player.balance += player.bet_amount
            results.append({
                "player": player.name, 
                "result": "push",
                "winnings": player.bet_amount,
                "balance": player.balance
            })
    
    # Reset bet amounts for next round
    for player in game_state["players"]:
        player.bet_amount = 0
        
    game_state["round_num"] += 1
    
    return jsonify({
        "status": "round_end",
        "dealer_cards": dealer_cards,
        "dealer_points": dealer_points,
        "results": results
    })

@app.route('/api/next_round', methods=['POST'])
def next_round():
    game_state["game_phase"] = "betting"
    
    # Keep the existing players (don't reset the player list)
    # Only reset their cards and bets
    for player in game_state["players"]:
        player.bet_amount = 0
        if hasattr(player, 'mycards'):
            player.mycards = []
    
    # Reset these values
    game_state["deck"] = None
    game_state["dealer"] = None
    game_state["players_blackjack"] = []
    game_state["players_lost"] = []
    game_state["current_player_index"] = 0
    
    # Increment round number
    game_state["round_num"] += 1
    
    # Remove players with no money
    game_state["players"] = [p for p in game_state["players"] if p.balance > 0]
    
    if not game_state["players"]:
        game_state["game_phase"] = "setup"
        return jsonify({
            "status": "game_over",
            "message": "All players are out of money!"
        })
    
    return jsonify({
        "status": "next_round",
        "round_num": game_state["round_num"],
        "players": [{
            "name": p.name,
            "balance": p.balance
        } for p in game_state["players"]]
    })

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    return jsonify({
        "phase": game_state["game_phase"],
        "round": game_state["round_num"],
        "current_player": game_state["current_player_index"] if game_state["players"] else -1,
        "players": [{
            "name": p.name,
            "balance": p.balance,
            "bet": p.bet_amount if hasattr(p, 'bet_amount') else 0,
            "cards": [str(card) for card in p.mycards] if hasattr(p, 'mycards') and p.mycards else [],
            "points": p.total_points() if hasattr(p, 'mycards') and p.mycards else 0
        } for p in game_state["players"]],
        "dealer": {
            "cards": [str(card) for card in game_state["dealer"].mycards] if game_state["dealer"] else [],
            "points": game_state["dealer"].total_points() if game_state["dealer"] else 0,
            "visible_card": str(game_state["dealer"].mycards[0]) if game_state["dealer"] and game_state["dealer"].mycards else ""
        } if game_state["dealer"] else None
    })

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)