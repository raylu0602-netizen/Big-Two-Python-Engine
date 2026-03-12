import random
import math
from collections import Counter

# --- 核心邏輯：Card & Hand ---
class Card:
    RANK_ORDER = {r: i for i, r in enumerate(['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'])}
    SUIT_ORDER = {'♣': 0, '♦': 1, '♥': 2, '♠': 3}
    def __init__(self, rank, suit):
        self.rank, self.suit = rank, suit
        self.power = self.RANK_ORDER[rank] * 4 + self.SUIT_ORDER[suit]
    def __repr__(self): return f"{self.suit}{self.rank}"
    def __lt__(self, other): return self.power < other.power

class Hand:
    SINGLE, PAIR, STRAIGHT, FULL_HOUSE, INVALID = 1, 2, 4, 6, -1
    def __init__(self, cards):
        self.cards = sorted(cards)
        self.hand_type = self.INVALID
        self.top_card = None
        self._analyze()

    def _analyze(self):
        n = len(self.cards)
        ranks = [c.rank for c in self.cards]
        counts = sorted(Counter(ranks).values(), reverse=True)
        if n == 1: self.hand_type, self.top_card = self.SINGLE, self.cards[0]
        elif n == 2 and counts == [2]: self.hand_type, self.top_card = self.PAIR, self.cards[1]
        elif n == 5:
            if self._is_straight(): self.hand_type, self.top_card = self.STRAIGHT, self.cards[4]
            elif counts == [3, 2]: self.hand_type, self.top_card = self.FULL_HOUSE, [c for c in self.cards if ranks.count(c.rank)==3][-1]

    def _is_straight(self):
        if len(set(c.rank for c in self.cards)) != 5: return False # 核心修正：點數唯一性
        powers = sorted([Card.RANK_ORDER[c.rank] for c in self.cards])
        if powers[4] - powers[0] == 4: return True
        for s in range(1, 5):
            shifted = sorted([p+13 if i < s else p for i, p in enumerate(powers)])
            if shifted[4] - shifted[0] == 4: return True
        return False

    def beats(self, other):
        if other is None: return True
        return self.hand_type == other.hand_type and self.top_card > other.top_card

# --- 玩家類別 (繼承體系) ---
class Player:
    def __init__(self, name):
        self.name, self.hand = name, []
    def sort_hand(self): self.hand.sort()
    # 這裡可以放原本的 Heuristic AI 邏輯

class HumanPlayer(Player):
    def find_valid_move(self, last_hand):
        # 這裡放入你具備防呆機制的 input 邏輯
        pass

# --- MCTS 核心準備 ---
class MCTSPlayer(Player):
    def simulate_random_game(self, initial_state):
        """
        進行一場隨機對戰直到結束，回傳贏家是否為自己。
        initial_state 應該包含所有玩家目前的殘餘手牌。
        """
        # 1. 為了不影響真實遊戲，我們要深拷貝一份狀態
        # (這裡假設 state 是一個包含手牌清單的物件)
        import copy
        sim_hands = copy.deepcopy(initial_state['hands'])
        current_turn = initial_state['current_turn']
        last_hand = None
        pass_count = 0

        # 2. 開始亂打循環
        while all(len(h) > 0 for h in sim_hands):
            player_hand = sim_hands[current_turn]
            
            # 找出所有合法的出牌組合 (目前我們先隨機選一個)
            valid_moves = self.get_all_valid_moves(player_hand, last_hand)
            
            if not valid_moves or (last_hand is not None and random.random() < 0.25):
                # 沒牌出，或是隨機決定 Pass (增加多樣性)
                pass_count += 1
                if pass_count == 3:
                    last_hand = None # 三家都 Pass，重開局
                    pass_count = 0
            else:
                chosen_move = random.choice(valid_moves)
                # 從該模擬玩家手牌中移除
                for card in chosen_move.cards:
                    player_hand.remove(card)
                last_hand = chosen_move
                pass_count = 0
                
            # 換下一位
            current_turn = (current_turn + 1) % 4

        # 3. 回傳結果：如果是自己贏了就回傳 1，輸了回傳 0
        my_index = initial_state['my_index']
        return 1 if len(sim_hands[my_index]) == 0 else 0

# --- 遊戲主流程 ---
def main():
    # 初始化遊戲、發牌、判定首攻...
    print("🚀 Big Two v2.0 開發版已啟動！")

if __name__ == "__main__":
    main()