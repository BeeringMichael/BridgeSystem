"""
Synthetic Bridge Bidding Dataset Generator
Generates training data for BERT-based bridge bidding prediction model.
"""

import random
import json
import os
import endplay
from typing import List, Dict, Tuple
from bidding_conditions_and_situation import PLAYER_ORDER, Players, BiddingSituation, Contract, PassContract, BidSuit

# Bridge suits and ranks
CONTRACT_TYPES = ["S", "♠", "♥", "♦", "♣"]
COLOURS = ["♠", "♥", "♦", "♣"]
CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "Z", "B", "D", "K", "A"]
COLOUR_ORDER = {"♠": 1, "♥": 2, "♦": 3, "♣": 4}
CARDS_ORDER = {"2": 12, "3": 11, "4": 10, "5": 9, "6": 8, "7": 7,
               "8": 6, "9": 5, "Z": 4, "B": 3, "D": 2, "K": 1, "A": 0
}


# DECK is constructed after the Card class is defined further below
DECK = []



VULNERABLE = ["keiner", " N--S ", " O--W ", "alle"]

# Bidding conventions
BIDDING_ACTIONS = [
    "1♣", "1♦", "1♥", "1♠", "1S", "2♣", "2♦", "2♥", "2♠", "2S",
    "3♣", "3♦", "3♥", "3♠", "3S", "4♣", "4♦", "4♥", "4♠", "4S",
    "5♣", "5♦", "5♥", "5♠", "5S", "6♣", "6♦", "6♥", "6♠", "6S",
    "7♣", "7♦", "7♥", "7♠", "7S"
    ]
BIDDING_REACTIONS= ["Double", "Redouble"]

BIDDING_PASS = ["Pass"]

# Hand patterns (distribution)
HAND_PATTERNS = [
 "4-3-3-3", "4-4-3-2", "4-4-4-1", "5-3-3-2", "5-4-2-2", "5-4-3-1", "5-4-4-0",
 "5-5-2-1", "5-5-3-0", "6-3-2-2", "6-3-3-1", "6-4-2-1", "6-4-3-0", "6-5-1-1",
 "6-5-2-0", "6-6-1-0", "7-2-2-2", "7-3-2-1", "7-3-3-0", "7-4-1-1", "7-4-2-0",
 "7-5-1-0", "7-6-0-0", "8-2-2-1", "8-3-1-1", "8-3-2-0", "8-4-1-0", "8-5-0-0",
 "9-2-1-1", "9-2-2-0", "9-3-1-0", "9-4-0-0", "10-1-1-1", "10-2-1-0",
 "10-3-0-0", "11-1-1-0", "11-2-0-0", "12-1-0-0", "13-0-0-0"
 ]


class Card:
    """Class represents a Card"""
    suit: str
    rank: str

    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"
    

# create DECK now that Card is defined
DECK = [Card(colour, card) for colour in COLOURS for card in CARDS]
    

class Suit:
    """Class represents a Suit"""
    suit: str
    cards: List[Card]

    def __init__(self, suit: str, cards: List[Card]):
        self.suit = suit
        self.cards = cards

    def get_cards(self) -> List[Card]:
        return self.cards

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        suit_to_str = "".join(card.rank for card in self.cards)
        return f"{self.suit}:{suit_to_str}"
    

class Hand:
    """Defines a Hand"""
    player: Players
    spades: Suit
    hearts: Suit
    diamonds: Suit
    clubs: Suit

    def __init__(self, player: Players, spades: Suit, hearts: Suit, diamonds: Suit, clubs: Suit):
        self.player = player
        self.spades = spades
        self.hearts = hearts
        self.diamonds = diamonds
        self.clubs = clubs

    def get_spades_cards(self) -> List[Card]:
        return self.spades.get_cards()

    def get_hearts_cards(self) -> List[Card]:
        return self.hearts.get_cards()

    def get_diamonds_cards(self) -> List[Card]:
        return self.diamonds.get_cards()

    def get_clubs_cards(self) -> List[Card]:
        return self.clubs.get_cards()

    def get_colour(self, colour: str) -> Suit:
        """Get the suit for the requested colour."""
        if colour == "♣":
            return self.clubs
        if colour == "♦":
            return self.diamonds
        if colour == "♥":
            return self.hearts
        if colour == "♠":
            return self.spades
        return Suit("", [])

    def get_spades_pattern(self) -> str:
        """Get the pattern string for spades."""
        return "".join([card.rank for card in cardsort(self.get_spades_cards())])

    def get_hearts_pattern(self) -> str:
        """Get the pattern string for hearts."""
        return "".join([card.rank for card in cardsort(self.get_hearts_cards())])

    def get_diamonds_pattern(self) -> str:
        """Get the pattern string for diamonds."""
        return "".join([card.rank for card in cardsort(self.get_diamonds_cards())])

    def get_clubs_pattern(self) -> str:
        """Get the pattern string for clubs."""
        return "".join([card.rank for card in cardsort(self.get_clubs_cards())])

    def get_pattern(self) -> str:
        """Get the overall hand shape as a sorted distribution."""
        colour_pattern = [
            len(self.spades),
            len(self.hearts),
            len(self.diamonds),
            len(self.clubs)]
        colour_pattern.sort(reverse=True)
        return "-".join(str(x) for x in colour_pattern)

    def get_distribution(self) -> str:
        """Get the hand distribution in the order spades, hearts, diamonds, clubs."""
        colour_distribution = [
            len(self.spades),
            len(self.hearts),
            len(self.diamonds),
            len(self.clubs)]
        return "-".join(str(x) for x in colour_distribution)

    def get_player(self) -> Players:
        """Get the player name."""
        return self.player


