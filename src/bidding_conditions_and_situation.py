from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class BidSuit(Enum):
    NONE = "p"
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"
    NOTRUMP = "N"


class Axis(Enum):
    NS = "NS"
    OW = "OW"

class Players(Enum):
    NORD = "Nord"
    OST = "Ost"
    SUED = "Sued"
    WEST = "West"

class Position(Enum):
    one = "1. Position"
    two = "2. Position" 
    three = "3. Position"
    four = "4. Position"

class Vulnerable(Enum):
    NONE = "keiner"
    NS = " N--S "
    OW = " O--W "
    ALL = "alle"

class BiddingPlayer:
    def __init__(self, player: Players, position: Position, vulnerable_axis: Axis):
        self.player = player
        self.position = position
        self.axis = Axis.NS if player in {Players.NORD, Players.SUED} else Axis.OW
        self.is_vulnerable = True if vulnerable_axis == self.axis else False

BID_ORDER = [
    BidSuit.CLUBS,
    BidSuit.DIAMONDS,
    BidSuit.HEARTS,
    BidSuit.SPADES,
    BidSuit.NOTRUMP,
]


@dataclass(frozen=True)
class Contract:
    axis: Axis
    level: int
    suit: BidSuit
    doubled: bool = False
    redoubled: bool = False
    

    def __str__(self) -> str:
        suffix = ""
        if self.redoubled:
            suffix = "xx"
        elif self.doubled:
            suffix = "x"
        return f"{self.level}{self.suit.value}{suffix}"

    @property
    def is_pass(self) -> bool:
        return True if self.suit == BidSuit.NONE else False
    def is_doubled(self) -> bool:
        return self.doubled 
    def is_redoubled(self) -> bool:
        return self.redoubled
    
    def is_bidaable(self, other: "Contract") -> bool:
        if self.is_pass:
            return True
        if self.is_doubled:
            return True if (self.axis != other.axis) and other.suit in BID_ORDER else True
        if self.is_redoubled: 
            return True if other.is_doubled and self.axis != other.axis else False
        if self.level < other.level:
            return False
        if self.level == other.level:
            return False if BID_ORDER.index(self.suit) <= BID_ORDER.index(other.suit) else True
        return True        


class Bid:
    player: BiddingPlayer
    contract: Contract
    is_pass: bool
    is_forcing: bool
    is_game_invitational: bool
    is_slam_invitational: bool
    is_game_forcing: bool
    is_forced: bool
    is_game_forced: bool
    is_artificial: bool
    is_asking_for_information: bool
    is_descriptive: bool
    is_asking_for_cardcontrol: bool
    is_shortage: bool
    is_length_increasing: bool
    is_suit_preference: bool
    is_nutral: bool

    def __str__(self) -> str:
        return f"{self.position} {self.player}: {self.contract}"


@dataclass
class BiddingRules:
    board_id: int
    dealer: str
    seat_order: List[str] = field(default_factory=lambda: ["Nord", "Ost", "Sued", "West"])

    def __post_init__(self):
        self.player_positions = {
            player: f"{index + 1}. Position"
            for index, player in enumerate(self.current_bid_order)
        }

    @property
    def current_bid_order(self) -> List[str]:
        if self.dealer in {"Ost", "East"}:
            return ["Ost", "West", "Nord", "Sued"]
        if self.dealer in {"West", "W"}:
            return ["West", "Nord", "Ost", "Sued"]
        if self.dealer in {"Nord", "North"}:
            return ["Nord", "Ost", "West", "Sued"]
        if self.dealer in {"Sued", "South"}:
            return ["Sued", "West", "Nord", "Ost"]
        return self.seat_order

    def position_of(self, player: str) -> str:
        return self.player_positions.get(player, "unbekannt")

    def axis_of(self, player: str) -> Axis:
        if player in {"Nord", "Sued", "North", "South"}:
            return Axis.NS
        return Axis.OW

    @staticmethod
    def all_contracts() -> List[Contract]:
        contracts: List[Contract] = []
        for level in range(1, 8):
            for suit in BID_ORDER:
                contracts.append(Contract(level, suit))
        return contracts

    @staticmethod
    def next_contracts(last: Optional[Contract]) -> List[Contract]:
        if last is None or last.is_pass:
            return BiddingRules.all_contracts()
        return [c for c in BiddingRules.all_contracts() if c.compare_to(last) > 0]


