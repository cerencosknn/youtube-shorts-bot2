import os
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import yt_dlp

HASHTAGLER = [
    'asmr',
    'asmrsounds',
    'satisfying',
    'satisfyingvideos',
    'relaxing',
    'komedi',
    'kahkaha',
    'komikvideolar',
    'eğlence',
    'beyazfutbol',
    'beyazfutbolkomik',
    'beyaztv',
    'ahmetçakar',
    'sinanengin',
    'rasimozan',
    'shorts',
    'viral',
]


def video_ara_ve_indir():
  secilen_tag = random.choice(HASHTAGLER)
  print(f'Seçilen arama etiketi: #{secilen_tag}')

  arama_opts = {
      'noplaylist': True,
      'quiet': True,
      'ignoreerrors': True,
      'no_warnings': True,
      'cookiefile': 'cookies.txt',
  }

  arama_sorgusu = f'ytsearch5:{secilen_tag}'

  with yt_dlp.YoutubeDL(arama_opts) as ydl:
    try:
      info = ydl.extract_info(arama_sorgusu, download=False)
      entries = info.get('entries', [])
      if not entries:
        print('Video bulunamadı!')
        return None, None

      uygun_videolar = [
          e for e in entries if e and e.get('duration', 0) <= 60
      ]
      if not uygun_videolar:
        uygun_videolar = [e for e in entries if e]

      if not uygun_videolar:
        print('Uygun video bulunamadı!')
        return None, None

      secilen = random.choice(uygun_videolar)
      video_url = secilen['webpage_url']
      video_baslik = secilen.get('title', 'Kısa Video')
      print(f'İndirilecek video: {video_baslik} ({video_url})')

    except Exception as e:
      print(f'Arama sırasında hata oluştu: {e}')
      return None, None

  cikti_temel_adi = 'indirilen_video'

  indirme_opts = {
      'format': 'bestvideo+bestaudio/best',
      'outtmpl': f'{cikti_temel_adi}.%(ext)s',
      'quiet': True,
      'noplaylist': True,
      'socket_timeout': 15,
      'ignoreerrors': True,
      'merge_output_format': 'mp4',
      'cookiefile': 'cookies.txt',
  }

  with yt_dlp.YoutubeDL(indirme_opts) as ydl:
    try:
      ydl.download([video_url])
      print('Video başarıyla indirildi.')
      return f'{cikti_temel_adi}.mp4', video_baslik
    except Exception as e:
      print(f'İndirme hatası: {e}')
      return None, None


def videoyu_yukle(dosya_yolu, baslik):
  if not os.path.exists(dosya_yolu):
    print('Yüklenecek dosya bulunamadı.')
    return

  SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
  creds = None
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  youtube = build('youtube', 'v3', credentials=creds)

  body = {
      'snippet': {
          'title': f'{baslik[:80]} #shorts',
          'description': 'Otomatik paylaşılan eğlenceli ve tatmin edici anlar!',
          'tags': ['shorts', 'asmr', 'komedi', 'beyazfutbol'],
          'categoryId': '24',
      },
      'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False},
  }

  media = MediaFileUpload(
      dosya_yolu, chunksize=-1, resumable=True, mimetype='video/mp4'
  )

  request = youtube.videos().insert(
      part='snippet,status', body=body, media_body=media
  )

  response = None
  while response is None:
    status, response = request.next_chunk()
    if status:
      print(f'Yükleniyor: {int(status.progress() * 100)}%')

  print('Video başarıyla YouTube Shorts olarak yüklendi!')


if __name__ == '__main__':
  dosya, baslik = video_ara_ve_indir()
  if dosya:
    videoyu_yukle(dosya, baslik)