class HandStatistics:
    """Class represents a HandStatistics"""
    hand: Hand
    biddingposition: int
    vulnerable: str
    total_points: int
    hand_pattern: str
    hand_distribution: str
    spades_points: int
    spades_length: int
    spades_card_pattern: str
    spades_tricks: int
    spades_loosers: int
    hearts_points: int
    hearts_length: int 
    hearts_tricks: int
    hearts_loosers: int
    hearts_card_pattern: str
    diamonds_points: int
    diamonds_length: int
    diamonds_tricks: int
    diamonds_loosers: int
    diamonds_card_pattern: str
    clubs_points: int
    clubs_length: int
    clubs_tricks: int
    clubs_loosers: int 
    clubs_card_pattern: str

    def __init__(self, hand: Hand):
        self.hand = hand
        self.total_points = get_hcp_total(hand)
        self.hand_pattern = hand.get_pattern()
        self.hand_distribution = hand.get_distribution()
        self.spades_points = get_colour_hcp(hand, "♠")
        self.spades_length = len(self.hand.spades)
        self.spades_card_pattern = self.hand.get_spades_pattern()
        self.spades_tricks = card_pattern_to_tricks(self.spades_card_pattern)
        self.spades_loosers = card_pattern_to_loosers(self.spades_card_pattern)
        self.hearts_points = get_colour_hcp(hand, "♥")
        self.hearts_length = len(self.hand.hearts)
        self.hearts_card_pattern = self.hand.get_hearts_pattern()
        self.hearts_tricks = card_pattern_to_tricks(self.hearts_card_pattern)
        self.hearts_loosers = card_pattern_to_loosers(self.hearts_card_pattern)
        self.diamonds_points = get_colour_hcp(hand, "♦")
        self.diamonds_length = len(self.hand.diamonds)
        self.diamonds_card_pattern = self.hand.get_diamonds_pattern()
        self.diamonds_tricks = card_pattern_to_tricks(self.diamonds_card_pattern)
        self.diamonds_loosers = card_pattern_to_loosers(self.diamonds_card_pattern)
        self.clubs_points = get_colour_hcp(hand, "♣")
        self.clubs_length = len(self.hand.clubs)
        self.clubs_card_pattern = self.hand.get_clubs_pattern()
        self.clubs_tricks = card_pattern_to_tricks(self.clubs_card_pattern)
        self.clubs_loosers = card_pattern_to_loosers(self.clubs_card_pattern)

