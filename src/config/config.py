"""
Módulo de Configuração - Gerentura centralizada das variáveis de ambiente
Implementa o padrão Singleton para garantir uma única instância
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carrega arquivo .env
load_dotenv()


class GoogleConfig(BaseModel):
    """Configuração do Google Gemini"""
    api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    
    class Config:
        populate_by_name = True


class OllamaConfig(BaseModel):
    """Configuração do Ollama Local"""
    base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    model: str = Field(default="llama2", alias="OLLAMA_MODEL")
    timeout: int = 300
    
    class Config:
        populate_by_name = True


class YoutubeConfig(BaseModel):
    """Configuração do YouTube"""
    client_id: Optional[str] = Field(default=None, alias="YOUTUBE_CLIENT_ID")
    client_secret: Optional[str] = Field(default=None, alias="YOUTUBE_CLIENT_SECRET")
    access_token: Optional[str] = Field(default=None, alias="YOUTUBE_ACCESS_TOKEN")
    
    class Config:
        populate_by_name = True


class AppConfig(BaseModel):
    """Configuração da Aplicação"""
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    videos_per_day: int = Field(default=3, alias="VIDEOS_PER_DAY")
    video_duration_minutes: int = Field(default=10, alias="VIDEO_DURATION_MINUTES")
    
    class Config:
        populate_by_name = True


class Config:
    """
    Classe Singleton para gerenciar todas as configurações da aplicação.
    Centraliza acesso a variáveis de ambiente e configurações.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.google = GoogleConfig(
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.ollama = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama2")
        )
        
        self.youtube = YoutubeConfig(
            client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            access_token=os.getenv("YOUTUBE_ACCESS_TOKEN")
        )
        
        self.app = AppConfig(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            videos_per_day=int(os.getenv("VIDEOS_PER_DAY", "3")),
            video_duration_minutes=int(os.getenv("VIDEO_DURATION_MINUTES", "10"))
        )
        
        # Diretórios da aplicação
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(self.base_dir, "output")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.src_dir = os.path.join(self.base_dir, "src")
        
        # Cria diretórios se não existirem
        for directory in [self.output_dir, self.logs_dir, self.data_dir]:
            os.makedirs(directory, exist_ok=True)
        
        Config._initialized = True
    
    def validate_credentials(self) -> dict:
        """
        Valida se as credenciais necessárias estão configuradas.
        
        Returns:
            dict: Dicionário com status de cada credencial
        """
        return {
            "google_api_key": self.google.api_key is not None,
            "youtube_configured": all([
                self.youtube.client_id,
                self.youtube.client_secret
            ]),
            "ollama_available": True,  # Ollama é sempre um fallback
        }
    
    def get_summary(self) -> str:
        """Retorna um sumário das configurações para exibição na UI"""
        credentials = self.validate_credentials()
        return f"""
        **Configurações Carregadas:**
        - Google Gemini API: {'✅ Configurado' if credentials['google_api_key'] else '❌ Não configurado'}
        - YouTube: {'✅ Configurado' if credentials['youtube_configured'] else '❌ Não configurado'}
        - Ollama (Fallback): ✅ Disponível
        - Vídeos por dia: {self.app.videos_per_day}
        - Duração dos vídeos: {self.app.video_duration_minutes} minutos
        """
