// blackjack.js

const suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs'];
const ranks = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace'];
const values = {
    'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
};

class Card {
    constructor(rank, suit) {
        this.rank = rank;
        this.suit = suit;
        this.value = values[rank];
    }
    toString() {
        return `${this.rank} of ${this.suit}`;
    }
}

class Deck {
    constructor() {
        this.allCards = [];
        for (let suit of suits) {
            for (let rank of ranks) {
                this.allCards.push(new Card(rank, suit));
            }
        }
    }
    shuffle() {
        for (let i = this.allCards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.allCards[i], this.allCards[j]] = [this.allCards[j], this.allCards[i]];
        }
    }
    selectOne() {
        return this.allCards.pop();
    }
}

class Player {
    constructor(name) {
        this.name = name;
        this.balance = 10000.00;
        this.myCards = [];
        this.myPoints = 0;
    }
    addCards(newCard) {
        this.myCards.push(newCard);
    }
    totalPoints() {
        this.myPoints = 0;
        this.myCards.sort((a, b) => a.value - b.value);
        for (let card of this.myCards) {
            if (card.rank !== 'Ace') {
                this.myPoints += card.value;
            } else if (this.myPoints <= 10) {
                this.myPoints += 11;
            } else {
                this.myPoints += 1;
            }
        }
        return this.myPoints;
    }
    showCards() {
        const points = this.totalPoints();
        console.log(`${this.name} has: ${this.myCards.map(card => card.toString()).join(', ')}`);
        console.log(`Total points: ${points}`);
        return points === 21;
    }
}

class Dealer extends Player {
    constructor() {
        super("Dealer");
    }
    gameAction(deck) {
        while (this.myPoints < 17) {
            const newCard = deck.selectOne();
            this.addCards(newCard);
            console.log(`${newCard.toString()} added to ${this.name}`);
            if (this.totalPoints() > 21) {
                console.log(`${this.name} has busted`);
                break;
            }
        }
    }
}

// Game state variables
let currentPlayerIndex = 0;
let gamePhase = 'setup';
let animationInProgress = false;

// UI control functions
function disableUI() {
    animationInProgress = true;
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = true;
    });
}

function enableUI() {
    animationInProgress = false;
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = false;
    });
}

function showActionMessage(message, duration) {
    showMessage(message);
    
    // You could create a fancy animated message div here if desired
    // For now, we'll just use the regular message area
}

// Function to show specified section and hide others
function showSection(sectionId) {
    document.querySelectorAll('.game-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
}

// Function to update the message
function showMessage(message) {
    const messageElement = document.getElementById('gameMessage');
    if (messageElement) {
        messageElement.innerText = message;
    }
}

// Start the game with player names
function startGame() {
    const namesInput = document.getElementById('playerNames').value;
    if (!namesInput) {
        showMessage('Please enter at least one player name');
        return;
    }
    
    const names = namesInput.split(',').map(name => name.trim()).filter(name => name);
    if (names.length < 1 || names.length > 5) {
        showMessage('Please enter between 1 and 5 player names');
        return;
    }
    
    fetch('/api/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({players: names})
    })
    .then(res => res.json())
    .then(data => {
        gamePhase = 'betting';
        showSection('betting');
        showMessage(data.message);
        refreshGameState();
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error starting game. Please try again.');
    });
}

