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
    def find_valid_move(self, last_hand):
        # 這就是我們要在 big_two_2.py 挑戰的新功能！
        print(f"🤖 {self.name} 正在透過模擬尋找最佳出牌...")
        # 暫時回傳 None (Pass) 或是調用原本的簡單邏輯
        return None

# --- 遊戲主流程 ---
def main():
    # 初始化遊戲、發牌、判定首攻...
    print("🚀 Big Two v2.0 開發版已啟動！")

if __name__ == "__main__":
    main()