import random  # 引入隨機模組
from collections import Counter
from itertools import combinations

class Hand:
    # 定義牌型代號，方便之後比大小
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    INVALID = -1

    def __init__(self, cards):
        self.cards = sorted(cards) # 進入判定前先排好序
        self.hand_type = self.INVALID
        self.top_card = None # 用來代表這組牌強度的牌
        self._analyze()

    def _analyze(self):
        n = len(self.cards)
        ranks = [c.rank for c in self.cards]
        suits = [c.suit for c in self.cards]
        rank_counts = Counter(ranks) # 計算每個點數出現幾次
        count_values = sorted(rank_counts.values(), reverse=True)

        # 1. 單張
        if n == 1:
            self.hand_type = self.SINGLE
            self.top_card = self.cards[0]
        
        # 2. 對子
        elif n == 2 and count_values == [2]:
            self.hand_type = self.PAIR
            self.top_card = self.cards[1] # 花色較大的那張
            
        # 3. 五張牌的邏輯
        elif n == 5:
            is_flush = len(set(suits)) == 1
            is_straight = self._check_straight()
            
            if is_flush and is_straight:
                self.hand_type = self.STRAIGHT_FLUSH
                self.top_card = self.cards[4]
            elif count_values == [4, 1]:
                self.hand_type = self.FOUR_OF_A_KIND
                # 鐵支要找四張一樣的那張點數
                self.top_card = [c for c in self.cards if rank_counts[c.rank] == 4][-1]
            elif count_values == [3, 2]:
                self.hand_type = self.FULL_HOUSE
                # 葫蘆強度取決於那三張
                self.top_card = [c for c in self.cards if rank_counts[c.rank] == 3][-1]
            elif is_flush:
                self.hand_type = self.FLUSH
                self.top_card = self.cards[4]
            # 在 _analyze 函式中的 n == 5 區塊內
            elif is_straight:
                self.hand_type = self.STRAIGHT
        
                # 處理特殊順子的強度代表
                powers = sorted([Card.RANK_ORDER[c.rank] for c in self.cards])
        
            # 判定 A-2-3-4-5 (點數包含 11, 12, 0, 1, 2)
                if set([11, 12, 0, 1, 2]).issubset(set(powers)):
                    # 根據台灣規則，A-2-3-4-5 通常以 '5' 作為強度代表（它是最小順子）
                    self.top_card = [c for c in self.cards if c.rank == '5'][0]
                # 判定 2-3-4-5-6 (點數包含 12, 0, 1, 2, 3)
                elif set([12, 0, 1, 2, 3]).issubset(set(powers)):
                    # 2-3-4-5-6 通常以 '6' 作為強度代表
                    self.top_card = [c for c in self.cards if c.rank == '6'][0]
                else:
                    # 一般順子，直接取最後一張（最大的）
                    self.top_card = self.cards[4]

    def _check_straight(self):
        """完美判定順子：支援 3-4-5-6-7 到 2-3-4-5-6"""
        if len(self.cards) != 5:
            return False

        # 取得目前的權重值並排序
        # 3=0, 4=1, ..., A=11, 2=12
        powers = sorted([Card.RANK_ORDER[c.rank] for c in self.cards])

        # --- 情況 A：標準順子 (例如 3-4-5-6-7 或 10-J-Q-K-A) ---
        # 只要最大減最小等於 4，且沒有重複（set判定過），就是連續的
        if powers[4] - powers[0] == 4:
            self.straight_type = "Normal"
            return True

        # --- 情況 B：跨越邊界的特殊順子 (例如 A-2-3-4-5 或 2-3-4-5-6) ---
        # 想法：嘗試將最小的牌加上 13 (一圈的長度)，看是否能組成連續數列
        # 我們測試將前 1, 2, 3 或 4 張牌分別平移 13 點
        for shift_count in range(1, 5):
            shifted_powers = sorted([
                powers[i] + 13 if i < shift_count else powers[i] 
                for i in range(5)
            ])
            if shifted_powers[4] - shifted_powers[0] == 4:
                # 這是特殊順子！
                self.straight_type = "Special"
                return True
        
        return False

    def __repr__(self):
        type_names = {1: "單張", 2: "對子", 6: "葫蘆", 4: "順子", -1: "無效牌型"}
        return f"[{type_names.get(self.hand_type, '其他')}] 強度代表: {self.top_card}"
    def beats(self, other_hand):
        """判斷目前這組牌是否能壓過另一組牌"""
        if other_hand is None: # 代表場上沒牌，出什麼都可以
            return True
        
        # 1. 檢查張數是否相同 (大老二基本規則)
        if len(self.cards) != len(other_hand.cards):
            return False
            
        # 2. 檢查牌型是否相同
        if self.hand_type != other_hand.hand_type:
            # 這裡可以加入鐵支壓順子的特殊邏輯，目前先簡單化
            return False
            
        # 3. 牌型相同時，比較強度代表 (top_card)
        return self.top_card > other_hand.top_card