class Board:
    """Class represents a Bridge-Board"""
    board_nr: int
    dealer: str
    vulnerable_sides: str
    north_hand: Hand
    east_hand: Hand
    south_hand: Hand
    west_hand: Hand
    best_contract: str
    north_south_spades_winning_tricks: int
    north_south_hearts_winning_tricks: int
    north_south_diamonds_winning_tricks: int
    north_south_clubs_winning_tricks: int  
    north_south_sans_winning_tricks: int
    east_west_spades_winning_tricks: int
    east_west_hearts_winning_tricks: int
    east_west_diamonds_winning_tricks: int
    east_west_clubs_winning_tricks: int
    east_west_sans_winning_tricks: int

    def __init__(self,
               board_nr: int,
               dealer: str,
               vulnerable_sides: str,
               north_hand: Hand,
               east_hand: Hand,
               south_hand: Hand,
               west_hand: Hand,
               best_contract: str = None,
               north_south_spades_winning_tricks: int = 0,
               north_south_hearts_winning_tricks: int = 0,
               north_south_diamonds_winning_tricks: int = 0,
               north_south_clubs_winning_tricks: int = 0,
               north_south_sans_winning_tricks: int = 0,
               east_west_spades_winning_tricks: int = 0,
               east_west_hearts_winning_tricks: int = 0,
               east_west_diamonds_winning_tricks: int = 0,
               east_west_clubs_winning_tricks: int = 0,
               east_west_sans_winning_tricks: int = 0):
        """initialisieren eines Board mit den Parametern"""
        self.board_nr = board_nr
        self.dealer = dealer
        self.vulnerable_sides = vulnerable_sides
        self.north_hand = north_hand
        self.east_hand = east_hand
        self.south_hand = south_hand
        self.west_hand = west_hand
        self.best_contract = best_contract

    def get_dealer(self) -> int:
        """get the dealer"""
        return PLAYER_ORDER.index(self.dealer) + 1

    def get_north_position(self) -> int:
        """get the north position in bidding sequence"""
        return PLAYER_ORDER.index(Players.NORD) + PLAYER_ORDER.index(self.dealer) % 4 + 1

    def get_west_position(self) -> int:
        """get the west position in bidding sequence"""
        return PLAYER_ORDER.index(Players.WEST) + PLAYER_ORDER.index(self.dealer) % 4 + 1

    def get_south_position(self) -> int:
        """get the south position in bidding sequence"""
        return PLAYER_ORDER.index(Players.SUED) + PLAYER_ORDER.index(self.dealer) % 4 + 1

    def get_east_position(self) -> int:
        """get the east position in bidding sequence"""
        return PLAYER_ORDER.index(Players.OST) + PLAYER_ORDER.index(self.dealer) % 4 + 1

    def compute_double_dummy(self) -> None:
        """Run a double-dummy analysis with endplay and set board trick attributes.

        This builds a PBN representation of the four hands, runs
        `endplay.calc_dd_table` and populates the following attributes on the
        Board instance:

        - `north_south_spades_winning_tricks`
        - `north_south_hearts_winning_tricks`
        - `north_south_diamonds_winning_tricks`
        - `north_south_clubs_winning_tricks`
        - `north_south_sans_winning_tricks`
        - `east_west_spades_winning_tricks`
        - `east_west_hearts_winning_tricks`
        - `east_west_diamonds_winning_tricks`
        - `east_west_clubs_winning_tricks`
        - `east_west_sans_winning_tricks`

        After the table is computed, the method also evaluates the best
        contract for either side based on usual bridge scoring.
        """
        # rank mapping from project ranks to PBN ranks
        rank_map = {
            "A": "A",
            "K": "K",
            "D": "Q",
            "B": "J",
            "Z": "T",
            "9": "9",
            "8": "8",
            "7": "7",
            "6": "6",
            "5": "5",
            "4": "4",
            "3": "3",
            "2": "2",
        }

        # map our german player names (if used) to PBN dealer letters
        dealer_map = {"Nord": "N", "Ost": "E", "Sued": "S", "West": "W",
                      "North": "N", "East": "E", "South": "S", "West": "W"}

        def hand_to_pbn_str(h: Hand) -> str:
            """Convert our Hand to a PBN hand string (spades.hearts.diamonds.clubs)."""
            def suit_str(cards):
                # sort ranks according to CARDS_ORDER (smaller => higher card in this file)
                ordered = sorted(cards, key=lambda c: CARDS_ORDER.get(c.rank, 99))
                return "".join(rank_map.get(c.rank, c.rank) for c in ordered)

            sp = suit_str(h.spades.cards)
            ht = suit_str(h.hearts.cards)
            di = suit_str(h.diamonds.cards)
            cl = suit_str(h.clubs.cards)
            return f"{sp}.{ht}.{di}.{cl}"

        # build PBN string: Dealer prefix and four hands in the order N E S W
        dealer_letter = dealer_map.get(self.dealer, "N")
        pbn = (
            f"{dealer_letter}:"
            f"{hand_to_pbn_str(self.north_hand)} "
            f"{hand_to_pbn_str(self.east_hand)} "
            f"{hand_to_pbn_str(self.south_hand)} "
            f"{hand_to_pbn_str(self.west_hand)}"
        )

        # create an endplay Deal from the PBN and compute double-dummy table
        deal = endplay.Deal().from_pbn(pbn)
        dd = endplay.calc_dd_table(deal)
        table = dd.to_list()  # list[Denom(spades,hearts,diamonds,clubs,nt)][Player(N,E,S,W)]

        # helpers for indices (import the enum classes)
        from endplay.types.denom import Denom as _Denom
        from endplay.types.player import Player as _Player

        sp_i = _Denom.spades.value
        ht_i = _Denom.hearts.value
        di_i = _Denom.diamonds.value
        cl_i = _Denom.clubs.value
        nt_i = _Denom.nt.value

        n_i = _Player.north.value
        e_i = _Player.east.value
        s_i = _Player.south.value
        w_i = _Player.west.value

        # compute NS and EW best trick counts per strain
        self.north_south_spades_winning_tricks = max(table[sp_i][n_i], table[sp_i][s_i])
        self.north_south_hearts_winning_tricks = max(table[ht_i][n_i], table[ht_i][s_i])
        self.north_south_diamonds_winning_tricks = max(table[di_i][n_i], table[di_i][s_i])
        self.north_south_clubs_winning_tricks = max(table[cl_i][n_i], table[cl_i][s_i])
        self.north_south_sans_winning_tricks = max(table[nt_i][n_i], table[nt_i][s_i])

        self.east_west_spades_winning_tricks = max(table[sp_i][e_i], table[sp_i][w_i])
        self.east_west_hearts_winning_tricks = max(table[ht_i][e_i], table[ht_i][w_i])
        self.east_west_diamonds_winning_tricks = max(table[di_i][e_i], table[di_i][w_i])
        self.east_west_clubs_winning_tricks = max(table[cl_i][e_i], table[cl_i][w_i])
        self.east_west_sans_winning_tricks = max(table[nt_i][e_i], table[nt_i][w_i])

        self.best_contract = self.find_best_contract()

    def get_vulnerability(self, side: str) -> bool:
        """Return whether the given side is vulnerable on this board."""
        if side == "NS":
            return self.vulnerable_sides.strip() in {"N--S", "alle"}
        if side == "EW":
            return self.vulnerable_sides.strip() in {"O--W", "alle"}
        return False

    def get_dd_tricks(self, side: str, strain: str) -> int:
        """Return the double-dummy tricks won by the given side in a strain."""
        key = f"{side.lower()}_{strain.lower()}_winning_tricks"
        key = key.replace("_nt_", "_sans_")
        return getattr(self, key, 0)

    def contract_score(self, level: int, strain: str, tricks_won: int, vulnerable: bool) -> int:
        """Compute a simple bridge score for a contract and result.

        All failing contracts are scored as doubled down contracts when finding
        the best contract.
        """
        target = 6 + level
        if tricks_won < target:
            undertricks = target - tricks_won
            if vulnerable:
                if undertricks == 1:
                    penalty = 200
                else:
                    penalty = 200 + (undertricks - 1) * 300
            else:
                if undertricks == 1:
                    penalty = 100
                else:
                    penalty = 100 + (undertricks - 1) * 200
            return -penalty

        made_tricks = tricks_won - target
        if strain == "N":
            trick_value = 40 if level >= 1 else 0
            trick_value += 30 * max(level - 1, 0)
        elif strain in {"H", "S"}:
            trick_value = 30
        else:
            trick_value = 20

        contract_points = level * trick_value
        overtrick_points = made_tricks * trick_value
        bonus = 300 if contract_points >= 100 else 50
        return contract_points + overtrick_points + bonus

    def format_contract(self, level: int, strain: str, side: str, tricks_won: int) -> str:
        """Format a contract string with side label and result details."""
        side_label = "NS" if side == "NS" else "EW"
        target = 6 + level
        if tricks_won < target:
            undertricks = target - tricks_won
            score = self.contract_score(level, strain, tricks_won, self.get_vulnerability(side))
            return f"{level}{strain} x {side_label} -{undertricks} / {score}"

        made_tricks = tricks_won - target
        score = self.contract_score(level, strain, tricks_won, self.get_vulnerability(side))
        return f"{level}{strain} {side_label} +{made_tricks} / {score}"

    def find_best_contract(self) -> str:
        """Find the best contract by bridge score for NS or EW."""
        best_score = -10_000
        best_contract = None

        for level in range(1, 8):
            for strain in ["C", "D", "H", "S", "N"]:
                for side in ["NS", "EW"]:
                    tricks_won = self.get_dd_tricks(side, strain)
                    score = self.contract_score(
                        level,
                        strain,
                        tricks_won,
                        self.get_vulnerability(side),
                    )
                    if score > best_score:
                        best_score = score
                        best_contract = self.format_contract(level, strain, side, tricks_won)

        return best_contract

    def map_board_to_endplay(self) -> Dict[str, Hand]:
        """Map the board to the endplay representation."""
        return {
            "N": self.north_hand,
            "E": self.east_hand,
            "S": self.south_hand,
            "W": self.west_hand
        } 
    
  

