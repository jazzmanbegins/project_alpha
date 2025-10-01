import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random
import os

# -------------------------
# พยายามโหลด pygame
try:
    import pygame
    pygame.mixer.init()
    SOUND_ENABLED = True
except Exception as e:
    print("⚠️ โหลด pygame ไม่ได้หรือเปิดเสียงไม่ได้:", e)
    SOUND_ENABLED = False

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 เกมจับคู่ภาพ")
        self.root.geometry("1200x950")
        self.root.resizable(False, False)
        self.root.configure(bg="#2C3E50")
        
        # --- โหลดเสียง (ถ้ามี) ---
        self.sounds = {}
        if SOUND_ENABLED:
            self.sound_folder = "Sounds"
            self.sounds = {
                "click": self.find_sound("click"),
                "wrong": self.find_sound("wrong"),
                "match": self.find_sound("match"),
                "win": self.find_sound("win"),
            }

        # --- ตั้งค่า ---
        self.image_folder = "Images"
        self.card_size = (150, 150)
        self.rows, self.cols = 4, 6
        self.corner_radius = 20

        # โหลดภาพ
        self.image_files = []
        self.load_images()

        # สร้างการ์ด
        self.cards = list(range(12)) * 2
        random.shuffle(self.cards)

        # โหลดการ์ด
        self.card_images = {}
        self.back_image = None
        self.load_card_images()

        # ตัวแปรเกม
        self.buttons = []
        self.revealed = []
        self.matched = []
        self.moves = 0
        self.pairs_found = 0

        # UI
        self.create_header()
        self.create_board()

    # -------------------------
    def find_sound(self, name):
        """หาว่ามีไฟล์เสียง .wav หรือ .mp3"""
        for ext in [".wav", ".mp3"]:
            path = os.path.join("Sounds", name + ext)
            if os.path.exists(path):
                return path
        return None

    # -------------------------
    def play_sound(self, key):
        """เล่นเสียง รองรับทั้ง wav/mp3"""
        if SOUND_ENABLED and key in self.sounds:
            path = self.sounds[key]
            if path and os.path.exists(path):
                try:
                    if path.lower().endswith(".mp3"):
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play()
                    else:
                        pygame.mixer.Sound(path).play()
                except Exception as e:
                    print("⚠️ เล่นเสียงล้มเหลว:", e)

    # -------------------------
    def load_images(self):
        if not os.path.exists(self.image_folder):
            messagebox.showerror("ข้อผิดพลาด", f"ไม่พบโฟลเดอร์ {self.image_folder}")
            self.root.destroy()
            return
        
        files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        files.sort()
        if len(files) >= 12:
            self.image_files = files[:12]
        else:
            messagebox.showerror("ข้อผิดพลาด", f"ต้องการอย่างน้อย 12 ภาพ แต่พบ {len(files)}")
            self.root.destroy()

    def round_corners(self, img, radius):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
        img.putalpha(mask)
        return img

    def load_card_images(self):
        back_path = os.path.join(self.image_folder, "back.jpg")
        if not os.path.exists(back_path):
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์ back.jpg")
            self.root.destroy()
            return
        
        back_img = Image.open(back_path).resize(self.card_size, Image.Resampling.LANCZOS)
        back_img = self.round_corners(back_img, self.corner_radius)
        self.back_image = ImageTk.PhotoImage(back_img)
        
        for i, filename in enumerate(self.image_files):
            img_path = os.path.join(self.image_folder, filename)
            img = Image.open(img_path).resize(self.card_size, Image.Resampling.LANCZOS)
            img = self.round_corners(img, self.corner_radius)
            self.card_images[i] = ImageTk.PhotoImage(img)

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#34495E", pady=10)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.pairs_label = tk.Label(header_frame, text=f"คู่ที่จับได้: {self.pairs_found}/12",
                                    font=("Cordia New", 24, "bold"), bg="#34495E", fg="#ECF0F1")
        self.pairs_label.pack(side=tk.LEFT, padx=20)
        
        self.moves_label = tk.Label(header_frame, text=f"จำนวนครั้ง: {self.moves}",
                                    font=("Cordia New", 24, "bold"), bg="#34495E", fg="#ECF0F1")
        self.moves_label.pack(side=tk.RIGHT, padx=20)
        
        reset_btn = tk.Button(self.root, text=" Reset Game ", font=("Cordia New", 24, "bold"),
                              bg="#2772C9", fg="white", activebackground="#1B6099",
                              command=self.reset_game, cursor="hand2", relief=tk.RAISED, bd=3)
        reset_btn.pack(pady=10)

    def create_board(self):
        board_frame = tk.Frame(self.root, bg="#2C3E50")
        board_frame.pack(pady=10, padx=20)
        
        for i in range(self.rows * self.cols):
            btn = tk.Label(board_frame, image=self.back_image, bg="#2C3E50", cursor="hand2")
            btn.bind("<Button-1>", lambda e, idx=i: self.card_clicked(idx))
            row = i // self.cols
            col = i % self.cols
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(btn)

    def card_clicked(self, index):
        if index in self.revealed or index in self.matched:
            return
        if len(self.revealed) >= 2:
            return

        self.play_sound("click")
        card_id = self.cards[index]
        self.buttons[index].config(image=self.card_images[card_id])
        self.revealed.append(index)
        
        if len(self.revealed) == 2:
            self.moves += 1
            self.moves_label.config(text=f"จำนวนครั้ง: {self.moves}")
            self.root.after(800, self.check_match)

    def check_match(self):
        idx1, idx2 = self.revealed
        if self.cards[idx1] == self.cards[idx2]:
            self.play_sound("match")
            self.matched.extend([idx1, idx2])
            self.pairs_found += 1
            self.pairs_label.config(text=f"คู่ที่จับได้: {self.pairs_found}/12")
            if self.pairs_found == 12:
                self.game_won()
        else:
            self.play_sound("wrong")
            self.buttons[idx1].config(image=self.back_image)
            self.buttons[idx2].config(image=self.back_image)
        self.revealed.clear()

    def game_won(self):
        self.play_sound("win")
        message = f"🎉 ยินดีด้วย! คุณชนะแล้ว! 🎉\n\n"
        message += f"จับคู่ได้ทั้งหมด {self.pairs_found} คู่\n"
        message += f"ใช้ไป {self.moves} ครั้ง"
        
        result = messagebox.askyesno("ชนะแล้ว!", message + "\n\nต้องการเล่นอีกครั้งไหม?")
        if result:
            self.reset_game()

    def reset_game(self):
        self.cards = list(range(12)) * 2
        random.shuffle(self.cards)
        self.revealed.clear()
        self.matched.clear()
        self.moves = 0
        self.pairs_found = 0
        self.pairs_label.config(text=f"คู่ที่จับได้: {self.pairs_found}/12")
        self.moves_label.config(text=f"จำนวนครั้ง: {self.moves}")
        
        for btn in self.buttons:
            btn.config(image=self.back_image)

# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()
