# Telegram Üzenetmásoló Alkalmazás

Ez az alkalmazás egy Docker konténerként telepíthető Flask webszerverrel rendelkezik, amely lehetővé teszi a felhasználók számára, hogy üzeneteket és médiát másoljanak egyik Telegram csatornáról a másikra, felhasználói ügynökként működve, anélkül, hogy a továbbítási címke megjelenne.

## Funkciók

*   **Flask Webszerver**: Könnyen használható webes felület a konfigurációhoz és az alkalmazás állapotának monitorozásához.
*   **Telegram API Integráció (Telethon)**: Felhasználói ügynökként működik, nem botként, így a másolt üzenetek nem tartalmaznak továbbítási címkét.
*   **Konfigurálható Csatornák**: Válassza ki a forrás és cél Telegram csatornákat egy drop-down listából.
*   **Perzisztens Konfiguráció**: Az API adatok és csatorna beállítások mentésre kerülnek, így az alkalmazás újraindításakor is megmaradnak.
*   **Docker Konténer**: Egyszerű telepítés és futtatás bármilyen Docker környezetben.

## Telepítés és Futtatás Dockerrel

Kövesse az alábbi lépéseket az alkalmazás telepítéséhez és futtatásához Docker konténerként.

### 1. Előfeltételek

*   **Docker**: Győződjön meg róla, hogy a Docker telepítve van a rendszerén. Ha nincs, kövesse a hivatalos Docker telepítési útmutatót: [Docker telepítése](https://docs.docker.com/get-docker/)

### 2. API ID és API Hash megszerzése

Az alkalmazás futtatásához szüksége lesz a Telegram API ID-jére és API Hash-jére:

1.  Látogasson el a [my.telegram.org](https://my.telegram.org) oldalra.
2.  Jelentkezzen be a telefonszámával.
3.  Kattintson az "API development tools" menüpontra.
4.  Hozzon létre egy új alkalmazást (bármilyen adatot megadhat, ami szükséges).
5.  Jegyezze fel az `App api_id` és `App api_hash` értékeket.

### 3. Az alkalmazás letöltése

Klónozza ezt a repository-t (vagy töltse le a forráskódot):

```bash
git clone <repository_url>
cd telegram_copier
```

### 4. Docker Image építése

Navigáljon az alkalmazás gyökérkönyvtárába (ahol a `Dockerfile` található), majd építse fel a Docker image-et:

```bash
docker build -t telegram-copier .
```

Ez a parancs letölti a szükséges függőségeket és elkészíti az alkalmazás Docker image-ét `telegram-copier` néven.

### 5. Docker Konténer Futtatása

Futtassa a Docker konténert a következő paranccsal:

```bash
docker run -d -p 5000:5000 --name telegram-copier-app telegram-copier
```

*   `-d`: A konténer a háttérben fog futni.
*   `-p 5000:5000`: A konténer 5000-es portját a gazdagép 5000-es portjára képezi le. Ezen a porton lesz elérhető a Flask webszerver.
*   `--name telegram-copier-app`: A konténernek ad egy könnyen azonosítható nevet.
*   `telegram-copier`: Az előző lépésben létrehozott Docker image neve.

**Fontos**: A Telethon munkamenet fájl és a konfigurációs fájl a konténeren belül a `/app/data` könyvtárban tárolódik. Ha szeretné, hogy ezek az adatok perzisztensek legyenek a konténer újraindítása vagy törlése után is, akkor csatlakoztasson egy volume-ot:

```bash
docker run -d -p 5000:5000 -v telegram_copier_data:/app/data --name telegram-copier-app telegram-copier
```

Itt a `telegram_copier_data` egy Docker volume, amely a `/app/data` könyvtárhoz lesz csatlakoztatva.

### 6. Az Alkalmazás Konfigurálása

Miután a konténer fut, nyissa meg a webböngészőjét, és navigáljon a következő címre:

```
http://localhost:5000
```

1.  **Beállítások oldal**: Kattintson a "Beállítások" menüpontra, vagy navigáljon a `http://localhost:5000/settings` címre.
2.  **API adatok megadása**: Adja meg a 2. lépésben megszerzett Telegram API ID-t és API Hash-t. Mentse el a beállításokat.
3.  **Telegram Bejelentkezés**: Térjen vissza a főoldalra (`http://localhost:5000`). Adja meg a telefonszámát nemzetközi formátumban (pl. `+36301234567`), majd kattintson a "Bejelentkezés" gombra. A Telegram elküld egy ellenőrző kódot. Adja meg ezt a kódot az alkalmazásban.
4.  **Csatornák kiválasztása**: Miután sikeresen bejelentkezett, térjen vissza a "Beállítások" oldalra. Ekkor a forrás és cél csatornák kiválasztásához egy drop-down lista fog megjelenni, amely az összes elérhető csatornát tartalmazza. Válassza ki a kívánt csatornákat, majd mentse el a beállításokat.
5.  **Másolás Indítása**: Térjen vissza a főoldalra, és kattintson a "Másolás Indítása" gombra. Az alkalmazás elkezdi figyelni a forrás csatornát, és másolja az új üzeneteket a cél csatornára.

## Alkalmazás Leállítása és Törlése

### Konténer leállítása

```bash
docker stop telegram-copier-app
```

### Konténer törlése

```bash
docker rm telegram-copier-app
```

### Image törlése

```bash
docker rmi telegram-copier
```

### Volume törlése (ha használt)

```bash
docker volume rm telegram_copier_data
```

## Fejlesztés

Ha fejleszteni szeretné az alkalmazást, a következő fájlok relevánsak:

*   `app.py`: Flask webszerver logika.
*   `config.py`: Konfigurációkezelés.
*   `telethon_client.py`: Telethon kliens inicializálása és Telegram interakciók.
*   `message_copier.py`: Üzenetmásolási logika.
*   `templates/`: HTML sablonok (Jinja2).
*   `static/`: CSS és JavaScript fájlok.
*   `requirements.txt`: Python függőségek.
*   `Dockerfile`: Docker build konfiguráció.

## Hibaelhárítás

*   **`Cannot connect to the Docker daemon`**: Győződjön meg róla, hogy a Docker fut a rendszerén (`sudo systemctl start docker`).
*   **`telethon.errors.rpc_error_list.ApiIdInvalidError`**: Ellenőrizze, hogy az API ID és API Hash helyes-e a `my.telegram.org` oldalon.
*   **`telethon.errors.rpc_error_list.PhoneCodeInvalidError`**: Győződjön meg róla, hogy a Telegram által küldött ellenőrző kódot helyesen adta meg.
*   **Csatornák nem jelennek meg**: Győződjön meg róla, hogy sikeresen bejelentkezett a Telegramba, és a megadott API ID/Hash helyes.

---
