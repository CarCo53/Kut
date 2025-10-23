# ai/strategies/planlama_stratejisi/en_akilli_ati_bul.py
from log import logger
from rules.rules_manager import Rules # Yeni import

@logger.log_function
def en_akilli_ati_bul(el, el_analizi, game): # Argüman atilan_taslar yerine game olarak değiştirildi
    
    jokersiz_el = [t for t in el if t.renk != "joker"]
    if not jokersiz_el:
        # El sadece jokerlerden oluşuyorsa, en yüksek değerli jokeri at
        return max(el, key=lambda t: t.deger or 0)
        
    en_dusuk_puan = float('inf')
    en_kotu_tas = None

    # KORUMA LİSTESİ: El açmak için kullanılan potansiyel tüm taşları korur.
    koruma_listesi_idler = set()
    for per_list in [el_analizi["seriler"], el_analizi["uc_taslilar"], el_analizi["dort_taslilar"], el_analizi["ciftler"]]:
        for per in per_list:
            for tas in per:
                koruma_listesi_idler.add(tas.id)
                
    joker_sayisi = sum(1 for t in el if t.renk == 'joker')

    # AI Oyuncunun index'ini elindeki taş listesini kullanarak bul
    ai_player_index = next((i for i, p in enumerate(game.oyuncular) if p.el == el), None)
    
    # ---------------------------------------------------------------------
    # KRİTİK KORUMA: EL AÇILDIKTAN SONRA MASAYLA ETKİLEŞİM İÇİN KORUMA
    # ---------------------------------------------------------------------
    if ai_player_index is not None and game.acilmis_oyuncular[ai_player_index]:
        
        for per_sahibi_idx, perler in game.acilan_perler.items():
            for per in perler:
                
                # A. Joker Değiştirme Koruması
                for per_tasi in per:
                    if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                        yerine_gecen = per_tasi.joker_yerine_gecen
                        eslesen_tas = next((t for t in jokersiz_el if t.renk == yerine_gecen.renk and t.deger == yerine_gecen.deger), None)
                        if eslesen_tas:
                            koruma_listesi_idler.add(eslesen_tas.id)
                            logger.debug(f"Joker Değiştirme Koruması: {eslesen_tas.renk}_{eslesen_tas.deger} koruma listesine eklendi.")

                # B. İşleme Yapma Koruması
                for tas in jokersiz_el:
                    if Rules.islem_dogrula(per, tas):
                        koruma_listesi_idler.add(tas.id)
                        logger.debug(f"İşleme Yapma Koruması: {tas.renk}_{tas.deger} koruma listesine eklendi.")
    # ---------------------------------------------------------------------
    
    # 3. YÜKSEK GÜVENLİK KORUMASI: JOKERLE TAMAMLANABİLİR POTANSİYEL TAŞLAR
    potansiyel_seri_kut_taslari = set()
    for per_cifti in el_analizi["ikili_potansiyeller"]["seri"] + el_analizi["ikili_potansiyeller"]["kut"]:
         for t in per_cifti:
              potansiyel_seri_kut_taslari.add(t.id)

    # En kötü atılacak taş listesi (Potansiyel puanı en düşük olanlar)
    en_kotu_adaylar = []

    for tas in jokersiz_el:
        # Puan, sadece potansiyel ve koruma için hesaplanır. (Sayı değeri DAHİL DEĞİLDİR)
        puan = 0 
        
        # Koruma Puanları (Çok yüksek, atılmasını engeller)
        if tas.id in koruma_listesi_idler:
            puan += 5000 
        
        if tas.id in potansiyel_seri_kut_taslari and joker_sayisi > 0:
            puan += 5000 
        
        # 4. MEVCUT BASİT POTANSİYEL PUANLAMA (Düşük = Atılmaya uygun)
        for diger_tas in el:
            if tas.id != diger_tas.id and diger_tas.renk != 'joker':
                # Aynı sayı (Küt potansiyeli)
                if tas.deger == diger_tas.deger: 
                    puan += 10
                # Ardışık (Seri potansiyeli)
                if tas.renk == diger_tas.renk:
                    fark = abs(tas.deger - diger_tas.deger)
                    if fark == 1: puan += 12
                    elif fark == 2: puan += 6
        
        if puan < en_dusuk_puan:
            en_dusuk_puan = puan
            en_kotu_adaylar = [tas]
        elif puan == en_dusuk_puan:
            en_kotu_adaylar.append(tas)

    # ---------------------------------------------------------------------
    # KRİTİK ADIM: TIE-BREAKER (En düşük potansiyelli taşlar arasından en yüksek değerli olanı at)
    # ---------------------------------------------------------------------
    if en_kotu_adaylar:
        # En düşük puana sahip adaylar arasından en yüksek değere (ceza puanına) sahip olanı seç.
        return max(en_kotu_adaylar, key=lambda t: t.deger)
        
    # Son çare: Joker olmayan herhangi bir taşı at (Bu kısma gelmemesi gerekir).
    return jokersiz_el[0]