// Enhanced renderBettingPhase to handle cases where player index might be incorrect
function renderBettingPhase(state) {
    const bettingArea = document.getElementById('bettingArea');
    let html = '';
    
    // Reset any stored player indices to prevent issues
    window.playerIndices = {};
    
    state.players.forEach((player, index) => {
        // Store mapping of player name to index
        window.playerIndices[player.name] = index;
        
        html += `
            <div class="player">
                <h3>${player.name}</h3>
                <p>Balance: ₹${player.balance}</p>
                <div id="bet-area-${index}">
                    <div class="form-group">
                        <input type="number" id="bet-player-${index}" placeholder="Enter bet amount">
                        <button onclick="placeBet(${index})">Place Bet</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    bettingArea.innerHTML = html;
}

// Place bet for a player
function placeBet(playerIndex) {
    // Safety check
    if (playerIndex === undefined || playerIndex < 0) {
        showMessage('Invalid player selection');
        return;
    }
    
    const betInput = document.getElementById(`bet-player-${playerIndex}`);
    if (!betInput) {
        showMessage(`Error: Bet input not found for player ${playerIndex}`);
        console.error(`Bet input not found: bet-player-${playerIndex}`);
        return;
    }
    
    const betAmount = betInput.value;
    if (!betAmount || isNaN(betAmount) || betAmount <= 0) {
        showMessage('Please enter a valid bet amount');
        return;
    }
    
    // Disable the button to prevent double-clicks
    const betButton = document.querySelector(`#bet-area-${playerIndex} button`);
    if (betButton) betButton.disabled = true;
    
    fetch('/api/bet', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            player_index: playerIndex,
            amount: parseFloat(betAmount)
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        if (data.status === 'error') {
            showMessage(data.message);
            console.error(data.message);
            // Re-enable the button on error
            if (betButton) betButton.disabled = false;
            return;
        }
        
        // Find bet area and update it
        const betArea = document.getElementById(`bet-area-${playerIndex}`);
        if (betArea) {
            betArea.innerHTML = `<p>Bet placed: ₹${betAmount}</p>`;
        }
        
        if (data.all_bet) {
            // Start the game
            showMessage("All bets placed! Dealing cards...");
            
            setTimeout(() => {
                gamePhase = 'player_turns';
                showSection('gameplay');
                
                // Get fresh game state
                fetch('/api/game_state')
                    .then(res => res.json())
                    .then(state => {
                        renderGameplayPhase(state);
                    })
                    .catch(error => {
                        console.error("Error fetching game state:", error);
                    });
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error placing bet:', error);
        showMessage('Error placing bet. Please try again.');
        // Re-enable the button on error
        if (betButton) betButton.disabled = false;
    });
}

// Player action: Hit
function hit() {
    fetch('/api/hit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'error') {
            showMessage(data.message);
            return;
        }
        
        refreshGameState();
        
        if (data.busted) {
            showMessage(`${data.player_name} busted with ${data.points} points!`);
        } else {
            showMessage(`${data.player_name} drew ${data.card}. Total: ${data.points} points.`);
        }
        
        if (data.status === 'round_end') {
            showRoundEnd(data);
        } else if (data.next_player !== null) {
            currentPlayerIndex = data.next_player;
            refreshGameState();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error hitting. Please try again.');
    });
}

// Player action: Stand
function stand() {
    fetch('/api/stand', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'round_end') {
            showRoundEnd(data);
        } else {
            currentPlayerIndex = data.next_player;
            showMessage(`Player stood. Next player's turn.`);
            refreshGameState();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error standing. Please try again.');
    });
}

// Start next round
function nextRound() {
    const nextRoundBtn = document.getElementById('nextRoundBtn');
    if (nextRoundBtn) nextRoundBtn.disabled = true;
    
    showMessage("Starting next round...");
    
    fetch('/api/next_round', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'game_over') {
            showMessage(data.message);
            setTimeout(() => {
                showSection('setup');
                if (nextRoundBtn) nextRoundBtn.disabled = false;
            }, 1500);
            return;
        }
        
        // Reset UI state
        gamePhase = 'betting';
        currentPlayerIndex = 0;
        
        setTimeout(() => {
            showSection('betting');
            
            // Fetch fresh game state for betting phase
            fetch('/api/game_state')
                .then(res => res.json())
                .then(state => {
                    renderBettingPhase(state);
                    
                    // Display round message
                    showMessage(`Round ${data.round_num} - Place your bets!`);
                    
                    if (nextRoundBtn) nextRoundBtn.disabled = false;
                })
                .catch(error => {
                    console.error("Error fetching game state:", error);
                    if (nextRoundBtn) nextRoundBtn.disabled = false;
                });
        }, 500);
    })
    .catch(error => {
        console.error('Error starting next round:', error);
        showMessage('Error starting next round. Please try again.');
        if (nextRoundBtn) nextRoundBtn.disabled = false;
    });
}

