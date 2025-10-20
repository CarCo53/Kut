# gui/buttons/butonlari_guncelle.py

from core.game_state import GameState
from log import logger
import tkinter as tk

@logger.log_function
def butonlari_guncelle(manager, oyun_durumu):
    """
    Oyun durumuna göre ButtonManager'daki butonların durumunu günceller.
    """
    # 1. Tüm butonları devre dışı bırak
    for btn in manager.butonlar.values():
        btn.config(state=tk.DISABLED)
    
    # 2. Oyun bitti mi kontrolü
    if oyun_durumu == GameState.BITIS:
         manager.butonlar["yeni_oyun"].config(state=tk.NORMAL)
         return
         
    oyun = manager.arayuz.oyun
    sira_bende = oyun.sira_kimde_index == 0
    
    # 3. Oyun durumuna göre butonları etkinleştir
    if oyun_durumu == GameState.ILK_TUR and sira_bende:
        manager.butonlar["tas_at"].config(state=tk.NORMAL)
    elif oyun_durumu == GameState.NORMAL_TUR and sira_bende:
        manager.butonlar["el_ac"].config(state=tk.NORMAL)
        manager.butonlar["desteden_cek"].config(state=tk.NORMAL)
    elif oyun_durumu == GameState.NORMAL_TAS_ATMA and sira_bende:
        manager.butonlar["tas_at"].config(state=tk.NORMAL)
        manager.butonlar["el_ac"].config(state=tk.NORMAL)
        
    elif oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
        degerlendiren_ben_miyim = oyun.atilan_tas_degerlendirici and oyun.atilan_tas_degerlendirici.siradaki() == 0
        if degerlendiren_ben_miyim:
            # Yerden al butonu kaldırıldığı için sadece "Geç" butonu etkin
            manager.butonlar["gec"].config(state=tk.NORMAL)