# --- 測試判定功能 ---
test_pair = [Card('2', '♣'), Card('2', '♠')]
h = Hand(test_pair)
print(f"測試手牌 {test_pair} -> 判定結果: {h}")

test_full_house = [Card('3', '♣'), Card('3', '♠'), Card('3', '♥'), Card('5', '♣'), Card('5', '♦')]
h2 = Hand(test_full_house)
print(f"測試手牌 {test_full_house} -> 判定結果: {h2}")

class Card:
    RANK_ORDER = {r: i for i, r in enumerate(['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'])}
    SUIT_ORDER = {'♣': 0, '♦': 1, '♥': 2, '♠': 3}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.power = self.RANK_ORDER[rank] * 4 + self.SUIT_ORDER[suit]

    def __repr__(self):
        return f"{self.suit}{self.rank}"
# 之前定義的比較邏輯，會讓 list.sort() 自動生效
    def __lt__(self, other):
        return self.power < other.power
# --- 新增：定義「相等」邏輯 ---
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

# --- 新增 Deck 類別 ---
class Deck:
    def __init__(self):
        self.cards = []
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        suits = ['♣', '♦', '♥', '♠']
        
        # 使用巢狀迴圈產生 52 張牌
        for s in suits:
            for r in ranks:
                self.cards.append(Card(r, s))
        
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
        print("--- 牌堆已重新洗牌 ---")

    def deal(self):
        """發一張牌"""
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
# --- 新增 Player 類別 ---
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = [] # 玩家的手牌列表

    def draw(self, card):
        """將一張牌加入手牌"""
        if card:
            self.hand.append(card)

    def sort_hand(self):
        """利用 Card 類別定義的 __lt__ 自動排序"""
        self.hand.sort()

    def __repr__(self):
        return f"{self.name}: {self.hand}"
    def get_components(self):
        """掃描手牌中的對子、三張、四張"""
        counts = Counter([c.rank for c in self.hand])
        pairs = [rank for rank, count in counts.items() if count >= 2]
        triples = [rank for rank, count in counts.items() if count >= 3]
        quads = [rank for rank, count in counts.items() if count == 4]
        return pairs, triples, quads
    def find_all_straights(self):
        """搜尋手中所有可能的順子組合"""
        results = []
        # 定義點數順序 (包含循環處理)
        rank_cycle = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '3', '4', '5', '6']
        
        # 將手牌按點數分組
        cards_by_rank = {}
        for c in self.hand:
            if c.rank not in cards_by_rank:
                cards_by_rank[c.rank] = []
            cards_by_rank[c.rank].append(c)

        # 使用滑動窗口在 rank_cycle 中找連續 5 個點數
        for i in range(len(rank_cycle) - 4):
            template = rank_cycle[i:i+5]
            # 檢查手牌是否擁有這 5 個點數
            if all(r in cards_by_rank for r in template):
                # 如果有，從每個點數中挑選一張牌
                # 為了節省資源，我們先挑選每個點數中「花色最小」的牌來組成測試
                # (進階 AI 可能會嘗試不同花色組合，但這裡我們先取一組代表)
                candidate_cards = [cards_by_rank[r][0] for r in template]
                results.append(Hand(candidate_cards))
        
        return results

    def find_all_full_houses(self):
        """特定搜尋：只找葫蘆"""
        pairs_ranks, triples_ranks, _ = self.get_components()
        results = []
        
        for t_rank in triples_ranks:
            for p_rank in pairs_ranks:
                if t_rank != p_rank:
                    # 找出對應的三張牌和對子
                    t_cards = [c for c in self.hand if c.rank == t_rank][:3]
                    p_cards = [c for c in self.hand if c.rank == p_rank][:2]
                    results.append(Hand(t_cards + p_cards))
        return results
    def find_valid_move(self, last_hand):
        if last_hand is None:
            # 發球權：出一張最小的牌 (或者是你想出的任何合法牌型)
            return Hand([self.hand.pop(0)])

        target_type = last_hand.hand_type
        
        # --- 順子搜尋分支 ---
        if target_type == Hand.STRAIGHT:
            straights = self.find_all_straights()
            # 依照強度排序 (利用我們在 Hand 類別定義的 top_card)
            straights.sort(key=lambda h: h.top_card.power)
            
            for candidate in straights:
                if candidate.beats(last_hand):
                    # 找到了！從手牌移除這 5 張牌
                    for c in candidate.cards:
                        # 注意：因為 Hand 裡是複製品，要比對 rank/suit 來移除
                        self.hand = [h for h in self.hand if not (h.rank == c.rank and h.suit == c.suit)]
                    return candidate
        if target_type == Hand.PAIR:
            pairs_ranks, _, _ = self.get_components()
            for rank in sorted(pairs_ranks, key=lambda r: Card.RANK_ORDER[r]):
                cards = [c for c in self.hand if c.rank == rank][:2]
                candidate = Hand(cards)
                if candidate.beats(last_hand):
                    for c in cards: self.hand.remove(c)
                    return candidate

        elif target_type == Hand.FULL_HOUSE:
            all_full_houses = self.find_all_full_houses()
            # 排序所有的葫蘆，從最小的開始壓
            all_full_houses.sort(key=lambda h: h.top_card.power)
            for candidate in all_full_houses:
                if candidate.beats(last_hand):
                    for c in candidate.cards: self.hand.remove(c)
                    return candidate
        if target_type == Hand.STRAIGHT:
            straights = self.find_all_straights()
            # 依照強度排序 (利用我們在 Hand 類別定義的 top_card)
            straights.sort(key=lambda h: h.top_card.power)
            
            for candidate in straights:
                if candidate.beats(last_hand):
                    # 找到了！從手牌移除這 5 張牌
                    for c in candidate.cards:
                        # 注意：因為 Hand 裡是複製品，要比對 rank/suit 來移除
                        self.hand = [h for h in self.hand if not (h.rank == c.rank and h.suit == c.suit)]
                    return candidate

        
        
        return None # 沒牌壓，Pass


