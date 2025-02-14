import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
from collections import defaultdict

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("自動點擊器")
        self.root.geometry("800x1000")
        
        # 設定基本顏色
        BG_COLOR = 'white'
        FG_COLOR = 'black'
        
        # 主frame
        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # URL 輸入區
        url_label = tk.Label(self.main_frame, text="請輸入網址 (每行一個):", 
                            bg=BG_COLOR, fg=FG_COLOR, font=('Arial', 12))
        url_label.pack(anchor='w', pady=(0,5))
        
        self.url_text = tk.Text(self.main_frame, width=70, height=10, 
                               bg='white', fg='black', font=('Arial', 11))
        self.url_text.pack(fill='x', pady=(0,10))
        
        # 設定區 Frame
        settings_frame = tk.LabelFrame(self.main_frame, text="設定", 
                                     bg=BG_COLOR, fg=FG_COLOR, font=('Arial', 12))
        settings_frame.pack(fill='x', pady=10)
        
        # 點擊次數設定
        clicks_frame = tk.Frame(settings_frame, bg=BG_COLOR)
        clicks_frame.pack(fill='x', pady=5, padx=5)
        
        clicks_label = tk.Label(clicks_frame, text="點擊次數:", 
                               bg=BG_COLOR, fg=FG_COLOR, font=('Arial', 11))
        clicks_label.pack(side='left')
        
        self.clicks_var = tk.StringVar(value="200")
        clicks_entry = tk.Entry(clicks_frame, textvariable=self.clicks_var, 
                              width=10, font=('Arial', 11))
        clicks_entry.pack(side='left', padx=5)
        
        # 影片播放時間設定
        video_frame = tk.Frame(settings_frame, bg=BG_COLOR)
        video_frame.pack(fill='x', pady=5, padx=5)
        
        video_label = tk.Label(video_frame, text="影片播放時間 (秒):", 
                              bg=BG_COLOR, fg=FG_COLOR, font=('Arial', 11))
        video_label.pack(side='left')
        
        self.video_time_var = tk.StringVar(value="3")
        video_entry = tk.Entry(video_frame, textvariable=self.video_time_var, 
                             width=10, font=('Arial', 11))
        video_entry.pack(side='left', padx=5)
        
        # 按鈕區
        button_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="開始執行", 
                                    command=self.start_clicking, 
                                    bg='#e0e0e0', fg='black',
                                    font=('Arial', 11))
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(button_frame, text="停止", 
                                   command=self.stop_clicking, 
                                   state='disabled',
                                   bg='#e0e0e0', fg='black',
                                   font=('Arial', 11))
        self.stop_button.pack(side='left', padx=5)
        
        # 日誌區
        log_label = tk.Label(self.main_frame, text="執行日誌:", 
                            bg=BG_COLOR, fg=FG_COLOR, font=('Arial', 12))
        log_label.pack(anchor='w', pady=(10,5))
        
        self.log_text = tk.Text(self.main_frame, width=70, height=20,
                               bg='white', fg='black', font=('Arial', 11))
        self.log_text.pack(fill='both', expand=True)
        
        # 添加捲軸
        scrollbar = tk.Scrollbar(self.main_frame, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.is_running = False
        self.driver = None
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_clicking(self):
        urls = self.url_text.get("1.0", tk.END).strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            self.log("錯誤: 請輸入至少一個網址")
            return
            
        try:
            target_clicks = int(self.clicks_var.get())
            video_time = int(self.video_time_var.get())
        except ValueError:
            self.log("錯誤: 請輸入有效的數字")
            return
            
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_running = True
        
        threading.Thread(target=self.clicking_thread, args=(urls, target_clicks, video_time), daemon=True).start()
        
    def stop_clicking(self):
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.log("程式已停止")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
    def clicking_thread(self, urls, target_clicks, video_time):
        try:
            edge_options = Options()
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            self.log("正在啟動瀏覽器...")
            self.driver = webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install()),
                options=edge_options
            )
            
            click_counts = defaultdict(int)
            total_clicks_needed = len(urls) * target_clicks
            total_clicks_done = 0
            
            while self.is_running:
                if all(click_counts[url] >= target_clicks for url in urls):
                    self.log("所有網址都已達到目標點擊數！")
                    break
                    
                for url in urls:
                    if not self.is_running:
                        break
                        
                    if click_counts[url] >= target_clicks:
                        continue
                        
                    try:
                        self.log(f"正在訪問: {url}")
                        self.driver.get(url)
                        click_counts[url] += 1
                        total_clicks_done += 1
                        
                        progress = f"進度: {total_clicks_done}/{total_clicks_needed} ({total_clicks_done/total_clicks_needed*100:.1f}%)"
                        self.log(progress)
                        
                        self.log(f"等待 {video_time} 秒...")
                        time.sleep(video_time)
                        
                    except Exception as e:
                        self.log(f"錯誤: {str(e)}")
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = webdriver.Edge(
                            service=Service(EdgeChromiumDriverManager().install()),
                            options=edge_options
                        )
            
        except Exception as e:
            self.log(f"發生錯誤: {str(e)}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')

def main():
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