def cardsort(cards: List[Card]) -> List[Card]:
    """Sorting cards"""
    return sorted(cards, key=lambda c: COLOUR_ORDER.get(c.suit, float('inf')) * 100 + CARDS_ORDER.get(c.rank, float('inf')))


def pick_up_hand(player: str, cards: List[Card]) -> Hand:
    """Order cards into a hand with Suit objects."""
    spades = []
    hearts = []
    diamonds = []
    clubs = []
    for card in cards:
        if card.suit == "♣":
            clubs.append(card)
        elif card.suit == "♦":
            diamonds.append(card)
        elif card.suit == "♥":
            hearts.append(card)
        elif card.suit == "♠":
            spades.append(card)
    return Hand(
        player,
        Suit("♠", cardsort(spades)),
        Suit("♥", cardsort(hearts)),
        Suit("♦", cardsort(diamonds)),
        Suit("♣", cardsort(clubs)),
    )


def deal_hands(board_nr: int) -> Board:
    """Deal hands to players."""
    dealer = PLAYER_ORDER[board_nr % 4]
    vulnerable_sides = VULNERABLE[board_nr % 4]
    distribute_deck = DECK.copy()
    random.shuffle(distribute_deck)

    hands = [[] for _ in PLAYER_ORDER]
    deal_index = PLAYER_ORDER.index(dealer)
    for card in distribute_deck:
        hands[deal_index].append(card)
        deal_index = (deal_index + 1) % 4
    return Board(
        board_nr,
        dealer,
        vulnerable_sides,
        pick_up_hand(PLAYER_ORDER[0], hands[0]),
        pick_up_hand(PLAYER_ORDER[1], hands[1]),
        pick_up_hand(PLAYER_ORDER[2], hands[2]),
        pick_up_hand(PLAYER_ORDER[3], hands[3]))


