"""
Publisher Agent - Publicação de Vídeos no YouTube
Responsável por: Upload, Metadados, Agendamento, Logging
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentStatus
from agents.youtube_manager import YouTubeManager, VideoMetadata
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class PublisherAgent(BaseAgent):
    """
    Agent responsável por publicação de vídeos no YouTube
    
    Pipeline:
    - Valida vídeo antes de upload
    - Autentica no YouTube API
    - Faz upload com retry automático
    - Registra vídeo em histórico
    - Envia notificações
    """
    
    def __init__(self):
        super().__init__(agent_name="PublisherAgent", max_retries=3)
        self.config = Config()
        self.file_manager = FileManager()
        self.youtube_manager = YouTubeManager()
        self.published_log = Path(self.config.data_dir) / "videos_publicados.json"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Cria arquivo de log se não existir"""
        
        self.published_log.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.published_log.exists():
            self.file_manager.save_json(
                str(self.published_log),
                {
                    "created_at": datetime.now().isoformat(),
                    "videos": []
                }
            )
            logger.info(f"Log de publicação criado: {self.published_log}")
    
    async def execute(self, payload: dict) -> dict:
        """
        Executa publicação de vídeo
        
        Payload:
        {
            "video_path": "output/video_123.mp4",
            "title": "Estoicismo: A Filosofia de Calma",
            "description": "Um guia completo sobre estoicismo...",
            "tags": ["estoicismo", "filosofia", "motivação"],
            "theme": "estoicismo",
            "category_id": "22",                    # Opcional
            "privacy_status": "private",            # private, unlisted, public
            "schedule_time": "2026-04-01T09:00:00", # ISO format, opcional
            "thumbnail_path": "output/thumb.jpg",   # Opcional
            "made_for_kids": False
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "video_id": "xxx",
                "url": "https://youtu.be/xxx",
                "title": "...",
                "file_size_mb": 125.5,
                "upload_time_seconds": 120,
                "privacy_status": "private"
            }
        }
        """
        
        try:
            video_path = payload.get("video_path")
            
            if not video_path:
                return {"success": False, "error": "Missing video_path"}
            
            video_path = Path(video_path)
            
            if not video_path.exists():
                return {
                    "success": False,
                    "error": f"Video file not found: {video_path}"
                }
            
            logger.info(f"🎥 Iniciando publicação: {video_path.name}")
            
            # STAGE 1: Valida credenciais
            logger.info("Stage 1: Validando credenciais...")
            
            if not self.youtube_manager.validate_credentials():
                logger.error(
                    "❌ Credenciais do YouTube não encontradas\n"
                    "   1. Acesse: https://console.cloud.google.com/apis/credentials\n"
                    "   2. Crie uma chave OAuth 2.0\n"
                    "   3. Salve como: credentials.json na raiz do projeto"
                )
                return {
                    "success": False,
                    "error": "YouTube credentials not found"
                }
            
            # STAGE 2: Autentica
            logger.info("Stage 2: Autenticando no YouTube...")
            
            auth_success = await self.youtube_manager.authenticate()
            
            if not auth_success:
                return {
                    "success": False,
                    "error": "YouTube authentication failed"
                }
            
            # STAGE 3: Prepara metadados
            logger.info("Stage 3: Preparando metadados...")
            
            title = payload.get("title", "Sem título")
            description = payload.get("description", "")
            tags = payload.get("tags", [])
            category_id = payload.get("category_id", "22")
            privacy = payload.get("privacy_status", "private")
            thumbnail_path = payload.get("thumbnail_path")
            made_for_kids = payload.get("made_for_kids", False)
            schedule_time_str = payload.get("schedule_time")
            
            schedule_time = None
            if schedule_time_str:
                try:
                    schedule_time = datetime.fromisoformat(schedule_time_str)
                    logger.info(f"   Agendado para: {schedule_time}")
                except:
                    logger.warning(f"   Formato de data inválido: {schedule_time_str}")
            
            metadata = VideoMetadata(
                title=title,
                description=description,
                tags=tags,
                category_id=category_id,
                privacy_status=privacy,
                made_for_kids=made_for_kids,
                thumbnail_path=thumbnail_path
            )
            
            # STAGE 4: Upload
            logger.info("Stage 4: Fazendo upload...")
            
            upload_start = datetime.now()
            success, video_id = await self.youtube_manager.upload_video(
                str(video_path),
                metadata,
                schedule_time
            )
            upload_time = (datetime.now() - upload_start).total_seconds()
            
            if not success:
                return {
                    "success": False,
                    "error": "Upload failed"
                }
            
            file_size_mb = video_path.stat().st_size / 1024 / 1024
            
            # STAGE 5: Registra no histórico
            logger.info("Stage 5: Registrando no histórico...")
            
            await self._record_published_video(
                video_id=video_id,
                title=title,
                theme=payload.get("theme", ""),
                file_size_mb=file_size_mb,
                upload_time_seconds=upload_time,
                privacy_status=privacy
            )
            
            logger.info(f"✅✅ Vídeo publicado com sucesso!")
            logger.info(f"   ID: {video_id}")
            logger.info(f"   URL: https://youtu.be/{video_id}")
            
            return {
                "success": True,
                "data": {
                    "video_id": video_id,
                    "url": f"https://youtu.be/{video_id}",
                    "title": title,
                    "file_size_mb": file_size_mb,
                    "upload_time_seconds": upload_time,
                    "privacy_status": privacy,
                    "theme": payload.get("theme", "")
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Erro na publicação: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _record_published_video(
        self,
        video_id: str,
        title: str,
        theme: str,
        file_size_mb: float,
        upload_time_seconds: float,
        privacy_status: str
    ):
        """Registra vídeo publicado no histórico"""
        
        try:
            log_data = self.file_manager.load_json(str(self.published_log))
            
            video_record = {
                "video_id": video_id,
                "url": f"https://youtu.be/{video_id}",
                "title": title,
                "theme": theme,
                "file_size_mb": file_size_mb,
                "upload_time_seconds": upload_time_seconds,
                "privacy_status": privacy_status,
                "published_at": datetime.now().isoformat()
            }
            
            log_data["videos"].append(video_record)
            log_data["last_published"] = datetime.now().isoformat()
            log_data["total_videos"] = len(log_data["videos"])
            
            self.file_manager.save_json(str(self.published_log), log_data)
            
            logger.info(f"✅ Registrado no histórico: {self.published_log.name}")
        
        except Exception as e:
            logger.error(f"⚠️  Erro ao registrar no histórico: {str(e)}")
    
    async def get_published_videos(self) -> list:
        """Retorna lista de vídeos publicados"""
        
        try:
            log_data = self.file_manager.load_json(str(self.published_log))
            return log_data.get("videos", [])
        
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {str(e)}")
            return []
    
    async def get_channel_stats(self) -> dict:
        """Obtém estatísticas do canal"""
        
        try:
            await self.youtube_manager.authenticate()
            
            channel_info = await self.youtube_manager.get_channel_info()
            
            if channel_info:
                published_videos = await self.get_published_videos()
                
                return {
                    "channel_title": channel_info.get("title"),
                    "total_subscribers": channel_info.get("subscribers"),
                    "total_views": channel_info.get("view_count"),
                    "total_videos_youtube": channel_info.get("video_count"),
                    "videos_published_by_factory": len(published_videos),
                    "last_publish": (
                        published_videos[-1]["published_at"]
                        if published_videos
                        else None
                    )
                }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}


def create_publisher_agent() -> PublisherAgent:
    """Factory function para criar PublisherAgent"""
    return PublisherAgent()