"""
shuffle的概念斗同以下程式
def fisher_yates_shuffle(data):
    # 從最後一個元素開始往前跑
    for i in range(len(data) - 1, 0, -1):
        # 隨機選一個 0 到 i 之間的位置 (包含 i)
        j = random.randint(0, i)
        # 交換位置
        data[i], data[j] = data[j], data[i]
    return data
"""


# --- 模擬遊戲流程 ---
print("=== 大老二遊戲模擬開始 ===")
def play_game():
    # 1. 初始化
    deck = Deck()
    deck.shuffle()
    players = [Player("玩家 A"), Player("玩家 B"), Player("玩家 C"), Player("玩家 D")]
    
    # 2. 發牌與排序
    for _ in range(13):
        for p in players:
            p.draw(deck.deal())
    for p in players:
        p.sort_hand()

    # 3. 尋找首攻玩家（梅花 3）
    club_3 = Card('3', '♣')
    current_idx = 0
    for i, p in enumerate(players):
        if club_3 in p.hand:
            current_idx = i
            break
    
    print(f"📢 遊戲開始！首攻玩家是：{players[current_idx].name}")
    print("-" * 30)
    
    last_hand = None
    pass_count = 0
    current_idx = starting_idx # 假設我們存了拿梅花 3 的索引

    while True: # 遊戲持續直到有人手牌為 0
        player = players[current_idx]
        
        # 1. 玩家嘗試出牌
        move = player.find_valid_move(last_hand)
        
        if move:
            print(f"[{player.name}] 出牌 -> {move}")
            last_hand = move
            pass_count = 0 # 有人出牌，重置 Pass 計數
        else:
            print(f"[{player.name}] Pass")
            pass_count += 1
        
        # 2. 檢查是否勝利
        if len(player.hand) == 0:
            print(f"🏆 恭喜 {player.name} 獲勝！")
            break
            
        # 3. 檢查是否全場 Pass (除了最後出牌的那位)
        if pass_count == 3:
            print("--- 全場 Pass，新局開始 ---")
            last_hand = None
            pass_count = 0
            # 下一位是最後出牌的人，邏輯會自動輪到他
            
        # 4. 下一位玩家
        current_idx = (current_idx + 1) % 4

    print("-" * 30)
    print("模擬結束，這就是回合切換的基本邏輯！")

# 執行遊戲模擬
if __name__ == "__main__":
    play_game()