def generate_hand() -> Hand:
    """Generate a single random hand from a fresh deal."""
    board = deal_hands(random.randint(0, 10000))
    return random.choice([
        board.north_hand,
        board.east_hand,
        board.south_hand,
        board.west_hand
    ])


def hand_to_text(hand: Hand) -> str:
    """Convert a hand to a compact textual representation."""
    return " ".join([
        f"♠:{''.join(card.rank for card in cardsort(hand.get_spades_cards()))}",
        f"♥:{''.join(card.rank for card in cardsort(hand.get_hearts_cards()))}",
        f"♦:{''.join(card.rank for card in cardsort(hand.get_diamonds_cards()))}",
        f"♣:{''.join(card.rank for card in cardsort(hand.get_clubs_cards()))}"
    ])


def suit_to_list(suit: Suit) -> List[str]:
    return [str(card) for card in cardsort(suit.get_cards())]


def hand_to_dict(hand: Hand) -> Dict[str, object]:
    return {
        "player": hand.player,
        "spades": suit_to_list(hand.spades),
        "hearts": suit_to_list(hand.hearts),
        "diamonds": suit_to_list(hand.diamonds),
        "clubs": suit_to_list(hand.clubs),
        "pattern": hand.get_pattern(),
        "distribution": hand.get_distribution(),
    }


def board_to_dict(board: Board) -> Dict[str, object]:
    return {
        "board_nr": board.board_nr,
        "dealer": board.dealer,
        "vulnerable_sides": board.vulnerable_sides,
        "best_contract": board.best_contract,
        "hands": {
            "N": hand_to_dict(board.north_hand),
            "E": hand_to_dict(board.east_hand),
            "S": hand_to_dict(board.south_hand),
            "W": hand_to_dict(board.west_hand),
        },
        "double_dummy": {
            "north_south": {
                "spades": getattr(board, "north_south_spades_winning_tricks", None),
                "hearts": getattr(board, "north_south_hearts_winning_tricks", None),
                "diamonds": getattr(board, "north_south_diamonds_winning_tricks", None),
                "clubs": getattr(board, "north_south_clubs_winning_tricks", None),
                "sans": getattr(board, "north_south_sans_winning_tricks", None),
            },
            "east_west": {
                "spades": getattr(board, "east_west_spades_winning_tricks", None),
                "hearts": getattr(board, "east_west_hearts_winning_tricks", None),
                "diamonds": getattr(board, "east_west_diamonds_winning_tricks", None),
                "clubs": getattr(board, "east_west_clubs_winning_tricks", None),
                "sans": getattr(board, "east_west_sans_winning_tricks", None),
            },
        },
    }


