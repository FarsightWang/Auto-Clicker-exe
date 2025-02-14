import tkinter as tk
from tkinter import scrolledtext
import threading
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
from collections import defaultdict

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("自動點擊器")
        
        # 設定視窗大小和位置
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 主容器
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # URL 輸入區域
        url_frame = tk.LabelFrame(main_frame, text="網址設定", padx=10, pady=10)
        url_frame.pack(fill='x', pady=(0, 15))
        
        url_label = tk.Label(url_frame, text="請輸入網址（每行一個）：")
        url_label.pack(anchor='w')
        
        # 使用Text widget搭配捲軸
        self.url_text = tk.Text(url_frame, height=6)
        url_scrollbar = tk.Scrollbar(url_frame, command=self.url_text.yview)
        self.url_text.configure(yscrollcommand=url_scrollbar.set)
        
        self.url_text.pack(side='left', fill='both', expand=True)
        url_scrollbar.pack(side='right', fill='y')
        
        # 設定區域
        settings_frame = tk.LabelFrame(main_frame, text="執行設定", padx=10, pady=10)
        settings_frame.pack(fill='x', pady=15)
        
        # 點擊次數設定
        clicks_frame = tk.Frame(settings_frame)
        clicks_frame.pack(fill='x', pady=5)
        
        clicks_label = tk.Label(clicks_frame, text="點擊次數：")
        clicks_label.pack(side='left')
        
        self.clicks_var = tk.StringVar(value="200")
        clicks_entry = tk.Entry(clicks_frame, textvariable=self.clicks_var, width=10)
        clicks_entry.pack(side='left', padx=5)
        
        # 等待時間設定
        wait_frame = tk.Frame(settings_frame)
        wait_frame.pack(fill='x', pady=5)
        
        wait_label = tk.Label(wait_frame, text="等待時間（秒）：")
        wait_label.pack(side='left')
        
        self.wait_var = tk.StringVar(value="3")
        wait_entry = tk.Entry(wait_frame, textvariable=self.wait_var, width=10)
        wait_entry.pack(side='left', padx=5)
        
        # 按鈕區域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        self.start_button = tk.Button(button_frame, 
                                    text="開始執行",
                                    command=self.start_clicking,
                                    width=15,
                                    height=2)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(button_frame,
                                   text="停止",
                                   command=self.stop_clicking,
                                   width=15,
                                   height=2,
                                   state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # 日誌區域
        log_frame = tk.LabelFrame(main_frame, text="執行日誌", padx=10, pady=10)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True)
        
        self.is_running = False
        self.driver = None
        
        # 添加關閉視窗的處理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """處理視窗關閉事件"""
        if self.is_running:
            self.stop_clicking()
        self.root.destroy()
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
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
            video_time = int(self.wait_var.get())
        except ValueError:
            self.log("錯誤: 請輸入有效的數字")
            return
            
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_running = True
        
        threading.Thread(target=self.clicking_thread,
                       args=(urls, target_clicks, video_time),
                       daemon=True).start()
    
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
                        
                        try:
                            # 等待 LINE VOOM 特定元素載入
                            self.log("等待頁面載入...")
                            
                            # 等待影片容器出現
                            video_container = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".post-detail"))
                            )
                            self.log("影片容器已載入")
                            
                            # 等待播放按鈕並點擊（如果存在）
                            try:
                                play_button = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".vjs-big-play-button"))
                                )
                                play_button.click()
                                self.log("已點擊播放按鈕")
                            except:
                                self.log("找不到播放按鈕，可能影片已自動播放")
                            
                            # 給予額外的載入時間
                            self.log("等待影片開始播放（5秒）...")
                            time.sleep(5)
                            
                        except Exception as e:
                            self.log(f"注意: 無法確認影片狀態 - {str(e)}")
                        
                        click_counts[url] += 1
                        total_clicks_done += 1
                        
                        progress = f"進度: {total_clicks_done}/{total_clicks_needed} "
                        progress += f"({total_clicks_done/total_clicks_needed*100:.1f}%)"
                        self.log(progress)
                        
                        self.log(f"播放持續 {video_time} 秒...")
                        time.sleep(video_time)
                        
                        # 完成後暫停一下，避免太快切換
                        time.sleep(2)
                        
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
