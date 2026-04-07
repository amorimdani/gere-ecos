"""
YouTube Manager - Integração com YouTube Data API v3
Responsável por: Autenticação OAuth, Upload de Vídeos, Metadados
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoMetadata:
    """Metadados de vídeo"""
    title: str
    description: str
    tags: list
    category_id: str = "22"  # People & Blogs
    privacy_status: str = "private"  # private, unlisted, public
    made_for_kids: bool = False
    thumbnail_path: Optional[str] = None


class YouTubeManager:
    """Gerenciador de upload para YouTube via API v3"""
    
    # Escopos de autenticação
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    # Categorias
    CATEGORIES = {
        "22": "People & Blogs",
        "23": "Shorts",
        "26": "Howto & Style",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism"
    }
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Inicializa gerenciador de YouTube
        
        Args:
            credentials_file: Arquivo de credenciais OAuth2
        """
        self.config = Config()
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(self.config.data_dir) / "youtube_token.json"
        self.youtube = None
        self.credentials = None
    
    async def authenticate(self) -> bool:
        """
        Autentica com YouTube API
        Fluxo:
        1. Carrega token existente se disponível
        2. Se expirado, faz refresh
        3. Se nenhum, inicia fluxo OAuth
        
        Returns:
            bool: True se autenticado com sucesso
        """
        
        try:
            # 1. Tenta carregar token existente
            if self.token_file.exists():
                logger.info(f"Carregando token existente: {self.token_file}")
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES
                )
                
                # Se expirado, faz refresh
                if self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing token...")
                    self.credentials.refresh(Request())
                    self._save_token()
            
            # 2. Se nenhum token, inicia fluxo OAuth
            if not self.credentials or not self.credentials.valid:
                if not self.credentials_file.exists():
                    logger.error(
                        f"❌ Arquivo de credenciais não encontrado: {self.credentials_file}\n"
                        f"   1. Baixe de: https://console.cloud.google.com/apis/credentials\n"
                        f"   2. Salve como: {self.credentials_file}\n"
                        f"   3. Execute novamente"
                    )
                    return False
                
                logger.info("Iniciando fluxo de autenticação OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file),
                    self.SCOPES
                )
                
                # Open a browser for authentication
                self.credentials = flow.run_local_server(port=8080)
                self._save_token()
                logger.info("✅ Autenticação bem-sucedida!")
            
            # 3. Cria cliente YouTube
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=self.credentials
            )
            
            logger.info("✅ Conectado à YouTube API v3")
            return True
        
        except google_auth_oauthlib.exceptions.InvalidGrant:
            logger.error("❌ Token expirado ou inválido. Delete youtube_token.json e tente novamente")
            if self.token_file.exists():
                self.token_file.unlink()
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {str(e)}", exc_info=True)
            return False
    
    def _save_token(self):
        """Salva token para futuras autenticações"""
        
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.token_file, "w") as f:
            f.write(self.credentials.to_json())
        
        logger.debug(f"Token salvo: {self.token_file}")
    
    async def upload_video(
        self,
        video_path: str,
        metadata: VideoMetadata,
        schedule_time: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        Upload de vídeo para YouTube
        
        Args:
            video_path: Caminho para o arquivo MP4
            metadata: Metadados do vídeo (título, descrição, tags)
            schedule_time: Data/hora de publicação (None = imediato)
        
        Returns:
            Tupla (sucesso: bool, video_id: str)
        """
        
        if not self.youtube:
            logger.error("❌ Não autenticado no YouTube")
            return False, ""
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
            return False, ""
        
        try:
            logger.info(f"📤 Iniciando upload: {video_path.name}")
            logger.info(f"   Título: {metadata.title}")
            logger.info(f"   Tamanho: {video_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Prepara request de inserção
            request_body = {
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": metadata.category_id,
                    "defaultLanguage": "pt",
                    "defaultAudioLanguage": "pt"
                },
                "status": {
                    "privacyStatus": metadata.privacy_status,
                    "madeForKids": metadata.made_for_kids
                }
            }
            
            # Se agendado, define tempo de publicação
            if schedule_time:
                request_body["status"]["publishAt"] = schedule_time.isoformat() + "Z"
                logger.info(f"   Agendado para: {schedule_time.isoformat()}")
            
            # Upload do vídeo
            media_file = googleapiclient.http.MediaFileUpload(
                str(video_path),
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024  # 1 MB chunks
            )
            
            insert_request = self.youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=media_file
            )
            
            # Executa com retry
            response = None
            retry_count = 0
            max_retries = 5
            
            while response is None and retry_count < max_retries:
                try:
                    status, response = insert_request.execute_once(num_retries=0)
                    
                    if status is not None:
                        progress = int((status.progress() * 100))
                        logger.info(f"   Upload: {progress}%")
                
                except googleapiclient.errors.HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        retry_count += 1
                        logger.warning(
                            f"   Erro temporário (tentativa {retry_count}/{max_retries}): {e.resp.status}"
                        )
                        import time
                        time.sleep(2 ** retry_count)  # Backoff exponencial
                    else:
                        raise
            
            if response is None:
                logger.error("❌ Upload falhou após múltiplas tentativas")
                return False, ""
            
            video_id = response["id"]
            
            # Se houver thumbnail, faz upload
            if metadata.thumbnail_path and Path(metadata.thumbnail_path).exists():
                await self._upload_thumbnail(video_id, metadata.thumbnail_path)
            
            logger.info(f"✅ Upload concluído!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: https://youtu.be/{video_id}")
            
            return True, video_id
        
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ Erro HTTP: {e.content}")
            return False, ""
        
        except Exception as e:
            logger.error(f"❌ Erro no upload: {str(e)}", exc_info=True)
            return False, ""
    
    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload de thumbnail customizado"""
        
        try:
            logger.info(f"📤 Upload de thumbnail: {Path(thumbnail_path).name}")
            
            insert_request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=googleapiclient.http.MediaFileUpload(
                    thumbnail_path,
                    mimetype="image/jpeg"
                )
            )
            
            response = insert_request.execute()
            
            logger.info(f"✅ Thumbnail atualizado")
            return True
        
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível atualizar thumbnail: {str(e)}")
            return False
    
    async def get_channel_info(self) -> Optional[Dict]:
        """Obtém informações do canal"""
        
        if not self.youtube:
            logger.error("❌ Não autenticado")
            return None
        
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            
            response = request.execute()
            
            if response["items"]:
                channel = response["items"][0]
                
                return {
                    "channel_id": channel["id"],
                    "title": channel["snippet"]["title"],
                    "description": channel["snippet"]["description"],
                    "subscribers": channel["statistics"].get("subscriberCount", "N/A"),
                    "view_count": channel["statistics"].get("viewCount", "0"),
                    "video_count": channel["statistics"].get("videoCount", "0")
                }
        
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações do canal: {str(e)}")
            return None
    
    async def list_recent_videos(self, max_results: int = 10) -> list:
        """Lista vídeos recentes do canal"""
        
        if not self.youtube:
            logger.error("❌ Não autenticado")
            return []
        
        try:
            # Obtém uploads playlist ID
            request = self.youtube.channels().list(
                part="contentDetails",
                mine=True
            )
            response = request.execute()
            
            if not response["items"]:
                return []
            
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Lista vídeos
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=min(max_results, 50),
                order="date"
            )
            
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                video = {
                    "video_id": item["snippet"]["resourceId"]["videoId"],
                    "title": item["snippet"]["title"],
                    "Published": item["snippet"]["publishedAt"],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
                }
                videos.append(video)
            
            return videos
        
        except Exception as e:
            logger.error(f"❌ Erro ao listar vídeos: {str(e)}")
            return []
    
    def validate_credentials(self) -> bool:
        """Valida se credenciais estão disponíveis"""
        
        return self.credentials_file.exists() or self.token_file.exists()
