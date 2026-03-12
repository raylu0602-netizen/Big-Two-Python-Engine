import random
def extended_gcd(a, b):
    """
    回傳 (gcd, x, y) 使得 ax + by = gcd
    """
    if b == 0:
        # 終止條件：gcd(a, 0) = a, 此時 1*a + 0*0 = a
        return a, 1, 0
    else:
        gcd, x_prime, y_prime = extended_gcd(b, a % b)
        
        # 根據推導公式更新 x 和 y
        x = y_prime
        y = x_prime - (a // b) * y_prime
        
        return gcd, x, y

def mod_inverse(e, phi):
    """
    計算 d 使得 (e * d) % phi == 1
    """
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError("不存在模反元素(e 與 phi 不互質)")
    else:
        # 確保結果為正數
        return x % phi
"""
def power_mod(base, exp, mod):
    res = 1
    base %= mod  # 先對底數取模，防止一開始就太大
    
    while exp > 0:
        # 如果次方是奇數，就乘進結果裡
        if exp % 2 == 1:
            res = (res * base) % mod
        
        # 次方減半 (位移運算)，底數平方
        exp //= 2
        base = (base * base) % mod
        
    return res
python 內建函式 pow(base, exp, mod) 也可以直接使用，效果相同：
"""

def is_prime_miller_rabin(n, k=40):
    """
    判斷 n 是否為質數，k為測試回合數（k越高，誤判率越低）
    """
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # 1. 將 n-1 分解為 (2^s) * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # 2. 進行 k 回合測試
    for _ in range(k):
        a = random.randint(2, n - 2)
        # 計算 a^d % n
        x = pow(a, d, n)  # 這裡直接用內建最佳化的快速冪
        
        if x == 1 or x == n - 1:
            continue
            
        # 進行 s-1 次平方探測
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            # 如果沒有一次平方後變成 n-1，那它一定是合數
            return False
            
    return True
k=random.randint(10**5, 10**6)
a=random.randint(k, k*2)
if(not a%2):
    a=a+1
while(not is_prime_miller_rabin(a)):
    a=a+2
print(f"{a} 是質數")
    
    
