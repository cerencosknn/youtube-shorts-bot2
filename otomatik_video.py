import glob
import os
import os.path
import random
import subprocess
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import imageio_ffmpeg
import yt_dlp

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Senin güncellediğin ve eklediğin tüm hashtag havuzu
HASHTAGLER = [
    # ASMR ve Satisfying
    "asmr",
    "asmrsounds",
    "satisfying",
    "satisfyingvideos",
    "relaxing",
    "tingles",
    "asmreating",
    "foodasmr",
    "crunchyasmr",
    "slimeasmr",
    "oddlysatisfying",
    "asmrcommunity",
    "asmrvideo",
    "asmrsoft",
    "sleepasmr",
    "asmrwhisper",
    "satisfyingasmr",
    "viralasmr",
    "asmrtriggers",
    "relaxingsounds",
    # Komedi ve Genel Mizah
    "komedi",
    "kahkaha",
    "komikvideolar",
    "eğlence",
    "şaka",
    "caps",
    "meme",
    "fails",
    "funnyclips",
    "viralvideo",
    "tiktoktrend",
    "keşfetteyiz",
    "foryou",
    "foryoupage",
    "relatable",
    "dailyfunny",
    "lol",
    "prank",
    "trendvideo",
    "gülmekgaranti",
    "güldürgüldür",
    "güldürgüldürshow",
    "güldürgüldürkomik",
    "komedikesitleri",
    "komiksahneler",
    "showtv",
    "komik",
    "funny",
    "comedy",
    "viral",
    "fyp",
    "keşfet",
    "mizah",
    "memes",
    "funnyvideos",
    "trend",
    "türkkomedi",
    "komikreplikler",
    "televizyonkesitleri",
    "komikanlar",
    "komikshorts",
    "reelskomik",
    # Beyaz Futbol ve Futbol Mizahı
    "beyazfutbol",
    "beyazfutbolkomik",
    "beyaztv",
    "ahmetçakar",
    "sinanengin",
    "rasimozan",
    "futbolmizahı",
    "futbolcaps",
    "türkmiti",
]


def dikey_shorts_yap(girdi_yolu, cikti_yolu="islenmis_shorts.mp4"):
  print(
      "Video, ekranı tamamen dolduran büyük boyutta ve telif koruması için"
      " işleniyor..."
  )
  ffmpeg_yolu = imageio_ffmpeg.get_ffmpeg_exe()

  komut = [
      ffmpeg_yolu,
      "-y",
      "-i",
      girdi_yolu,
      "-vf",
      (
          "setpts=0.96*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
      ),
      "-af",
      "atempo=1.04",
      "-c:v",
      "libx264",
      "-preset",
      "ultrafast",
      "-crf",
      "23",
      "-c:a",
      "aac",
      "-b:a",
      "192k",
      cikti_yolu,
  ]

  subprocess.run(komut, check=True)
  return cikti_yolu


def video_bul_ve_indir(cikti_temel_adi="gunun_videosu"):
  secilen_tag = random.choice(HASHTAGLER)
  arama_sorgusu = f"ytsearch15:{secilen_tag} shorts #shorts"
  print(f"Seçilen Tag: #{secilen_tag} - Güvenli ve sesli video aranıyor...")

  yasakli_kelimeler = [
      "hot",
      "sexy",
      "girl",
      "bikini",
      "model",
      "sensual",
      "dating",
      "flirt",
      "romance",
      "kiss",
      "couple",
      "sheesha",
      "dance",
      "twerk",
  ]

  arama_opts = {
      "noplaylist": True,
      "quiet": True,
      "ignoreerrors": True,
      "no_warnings": True,
  }

  video_url = None
  video_baslik_metni = None

  try:
    with yt_dlp.YoutubeDL(arama_opts) as ydl:
      arama_sonucu = ydl.extract_info(arama_sorgusu, download=False)

      if arama_sonucu and "entries" in arama_sonucu:
        for entry in arama_sonucu["entries"]:
          if entry:
            duration = entry.get("duration", 0)
            baslik = entry.get("title", "").lower()

            if not duration or not (3 <= duration <= 60):
              continue

            if any(yasakli in baslik for yasakli in yasakli_kelimeler):
              continue

            video_url = entry.get("webpage_url")
            video_baslik_metni = entry.get("title", "Güvenli Viral Shorts")
            break
  except Exception as e:
    return None, None

  if not video_url:
    return None, None

  print(f"Seçilen Video: {video_baslik_metni}")
  print("Ses ve görüntü indirilip birleştiriliyor...")

  for eski_dosya in glob.glob(f"{cikti_temel_adi}.*"):
    try:
      os.remove(eski_dosya)
    except:
      pass

  ffmpeg_yolu = imageio_ffmpeg.get_ffmpeg_exe()

  indirme_opts = {
      "format": "bestvideo+bestaudio/best",
      "outtmpl": f"{cikti_temel_adi}.%(ext)s",
      "ffmpeg_location": ffmpeg_yolu,
      "quiet": True,
      "noplaylist": True,
      "socket_timeout": 15,
      "ignoreerrors": True,
      "merge_output_format": "mp4",
  }

  try:
    with yt_dlp.YoutubeDL(indirme_opts) as ydl:
      ydl.download([video_url])
  except:
    return None, None

  bulunan_dosyalar = glob.glob(f"{cikti_temel_adi}.*")
  if bulunan_dosyalar:
    ham_dosya = bulunan_dosyalar[0]
    son_dosya = dikey_shorts_yap(ham_dosya, "final_shorts.mp4")
    return son_dosya, video_baslik_metni
  else:
    return None, None


def youtube_baglantisi_kur():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "client_secret.json", SCOPES
      )
      creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
      token.write(creds.to_json())

  return build("youtube", "v3", credentials=creds)


def youtubea_yukle(dosya_yolu, baslik, aciklama):
  youtube = youtube_baglantisi_kur()

  temiz_baslik = baslik[:50] + " #shorts #viral"
  detayli_aciklama = (
      f"{aciklama}\n\n#güldürgüldür #beyazfutbol #komedi #mizah #shorts #viral"
      " #trending #shortsvideo"
  )

  body = {
      "snippet": {
          "title": temiz_baslik,
          "description": detayli_aciklama,
          "tags": [
              "shorts",
              "güldürgüldür",
              "beyazfutbol",
              "komedi",
              "mizah",
              "viral",
              "trending",
              "shortsvideo",
          ],
          "categoryId": "22",
      },
      "status": {
          "privacyStatus": "public",
          "selfDeclaredMadeForKids": False,
      },
  }

  media = MediaFileUpload(dosya_yolu, chunksize=-1, resumable=True)

  print("YouTube'a sesli, tam ekran büyük boyutta Shorts olarak yükleniyor...")
  request = youtube.videos().insert(
      part="snippet,status", body=body, media_body=media
  )
  response = request.execute()
  print(f"Yüklendi! Video ID: {response['id']}")


if __name__ == "__main__":
  video_dosyasi, orijinal_baslik = None, None

  while not video_dosyasi:
    video_dosyasi, orijinal_baslik = video_bul_ve_indir()

  if video_dosyasi and os.path.exists(video_dosyasi):
    video_aciklama = "En trend içerikler."
    youtubea_yukle(video_dosyasi, orijinal_baslik, video_aciklama)

    try:
      os.remove(video_dosyasi)
      for f in glob.glob("gunun_videosu.*"):
        os.remove(f)
    except:
      pass

    print("İşlem başarıyla tamamlandı!")
  else:
    print("Hata oluştu.")