// Refresh game state from server
function refreshGameState() {
    fetch('/api/game_state')
        .then(res => res.json())
        .then(state => {
            gamePhase = state.phase;
            currentPlayerIndex = state.current_player;
            
            switch (gamePhase) {
                case 'betting':
                    renderBettingPhase(state);
                    break;
                    
                case 'player_turns':
                    renderGameplayPhase(state);
                    break;
                    
                case 'dealer_turn':
                    renderGameplayPhase(state);
                    showMessage("Dealer's turn...");
                    break;
                    
                case 'round_end':
                    // Will be handled by showRoundEnd
                    break;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Render gameplay phase UI
function renderGameplayPhase(state) {
    // Render dealer
    const dealerCards = document.getElementById('dealerCards');
    const dealerPoints = document.getElementById('dealerPoints');
    
    if (state.dealer) {
        // In player turn, show only first card
        if (gamePhase === 'player_turns') {
            dealerCards.innerHTML = renderCard(state.dealer.cards[0]) + '<div class="card back">?</div>';
            dealerPoints.innerHTML = '';
        } else {
            // In dealer turn or round end, show all cards and points
            dealerCards.innerHTML = state.dealer.cards.map(card => renderCard(card)).join('');
            dealerPoints.innerHTML = `Points: ${state.dealer.points}`;
        }
    }
    
    // Render players
    const playersArea = document.getElementById('playersArea');
    let html = '';
    
    state.players.forEach((player, index) => {
        const isActive = index === currentPlayerIndex && gamePhase === 'player_turns';
        const hasBlackjack = player.points === 21 && player.cards.length === 2;
        
        let statusMessage = '';
        if (hasBlackjack) {
            statusMessage = '<div class="status win">BLACKJACK!</div>';
        } else if (isActive) {
            statusMessage = '<div class="status active">YOUR TURN</div>';
        }
        
        html += `
            <div class="player ${isActive ? 'active' : ''} ${hasBlackjack ? 'blackjack' : ''}">
                <h3>${player.name} ${isActive ? '(Active)' : ''}</h3>
                <div class="cards">
                    ${player.cards.map(card => renderCard(card)).join('')}
                </div>
                <div class="points">Points: ${player.points}</div>
                <p>Balance: ₹${player.balance}</p>
                <p>Bet: ₹${player.bet}</p>
                ${statusMessage}
            </div>
        `;
    });
    
    playersArea.innerHTML = html;
    
    // Show/hide action buttons - don't show if current player has blackjack
    const actionButtons = document.getElementById('actions');
    const currentPlayer = state.current_player < state.players.length ? state.players[state.current_player] : null;
    const currentPlayerHasBlackjack = currentPlayer && currentPlayer.points === 21 && currentPlayer.cards.length === 2;
    
    if (gamePhase === 'player_turns' && currentPlayer && !currentPlayerHasBlackjack) {
        actionButtons.style.display = 'flex';
    } else {
        actionButtons.style.display = 'none';
    }
    
    // If it's a player's turn and they have blackjack, automatically stand for them
    if (gamePhase === 'player_turns' && currentPlayerHasBlackjack) {
        showMessage(`${currentPlayer.name} has Blackjack! Automatically standing.`);
        setTimeout(() => {
            stand();
        }, 2000);
    }
}

// Show round end results
function showRoundEnd(data) {
    showSection('roundEnd');
    
    const resultsDiv = document.getElementById('results');
    let html = `
        <div class="dealer-final">
            <h3>Dealer</h3>
            <div class="cards">
                ${data.dealer_cards.map(card => renderCard(card)).join('')}
            </div>
            <div class="points">Points: ${data.dealer_points}</div>
        </div>
        <h3>Results</h3>
    `;
    
    data.results.forEach(result => {
        let resultClass = '';
        if (result.result === 'win' || result.result === 'blackjack') {
            resultClass = 'win';
        } else if (result.result === 'lose' || result.result === 'bust') {
            resultClass = 'lose';
        } else {
            resultClass = 'push';
        }
        
        html += `
            <div class="result-item ${resultClass}">
                <h4>${result.player}</h4>
                <p>${getResultMessage(result)}</p>
                <p>New Balance: ₹${result.balance}</p>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// Helper to generate result message
function getResultMessage(result) {
    switch(result.result) {
        case 'blackjack': 
            return `BLACKJACK! Won ₹${result.winnings}`;
        case 'win': 
            return `Won ₹${result.winnings}`;
        case 'push': 
            return `Push - Bet returned: ₹${result.winnings}`;
        case 'lose': 
            return `Lost bet`;
        case 'bust':
            return `Busted - Lost bet`;
        default: 
            return '';
    }
}

// Render a card as HTML
function renderCard(cardStr) {
    const parts = cardStr.split(' of ');
    if (parts.length !== 2) return `<div class="card">Invalid</div>`;
    
    const rank = parts[0];
    const suit = parts[1];
    
    return `
        <div class="card ${suit.toLowerCase()}">
            <div class="rank">${rank}</div>
            <div class="suit">${getSuitSymbol(suit)}</div>
        </div>
    `;
}

// Get unicode symbol for suit
function getSuitSymbol(suit) {
    switch(suit) {
        case 'Hearts': return '♥';
        case 'Diamonds': return '♦';
        case 'Clubs': return '♣';
        case 'Spades': return '♠';
        default: return suit;
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', function() {
    showSection('setup');
});