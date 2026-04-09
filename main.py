#!/usr/bin/env python3
"""
Letterboxd Film Öneri Uygulaması
Ana uygulama giriş noktası

Kullanım: python main.py
"""

import tkinter as tk
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.ui import LetterboxdApp

def main():
    """
    Ana uygulama fonksiyonu
    """
    try:
        # Tkinter root window oluştur
        root = tk.Tk()
        
        # Uygulama konfigürasyonu
        root.title("Letterboxd Film Öneri Uygulaması")
        root.geometry("900x700")
        root.minsize(800, 600)
        
        # Pencere ikonu (varsa)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            if os.path.exists(icon_path):
                if sys.platform == "win32":
                    root.iconbitmap(icon_path)
                else:
                    photo = tk.PhotoImage(file=icon_path)
                    root.iconphoto(True, photo)
        except Exception:
            pass  # İkon bulunamadı ise devam et
        
        # Uygulama örneği oluştur
        app = LetterboxdApp(root)
        
        # Pencere kapatma olayı
        def on_closing():
            root.quit()
            root.destroy()
            sys.exit(0)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Başlangıç mesajı
        print("🎬 Letterboxd Film Öneri Uygulaması başlatılıyor...")
        print("📊 API ve scraping modülleri yükleniyor...")
        
        # Ana döngüyü başlat
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Uygulama kullanıcı tarafından durduruldu.")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Modül import hatası: {e}")
        print("🔧 Lütfen gerekli kütüphanelerin yüklü olduğundan emin olun:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Uygulama başlatma hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()