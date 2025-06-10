import random
from itertools import permutations
from collections import defaultdict

def naive_shuffle(cards):
    """Naive Shuffle: 每次都從整個 range(0, len(cards)-1) 取隨機索引並交換。"""
    for i in range(len(cards)):
        n = random.randint(0, len(cards)-1)
        cards[i], cards[n] = cards[n], cards[i]

def fisher_yates_shuffle(cards):
    """Fisher-Yates Shuffle: 從最後一張卡往前，確保僅在尚未洗過的區間取亂數索引並交換。"""
    for i in range(len(cards)-1, 0, -1):
        n = random.randint(0, i)
        cards[i], cards[n] = cards[n], cards[i]

def simulate(shuffle_fn, trials=1000000):
    """重複執行洗牌並統計結果。"""
    results = defaultdict(int)
    for _ in range(trials):
        cards = [1, 2, 3, 4]
        shuffle_fn(cards)
        results[tuple(cards)] += 1
    return results

def print_all_permutations(title, results):
    """強制生成所有24種排列，確保未出現的排列顯示次數為 0。"""
    print(title)
    all_perms = permutations([1, 2, 3, 4])  # 生成所有可能排列
    for perm in sorted(all_perms):
        count = results.get(perm, 0)         # 若不存在則返回 0
        print(f"{list(perm)}: {count}")

if __name__ == "__main__":
    # 模擬兩種洗牌方法
    naive_counts = simulate(naive_shuffle, 1000000)
    fy_counts = simulate(fisher_yates_shuffle, 1000000)

    # 輸出完整排列結果
    print_all_permutations("Naive Shuffle Results:", naive_counts)
    print("\n" + "="*50 + "\n")
    print_all_permutations("Fisher-Yates Shuffle Results:", fy_counts)
