# engine/turn_manager/desteden_cek.py

from core.game_state import GameState
from log import logger

@logger.log_function
def desteden_cek(game, oyuncu_index):
    """
    Sırası gelen oyuncunun desteden taş çekmesini sağlar.
    """
    if not (game.oyun_durumu == GameState.NORMAL_TUR and game.sira_kimde_index == oyuncu_index):
        return False
    
    oyuncu = game.oyuncular[oyuncu_index]
    tas = game.deste.tas_cek()
    
    if tas:
        # Başarılı çekme
        oyuncu.tas_al(tas)
        game.turda_tas_cekildi[oyuncu_index] = True
        game.oyun_durumu = GameState.NORMAL_TAS_ATMA
        oyuncu.el_sirala()
        
        # YENİ EKLENEN KISIM: Yeni tur başladığı için ana hamle bayrağını sıfırla
        game.oyuncu_hamle_yapti[oyuncu_index] = False
        
        return True
    else:
        # KRİTİK DÜZELTME: Deste boşsa (tas None döndüyse), oyun sonlanır.
        # Bu, son taşı çeken oyuncunun hamlesini bitirdikten sonraki oyuncunun sırasıdır.
        if not game.deste.taslar:
            game.oyun_durumu = GameState.BITIS
            game.kazanan_index = None # Deste bittiği için kazanan yok
            logger.info("Deste boşken sırası gelen oyuncu taş çekemediği için oyun sonlandırılıyor.")
            return False # Çekme işlemi gerçekleşmedi
            
    return False