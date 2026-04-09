"""
Tkinter UI Module (Geliştirilmiş ve Modern)
Letterboxd Film Öneri Uygulaması arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

class LetterboxdApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Letterboxd Film Öneri")
        self.root.geometry("1000x750")
        self.root.configure(bg='#1a1a2e')
        self.root.minsize(800, 600)
        
        # Modern renk paleti - daha görünür
        self.colors = {
            'bg': '#0f1419',           # Daha koyu arka plan
            'card_bg': '#1c1f26',       # Daha belirgin kart arka planı
            'accent': '#1da1f2',         # Twitter mavisi - daha belirgin
            'accent_hover': '#1a91da',    # Hover rengi
            'text_primary': '#ffffff',     # Ana metin
            'text_secondary': '#8899a6',  # İkincil metin
            'success': '#28a745',        # Başarı rengi
            'warning': '#ffc107',        # Uyarı rengi
            'error': '#dc3545',          # Hata rengi
            'border': '#38444d'         # Kenarlık
        }
        
        # Değişkenler
        self.current_recommendations = []
        self.poster_images = {}
        
        # Font'lar
        self.fonts = {
            'title': ("SF Pro Display", 24, "bold"),
            'subtitle': ("SF Pro Display", 12, "normal"),
            'card_title': ("SF Pro Display", 14, "bold"),
            'card_text': ("SF Pro Text", 10, "normal"),
            'button': ("SF Pro Display", 12, "bold"),
            'input': ("SF Pro Text", 11, "normal")
        }
        
        # Ana container
        self.main_container = tk.Frame(root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        self.create_header()
        
        # Ana içerik alanı
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Başlangıç ekranını göster
        self.show_input_screen()
    
    def create_header(self):
        """
        Modern uygulama başlığı oluşturur
        """
        header_frame = tk.Frame(self.main_container, bg=self.colors['card_bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        # Gradient efekti için çizgiler
        for i in range(3):
            line = tk.Frame(
                header_frame, 
                bg=self.colors['accent'] if i == 0 else self.colors['bg'],
                height=2 if i == 0 else 1
            )
            line.pack(fill=tk.X, pady=(0, 2) if i == 0 else (1, 0))
        
        # Başlık container
        title_container = tk.Frame(header_frame, bg=self.colors['card_bg'])
        title_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        title_label = tk.Label(
            title_container,
            text="🎬 Letterboxd Film Öneri",
            font=self.fonts['title'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_container,
            text="Kişiselleştirilmiş film önerileri keşfedin",
            font=self.fonts['subtitle'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Alt çizgi
        bottom_line = tk.Frame(
            header_frame, 
            bg=self.colors['accent'], 
            height=3
        )
        bottom_line.pack(fill=tk.X, side=tk.BOTTOM)
    
    def show_input_screen(self):
        """
        Modern giriş ekranı gösterir
        """
        # Temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Ana container
        input_container = tk.Frame(self.content_frame, bg=self.colors['bg'])
        input_container.pack(expand=True, fill=tk.BOTH, padx=40)
        
        # Kart tasarımı
        card_frame = tk.Frame(
            input_container, 
            bg=self.colors['card_bg'],
            relief=tk.RAISED,
            bd=1
        )
        card_frame.pack(expand=True, fill=tk.BOTH, pady=40)
        
        # Kart içeriği
        card_content = tk.Frame(card_frame, bg=self.colors['card_bg'], padx=40, pady=40)
        card_content.pack(expand=True, fill=tk.BOTH)
        
        # Icon ve başlık
        header_section = tk.Frame(card_content, bg=self.colors['card_bg'])
        header_section.pack(fill=tk.X, pady=(0, 30))
        
        icon_label = tk.Label(
            header_section,
            text="🎭",
            font=("SF Pro Display", 48),
            bg=self.colors['card_bg'],
            fg=self.colors['accent']
        )
        icon_label.pack()
        
        welcome_label = tk.Label(
            header_section,
            text="Film Önerileri İçin Başlayın",
            font=self.fonts['card_title'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        welcome_label.pack(pady=(15, 10))
        
        desc_label = tk.Label(
            header_section,
            text="Letterboxd profilinizi analiz ederek size özel film önerileri sunalım",
            font=self.fonts['card_text'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            wraplength=400
        )
        desc_label.pack()
        
        # Input bölümü
        input_section = tk.Frame(card_content, bg=self.colors['card_bg'])
        input_section.pack(fill=tk.X, pady=(30, 0))
        
        url_label = tk.Label(
            input_section,
            text="📽️ Letterboxd Profil URL",
            font=self.fonts['card_text'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        url_label.pack(anchor=tk.W, pady=(0, 10))
        
        input_container_frame = tk.Frame(input_section, bg=self.colors['card_bg'])
        input_container_frame.pack(fill=tk.X)
        
        self.url_entry = tk.Entry(
            input_container_frame,
            width=40,
            font=self.fonts['input'],
            bg=self.colors['bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=self.colors['accent']
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.url_entry.insert(0, "https://letterboxd.com/berkecraft/")
        
        # Buton - daha belirgin ve yüksek kontrast
        analyze_btn = tk.Button(
            input_container_frame,
            text="🔍 ANALİZ ET",
            command=self.start_analysis,
            font=("SF Pro Display", 13, "bold"),
            bg='#ffffff',                    # Beyaz arka plan
            fg='#1da1f2',                  # Mavi metin - yüksek kontrast
            activebackground='#f0f8ff',     # Çok açık mavi hover
            activeforeground='#1da1f2',
            relief=tk.RAISED,                # Kabartılmış
            bd=3,                           # Kalın border
            padx=35,
            pady=16,
            cursor='hand2',
            width=14,
            highlightthickness=2,
            highlightbackground='#1da1f2',
            highlightcolor='#1da1f2'
        )
        analyze_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Hover efekti - daha belirgin
        def on_enter(e):
            analyze_btn.config(
                bg='#e8f5ff',              # Açık mavi hover
                relief=tk.GROOVE,
                bd=4
            )
        
        def on_leave(e):
            analyze_btn.config(
                bg='#ffffff',
                relief=tk.RAISED,
                bd=3
            )
        
        analyze_btn.bind("<Enter>", on_enter)
        analyze_btn.bind("<Leave>", on_leave)
        
        # Özellikler section
        features_frame = tk.Frame(card_content, bg=self.colors['card_bg'])
        features_frame.pack(fill=tk.X, pady=(40, 0))
        
        features_title = tk.Label(
            features_frame,
            text="✨ Özellikler",
            font=self.fonts['card_text'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        features_title.pack(anchor=tk.W, pady=(0, 15))
        
        features = [
            "🎯 Kişiselleştirilmiş öneriler",
            "🎭 Tercihlerinize göre tür analizi", 
            "⭐ Yüksek puanlı kaliteli filmler",
            "🔍 Yeni türler keşfedin"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=self.fonts['card_text'],
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            feature_label.pack(anchor=tk.W, pady=3)
    
    def show_loading_screen(self):
        """
        Modern yükleme ekranı gösterir
        """
        # Temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        loading_container = tk.Frame(self.content_frame, bg=self.colors['bg'])
        loading_container.pack(expand=True, fill=tk.BOTH)
        
        # Loading card
        card_frame = tk.Frame(
            loading_container, 
            bg=self.colors['card_bg'],
            relief=tk.RAISED,
            bd=1
        )
        card_frame.pack(expand=True, pady=100)
        
        card_content = tk.Frame(card_frame, bg=self.colors['card_bg'], padx=60, pady=60)
        card_content.pack()
        
        # Loading icon
        loading_icon = tk.Label(
            card_content,
            text="🎬",
            font=("SF Pro Display", 48),
            bg=self.colors['card_bg'],
            fg=self.colors['accent']
        )
        loading_icon.pack(pady=(0, 20))
        
        # Progress container
        progress_container = tk.Frame(card_content, bg=self.colors['card_bg'])
        progress_container.pack(fill=tk.X, pady=(0, 20))
        
        # Modern progress bar
        progress_bg = tk.Frame(
            progress_container,
            bg=self.colors['bg'],
            height=6
        )
        progress_bg.pack(fill=tk.X)
        progress_bg.pack_propagate(False)
        
        # Progress animation için bar
        self.progress_bar = tk.Frame(
            progress_bg,
            bg=self.colors['accent'],
            height=6
        )
        self.progress_bar.place(x=0, y=0, width=0)
        self.animate_progress()
        
        # Durum metni
        self.status_label = tk.Label(
            card_content,
            text="Profiliniz analiz ediliyor...",
            font=self.fonts['card_text'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(pady=10)
        
        # Alt bilgi
        info_label = tk.Label(
            card_content,
            text="Lütfen bekleyin, bu işlem biraz zaman alabilir...",
            font=("SF Pro Text", 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        info_label.pack(pady=(20, 0))
    
    def animate_progress(self):
        """
        Progress bar animasyonu
        """
        def update_width():
            try:
                current_width = self.progress_bar.winfo_width()
                if current_width < 300:
                    new_width = current_width + 10
                    self.progress_bar.place(width=new_width)
                    self.root.after(100, update_width)
                else:
                    self.progress_bar.place(width=0)
                    self.root.after(100, update_width)
            except:
                pass
        
        self.root.after(100, update_width)
    
    def update_status(self, message):
        """
        Durum metnini günceller
        """
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            self.root.update()
    
    def show_results_screen(self, recommendations, user_stats):
        """
        Modern sonuç ekranı gösterir
        """
        # Temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Header
        results_header = tk.Frame(self.content_frame, bg=self.colors['bg'])
        results_header.pack(fill=tk.X, padx=40, pady=(20, 0))
        
        # Sol taraf - Başlık
        title_frame = tk.Frame(results_header, bg=self.colors['bg'])
        title_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        results_title = tk.Label(
            title_frame,
            text="🎯 Film Önerileriniz",
            font=self.fonts['card_title'],
            bg=self.colors['bg'],
            fg=self.colors['text_primary']
        )
        results_title.pack(anchor=tk.W)
        
        # İstatistikler
        stats_container = tk.Frame(title_frame, bg=self.colors['bg'])
        stats_container.pack(anchor=tk.W, pady=(5, 0))
        
        # Ana istatistikler
        total_films = user_stats.get('total_films', 0)
        high_rated = user_stats.get('high_rated_count', 0)
        low_rated = total_films - high_rated
        
        # Öneri sayısını hesapla
        if total_films < 5:
            expected_recs = 8
        elif total_films < 10:
            expected_recs = 12
        elif total_films < 20:
            expected_recs = 15
        elif total_films < 50:
            expected_recs = 18
        else:
            expected_recs = 20
        
        # İstatistik metni
        stats_text = f"📊 {total_films} film analiz edildi → {expected_recs} öneri"
        stats_label = tk.Label(
            stats_container,
            text=stats_text,
            font=self.fonts['card_text'],
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        stats_label.pack(anchor=tk.W)
        
        # Film dağılımı
        breakdown_container = tk.Frame(stats_container, bg=self.colors['bg'])
        breakdown_container.pack(anchor=tk.W, pady=(8, 0))
        
        # Film dağılım etiketleri
        breakdown_text = f"⭐ {high_rated} yüksek puanlı  •  ⚪ {low_rated} düşük puanlı"
        breakdown_label = tk.Label(
            breakdown_container,
            text=breakdown_text,
            font=("SF Pro Text", 9, "normal"),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        breakdown_label.pack(anchor=tk.W)
        stats_label = tk.Label(
            title_frame,
            text=stats_text,
            font=self.fonts['card_text'],
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        stats_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Sağ taraf - Buton
        new_analysis_btn = tk.Button(
            results_header,
            text="🔄 Yeni Analiz",
            command=self.show_input_screen,
            font=self.fonts['button'],
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent_hover'],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        new_analysis_btn.pack(side=tk.RIGHT)
        
        # Film listesi
        if recommendations:
            self.create_movie_list(recommendations)
        else:
            self.show_no_results()
    
    def create_movie_list(self, recommendations):
        """
        Modern film listesi oluşturur
        """
        # Scrollable container
        canvas = tk.Canvas(self.content_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Filmleri modern kartlar olarak ekle
        for i, movie in enumerate(recommendations):
            self.create_movie_card(scrollable_frame, movie, i + 1)
        
        canvas.pack(side="left", fill="both", expand=True, padx=40, pady=(20, 40))
        scrollbar.pack(side="right", fill="y", pady=(20, 40))
    
    def create_movie_card(self, parent, movie, index):
        """
        Modern film kartı oluşturur
        """
        # Kart container
        card_container = tk.Frame(parent, bg=self.colors['bg'])
        card_container.pack(fill=tk.X, pady=(0, 20))
        
        # Kart
        card = tk.Frame(
            card_container,
            bg=self.colors['card_bg'],
            relief=tk.RAISED,
            bd=1
        )
        card.pack(fill=tk.X, padx=(20, 20))
        
        # Kart içeriği
        card_content = tk.Frame(card, bg=self.colors['card_bg'], padx=25, pady=20)
        card_content.pack(fill=tk.X)
        
        # Sol taraf - Poster
        poster_frame = tk.Frame(card_content, bg=self.colors['card_bg'], width=120, height=180)
        poster_frame.pack(side=tk.LEFT, padx=(0, 25))
        poster_frame.pack_propagate(False)
        
        # Poster yükleme
        self.load_poster(poster_frame, movie.get('poster_url'))
        
        # Sağ taraf - Bilgiler
        info_frame = tk.Frame(card_content, bg=self.colors['card_bg'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Sıra no ve başlık
        header_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Modern sıra numarası
        index_bg = tk.Frame(
            header_frame, 
            bg=self.colors['accent'],
            width=35,
            height=35
        )
        index_bg.pack(side=tk.LEFT, padx=(0, 15))
        index_bg.pack_propagate(False)
        
        index_label = tk.Label(
            index_bg,
            text=f"{index:02d}",
            font=("SF Pro Display", 14, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['text_primary']
        )
        index_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        title_label = tk.Label(
            header_frame,
            text=movie.get('title', 'Bilinmeyen Film'),
            font=self.fonts['card_title'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        year = movie.get('year')
        if year:
            year_label = tk.Label(
                header_frame,
                text=f"({year})",
                font=self.fonts['card_text'],
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            year_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Genre'ler
        genres = movie.get('genres', [])
        if genres:
            genre_container = tk.Frame(info_frame, bg=self.colors['card_bg'])
            genre_container.pack(fill=tk.X, pady=(0, 12))
            
            # Max 3 genre göster
            for i, genre in enumerate(genres[:3]):
                genre_tag = tk.Frame(
                    genre_container,
                    bg=self.colors['accent'],
                    relief=tk.FLAT
                )
                genre_tag.pack(side=tk.LEFT, padx=(0, 8))
                
                genre_label = tk.Label(
                    genre_tag,
                    text=genre,
                    font=("SF Pro Text", 8, "bold"),
                    bg=self.colors['accent'],
                    fg=self.colors['text_primary'],
                    padx=8,
                    pady=3
                )
                genre_label.pack()
        
        # Overview
        overview = movie.get('overview', '')
        if overview:
            overview_container = tk.Frame(info_frame, bg=self.colors['card_bg'])
            overview_container.pack(fill=tk.X, pady=(0, 15))
            
            # Metni kısalt
            if len(overview) > 180:
                overview = overview[:180] + "..."
            
            overview_label = tk.Label(
                overview_container,
                text=overview,
                font=self.fonts['card_text'],
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary'],
                wraplength=600,
                justify=tk.LEFT
            )
            overview_label.pack(anchor=tk.W)
        
        # Footer - Tarih ve öneri bilgisi
        footer_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Sol taraf - Puanlar
        score_container = tk.Frame(footer_frame, bg=self.colors['card_bg'])
        score_container.pack(side=tk.LEFT)
        
        # TMDb puanı
        vote_avg = movie.get('vote_average', 0)
        if vote_avg > 0:
            score_frame = tk.Frame(score_container, bg=self.colors['card_bg'])
            score_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            score_icon = tk.Label(
                score_frame,
                text="⭐",
                font=("SF Pro Display", 12),
                bg=self.colors['card_bg'],
                fg='#ffc107'
            )
            score_icon.pack(side=tk.LEFT)
            
            score_label = tk.Label(
                score_frame,
                text=f"{vote_avg:.1f}",
                font=self.fonts['card_text'],
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            score_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Öneri skoru
        rec_score = movie.get('recommendation_score', 0)
        if rec_score > 0:
            match_frame = tk.Frame(score_container, bg=self.colors['card_bg'])
            match_frame.pack(side=tk.LEFT)
            
            match_icon = tk.Label(
                match_frame,
                text="🎯",
                font=("SF Pro Display", 12),
                bg=self.colors['card_bg'],
                fg=self.colors['success']
            )
            match_icon.pack(side=tk.LEFT)
            
            match_label = tk.Label(
                match_frame,
                text=f"%{int(rec_score)} uyum",
                font=self.fonts['card_text'],
                bg=self.colors['card_bg'],
                fg=self.colors['success']
            )
            match_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Sağ taraf - Kaynak bilgisi
        source = movie.get('source')
        if source:
            source_info = {
                'genre': ('🎭', 'Tüm Beğenilen Türler', '#28a745'),
                'similar': ('🎬', 'Benzer Filmler', '#17a2b8'),
                'popular': ('⭐', 'Popüler Filmler', '#ffc107'),
                'discovery': ('🔍', 'Keşif Önerisi', '#6f42c1'),
                'bonus': ('🎁', 'Bonus Öneriler', '#fd7e14')
            }
            
            if source in source_info:
                icon, text, color = source_info[source]
                
                source_frame = tk.Frame(footer_frame, bg=self.colors['card_bg'])
                source_frame.pack(side=tk.RIGHT)
                
                source_label = tk.Label(
                    source_frame,
                    text=f"{icon} {text}",
                    font=("SF Pro Text", 9, "bold"),
                    bg=self.colors['card_bg'],
                    fg=color
                )
                source_label.pack()
        
        # Tarih dönemi bilgisi (popüler filmler için)
        period = movie.get('source_period')
        if period:
            period_frame = tk.Frame(footer_frame, bg=self.colors['card_bg'])
            period_frame.pack(side=tk.RIGHT, padx=(0, 15))
            
            period_label = tk.Label(
                period_frame,
                text=f"📅 {period}",
                font=("SF Pro Text", 8),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            period_label.pack()
        
        # Dayanak film (benzer filmler için)
        based_on = movie.get('based_on_movie')
        if based_on and source == 'similar':
            based_frame = tk.Frame(footer_frame, bg=self.colors['card_bg'])
            based_frame.pack(side=tk.RIGHT, padx=(0, 20))
            
            based_label = tk.Label(
                based_frame,
                text=f"📺 {based_on} filmine dayalı",
                font=("SF Pro Text", 9),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            based_label.pack()
    
    def load_poster(self, parent_frame, poster_url):
        """
        Modern poster yükler
        """
        def load_image():
            try:
                if poster_url:
                    response = requests.get(poster_url, timeout=8)
                    response.raise_for_status()
                    
                    image_data = BytesIO(response.content)
                    image = Image.open(image_data)
                    
                    # Boyutlandır ve crop et
                    image = image.resize((120, 180), Image.Resampling.LANCZOS)
                    
                    # Border ekle
                    photo = ImageTk.PhotoImage(image)
                    
                    poster_label = tk.Label(
                        parent_frame, 
                        image=photo,
                        bg=self.colors['card_bg'],
                        relief=tk.RAISED,
                        bd=1
                    )
                    setattr(poster_label, 'image', photo)
                    poster_label.pack(expand=True, fill=tk.BOTH)
                    return
                
            except Exception:
                pass
            
            # Placeholder
            placeholder = tk.Label(
                parent_frame,
                text="🎬\n\nPoster\nYok",
                font=("SF Pro Display", 10),
                bg='#2c3e50',
                fg=self.colors['text_secondary']
            )
            placeholder.pack(expand=True, fill=tk.BOTH, relief=tk.SUNKEN, bd=1)
        
        # Ayrı thread'de yükle
        threading.Thread(target=load_image, daemon=True).start()
    
    def show_no_results(self):
        """
        Modern "sonuç bulunamadı" ekranı
        """
        # Temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        container = tk.Frame(self.content_frame, bg=self.colors['bg'])
        container.pack(expand=True, fill=tk.BOTH, padx=40)
        
        # Card
        card_frame = tk.Frame(
            container, 
            bg=self.colors['card_bg'],
            relief=tk.RAISED,
            bd=1
        )
        card_frame.pack(expand=True, pady=100)
        
        card_content = tk.Frame(card_frame, bg=self.colors['card_bg'], padx=50, pady=50)
        card_content.pack()
        
        # Icon
        icon_label = tk.Label(
            card_content,
            text="😔",
            font=("SF Pro Display", 48),
            bg=self.colors['card_bg'],
            fg=self.colors['warning']
        )
        icon_label.pack(pady=(0, 20))
        
        # Başlık
        title_label = tk.Label(
            card_content,
            text="Öneri Bulunamadı",
            font=self.fonts['card_title'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Mesaj
        message_label = tk.Label(
            card_content,
            text="Profilinizde yeterli miktarda puanlanmış film bulunamadı.\nDaha fazla film puanladıktan sonra tekrar deneyin.",
            font=self.fonts['card_text'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            justify=tk.CENTER
        )
        message_label.pack(pady=(0, 30))
        
        # Buton - daha belirgin
        new_analysis_btn = tk.Button(
            card_content,
            text="🔄 YENİ ANALİZ",
            command=self.show_input_screen,
            font=("SF Pro Display", 11, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent_hover'],
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            width=12
        )
        new_analysis_btn.pack()
    
    def start_analysis(self):
        """
        Analiz işlemini başlatır
        """
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Hata", "Lütfen Letterboxd profil URL'sini girin!")
            return
        
        # Input sanitization and validation
        if not self._validate_letterboxd_url(url):
            messagebox.showerror("Hata", "Geçersiz Letterboxd URL'si!\nURL şu formatlarda olmalı:\nhttps://letterboxd.com/username/\nhttps://letterboxd.com/username/films/")
            return
        
        # Yükleme ekranına geç
        self.show_loading_screen()
        
        # Analizi ayrı thread'de başlat
        threading.Thread(target=self.analyze_profile, args=(url,), daemon=True).start()
    
    def _validate_letterboxd_url(self, url):
        """
        Letterboxd URL'sini validate ve sanitize eder
        """
        if not url or not isinstance(url, str):
            return False
            
        # URL uzunluk kontrolü (DOS saldırılarına karşı)
        if len(url) > 2048:
            return False
            
        # Protocol kontrolü ve normalization
        if not url.startswith('https://letterboxd.com/') and not url.startswith('http://letterboxd.com/'):
            return False
            
        # Protocol'u https'ye zorla (güvenlik için)
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
            
        # URL parsing
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
        except Exception:
            return False
            
        # Domain kontrolü
        if parsed.netloc not in ['letterboxd.com', 'www.letterboxd.com']:
            return False
            
        # Path kontrolü - username/veya username/films/ formatında olmalı
        path_parts = [part for part in parsed.path.split('/') if part]
        if len(path_parts) == 0 or len(path_parts) > 2:
            return False
            
        # Username kontrolü (boş olamaz, özel karakterler içermemeli)
        username = path_parts[0]
        if not username:
            return False
            
        # Username karakter kontrolü (Letterboxd standartları)
        import re
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', username):
            return False
            
        # İkinci path parçası varsa, sadece 'films' olabilir
        if len(path_parts) == 2 and path_parts[1] != 'films':
            return False
            
        # Query parametreleri kontrolü (güvenlik için)
        if parsed.query:
            # Basit query parameter injection koruması
            if ';' in parsed.query or '&' in parsed.query.split('&')[0] if '&' in parsed.query else False:
                # Basit kontrol - kötü niyetli parametreleri tespit et
                import urllib.parse
                try:
                    params = urllib.parse.parse_qs(parsed.query)
                    # Her parametre değerini kontrol et
                    for param_values in params.values():
                        for value in param_values:
                            if not isinstance(value, str) or len(value) > 100:
                                return False
                except Exception:
                    return False
                    
        return True
    
    def analyze_profile(self, url):
        """
        Profil analizi yapar (ayrı thread'de çalışır)
        """
        try:
            from .scraper import LetterboxdScraper
            from .tmdb_api import TMDBAPI
            from .recommender import MovieRecommender
            
            # Adım 1: Letterboxd'den veri çek
            self.update_status("🔍 Letterboxd profili taranıyor...")
            scraper = LetterboxdScraper()
            profile_data = scraper.scrape_profile(url)
            
            high_rated_films = profile_data.get('high_rated_films', [])
            
            if not high_rated_films:
                self.root.after(0, lambda: self.show_results_screen([], profile_data))
                return
            
            # Adım 2: TMDb ile veri zenginleştirme
            self.update_status("📊 Film verileri zenginleştiriliyor...")
            tmdb = TMDBAPI()
            enriched_films = tmdb.enrich_letterboxd_films(high_rated_films)
            
            # Adım 3: Öneri algoritması
            self.update_status("🎯 Film önerileri hazırlanıyor...")
            recommender = MovieRecommender()
            recommendations = recommender.get_recommendations(enriched_films, 10)
            
            # Sonuçları göster
            self.root.after(0, lambda: self.show_results_screen(recommendations, profile_data))
            
        except Exception as e:
            error_message = f"Analiz sırasında hata oluştu:\n{str(e)}"
            self.root.after(0, lambda: self.show_error(error_message))
    
    def show_error(self, message):
        """
        Hata mesajı gösterir
        """
        messagebox.showerror("Hata", message)
        self.show_input_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = LetterboxdApp(root)
    root.mainloop()