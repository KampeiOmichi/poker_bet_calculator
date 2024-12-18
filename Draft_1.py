import random
from treys import Card, Evaluator

class CardDeck:
    def __init__(self):
        self.ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.original_deck = self._create_deck()
        self.deck = list(self.original_deck)
        random.shuffle(self.deck)

        self.evaluator = Evaluator()  # Initialize treys evaluator

    def _create_deck(self):
        return [(rank, suit) for suit in self.suits for rank in self.ranks]

    def deal_cards(self, num_cards):
        dealt = self.deck[:num_cards]
        self.deck = self.deck[num_cards:]
        return dealt

    def reset_deck(self):
        self.deck = list(self.original_deck)
        random.shuffle(self.deck)

    def to_treys_card(self, card):
        rank_map = {
            'Ace': 'A', 'King': 'K', 'Queen': 'Q', 'Jack': 'J', '10': 'T',
            '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'
        }
        suit_map = {
            'Spades': 's', 'Hearts': 'h', 'Diamonds': 'd', 'Clubs': 'c'
        }
        r, s = card
        treys_str = rank_map[r] + suit_map[s]
        return Card.new(treys_str)

    def evaluate_hand(self, hole_cards, community_cards):
        hole_treys = [self.to_treys_card(c) for c in hole_cards]
        community_treys = [self.to_treys_card(c) for c in community_cards]
        score = self.evaluator.evaluate(community_treys, hole_treys)
        return -score  # invert so that a better hand is higher

    def simulate_win_percentage(self, your_hand, board, num_opponents=1, iterations=10000):
        known_cards = your_hand + board
        unknown_deck = [card for card in self.original_deck if card not in known_cards]

        wins = 0
        ties = 0

        for _ in range(iterations):
            sim_deck = list(unknown_deck)
            random.shuffle(sim_deck)

            # All 5 community cards known, no need to deal river
            final_board = board

            # Deal opponents' hole cards
            opponents_hands = []
            for _o in range(num_opponents):
                opp_cards = [sim_deck.pop(0), sim_deck.pop(0)]
                opponents_hands.append(opp_cards)

            your_score = self.evaluate_hand(your_hand, final_board)
            opponents_scores = [self.evaluate_hand(opp, final_board) for opp in opponents_hands]

            if not opponents_scores:
                # No opponents means auto "win"
                wins += 1
            else:
                max_opp = max(opponents_scores)
                if your_score > max_opp:
                    wins += 1
                elif your_score == max_opp:
                    ties += 1

        win_percentage = (wins / iterations) * 100
        tie_percentage = (ties / iterations) * 100
        return win_percentage, tie_percentage

def get_card_input(prompt, deck):
    """
    Ask user for a card in the format "Rank Suit"
    e.g., "Ace Hearts", "10 Diamonds", "King Spades"
    Will re-prompt if input is invalid or not recognized.
    """
    ranks = deck.ranks
    suits = deck.suits

    while True:
        card_str = input(prompt).strip()
        parts = card_str.split()
        if len(parts) < 2:
            print("Please enter card in 'Rank Suit' format (e.g. 'Ace Hearts'). Try again.\n")
            continue

        *rank_parts, suit = parts
        rank = " ".join(rank_parts)

        if rank not in ranks:
            print(f"'{rank}' is not a recognized rank. Valid ranks: {ranks}. Try again.\n")
            continue
        if suit not in suits:
            print(f"'{suit}' is not a recognized suit. Valid suits: {suits}. Try again.\n")
            continue

        if (rank, suit) not in deck.original_deck:
            print("That card does not exist in a standard deck. Try again.\n")
            continue

        return (rank, suit)

def main():
    card_deck = CardDeck()

    # Get your hole cards
    print("Enter your 2 hole cards:")
    your_hand = []
    your_hand.append(get_card_input("Card 1: ", card_deck))
    your_hand.append(get_card_input("Card 2: ", card_deck))

    # Get the full 5-card board
    print("\nEnter the 5 community cards:")
    board = []
    for i in range(1, 6):
        board.append(get_card_input(f"Card {i}: ", card_deck))

    print("\nYour Hand:", your_hand)
    print("Board (5 cards):", board)
    print()

    # Get pot size and cost to call
    while True:
        try:
            pot_size = float(input("Enter the current pot size (e.g., 100): "))
            call_amount = float(input("Enter the amount it costs you to call (e.g., 25): "))
            break
        except ValueError:
            print("Please enter valid numerical values for pot size and call amount.\n")

    # Simulate against 1 opponent as example
    win_percentage, tie_percentage = card_deck.simulate_win_percentage(your_hand, board, num_opponents=1, iterations=10000)
    print(f"\nEstimated win percentage: {win_percentage:.2f}%")
    print(f"Estimated tie percentage: {tie_percentage:.2f}%")

    # Determine break-even percentage
    # break-even equity = call / (pot + call) * 100%
    break_even_equity = (call_amount / (pot_size + call_amount)) * 100

    print(f"\nBreak-even equity needed: {break_even_equity:.2f}%")

    equity_margin = win_percentage - break_even_equity

    # Decision logic:
    if win_percentage < break_even_equity:
        # Below break-even: fold
        print("Your win percentage is below the break-even point. You should fold.")
    elif break_even_equity <= win_percentage < break_even_equity + 10:
        # Slightly above break-even: call
        print("Your win percentage is slightly above the break-even point. Calling is reasonable.")
    else:
        # Well above break-even: raise
        # For a suggestion, we could, for example, raise the pot by the current pot_size.
        raise_amount = pot_size  # pot-sized raise
        new_pot = pot_size + call_amount + raise_amount
        print("Your win percentage is significantly above the break-even point.")
        print(f"Consider raising. For instance, you could increase the pot by about {raise_amount:.2f}, making the new pot {new_pot:.2f}.")

    card_deck.reset_deck()

if __name__ == "__main__":
    main()
