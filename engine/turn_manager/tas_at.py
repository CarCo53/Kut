# engine/turn_manager/tas_at.py
from core.game_state import GameState, AtilanTasDegerlendirici
from log import logger

@logger.log_function
def tas_at(game, oyuncu_index, tas_id):
    """
    Oyuncunun elindeki bir taşı yere atmasını sağlar.
    """
    oyuncu = game.oyuncular[oyuncu_index]
    
    # Yeni mantık için deste boş mu kontrolü
    is_deck_empty = not game.deste.taslar
    
    # 1. Eli bitirerek kazanma (Düz Okey)
    if not oyuncu.el and game.acilmis_oyuncular[oyuncu_index]:
        game.oyun_durumu = GameState.BITIS
        game.kazanan_index = oyuncu_index
        return True
    
    # 2. Oyun Durumu Kontrolleri
    if game.oyun_durumu not in [GameState.ILK_TUR, GameState.NORMAL_TAS_ATMA]:
        return False
    if oyuncu_index != game.sira_kimde_index:
        return False
        
    atilan_tas = oyuncu.tas_at(tas_id)
    if atilan_tas:
        
        game.atilan_taslar.append(atilan_tas)
        
        # 3. Eli bitirerek kazanma (Okey atma)
        if game.acilmis_oyuncular[oyuncu_index] and not oyuncu.el:
            game.oyun_durumu = GameState.BITIS
            game.kazanan_index = oyuncu_index
            return True

        game.oyuncu_hamle_yapti = [False] * len(game.oyuncular)

        # KRİTİK EKLENTİ: Eğer desteden son taşı çeken oyuncu taşını attıysa, oyun biter.
        # atilan_tas_degerlendirme aşamasına geçmeye gerek yoktur.
        if is_deck_empty:
            game.oyun_durumu = GameState.BITIS
            game.kazanan_index = None # Elini bitirmediği sürece kazanan yok (puanlama yapılacak)
            logger.info("Deste boşken son taşı atan oyuncunun hamlesi tamamlandığı için oyun sonlandırılıyor.")
            return True # Taş atıldı, oyun bitti

        # 4. Normal Akış: Taş değerlendirme
        game.oyun_durumu = GameState.ATILAN_TAS_DEGERLENDIRME
        game.atilan_tas_degerlendirici = AtilanTasDegerlendirici(oyuncu_index, len(game.oyuncular))
        game.turda_tas_cekildi[oyuncu_index] = False
        return True
    return False