def board_to_text(board: Board) -> str:
    """Create a BERT-friendly text representation for a board."""
    def suit_str_of(hand: Hand, suit: str) -> str:
        cards = cardsort(hand.get_colour(suit).get_cards())
        return "".join(card.rank for card in cards)

    parts = [
        f"Board {board.board_nr}",
        f"Dealer {board.dealer}",
        f"Vulnerable {board.vulnerable_sides}",
    ]

    for player, hand in [
        ("N", board.north_hand),
        ("E", board.east_hand),
        ("S", board.south_hand),
        ("W", board.west_hand),
    ]:
        parts.append(
            f"{player}: ♠{suit_str_of(hand, '♠')} ♥{suit_str_of(hand, '♥')} ♦{suit_str_of(hand, '♦')} ♣{suit_str_of(hand, '♣')}"
        )

    parts.append(
        f"DD NS: S{getattr(board, 'north_south_spades_winning_tricks', '?')} "
        f"H{getattr(board, 'north_south_hearts_winning_tricks', '?')} "
        f"D{getattr(board, 'north_south_diamonds_winning_tricks', '?')} "
        f"C{getattr(board, 'north_south_clubs_winning_tricks', '?')} "
        f"N{getattr(board, 'north_south_sans_winning_tricks', '?')}"
    )
    parts.append(
        f"DD EW: S{getattr(board, 'east_west_spades_winning_tricks', '?')} "
        f"H{getattr(board, 'east_west_hearts_winning_tricks', '?')} "
        f"D{getattr(board, 'east_west_diamonds_winning_tricks', '?')} "
        f"C{getattr(board, 'east_west_clubs_winning_tricks', '?')} "
        f"N{getattr(board, 'east_west_sans_winning_tricks', '?')}"
    )

    return " | ".join(parts)


def is_forum_d_1nt_open(hand: Hand) -> bool:
    """Return true when the hand qualifies for Forum-D 1NT opening."""
    pattern = hand.get_pattern()
    if pattern not in {"4-3-3-3", "4-4-3-2", "5-3-3-2"}:
        return False

    if pattern == "5-3-3-2":
        # In Forum D, a 5-card suit must not be a major suit for the 1NT opening.
        suit_lengths = {
            "♠": len(hand.spades),
            "♥": len(hand.hearts),
            "♦": len(hand.diamonds),
            "♣": len(hand.clubs),
        }
        long_suit = max(suit_lengths, key=suit_lengths.get)
        if long_suit in {"♠", "♥"}:
            return False

    return 15 <= get_hcp_total(hand) <= 17


def is_forum_d_major_open(hand: Hand) -> bool:
    """Return true when the hand qualifies for Forum-D 1H/1S opening."""
    hcp = get_hcp_total(hand)
    if not (12 <= hcp <= 19):
        return False

    if len(hand.hearts) >= 5:
        return True
    if len(hand.spades) >= 5:
        return True
    return False


def major_one_open_suit(hand: Hand) -> str:
    """Return the major suit for a Forum-D 1H/1S opening, if any."""
    if len(hand.spades) >= 5:
        return "S"
    if len(hand.hearts) >= 5:
        return "H"
    return ""


def get_ew_opening_sequence(board: Board) -> List[tuple[str, str, Hand]]:
    """Return the EW opening candidates and pass conditions in bidding order."""
    if board.dealer in {"Ost", "East"}:
        return [("Ost", "keine vorherigen Pässe", board.east_hand)]
    if board.dealer in {"West", "W"}:
        return [("West", "keine vorherigen Pässe", board.west_hand)]
    if board.dealer in {"Nord", "North"}:
        return [
            ("Ost", "nach Nord passt", board.east_hand),
            ("West", "nach Nord und Ost passen", board.west_hand),
        ]
    if board.dealer in {"Sued", "South"}:
        return [
            ("West", "nach Süd passt", board.west_hand),
            ("Ost", "nach Süd und West passen", board.east_hand),
        ]
    return []


def get_bid_order(board: Board) -> List[str]:
    """Return the order of players for the first bidding round starting with dealer."""
    if board.dealer in {"Ost", "East"}:
        return ["Ost", "West", "Nord", "Sued"]
    if board.dealer in {"West", "W"}:
        return ["West", "Nord", "Ost", "Sued"]
    if board.dealer in {"Nord", "North"}:
        return ["Nord", "Ost", "West", "Sued"]
    if board.dealer in {"Sued", "South"}:
        return ["Sued", "West", "Nord", "Ost"]
    return ["Ost", "West", "Nord", "Sued"]


def position_label(index: int) -> str:
    return f"{index + 1}. Position"


def contract_to_text(contract: Contract) -> str:
    if contract.is_pass:
        return "Pass"
    suit_text = "NT" if contract.suit == BidSuit.NOTRUMP else contract.suit.value
    return f"{contract.level}{suit_text}"


def format_bid_history(situation: BiddingSituation) -> str:
    return "; ".join(
        f"{bid.position} {bid.player}: {contract_to_text(bid.contract)}"
        for bid in situation.bids
    )


