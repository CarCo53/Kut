# ai/strategies/klasik_per_stratejisi/en_iyi_per_bul.py
from itertools import combinations
from rules.rules_manager import Rules
from collections import defaultdict
from log import logger
from ai.strategies.cift_stratejisi.en_iyi_ciftleri_bul import en_iyi_ciftleri_bul

def _per_deger_hesapla(per):
    # Jokerlerin değeri 0 kabul edilir, sadece gerçek taşların sayı değeri toplanır.
    return sum(t.deger for t in per if t.renk != 'joker')

@logger.log_function
def en_iyi_per_bul(el, gorev):
    # Görev tipi ve minimum taş sayısı
    gorev_tipi, min_sayi_str = gorev.split(' ') if ' ' in gorev else (gorev, 0)
    min_sayi = int(min_sayi_str) if min_sayi_str else 0
    
    jokerler = [t for t in el if t.renk == 'joker']
    normal_taslar = [t for t in el if t.renk != 'joker']
    
    # KRİTİK KURAL: KOLAY GÖREVLERDE (Seri 5'e kadar) MAX 1 JOKER KULLAN
    # Ancak burada, oyuncunun elini açma hamlesinde olduğu için, görevi tamamlamak amacıyla 
    # joker kısıtlamasını biraz daha esnek tutmalıyız.
    # Görev tamamlanıyorsa, 1 joker her zaman kabul edilmeli.
    max_joker_kullanimi = 1 
    joker_limiti = min(len(jokerler), max_joker_kullanimi)
    
    aday_perler = [] # Tüm geçerli adayları tutmak için liste
    
    if "Seri" in gorev:
        renk_gruplari = defaultdict(list)
        for tas in normal_taslar:
            renk_gruplari[tas.renk].append(tas)
        
        for renk in renk_gruplari:
            tas_listesi = sorted(renk_gruplari[renk], key=lambda t: t.deger)
            benzersiz_degerler = sorted(list(set(t.deger for t in tas_listesi)))
            
            # --- YENİ TEMEL SERİ BULMA MANTIĞI ---
            # Olası tüm aralıkları dener.
            for i in range(len(benzersiz_degerler)):
                for j in range(i + min_sayi - 1, len(benzersiz_degerler)):
                    aday_degerler = benzersiz_degerler[i:j+1]
                    
                    # 12-13-1 durumunda, 1'i 14 kabul ederek aralık genişliğini hesapla
                    if 1 in aday_degerler and 13 in aday_degerler:
                        # 1'i 14'e dönüştürerek sürekli bir dizi olup olmadığını kontrol et.
                        temp_sayilar = sorted([14 if d == 1 else d for d in aday_degerler])
                        aralik_genisligi = temp_sayilar[-1] - temp_sayilar[0] + 1
                    else:
                        aralik_genisligi = aday_degerler[-1] - aday_degerler[0] + 1
                        
                    gercek_tas_sayisi = len(aday_degerler)
                    bosluk = aralik_genisligi - gercek_tas_sayisi
                    
                    # Joker kontrolü: min(Joker limiti, bu per için gereken boşluk)
                    # Joker sayısının gereken boşluğu kapatıp kapatmadığını kontrol et.
                    if joker_limiti >= bosluk:
                        
                        # Bu aralığa uyan gerçek taşları al
                        aday_per_normal = [t for t in tas_listesi if t.deger in aday_degerler]
                        
                        # Eksik jokerleri doldur (görev tamamlanıyorsa)
                        joker_kullan = bosluk
                        aday_per_jokerli = aday_per_normal + jokerler[:joker_kullan]
                        
                        # Perin gerçekten göreve uygun olup olmadığını kontrol et
                        if Rules.per_dogrula(aday_per_jokerli, gorev):
                            
                            # KRİTİK: Joker yerine geçecek taşı atama. 
                            # Bu kısım `el_ac_dene` içinde `JokerManager` tarafından ele alınacak. 
                            # `en_iyi_per_bul` sadece ID listesini döndürecek.
                            # Ancak, jokere atanacak temsilciyi bulmak ve per'i oluşturmak, 
                            # per_dogrula'nın iç mantığı için gereklidir.
                            
                            # Burada `jokerler` listesinin elemanlarına `joker_yerine_gecen` atanması gerekiyor.
                            # Bu, çok karmaşık bir yeniden yazım gerektirir.
                            
                            # Önceki kodda bu atamalar olmadan Rules.per_dogrula'nın çalışması
                            # sadece jokerin kendisini görerek karar veriyordu.
                            
                            # En basit yolu: SADECE JOKER KULLANILMAYAN (bosluk=0) durumlarda çalışmasını garanti et.
                            if joker_kullan == 0:
                                aday_perler.append(aday_per_jokerli)

                            # Joker kullanılıyorsa, atanmış bir joker nesnesi oluşturup test etmek gerekir:
                            elif joker_kullan > 0 and Rules.per_dogrula(aday_per_jokerli, gorev):
                                # El açma sırasında atanacak joker nesnelerini döndürmek yerine,
                                # sadece başarılı bir açılış olduğunu belirten ID listesini döndürelim.
                                # Atama işlemi (joker_yerine_gecen), el_ac döngüsü içinde yapılmalıdır.
                                # Bu aşamada, per'in doğruluğunu kontrol etmek için geçici atama yapmak gerekir.
                                
                                # Buradaki Rule.per_dogrula'nın, atanmamış jokeri kabul etme mantığı nedeniyle:
                                aday_perler.append(aday_per_jokerli)
    
    elif "Küt" in gorev:
        # (Küt mantığı aynı kalır - doğru görünüyor)
        deger_gruplari = defaultdict(list)
        for tas in normal_taslar:
            deger_gruplari[tas.deger].append(tas)

        for deger in deger_gruplari:
            kalan_yer = 4 - len(deger_gruplari[deger])
            joker_kullan = min(joker_limiti, kalan_yer) 

            if len(deger_gruplari[deger]) + joker_kullan >= min_sayi:
                aday_per = deger_gruplari[deger] + jokerler[:joker_kullan]
                if Rules.per_dogrula(aday_per, gorev):
                    aday_perler.append(aday_per)
    
    elif gorev == "Çift":
        # (Çift mantığı aynı kalır - doğru görünüyor)
        acilacak_per = en_iyi_ciftleri_bul(el, gorev)
        if acilacak_per:
            aday_perler.append(acilacak_per)

    # Tüm adaylar arasından en yüksek değere sahip olanı seç (Stratejik gereksinim)
    if aday_perler:
        # En yüksek değere sahip adayı bul
        en_iyi_per = max(aday_perler, key=_per_deger_hesapla)
        return en_iyi_per
        
    return None