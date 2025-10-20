# gui/buttons/el_ac.py
from log import logger

@logger.log_function
def el_ac(arayuz):
    # DÜZELTME: GUI seviyesindeki gereksiz kontrol kaldırıldı, motor kontrolü yeterli.
    
    secili_idler = arayuz.secili_tas_idler
    if not secili_idler:
        arayuz.statusbar.guncelle("Lütfen açmak için taş seçin.")
        return
    sonuc = arayuz.oyun.el_ac(0, secili_idler)
    
    if sonuc.get("status") == "success":
        arayuz.secili_tas_idler = []
        # game.oyuncu_hamle_yapti'ye bakarak hangi mesajı vereceğimizi bulalım.
        oyuncu_index = 0
        if arayuz.oyun.oyuncu_hamle_yapti[oyuncu_index]: 
             # İlk el açılışı yapıldıysa (oyuncu_hamle_yapti = True olduysa)
             arayuz.statusbar.guncelle("Görevi başarıyla açtınız. Lütfen sırayı bitirmek için bir taş atın.")
        else:
             # Sonraki turlarda el açıldıysa (sınırsız hamle)
             arayuz.statusbar.guncelle("Per başarıyla açıldı! Tekrar açmaya/işlemeye devam edebilir veya taş atabilirsiniz.")

    elif sonuc.get("status") == "joker_choice_needed":
        options = sonuc["options"]
        joker = sonuc["joker"]
        secilen_taslar = sonuc["secilen_taslar"]
        
        # YENİ KRİTİK MANTIK: Tek seçenek varsa otomatik seç
        if len(options) == 1:
            secilen_deger = options[0]
            # Pencere açmaya gerek yok, direkt işlemi yap
            arayuz.oyun.el_ac_joker_ile(0, secilen_taslar, joker, secilen_deger)
            arayuz.secili_tas_idler = []
            
            # Başarılı el açma mesajını tekrar gönder
            oyuncu_index = 0
            if arayuz.oyun.oyuncu_hamle_yapti[oyuncu_index]:
                 arayuz.statusbar.guncelle("Joker otomatik seçildi. Görevi başarıyla açtınız. Lütfen sırayı bitirmek için bir taş atın.")
            else:
                 arayuz.statusbar.guncelle("Joker otomatik seçildi. Per başarıyla açıldı! Tekrar açmaya/işlemeye devam edebilir veya taş atabilirsiniz.")
            
        elif len(options) > 1:
            # Birden fazla seçenek varsa, pop-up'ı aç
            arayuz.joker_secim_penceresi_ac(options, joker, secilen_taslar)
            
        else:
             # Seçenek yoksa (Bu durum JokerManager'da engellenmeli ama yine de güvenlik için)
             arayuz.statusbar.guncelle(sonuc.get("message", "Joker için uygun seçenek bulunamadı."))
    else:
        # Motorun döndürdüğü 'fail' mesajını kullan
        arayuz.statusbar.guncelle(sonuc.get("message", "Geçersiz per!"))
        
    arayuz.arayuzu_guncelle()