def complete_first_round_with_passes(situation: BiddingSituation) -> None:
    while len(situation.bids) < 4:
        situation.record_bid(PassContract())


def forum_d_ew_opening_description(board: Board) -> str:
    """Describe the ungestörte Forum D opening for EW using bidding state."""
    sequence = get_ew_opening_sequence(board)
    if not sequence:
        return "Weder Ost noch West ist gleich am Zug, daher keine ungestörte Forum D EW-Eröffnung."

    situation = BiddingSituation(board.board_nr, board.dealer)

    for opener, condition, opener_hand in sequence:
        while situation.current_player != opener:
            situation.record_bid(PassContract())

        hcp = get_hcp_total(opener_hand)
        pattern = opener_hand.get_pattern()

        if is_forum_d_1nt_open(opener_hand):
            situation.record_bid(Contract(1, BidSuit.NOTRUMP))
            complete_first_round_with_passes(situation)
            return (
                f"{opener} darf eröffnen, {condition}. "
                f"{opener} eröffnet 1NT mit ausgeglichener Hand ({pattern}) und {hcp} Figurenpunkten. "
                f"{rules_partner_text(opener)} hat noch nicht gereizt. "
                f"Bietsequenz: {format_bid_history(situation)}"
            )

        if is_forum_d_major_open(opener_hand):
            suit = major_one_open_suit(opener_hand)
            bid_suit = BidSuit.HEARTS if suit == "H" else BidSuit.SPADES
            situation.record_bid(Contract(1, bid_suit))
            complete_first_round_with_passes(situation)
            return (
                f"{opener} darf eröffnen, {condition}. "
                f"{opener} eröffnet 1{suit} mit mindestens 5 Karten in {suit} und {hcp} Figurenpunkten. "
                f"{rules_partner_text(opener)} hat noch nicht gereizt. "
                f"Bietsequenz: {format_bid_history(situation)}"
            )

        situation.record_bid(PassContract())

    complete_first_round_with_passes(situation)
    return (
        "Die ungestörte EW-Reizung endet mit vier aufeinanderfolgenden Pässen."
        f" Bietsequenz: {format_bid_history(situation)}."
        " Der Kontrakt ist Pass mit Score 0."
    )


def rules_partner_text(player: str) -> str:
    return "West" if player == "Ost" else "Ost"


def board_to_bert_example(board: Board) -> Dict[str, object]:
    """Build a single BERT dataset example from a board."""
    return {
        "id": f"board_{board.board_nr}",
        "input_text": board_to_text(board),
        "forum_d_ew_text": forum_d_ew_opening_description(board),
        "board": board_to_dict(board),
    }


def board_to_forum_d_bert_example(board: Board) -> Dict[str, object]:
    """Build a BERT example focused on Forum D EW opening description."""
    return {
        "id": f"board_{board.board_nr}_forum_d",
        "input_text": forum_d_ew_opening_description(board),
        "board": board_to_dict(board),
    }


def generate_bert_dataset(turnier: "Turnier", output_path: str) -> List[Dict[str, object]]:
    """Generate a BERT-friendly JSON dataset from a Turnier."""
    examples = [board_to_bert_example(board) for board in turnier.boards]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    return examples


def generate_forum_d_bert_dataset(turnier: "Turnier", output_path: str) -> List[Dict[str, object]]:
    """Generate a second BERT dataset with Forum D EW opening descriptions."""
    examples = [board_to_forum_d_bert_example(board) for board in turnier.boards]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    return examples


class Turnier:
    """A collection of boards for BERT dataset generation."""

    def __init__(self, name: str, boards: List[Board]):
        self.name = name
        self.boards = boards

    @classmethod
    def generate(cls, num_boards: int = 10, start_board_nr: int = 0) -> "Turnier":
        boards = []
        for index in range(start_board_nr, start_board_nr + num_boards):
            board = deal_hands(index)
            board.compute_double_dummy()
            boards.append(board)
        return cls("Turnier", boards)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "boards": [board_to_dict(board) for board in self.boards],
        }

    def save(self, file_path: str) -> str:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return file_path


def get_hcp_total(hand: Hand) -> int:
    """get the total HCP of a hand """
    retval = 0
    retval += get_colour_hcp(hand, "♣")
    retval += get_colour_hcp(hand, "♦")
    retval += get_colour_hcp(hand, "♥")
    retval += get_colour_hcp(hand, "♠")
    return retval


