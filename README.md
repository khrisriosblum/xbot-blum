
# X-bot-final (Khris Rios / Blum Recordings)

Bot de X que publica **5 posts/día** (10:00, 13:00, 16:00, 19:00, 22:00) con **±15 min** aleatorio, a partir de un **Excel .xlsx** maestro.

## Reglas clave

- Hoja **Sheet1**: columnas C `Artist`, D `TrackTitle`, E `Mix`, F `YoutubeURL`, G `AppleMusicURL`, H `SpotifyURL`, K `ReleaseDate` (YYYY-MM-DD).
- Hoja **Soundcloud**: columnas A `Title`, B `SoundcloudURL`, C `ReleaseDate` (YYYY-MM-DD).
- Hoja **SpotifyTops**: B `SpotifyTopsURL`, C `ReleaseDate` (YYYY-MM-DD). (Si tu Excel tuviera la URL en otra columna pero con cabecera `SpotifyTopsURL`, se detecta por nombre).

### Priorización
- **Lanzamientos recientes (≤ 2 días)** salen **primero** en la cola.
- Anti-duplicados: **no repetir** la misma URL durante **70 días**.
- **19:00**: cada **3 días** publica SoundCloud (B), cada **10 días** publica SpotifyTops (B). Si coinciden, **SpotifyTops** tiene prioridad. Si hay recientes en esa hoja, se priorizan.

### Formatos de texto (literal según tu especificación)
- Sheet1 F (YouTube): `Techouse on Youtube For You!` + **3 Sheet1Hashtags** + `Artist` + `TrackTitle` + `Mix` + `YoutubeURL`  
- Sheet1 G (Apple): `Music ON Apple` + **3 SoundcloudHashtags** + `Artist` + `TrackTitle` + `Mix` + `AppleMusicURL`  
- Sheet1 H (Spotify): `Listening Techouse On Spotify` + **3 SpotifyTopsHashtags** + `Artist` + `TrackTitle` + `Mix` + `SpotifyURL`  
- Soundcloud: `Long Sets On My Souncloud` + `SoundcloudURL`  
- SpotifyTops: `Khris Rios Tops 10` + `SpotifyTopsURL`  

**Etiquetas especiales (solo si ≤ 2 días):**
- Sheet1: `#NewMusic #OutNow #Beatport`
- Soundcloud: `#NowPlaying #SoundCloud #DJSet`
- SpotifyTops: `#newcharts #playlist #spotify`

> Nota: respetamos tus cadenas tal cual, incluyendo el caso de Apple con *SoundcloudHashtags* (fue literal en tu briefing).

## Arquitectura

- **FastAPI** web + **APScheduler** en el mismo servicio (Render).
- **Pandas + openpyxl** para leer el Excel cada día (crece con el tiempo).
- **SQLite** para historial/antidup en `/data/bot.db` (usa **Persistent Disk** en Render).
- **Tweepy** para publicar en X. `DRY_RUN=true` evita publicar (modo seguro).

## Despliegue con Render

1. **Crea repo** en GitHub y sube todos los archivos de este proyecto.
2. En Render → New → **Blueprint** → conecta el repo. Render detectará `render.yaml`.
3. En el servicio `x-bot`, añade un **Persistent Disk** (ya viene en `render.yaml`) y pon:
   - `EXCEL_PATH=/data/tracks.xlsx`
   - `DB_PATH=/data/bot.db`
4. Sube tu Excel al disco del servicio. Opciones:
   - En local: monta `render.yaml` y haz `render disks sshfs` (o usa la consola de Render para subir el archivo a `/data`).
   - O arranca con el Excel de ejemplo y luego **sustituye** el archivo por el tuyo.
5. Configura **env vars secretas** de X:
   - `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`
   
   El bot utiliza la **API v2** de X mediante `tweepy.Client.create_tweet()`【290481613596620†L909-L975】,
   por lo que ya **no hace llamadas a la API v1.1** (como `update_status`),
   restringida a planes de pago en 2025. No es necesario un Bearer Token
   adicional siempre y cuando suministres las cuatro credenciales de usuario;
   Tweepy usará OAuth 1.0a con contexto de usuario para firmar las
   peticiones. Asegúrate de que tu App en el portal de desarrolladores tenga
   permisos de escritura y esté asociada a un proyecto para habilitar el
   endpoint de publicación【187664688831490†L89-L94】.
6. Inicialmente deja `DRY_RUN=true` y mira los logs en Render.
7. Visita `/health`, `/queue`, `/history` para comprobar.

## Local (opcional)

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Estructura

```
app/
  excel_loader.py   # lee Excel y produce candidatos
  queue_manager.py  # selección por slot (prioriza recientes + reglas 19:00)
  poster.py         # publica en X (tweepy v2), respeta wait de 15s
  scheduler.py      # planifica horas diarias con ±15m y jobs one-shot
  storage.py        # SQLite + historial
  settings.py       # configuración via env
  hashtags.py       # listas de hashtags
  main.py           # FastAPI
data/
  tracks.xlsx       # ejemplo de estructura (vacío con cabeceras)
Dockerfile
render.yaml
requirements.txt
.env.example
```

## Importante

- El **jitter** es *±15 min reales* (generamos horas concretas cada día).
- Si no hay candidatos por antidup/reciente, se hace fallback a cualquier Sheet1; si sigue sin haber, salta el slot (queda en `runs` con `skipped`).
- Si usas API oficial de X, recuerda que Tweepy requiere **acceso de escritura** (user context).

---

© 2025 Khris Rios / Blum Recordings
