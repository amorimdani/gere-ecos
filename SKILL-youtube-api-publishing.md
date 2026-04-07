# Skill: YouTube API Publishing & Automation

**Description**: Master YouTube API integration, video uploads, scheduling, and automation. Use this skill when uploading videos to YouTube, managing video metadata, scheduling publications, debugging YouTube API errors, handling quotas, automating bulk uploads, or troubleshooting authentication issues.

**Triggers**:

- "How do I upload to YouTube?"
- "YouTube API setup", "YouTube authentication", "OAuth2"
- "Upload video/publish", "schedule video", "set metadata"
- "YouTube quota exceeded", "API errors", "YouTube API limits"
- "Bulk upload", "automate YouTube", "batch publishing"
- "Why isn't my video published?", "Debug YouTube issues"

## YouTube Publishing Pipeline

### PublisherAgent Architecture

**Location**: `src/agents/publisher_agent.py`

**YouTube Manager**: `src/agents/youtube_manager.py`

## YouTube API Setup

### Authentication (OAuth 2.0)

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Gere Ecos Videos"
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 Desktop Application** credentials
5. Download credentials → `credentials.json`

#### Step 2: Store Credentials

```
credentials.json → Armazena tokens de autenticação
```

#### Step 3: First-Time Authentication

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    SCOPES
)

credentials = flow.run_local_server(port=8080)
# Browser abre para fazer login → autoriza app
```

## Video Upload

### Basic Upload

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(video_path, title, description):
    youtube = build('youtube', 'v3', credentials=credentials)

    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['filosofia', 'estoicismo', 'sabedoria'],
            'categoryId': '27'  # Education category
        },
        'status': {
            'privacyStatus': 'private'  # private/unlisted/public
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype='video/mp4',
        resumable=True
    )

    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = request.execute()
    return response['id']  # Video ID
```

### Upload with Progress Tracking

```python
def upload_with_progress(video_path, title, description):
    youtube = build('youtube', 'v3', credentials=credentials)

    request_body = {...}
    media = MediaFileUpload(video_path, resumable=True)

    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"Upload Progress: {progress}%")

    print(f"Upload Concluído! Video ID: {response['id']}")
    return response['id']
```

## Video Metadata Management

### Set Thumbnail

```python
def set_custom_thumbnail(video_id, thumbnail_path):
    youtube = build('youtube', 'v3', credentials=credentials)

    media = MediaFileUpload(
        thumbnail_path,
        mimetype='image/jpeg'
    )

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=media
    ).execute()

    print(f"Thumbnail set for {video_id}")
```

### Update Video Details

```python
def update_video_metadata(video_id, title, description, tags):
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.videos().update(
        part='snippet',
        body={
            'id': video_id,
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '27'  # Education
            }
        }
    )

    request.execute()
    print(f"Metadata updated for {video_id}")
```

## Schedule Publishing

### Schedule Publish (Future Date)

```python
from datetime import datetime, timedelta

def schedule_video(video_id, publish_time):
    """
    publish_time: datetime object
    Example: datetime.now() + timedelta(days=1, hours=8)
    """
    youtube = build('youtube', 'v3', credentials=credentials)

    youtube.videos().update(
        part='status',
        body={
            'id': video_id,
            'status': {
                'privacyStatus': 'scheduled',
                'publishAt': publish_time.isoformat() + 'Z'
            }
        }
    ).execute()

    print(f"Video {video_id} scheduled for {publish_time}")
```

### Publish Immediately

```python
def publish_video(video_id):
    youtube = build('youtube', 'v3', credentials=credentials)

    youtube.videos().update(
        part='status',
        body={
            'id': video_id,
            'status': {
                'privacyStatus': 'public'
            }
        }
    ).execute()

    print(f"Video {video_id} is now public!")
```

## Automating 3 Videos Per Day

### Scheduling Strategy

```python
from datetime import datetime, time

# Horários fixes para publicar 3 vídeos diários
PUBLISH_TIMES = [
    time(8, 0),   # 08:00 UTC
    time(14, 0),  # 14:00 UTC
    time(20, 0)   # 20:00 UTC
]

def schedule_daily_videos(videos_data):
    """
    videos_data: Lista de 3 dicts com video_path, title, description
    """
    youtube = build('youtube', 'v3', credentials=credentials)

    for idx, video_info in enumerate(videos_data):
        # 1. Upload vídeo (privado)
        video_id = upload_video(
            video_info['path'],
            video_info['title'],
            video_info['description']
        )

        # 2. Schedule publicação
        publish_time = datetime.combine(
            datetime.today(),
            PUBLISH_TIMES[idx]
        )

        schedule_video(video_id, publish_time)
```

## Error Handling & Quotas

### YouTube API Quotas

