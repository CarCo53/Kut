# gui/game_loop/ai_oynat.py

from core.game_state import GameState
from ai.ai_player import AIPlayer
from log import logger
from rules.rules_manager import Rules 

def ai_oynat(arayuz):
    oyun = arayuz.oyun
    
    # Oyun bittiğinde yapılacak tek şey arayüzü güncellemek ve çıkmak.
    if oyun.oyun_bitti_mi(): 
        # KRİTİK DÜZELTME: Oyun zaten bitti ve arayüzü güncelleme (puan hesaplama) 
        # işlemi oyunu sonlandıran hamlenin hemen ardından yapıldı.
        # Burada tekrar çağırmak, sadece puan hesaplamasını tekrarlar. Bu satır kaldırılmıştır.
        # arayuz.arayuzu_guncelle() 
        return

    if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
        degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
        if isinstance(oyun.oyuncular[degerlendiren_idx], AIPlayer):
            ai_oyuncu = oyun.oyuncular[degerlendiren_idx]
            atilan_tas = oyun.atilan_taslar[-1]
            if ai_oyuncu.atilan_tasi_degerlendir(oyun, atilan_tas):
                oyun.atilan_tasi_al(degerlendiren_idx)
            else:
                oyun.atilan_tasi_gecti()
            
            if oyun.oyun_bitti_mi(): # Hamleden sonra biterse çık
                arayuz.arayuzu_guncelle()
                return

            arayuz.arayuzu_guncelle()

    elif oyun.oyun_durumu in [GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
        sira_index = oyun.sira_kimde_index
        if sira_index != 0 and isinstance(oyun.oyuncular[sira_index], AIPlayer):
            ai_oyuncu = oyun.oyuncular[sira_index]

            if oyun.oyun_durumu == GameState.NORMAL_TUR:
                oyun.desteden_cek(sira_index)
                if oyun.oyun_bitti_mi(): # Taş çekildi ve bitti
                    arayuz.arayuzu_guncelle()
                    return
                arayuz.arayuzu_guncelle()

            elini_acti_mi = oyun.acilmis_oyuncular[sira_index]

            # --- İKİNCİL HAMLE DÖNGÜSÜ ---
            action_performed_in_loop = True
            while action_performed_in_loop:
                action_performed_in_loop = False

                # 1. GÖREVİ AÇMA
                if not elini_acti_mi:
                    # El açma mantığı buraya entegre edilir (önceki düzeltmedeki gibi)
                    ac_kombo = ai_oyuncu.ai_el_ac_dene(oyun)
                    if ac_kombo:
                        result = oyun.el_ac(sira_index, ac_kombo)

                        # JOKER SEÇİMİ OTOMATİKLEŞTİRME DÜZELTMESİ (Burada korundu)
                        if result and result.get('status') == 'joker_choice_needed':
                            secilen_taslar = result["secilen_taslar"]
                            joker = result["joker"]
                            secilen_deger = None
                            
                            for option in result["options"]:
                                joker.joker_yerine_gecen = option 
                                if Rules.per_dogrula(secilen_taslar, oyun.mevcut_gorev):
                                    secilen_deger = option
                                    break
                                joker.joker_yerine_gecen = None
                            
                            if secilen_deger:
                                logger.info(f"AI Otomatik Joker Seçimi: El açmak için jokerin yerine {secilen_deger.renk}_{secilen_deger.deger} seçildi.")
                                joker.joker_yerine_gecen = secilen_deger 
                                oyun.el_ac_joker_ile(sira_index, secilen_taslar, joker, secilen_deger)
                                result = None
                            else:
                                logger.error("AI Otomatik Joker Seçimi Başarısız: Geçerli joker seçeneği bulunamadı.")
                                result['status'] = 'fail'
                        
                        if result is None or (result and result.get('status') != 'fail'):
                            if oyun.oyun_bitti_mi(): 
                                arayuz.arayuzu_guncelle()
                                return
                            arayuz.arayuzu_guncelle()
                            elini_acti_mi = True
                            action_performed_in_loop = True
                            continue 
                       
                # 2. İŞLEME / JOKER DEĞİŞTİRME 
                # (Kural: İlk el açma hamlesinin yapıldığı turda işleme yapılamaz. Ancak burada AI olduğu için, 
                # sadece el açma durumu ile aynı turda olmadığını kontrol etmek yeterlidir)
                if elini_acti_mi and oyun.ilk_el_acan_tur.get(sira_index, -1) < oyun.tur_numarasi:
                    islem_hamlesi = ai_oyuncu.ai_islem_yap_dene(oyun)
                    if islem_hamlesi:
                        if islem_hamlesi.get("action_type") == "joker_degistir":
                            oyun.joker_degistir(sira_index, islem_hamlesi['sahip_idx'], islem_hamlesi['per_idx'], islem_hamlesi['tas_id'])
                        elif islem_hamlesi.get("action_type") == "islem_yap":
                            oyun.islem_yap(sira_index, islem_hamlesi['sahip_idx'], islem_hamlesi['per_idx'], islem_hamlesi['tas_id'])
                        
                        if oyun.oyun_bitti_mi(): 
                            arayuz.arayuzu_guncelle()
                            return
                        arayuz.arayuzu_guncelle()
                        action_performed_in_loop = True
                        continue 

                # 3. YENİ EL AÇMA (Eli açık oyuncu için)
                # ... (Kod tekrarları kaldırıldı, yukarıdaki mantık yeterli) ...
                
                # Sadece 2. hamle olarak açma denemesini kaldırdım, çünkü 
                # 1. GÖREVİ AÇMA zaten ilk açılışı kapsıyor, 
                # ve 2. İŞLEME/JOKER DEĞİŞTİRME sonrasında döngü tekrar başlar.

            # --- DÖNGÜ SONU ---
            
            # 4. TAŞ ATMA 
            if ai_oyuncu.el and oyun.oyun_durumu == GameState.NORMAL_TAS_ATMA:
                tas_to_discard = ai_oyuncu.karar_ver_ve_at(oyun)
                if tas_to_discard:
                    oyun.tas_at(sira_index, tas_to_discard.id)
                else:
                    oyun.oyun_durumu = GameState.BITIS
                    oyun.kazanan_index = sira_index
            
            # Son hamleden sonra oyun biterse çık
            if oyun.oyun_bitti_mi():
                arayuz.arayuzu_guncelle()
                return
                
            arayuz.arayuzu_guncelle() # Son atma hamlesi için arayüzü güncelle
            
    # KRİTİK FİNAL KONTROLÜ: Oyun bitmediyse (yani yukarıdaki return'lerden hiçbirine girilmediyse), 
    # bir sonraki AI turunu planla. Bu, Tkinter'ın after döngüsünün durmasını sağlar.
    if not oyun.oyun_bitti_mi():
        arayuz.pencere.after(750, arayuz.ai_oynat)