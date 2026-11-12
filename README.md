# Viomi V8 Vacuum for Home Assistant

Local control for the **Mi Robot Vacuum-Mop P** (`viomi.vacuum.v8`, STYJ02YM).
No cloud, no Xiaomi account at runtime: Home Assistant talks to the robot over
your LAN using python-miio's legacy miIO protocol.

[Türkçe bölüm aşağıda](#türkçe)

## Features

| Feature | Entity |
|---|---|
| Start, pause, stop, return to dock, locate | `vacuum` |
| Fan speed (silent / standard / medium / turbo) | `vacuum` |
| Clean specific rooms (`viomi_v8.clean_rooms`) | service |
| Water level (low / medium / high) | `select` |
| Cleaning mode (vacuum / vacuum and mop / mop) | `select` |
| Mop pattern (S / Y) | `select` |
| Battery, cleaned area, cleaning time | `sensor` |
| Error text, attached dust bin / water tank | `sensor` (diagnostic) |
| Raw commands (`vacuum.send_command`) | service |

**Not included:** map image, room names, schedules, do-not-disturb, consumable
counters. The v8 does not use MIoT, so none of the MIoT map tooling applies.

## Install

**HACS:** HACS → ⋮ → Custom repositories → add this repo as *Integration* →
download → restart Home Assistant.
**Manual:** copy `custom_components/viomi_v8` into your config's `custom_components/`.

Then: Settings → Devices & services → Add integration → **Viomi V8 Vacuum**.

You need the robot's **IP address** (give it a fixed IP in your router) and its
**32-character token**. The token can be extracted from your Xiaomi account, for
example with the open-source *Xiaomi Cloud Tokens Extractor*. The model reported
by the device must be `viomi.vacuum.v8`.

## Cleaning rooms

```yaml
action: viomi_v8.clean_rooms
target:
  entity_id: vacuum.viomi_v8
data:
  rooms: [10, 13]
  edge: false
```

The v8 does not hand out room names locally. Find the ids by trying them: call
the service with one id at a time (the app and the robot show which room it
heads to). If you re-split rooms in the Mi Home app, rooms get new ids.

## Verification status

Commands come from python-miio's `ViomiVacuum`, the homebridge viomi plugin and
community reports for this exact model. The unit tests check parsing and the
exact commands sent against a fake device. Please report anything that behaves
differently on real hardware, especially:

- the *paused* state (`run_state` 2), and
- the *find* (locate) command.

Debug logging: `logger: logs: custom_components.viomi_v8: debug`.

## Development

`pip install pytest && pytest` runs the tests without Home Assistant installed.

---

# Türkçe

**Mi Robot Vacuum-Mop P** (`viomi.vacuum.v8`, STYJ02YM) için yerel Home Assistant
entegrasyonu. Bulut yok; Home Assistant robotla yerel ağda eski miIO protokolüyle
konuşur.

## Özellikler

- Başlat, duraklat, durdur, şarja dön, süpürgeyi bul (`vacuum`)
- Fan hızı: silent / standard / medium / turbo
- Belirli odaları temizleme: `viomi_v8.clean_rooms` servisi
- Su seviyesi, temizlik modu (süpür / süpür+paspas / paspas), paspas deseni (S / Y)
- Sensörler: pil, temizlenen alan, temizlik süresi, hata metni, takılı hazne
- `vacuum.send_command` ile ham komut

**Yok:** harita görüntüsü, oda isimleri, zamanlayıcı, rahatsız etme modu,
sarf malzemesi sayaçları.

## Kurulum

1. HACS → Özel depolar → bu repoyu *Integration* olarak ekleyin → indirin →
   Home Assistant'ı yeniden başlatın (ya da `custom_components/viomi_v8`
   klasörünü elle kopyalayın).
2. Ayarlar → Cihazlar ve hizmetler → Entegrasyon ekle → **Viomi V8 Vacuum**.
3. Süpürgenin **IP adresini** (router'dan sabit IP verin) ve **32 karakterlik
   token'ını** girin.

## Oda temizliği

```yaml
action: viomi_v8.clean_rooms
target:
  entity_id: vacuum.viomi_v8
data:
  rooms: [10, 13]
```

Oda numaraları yerel olarak okunamıyor. Numaraları tek tek deneyerek bulun:
servisi tek bir numarayla çağırın ve robotun hangi odaya gittiğine bakın.
Mi Home uygulamasında odaları yeniden bölerseniz numaralar değişir.

## Test durumu

Komutlar python-miio, homebridge viomi eklentisi ve bu model için topluluk
raporlarından alındı. Birim testleri ayrıştırmayı ve gönderilen komutları sahte
bir cihazla doğrular. Gerçek cihazda farklı davranış görürseniz bildirin; özellikle
*duraklatıldı* durumu (`run_state` 2) ve *bul* komutu.