| Limite              | Valor                                   | Reset     |
| ------------------- | --------------------------------------- | --------- |
| **Queries per day** | 10,000 (free tier)                      | 00:00 UTC |
| **Upload quota**    | 10,000 min/24h (1 HD video ≈ 10-20 min) | 00:00 UTC |
| **Uploads per day** | Ilimitado (mas volume total limitado)   | 00:00 UTC |

### Handling Quota Exceeded

```python
def upload_with_quota_handling(video_path, title, description):
    try:
        video_id = upload_video(video_path, title, description)
        return video_id

    except HttpError as e:
        if e.resp.status == 403:
            error_reason = e.content.decode('utf-8')

            if 'quotaExceeded' in error_reason:
                print("YouTube quota exceeded! Aguardando reset (00:00 UTC)...")
                # Agenda retry para próximo dia
                schedule_retry_tomorrow(video_path, title, description)
                return None
```

### Implement Retry Logic

```python
import time

def upload_with_retries(video_path, title, description, max_retries=3):
    for attempt in range(max_retries):
        try:
            return upload_video(video_path, title, description)

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt+1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Upload failed after {max_retries} attempts: {e}")
                raise
```

## Broadcasting Statistics

### Get Video Stats

```python
def get_video_stats(video_id):
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.videos().list(
        part='statistics,snippet',
        id=video_id
    )

    response = request.execute()
    video = response['items'][0]

    return {
        'title': video['snippet']['title'],
        'views': int(video['statistics'].get('viewCount', 0)),
        'likes': int(video['statistics'].get('likeCount', 0)),
        'comments': int(video['statistics'].get('commentCount', 0))
    }
```

### Track Publishing Metrics

```python
import json

def log_publishing_stats(video_id, title):
    """Registra estatísticas de publicação"""
    stats = get_video_stats(video_id)

    # Append to JSON log
    stats_log = 'data/videos_publicados.json'

    try:
        with open(stats_log, 'r') as f:
            videos = json.load(f)
    except:
        videos = []

    videos.append({
        'video_id': video_id,
        'title': title,
        'published_at': datetime.now().isoformat(),
        'stats': stats
    })

    with open(stats_log, 'w') as f:
        json.dump(videos, f, indent=2)
```

## Integration with Pipeline

### PublisherAgent Workflow

```python
1. EditorAgent outputs: video_final.mp4
2. PublisherAgent receives:
   {
       'video_file': 'output/video_final.mp4',
       'title': 'Título do Vídeo',
       'description': 'Descrição e links',
       'tags': ['filosofia', 'estoicismo'],
       'schedule_time': datetime,
       'thumbnail': 'thumbnail.jpg'
   }

3. PublisherAgent:
   - Faz upload do vídeo
   - Define metadados
   - Configura thumbnail
   - Agenda publicação
   - Registra estatísticas

4. Returns:
   {
       'success': True,
       'video_id': 'ABC123...',
       'url': 'https://youtube.com/watch?v=ABC123',
       'published_at': datetime
   }
```

## Monitoring & Maintenance

### Channel Health Check

```python
def check_channel_health():
    youtube = build('youtube', 'v3', credentials=credentials)

    channel = youtube.channels().list(
        part='statistics',
        mine=True
    ).execute()

    stats = channel['items'][0]['statistics']

    return {
        'subscribers': int(stats.get('subscriberCount', 0)),
        'total_views': int(stats.get('viewCount', 0)),
        'videos_count': int(stats.get('videoCount', 0))
    }
```

### Daily Report

```python
def generate_daily_report():
    """Relatório de performance diária"""
    health = check_channel_health()

    report = {
        'date': datetime.now().isoformat(),
        'channel_health': health,
        'quota_remaining': check_quota_status(),
        'scheduled_videos': get_scheduled_videos()
    }

    print(json.dumps(report, indent=2))
```

## Troubleshooting Common Issues

| Problema                 | Causa                              | Solução                                 |
| ------------------------ | ---------------------------------- | --------------------------------------- |
| **Auth failed**          | credentials.json inválido/expirado | Delete token cache, reautentica         |
| **403 Forbidden**        | Permissões insufficient            | Verifica SCOPES inclui youtube.upload   |
| **Quota exceeded**       | Atingiu limite upload              | Aguarda reset (00:00 UTC)               |
| **Video não inicia**     | Upload incompleto                  | Checa file size, tenta upload novamente |
| **Metadata not updated** | Video ainda em processamento       | Aguarda 10-15 min após upload           |
| **Schedule failed**      | DateTime formato inválido          | Usa ISO format + 'Z' (UTC timestamp)    |

## Related Skills

- **video-pipeline-orchestration** - Orquestra publicação
- **video-editing-effects** - Prepara vídeo para upload
- **video-agents-architecture** - PublisherAgent overview
