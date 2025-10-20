# gui/buttons/__init__.py

import tkinter as tk
from core.game_state import GameState
from log import logger

# Ayırdığımız fonksiyonları import et
from gui.buttons.yerden_al import yerden_al # Fonksiyon hala import ediliyor ama ButtonManager kullanmayacak
from gui.buttons.gec import gec
from gui.buttons.desteden_cek import desteden_cek
from gui.buttons.el_ac import el_ac
from gui.buttons.tas_at import tas_at
from gui.buttons.yeni_oyun import yeni_oyun
from gui.buttons.butonlari_guncelle import butonlari_guncelle # YENİ IMPORT

class ButtonManager:
    @logger.log_function
    def __init__(self, arayuz):
        self.arayuz = arayuz
        self.butonlar = {}

    def ekle_butonlar(self, parent):
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        # self.butonlar["yerden_al"] = tk.Button(frame, text="Yerden Al", command=self.yerden_al) # KALDIRILDI
        self.butonlar["gec"] = tk.Button(frame, text="Geç", command=self.gec)
        self.butonlar["desteden_cek"] = tk.Button(frame, text="Desteden Çek", command=self.desteden_cek)
        self.butonlar["el_ac"] = tk.Button(frame, text="Elini Aç", command=self.el_ac)
        self.butonlar["tas_at"] = tk.Button(frame, text="Taş At", command=self.tas_at)
        self.butonlar["yeni_oyun"] = tk.Button(frame, text="Yeni Oyun", command=self.yeni_oyun)
        
        for btn in self.butonlar.values():
            btn.pack(side=tk.LEFT, padx=8)

    
    def butonlari_guncelle(self, oyun_durumu):
        # Modüler fonksiyona devret
        return butonlari_guncelle(self, oyun_durumu)

    # def yerden_al(self): # KALDIRILDI
    #     yerden_al(self.arayuz) # KALDIRILDI

    @logger.log_function
    def gec(self):
        gec(self.arayuz)

    @logger.log_function
    def desteden_cek(self):
        desteden_cek(self.arayuz)

    @logger.log_function
    def el_ac(self):
        el_ac(self.arayuz)

    @logger.log_function
    def tas_at(self):
        tas_at(self.arayuz)

    @logger.log_function
    def yeni_oyun(self):
        yeni_oyun(self.arayuz)