def get_colour_hcp(hand: Hand, colour: str) -> int:
    """get the HCP of a colour in a hand"""
    retval = int("0")
    if hand.get_colour(colour).__str__().find("A") != -1:
        retval += 4
    if hand.get_colour(colour).__str__().find("K") != -1:
        retval += 3
    if hand.get_colour(colour).__str__().find("D") != -1:
        retval += 2
    if hand.get_colour(colour).__str__().find("B") != -1:
        retval += 1
    if retval > 1 and len(hand.get_colour(colour)) > 4:
        retval += (len(hand.get_colour(colour)) - 4)
    if len(hand.get_colour(colour)) < 3 and retval < 3:
        retval = 0
    return retval


def get_partner(player: str) -> str:
    """Get the partner of a player."""
    return PLAYER_ORDER[(PLAYER_ORDER.index(player) + 2) % 4]


def get_lefthand_opponent(player: str) -> str:
    """Get the left hand player."""
    return PLAYER_ORDER[PLAYER_ORDER.index(player) + 1]


def get_righthand_opponent(player: str) -> str:
    """Get the right hand player."""
    return PLAYER_ORDER[PLAYER_ORDER.index(player) - 1]


def colour_to_str(hand: Hand, suit: str) -> str:
    """get text-repräsentation of a hand"""
    return json.dumps(cardsort(hand.get_colour(suit)))


def hand_to_str(hand: Hand) -> str:
    """Convert hand to text representation."""
    return json.dumps(hand)


def board_to_str(board: Board) -> str:
    """Convert Boards to text representation."""
    return json.dumps(board)


def card_pattern_to_tricks(card_pattern: str) -> int:
    """Convert a card pattern to the number of tricks it represents."""
    card_lengths = card_pattern.__len__()
    if card_lengths > 3 and card_pattern.find("AKDB") != -1:
        return 4
    if card_lengths > 2 and card_pattern.find("AKD") != -1:
        return 3
    if card_lengths > 1 and card_pattern.find("AK") != -1:
        return 2
    if card_lengths > 0 and card_pattern.find("A") != -1:
        return 1    
    return 0

def card_pattern_to_loosers(card_pattern: str) -> int:
    """Convert a card pattern to the number of loosers it represents."""
    loosers = ["2", "3", "4", "5", "6", "7", "8", "9", "Z"]
    
    card_lengths = card_pattern.__len__()
    lcnt = 0
    if card_lengths > 0:
        for card in loosers:
            if card_pattern.find(card) != -1:
                lcnt += 1
    if lcnt > 4:
        lcnt = 4
    lcnt = lcnt - card_pattern_to_tricks(card_pattern)
    if lcnt < 0:
        lcnt = 0
    return lcnt
  

def generate_bidding_sequence() -> Tuple[List[str], str]:
    """Generate a random bidding sequence and final contract."""
    sequence = []
    dealer = random.choice(PLAYER_ORDER)

    # Generate 0-4 opening bids
    num_bids = random.randint(0, 4)

    for i in range(num_bids):
        if i == 0:
            # Opening bid
            action = random.choice(["1C", "1D", "1H", "1S", "1N"])
        else:
            # Response or overcall
            action = random.choice(BIDDING_ACTIONS)
        sequence.append(action)

    # Add final contract
    level = random.randint(1, 7)
    strain = random.choice(["C", "D", "H", "S", "N"])
    contract = f"{level}{strain}"

    return sequence, contract


def generate_training_example() -> Dict:
    """Generate a single training example."""
    hand = generate_hand()
    sequence, contract = generate_bidding_sequence()

    # Create input text
    hand_text = hand_to_text(hand)
    sequence_text = " ".join(sequence)

    # Target: predict the contract from the bidding sequence
    input_text = f"Hand: {hand_text} Bidding: {sequence_text}"

    return {
        "input": input_text,
        "target": contract,
        "hand": hand_to_dict(hand),
        "bidding_sequence": sequence,
    }


def generate_dataset(num_samples: int, output_path: str):
    """Generate a dataset with num_samples examples."""
    dataset = []
    for _ in range(num_samples):
        dataset.append(generate_training_example())

    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    return dataset


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_dataset(10000, "data/bridge_bidding_synthetic.json")

    turnier = Turnier.generate(num_boards=10, start_board_nr=0)
    turnier.save("data/turnier.json")
    generate_bert_dataset(turnier, "data/turnier_bert.json")
    generate_forum_d_bert_dataset(turnier, "data/turnier_forum_d_bert.json")

    print("Generated 10000 synthetic bridge bidding examples")
    print("Generated Turnier dataset with 10 boards at data/turnier.json")
    print("Generated BERT-ready dataset with 10 boards at data/turnier_bert.json")
    print("Generated Forum D EW dataset with 10 boards at data/turnier_forum_d_bert.json")
