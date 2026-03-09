import random
import sys
from collections import Counter
from itertools import combinations

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- 核心類別：Card ---
class Card:
    RANK_ORDER = {r: i for i, r in enumerate(['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'])}
    SUIT_ORDER = {'♣': 0, '♦': 1, '♥': 2, '♠': 3}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.power = self.RANK_ORDER[rank] * 4 + self.SUIT_ORDER[suit]

    def __repr__(self):
        return f"{self.suit}{self.rank}"

    def __lt__(self, other): return self.power < other.power
    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

# --- 核心類別：Hand (牌型判定) ---
class Hand:
    SINGLE, PAIR, STRAIGHT, FULL_HOUSE, INVALID = 1, 2, 4, 6, -1

    def __init__(self, cards):
        self.cards = sorted(cards)
        self.hand_type = self.INVALID
        self.top_card = None
        self._analyze()

    def _analyze(self):
        n = len(self.cards)
        # 取得點數與花色統計
        ranks = [c.rank for c in self.cards]
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)

        # --- 核心邏輯：根據張數分流 ---
        if n == 1:
            self.hand_type = self.SINGLE
            self.top_card = self.cards[0]
        elif n == 2 and counts == [2]:
            self.hand_type = self.PAIR
            self.top_card = self.cards[1]
        elif n == 5:
            # 優先判定順子 (必須滿足 _is_straight 的嚴格檢查)
            if self._is_straight():
                self.hand_type = self.STRAIGHT
                self.top_card = self._get_straight_top_card()
            # 判定葫蘆
            elif counts == [3, 2]:
                self.hand_type = self.FULL_HOUSE
                self.top_card = [c for c in self.cards if rank_counts[c.rank] == 3][-1]

    def _is_straight(self):
        if len(self.cards) != 5: 
            return False
        
        ranks = [c.rank for c in self.cards]
        unique_ranks = set(ranks)
        if len(unique_ranks) != 5:
            return False 
        
        # 連續性檢查
        powers = sorted([Card.RANK_ORDER[c.rank] for c in self.cards])
        
        # 標準情況 (3-4-5-6-7)
        if powers[4] - powers[0] == 4:
            return True
            
        # 循環情況 (A-2-3-4-5)
        # 因為前面已經確認過 5 張點數都不同，所以這裡的 Max-Min=4 就是唯一的連續可能
        for s in range(1, 5):
            shifted = sorted([p + 13 if j < s else p for j, p in enumerate(powers)])
            if shifted[4] - shifted[0] == 4:
                return True
        return False

    def _get_straight_top_card(self):
        """取得順子的最強牌"""
        ranks = [c.rank for c in self.cards]
        # 取權重最大的那張
        return self.cards[4]

    def beats(self, other):
        if other is None: return True
        if self.hand_type != other.hand_type: return False
        return self.top_card > other.top_card

    def __repr__(self):
        names = {1: "單張", 2: "對子", 4: "順子", 6: "葫蘆", -1: "無效"}
        return f"{names.get(self.hand_type, '無效')}({self.cards})"


# --- 核心類別：Player (AI 邏輯) ---
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def sort_hand(self):
        self.hand.sort()

    def remove_card_from_hand(self, card):
        self.hand.remove(card)

    # --- 補上這個：掃描手牌組件 ---
    def get_components(self):
        counts = Counter([c.rank for c in self.hand])
        pairs = [rank for rank, count in counts.items() if count >= 2]
        triples = [rank for rank, count in counts.items() if count >= 3]
        return pairs, triples

    # --- 補上這個：專門找順子的工具 ---
    def find_all_straights(self):
        results = []
        rank_cycle = ['3','4','5','6','7','8','9','10','J','Q','K','A','2','3','4','5','6']
        cards_by_rank = {}
        for c in self.hand:
            if c.rank not in cards_by_rank: cards_by_rank[c.rank] = []
            cards_by_rank[c.rank].append(c)

        for i in range(len(rank_cycle) - 4):
            template = rank_cycle[i:i+5]
            if all(r in cards_by_rank for r in template):
                # 每個點數挑一張花色最小的
                candidate_cards = [cards_by_rank[r][0] for r in template]
                results.append(Hand(candidate_cards))
        return results

    # --- 補上這個：專門找葫蘆的工具 ---
    def find_all_full_houses(self):
        pairs_ranks, triples_ranks = self.get_components()
        results = []
        for t_rank in triples_ranks:
            for p_rank in pairs_ranks:
                if t_rank != p_rank:
                    t_cards = [c for c in self.hand if c.rank == t_rank][:3]
                    p_cards = [c for c in self.hand if c.rank == p_rank][:2]
                    results.append(Hand(t_cards + p_cards))
        return results

    # 然後才是你的 find_valid_move...

    def find_valid_move(self, last_hand):
        # 1. 如果是「發球權」(n=0)
        n = len(last_hand.cards) if last_hand else 0
        if last_hand is None:
            # 優先嘗試尋找並出掉 5 張牌 (順子、葫蘆)
            # 我們可以使用之前寫的 find_all_straights 和 find_all_full_houses
            straights = self.find_all_straights()
            if straights:
                move = straights[0] # 出最小的順子
                for c in move.cards: self.remove_card_from_hand(c)
                return move
                
            full_houses = self.find_all_full_houses()
            if full_houses:
                move = full_houses[0]
                for c in move.cards: self.remove_card_from_hand(c)
                return move

            # 如果沒有 5 張牌，找找有沒有對子
            pairs_ranks, _ = self.get_components()
            if pairs_ranks:
                rank = sorted(pairs_ranks, key=lambda r: Card.RANK_ORDER[r])[0]
                cards = [c for c in self.hand if c.rank == rank][:2]
                move = Hand(cards)
                for c in cards: self.remove_card_from_hand(c)
                return move

            # 真的都沒組合，才出單張
            move = Hand([self.hand.pop(0)])
            return move
        # 2. 搜尋邏輯
        if n == 1:
            for c in self.hand:
                cand = Hand([c])
                if cand.beats(last_hand):
                    if cand.top_card.rank == '2' and len(self.hand) > 5:
                        # print(f"💡 [{self.name}] 決定保留實力，不交出 {cand.top_card}")
                        return None # 這裡回傳 None 代表 Pass
                    self.hand.remove(c)
                    return cand
        elif n == 2:
            for combo in combinations(self.hand, 2):
                cand = Hand(list(combo))
                if cand.hand_type == Hand.PAIR and cand.beats(last_hand):
                    for c in combo: self.hand.remove(c)
                    return cand
        elif n == 5:
            for combo in combinations(self.hand, 5):
                cand = Hand(list(combo))
                if cand.hand_type != Hand.INVALID and cand.beats(last_hand):
                    for c in combo: self.hand.remove(c)
                    return cand
        return None
