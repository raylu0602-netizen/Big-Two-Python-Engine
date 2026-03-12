import random

class RSACipher:
    def __init__(self, bits=1024):
        self.bits = bits
        self.public_key = None  # (e, n)
        self.private_key = None # (d, n)

    # --- 工具函式 (從之前的討論整合而來) ---
    
    def _is_prime(self, n, k=40):
        if n <= 1: return False
        if n <= 3: return True
        if n % 2 == 0: return False
        d, s = n - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1: continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else: return False
        return True

    def _generate_prime(self):
        while True:
            # 生成指定位元的隨機數
            p = random.getrandbits(self.bits)
            # 確保是奇數且位元數正確
            p |= (1 << (self.bits - 1)) | 1
            if self._is_prime(p):
                return p

    def _extended_gcd(self, a, b):
        if b == 0: return a, 1, 0
        gcd, x1, y1 = self._extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return gcd, x, y

    def _mod_inverse(self, e, phi):
        gcd, x, y = self._extended_gcd(e, phi)
        if gcd != 1: raise ValueError("GCD is not 1")
        return x % phi

    # --- 核心功能 ---

    def generate_keys(self):
        print("正在生成質數 p...")
        p = self._generate_prime()
        print("正在生成質數 q...")
        q = self._generate_prime()
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        e = 65537 # 常用的公鑰指數
        d = self._mod_inverse(e, phi)
        
        self.public_key = (e, n)
        self.private_key = (d, n)
        print("金鑰生成完畢！")

    def encrypt(self, message):
        """將字串加密成數字清單"""
        e, n = self.public_key
        # 將字串轉換為整數 (簡單做法：轉為 bytes 再轉 int)
        msg_int = int.from_bytes(message.encode('utf-8'), 'big')
        if msg_int >= n:
            raise ValueError("訊息太長，超過模數 n")
        
        return pow(msg_int, e, n)

    def decrypt(self, ciphertext):
        """將數字解密回字串"""
        d, n = self.private_key
        msg_int = pow(ciphertext, d, n)
        
        # 將整數轉回字串
        msg_bytes = msg_int.to_bytes((msg_int.bit_length() + 7) // 8, 'big')
        return msg_bytes.decode('utf-8')
    
    # 在 RSACipher 類別中加入這個方法
    def encrypt_with_external_key(self, message, e_external, n_external):
        """使用外部傳入的公鑰進行加密"""
        msg_int = int.from_bytes(message.encode('utf-8'), 'big')
        if msg_int >= n_external:
            raise ValueError("訊息太長，超過對方的模數 n")
        
        # 使用傳入的 e_external 和 n_external 進行快速冪
        return pow(msg_int, e_external, n_external)

# --- 測試專案 ---
