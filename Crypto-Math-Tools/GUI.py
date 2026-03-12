import tkinter as tk
from tkinter import messagebox
from RSACipher import RSACipher
# 假設你之前的 RSACipher 類別已經定義好了
# class RSACipher: ... (這裡省略，請確保類別在同一個檔案內)

class RSAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("數論密碼學工具 - RSA")
        self.cipher = RSACipher(bits=512)
        
        # 設定 UI 元件
        self._setup_ui()

    def _setup_ui(self):
        # --- 金鑰生成區 ---
        tk.Label(self.root, text="RSA 金鑰設定", font=('Arial', 12, 'bold')).pack(pady=5)
        tk.Button(self.root, text="生成新金鑰 (512-bit)", command=self._cmd_generate).pack()
        
        self.key_status = tk.Label(self.root, text="狀態: 尚未生成金鑰", fg="red")
        self.key_status.pack()

        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=10)

        # --- 加密區 ---
        tk.Label(self.root, text="【加密】輸入明文:").pack()
        self.entry_plain = tk.Entry(self.root, width=50)
        self.entry_plain.pack(pady=5)
        
        tk.Button(self.root, text="執行加密", command=self._cmd_encrypt).pack()
        
        self.label_cipher = tk.Label(self.root, text="密文 (Hex):")
        self.label_cipher.pack()
        self.text_cipher = tk.Text(self.root, height=3, width=50)
        self.text_cipher.pack(pady=5)

        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=10)

        # --- 解密區 ---
        tk.Label(self.root, text="【解密】輸入密文 (Hex):").pack()
        self.entry_cipher_in = tk.Entry(self.root, width=50)
        self.entry_cipher_in.pack(pady=5)

        tk.Button(self.root, text="執行解密", command=self._cmd_decrypt).pack()
        
        self.label_decrypted = tk.Label(self.root, text="解密後的結果:")
        self.label_decrypted.pack()
        self.result_text = tk.Label(self.root, text="", fg="blue", font=('Arial', 10, 'bold'))
        self.result_text.pack(pady=5)

    # --- 功能函式 ---
    def _cmd_generate(self):
        self.cipher.generate_keys()
        self.key_status.config(text="狀態: 金鑰已就緒", fg="green")
        messagebox.showinfo("成功", "金鑰生成完畢！")

    def _cmd_encrypt(self):
        if not self.cipher.public_key:
            messagebox.showwarning("警告", "請先生成金鑰")
            return
        msg = self.entry_plain.get()
        if not msg: return
        
        try:
            cipher_int = self.cipher.encrypt(msg)
            # 轉換為 16 進位顯示比較好看
            self.text_cipher.delete(1.0, tk.END)
            self.text_cipher.insert(tk.END, hex(cipher_int))
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def _cmd_decrypt(self):
        if not self.cipher.private_key:
            messagebox.showwarning("警告", "請先生成金鑰")
            return
        try:
            hex_input = self.entry_cipher_in.get()
            cipher_int = int(hex_input, 16)
            result = self.cipher.decrypt(cipher_int)
            self.result_text.config(text=result)
        except Exception as e:
            messagebox.showerror("錯誤", "解密失敗，請檢查輸入格式")

if __name__ == "__main__":
    root = tk.Tk()
    app = RSAApp(root)
    root.mainloop()