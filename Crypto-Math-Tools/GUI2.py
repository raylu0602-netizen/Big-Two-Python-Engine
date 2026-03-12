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
        # 在 _setup_ui 方法中，找到生成金鑰按鈕下方
        tk.Label(self.root, text="我的公鑰 (分享給好友):", font=('Arial', 10, 'bold')).pack(pady=5)

        # --- 在 _setup_ui 中找到原有的金鑰顯示區，替換成這個 ---
        self.export_frame = tk.LabelFrame(self.root, text=" 🔐 我的公鑰卡片 (分享給好友) ", padx=10, pady=10)
        self.export_frame.pack(pady=10, padx=20, fill="x")

        # 我的 e
        tk.Label(self.export_frame, text="指數 (e):").grid(row=0, column=0, sticky="w")
        self.entry_my_e = tk.Entry(self.export_frame, width=40, state='readonly')
        self.entry_my_e.grid(row=0, column=1, padx=5, pady=2)

        # 我的 n
        tk.Label(self.export_frame, text="模數 (n):").grid(row=1, column=0, sticky="w")
        self.entry_my_n = tk.Entry(self.export_frame, width=40, state='readonly')
        self.entry_my_n.grid(row=1, column=1, padx=5, pady=2)

        # 一鍵複製按鈕 (跨兩列放置)
        self.btn_copy_all = tk.Button(
            self.export_frame, 
            text=" 📋 複製完整公鑰 ", 
            command=self._cmd_copy_full_public_key,
            bg="#FBEEE6"
        )
        self.btn_copy_all.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

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
        
        # 在 RSAApp 的 _setup_ui 中加入
        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=10)
        tk.Label(self.root, text="【好友公鑰匯入】", font=('Arial', 10, 'bold'), fg="purple").pack()

        # 朋友的 e
        tk.Label(self.root, text="好友的 e:").pack()
        self.entry_peer_e = tk.Entry(self.root, width=50)
        self.entry_peer_e.pack()

        # 朋友的 n
        tk.Label(self.root, text="好友的 n:").pack()
        self.entry_peer_n = tk.Entry(self.root, width=50)
        self.entry_peer_n.pack()

        tk.Button(self.root, text="使用好友公鑰加密並傳送", command=self._cmd_encrypt_for_peer, bg="#E6E6FA").pack(pady=5)

    # --- 功能函式 ---
    def _cmd_generate(self):
        self.cipher.generate_keys()
        e, n = self.cipher.public_key
        
        self.key_status.config(text="狀態: 金鑰已就緒", fg="green")
        
        # 更新 e
        self.entry_my_e.config(state='normal')
        self.entry_my_e.delete(0, tk.END)
        self.entry_my_e.insert(0, str(e))
        self.entry_my_e.config(state='readonly')
        
        # 更新 n
        self.entry_my_n.config(state='normal')
        self.entry_my_n.delete(0, tk.END)
        self.entry_my_n.insert(0, str(n))
        self.entry_my_n.config(state='readonly')

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
        # 在 class RSAApp 裡面新增這個方法 (建議放在 _cmd_encrypt 附近)
    def _cmd_encrypt_for_peer(self):
        try:
            # 從介面的輸入框抓取好友的 e 和 n
            e_peer = int(self.entry_peer_e.get())
            n_peer = int(self.entry_peer_n.get())
            
            # 抓取你想傳送的明文
            msg = self.entry_plain.get()
            if not msg:
                messagebox.showwarning("提示", "請輸入要加密的明文")
                return
            
            # 呼叫剛剛在 RSACipher 寫好的邏輯
            cipher_int = self.cipher.encrypt_with_external_key(msg, e_peer, n_peer)
            
            # 將結果轉為 Hex 並顯示在密文區
            self.text_cipher.delete(1.0, tk.END)
            self.text_cipher.insert(tk.END, hex(cipher_int))
            
            messagebox.showinfo("成功", "已成功使用好友公鑰加密！\n你可以複製下方的密文傳送給好友了。")
            
        except ValueError:
            messagebox.showerror("錯誤", "好友的 e 或 n 格式不正確，請輸入純數字。")
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
    def _cmd_copy_n(self):
    # 取得目前的 n (從 entry 裡面抓，或是直接從 cipher 抓)
        n_content = self.entry_my_n.get()
        
        if n_content:
            self.root.clipboard_clear()        # 清除剪貼簿
            self.root.clipboard_append(n_content)  # 存入新內容
            messagebox.showinfo("成功", "模數 n 已複製到剪貼簿！")
        else:
            messagebox.showwarning("警告", "請先生成金鑰後再複製")
            
    def _cmd_copy_e(self):
        e_content = self.entry_my_e.get()
        if e_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(e_content)
            messagebox.showinfo("成功", "指數 e 已複製到剪貼簿！")
    def _cmd_copy_full_public_key(self):
        e = self.entry_my_e.get()
        n = self.entry_my_n.get()
        
        if not e or not n:
            messagebox.showwarning("警告", "請先生成金鑰！")
            return
        
        # 格式化輸出的文字
        export_text = f"--- 我的 RSA 公鑰 ---\ne: {e}\nn: {n}\n--------------------"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(export_text)
        messagebox.showinfo("成功", "公鑰卡片已複製！你可以直接貼給好友了。")

if __name__ == "__main__":
    root = tk.Tk()
    app = RSAApp(root)
    root.mainloop()