class HumanPlayer(Player):
    def find_valid_move(self, last_hand):
        while True:
            print(f"\n" + "="*40)
            print(f"【{self.name} 的回合】")
            print(f"場上的牌: {last_hand if last_hand else '⭐ 您獲得發球權！'}")
            
            # 顯示手牌，加上編號讓玩家好選
            print("您的手牌:")
            for i, card in enumerate(self.hand):
                print(f"[{i}]{card}", end=" ")
            print("\n" + "="*40)
            
            user_input = input("👉 請輸入索引 (多張請用逗號隔開，如 0,1,2) 或輸入 'p' 放棄: ").strip().lower()

            # 1. 處理放棄 (Pass)
            if user_input == 'p':
                if last_hand is None:
                    print("❌ 警告：您是發球者，必須出牌，不能 Pass！")
                    continue
                return None

            # 2. 驗證輸入格式 (防呆機制)
            try:
                # 將輸入轉為整數列表
                indices = [int(i.strip()) for i in user_input.split(',') if i.strip().isdigit()]
                
                # 檢查是否輸入了空內容或非數字
                if not indices:
                    print("❌ 錯誤：請輸入有效的數字索引！")
                    continue
                
                # 檢查索引是否超出範圍 (Out of bounds)
                if any(i < 0 or i >= len(self.hand) for i in indices):
                    print(f"❌ 錯誤：索引超出範圍！請輸入 0 到 {len(self.hand)-1} 之間的數字。")
                    continue
                
                # 選出對應的卡片
                selected_cards = [self.hand[i] for i in indices]
                
            except ValueError:
                print("❌ 錯誤：輸入格式不正確，請使用數字與逗號。")
                continue

            # 3. 判定牌型合法性
            candidate = Hand(selected_cards)
            if candidate.hand_type == Hand.INVALID:
                print(f"❌ 無效牌型：您選的 {selected_cards} 不成牌型！")
                continue

            # 4. 判定是否壓得過場上
            if not candidate.beats(last_hand):
                print(f"❌ 錯誤：您的 {candidate} 壓不過場上的 {last_hand}！")
                continue

            # --- 通過所有檢查，正式出牌 ---
            # 從手牌移除 (注意：要從索引大的開始移除，才不會影響前面的索引)
            for i in sorted(indices, reverse=True):
                self.hand.pop(i)
            
            print(f"✅ 您打出了：{candidate}")
            return candidate

# --- 核心類別：Deck ---
class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for s in ['♣', '♦', '♥', '♠'] for r in ['3','4','5','6','7','8','9','10','J','Q','K','A','2']]
    def shuffle(self): random.shuffle(self.cards)
    def deal(self): return self.cards.pop()

# --- 遊戲主循環 ---
def main():
    deck = Deck()
    deck.shuffle()
    players = [
        HumanPlayer("你 (玩家A)"), 
        Player("AI-B"), 
        Player("AI-C"), 
        Player("AI-D")
    ]
    for _ in range(13):
        for p in players: p.hand.append(deck.deal())
    for p in players: p.sort_hand()

    # 找出首攻 (梅花 3)
    curr_idx = 0
    club_3 = Card('3', '♣')
    for i, p in enumerate(players):
        if club_3 in p.hand:
            curr_idx = i
            break

    last_hand = None
    pass_count = 0
    print(f"遊戲開始！首攻玩家：{players[curr_idx].name}\n")

    while True:
        player = players[curr_idx]
        move = player.find_valid_move(last_hand)
        

        if move:
            print(f"[{player.name}] 丟出 {move}")
            last_hand = move
            pass_count = 0
        else:
            print(f"[{player.name}] Pass")
            pass_count += 1

        if len(player.hand) == 0:
            print(f"\n🏆 遊戲結束！ {player.name} 贏了！")
            break

        if pass_count == 3:
            print("--- 全場 Pass，新局開始 ---\n")
            last_hand = None
            pass_count = 0

        curr_idx = (curr_idx + 1) % 4

if __name__ == "__main__":
    main()
