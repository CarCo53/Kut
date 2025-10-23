# gui/visuals.py
import os
from PIL import Image, ImageTk
from log import logger
import sys # <-- YENİ İMPORT

class Visuals:
    @logger.log_function
    def __init__(self):
        self.tas_resimleri = {}

    @logger.log_function
    def yukle(self, images_path="images", boyut=(40, 60)):
        
        # --- KRİTİK DÜZELTME BAŞLANGIÇ ---
        # PyInstaller ile paketlenmişse, images_path'i geçici dizinin altındaki doğru yola ayarlayın.
        if getattr(sys, 'frozen', False):
            # PyInstaller'ın geçici dizinini alıp images alt dizinini ekleyin
            base_path = sys._MEIPASS
            images_path = os.path.join(base_path, images_path)
            logger.info(f"PyInstaller algılandı. Görsel yolu ayarlandı: {images_path}")
        # --- KRİTİK DÜZELTME SONU ---
        
        for dosya in os.listdir(images_path):
            if dosya.endswith(".png"):
                tam_yol = os.path.join(images_path, dosya)
                try:
                    img = Image.open(tam_yol)
                    img = img.resize(boyut, Image.Resampling.LANCZOS)
                    self.tas_resimleri[dosya] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Görsel yüklenemedi: {tam_yol} ({e})")