@dataclass
class BiddingSituation:
    board_id: int
    dealer: str
    seat_order: List[str] = field(default_factory=lambda: ["Nord", "Ost", "Sued", "West"])
    bids: List[Bid] = field(default_factory=list)
    consecutive_passes: int = 0
    opener: Optional[str] = None

    def __post_init__(self):
        self.rules = BiddingRules(self.board_id, self.dealer, self.seat_order)

    @property
    def current_round(self) -> int:
        return len(self.bids) // 4 + 1

    @property
    def current_position_index(self) -> int:
        return len(self.bids) % 4

    @property
    def current_player(self) -> str:
        return self.rules.current_bid_order[self.current_position_index]

    @property
    def current_position(self) -> str:
        return self.rules.position_of(self.current_player)

    @property
    def current_axis(self) -> Axis:
        return self.rules.axis_of(self.current_player)

    @property
    def primary_axis(self) -> Optional[Axis]:
        if self.opener is None:
            return None
        return self.rules.axis_of(self.opener)

    @property
    def last_bid(self) -> Optional[Bid]:
        for bid in reversed(self.bids):
            if not bid.contract.is_pass:
                return bid
        return None

    @property
    def highest_contract_to_beat(self) -> Optional[Contract]:
        last = self.last_bid
        return last.contract if last else None

    @property
    def allowed_contracts(self) -> List[Contract]:
        return BiddingRules.next_contracts(
            self.highest_contract_to_beat
        )

    @property
    def allowed_double(self) -> bool:
        last = self.last_bid
        if not last or last.contract.is_pass:
            return False
        return self.rules.axis_of(last.player) != self.current_axis and not last.contract.doubled

    @property
    def allowed_redouble(self) -> bool:
        last = self.last_bid
        if not last or last.contract.is_pass or not last.contract.doubled:
            return False
        return self.rules.axis_of(last.player) != self.current_axis and not last.contract.redoubled

    @property
    def bid_history(self) -> List[str]:
        return [str(bid) for bid in self.bids]

    def record_bid(self, contract: Contract) -> None:
        bid = Bid(
            player=self.current_player,
            position=self.current_position,
            contract=contract,
        )
        self.bids.append(bid)
        if contract.is_pass:
            self.consecutive_passes += 1
        else:
            self.consecutive_passes = 0
            if self.opener is None:
                self.opener = self.current_player

    def is_passout(self) -> bool:
        return self.consecutive_passes >= 4

    def status_summary(self) -> str:
        opener_text = self.opener or "kein Eröffner"
        last = self.last_bid
        last_text = str(last.contract) if last else "kein Gebot"
        to_beat = str(self.highest_contract_to_beat) if self.highest_contract_to_beat else "kein Gebot"
        allowed = ", ".join(str(c) for c in self.allowed_contracts[:10])
        if len(self.allowed_contracts) > 10:
            allowed += ", ..."

        return (
            f"Board {self.board_id}, Dealer {self.dealer}, aktuelle Position {self.current_position} ({self.current_player}), "
            f"Achse {self.current_axis.value}, bisherige Gebote {self.bid_history}, "
            f"Eröffner: {opener_text}, letztes Gebot: {last_text}, zu überbieten: {to_beat}, "
            f"erlaubte Gebote: {allowed}, aufeinanderfolgende Pässe: {self.consecutive_passes}, "
            f"primäre Achse: {self.primary_axis.value if self.primary_axis else 'keine'}"
        )


def initialize_bidding_situation(board_id: int, dealer: str) -> BiddingSituation:
    return BiddingSituation(board_id=board_id, dealer=dealer)
