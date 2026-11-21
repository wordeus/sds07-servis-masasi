"""İş kuralları katmanı (NFR-16).

Görünümler talep ve kategori sorgularını doğrudan yapmaz; bu paketteki fonksiyonları
çağırır. Kurallar tek yerde olduğu için test edilmesi ve gözden geçirilmesi kolaydır.
Bağımlılık yönü: views -> services -> models. Bu paket views'e, şablonlara veya HTTP
katmanına bağımlı değildir (TC-ARCH-01 bu kuralı denetler).
"""
