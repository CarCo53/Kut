# ai/strategies/degerlendirme_stratejisi/tas_degerlendir.py
from log import logger
from itertools import combinations
from rules.rules_manager import Rules
from ai.strategies.planlama_stratejisi.eli_analiz_et import eli_analiz_et
# YENİ IMPORT: El potansiyelini puanlayan heuristik fonksiyon
from ai.strategies.degerlendirme_stratejisi._eli_puanla import _eli_puanla

@logger.log_function
def tas_degerlendir(ai_player, game, atilan_tas):
    # Kural 1: Açılmış per'e işleme
    if game.acilmis_oyuncular[ai_player.index]:
        for per_idx, per in enumerate(game.acilan_perler[ai_player.index]):
            if Rules.islem_dogrula(per, atilan_tas):
                logger.info(f"AI {ai_player.isim} açılmış perine taş eklemek için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
                return True
    else:
        # A. Anlık Gelişim Analizi için geçici el oluşturulur
        mevcut_el = ai_player.el
        gecici_el = ai_player.el + [atilan_tas]
        gecici_el_analizi = eli_analiz_et(gecici_el)
        
        # Kural 2: GÖREVİ TAMAMLAMA (Oyun bitirme veya el açma)
        if any(Rules.per_dogrula(list(kombo), game.mevcut_gorev) for kombo in gecici_el_analizi['seriler'] + gecici_el_analizi['uc_taslilar'] + gecici_el_analizi['dort_taslilar'] + gecici_el_analizi['ciftler']):
            logger.info(f"AI {ai_player.isim} görevi tamamlamak için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
            return True
        
        # Kural 3: ATILAN TAŞ, HEMEN 3'LÜ VEYA 4'LÜ GEÇERLİ BİR PER OLUŞTURMALI
        yeni_per_bulundu = False
        for boyut in [3, 4]:
            for kombo in combinations(gecici_el, boyut):
                if atilan_tas in kombo:
                    if Rules.genel_per_dogrula(list(kombo)):
                        logger.info(f"AI {ai_player.isim} en az {boyut}'lu geçerli per oluşturduğu için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
                        yeni_per_bulundu = True
                        break 
            if yeni_per_bulundu:
                return True
        
        # YENİ KURAL 4: PUAN/POTANSİYEL ARTIŞI KONTROLÜ (Daha esnek strateji)
        # Bu kural, oyunun ortalarındaki değerli ancak kritik olmayan taşları almayı sağlar.
        mevcut_el_puan = _eli_puanla(mevcut_el)
        yeni_el_puan = _eli_puanla(gecici_el)
        
        puan_farki = yeni_el_puan - mevcut_el_puan
        
        # Eşik değeri: 40 puan, 2 adet 2'li potansiyeli anında tamamlamak (2 * 12 = 24, +10 Eşleşme, vb.) gibi bir potansiyel artışına denk gelir.
        if puan_farki > 40: 
            logger.info(f"AI {ai_player.isim} atılan taşı yüksek potansiyel artışı ({puan_farki}) nedeniyle alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
            return True


    logger.info(f"AI {ai_player.isim} atılan taşı değerlendiriyor. Almadı.")
    return False