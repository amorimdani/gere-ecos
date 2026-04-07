"""
TTS Manager - Gerenciador de Text-to-Speech com fallback automático
Implementa edge-tts (Microsoft) com fallback para gTTS (Google)
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


class TTSProvider(ABC):
    """Interface para provedores de TTS"""
    
    @abstractmethod
    async def generate(self, text: str, output_path: str, 
                      duration_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Gera arquivo de áudio MP3"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Verifica disponibilidade do provedor"""
        pass


class EdgeTTSProvider(TTSProvider):
    """Provedor Microsoft Edge TTS (Neural Voices)"""
    
    def __init__(self, voice: str = "pt-BR-AntonioNeural"):
        """
        Inicializa Edge TTS.
        
        Args:
            voice: Voz a usar (padrão: pt-BR-AntonioNeural - voz masculina grave)
        """
        self.voice = voice
        self.logger = get_logger("tts.edge")
        
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.logger.info(f"Edge TTS inicializado (voz: {voice})")
        except ImportError:
            self.logger.error("edge-tts não instalado")
            self.edge_tts = None
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do Edge TTS"""
        try:
            if not self.edge_tts:
                return False
            
            # Tenta gerar áudio curto para teste
            communicate = self.edge_tts.Communicate(
                text="teste",
                voice=self.voice
            )
            
            # Se conseguir criar a comunicação, está disponível
            self.logger.info("Edge TTS: Disponível")
            return True
            
        except Exception as e:
            self.logger.warning(f"Edge TTS indisponível: {str(e)}")
            return False
    
    async def generate(self, text: str, output_path: str,
                      duration_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera áudio MP3 usando Edge TTS.
        
        Args:
            text: Texto a converter em áudio
            output_path: Caminho para salvar MP3
            duration_seconds: Duração esperada (para ajuste de velocidade)
            
        Returns:
            dict com status e metadata
        """
        try:
            if not self.edge_tts:
                raise Exception("Edge TTS não configurado")
            
            self.logger.info(f"Gerando áudio com Edge TTS (voz: {self.voice})")
            
            # Calcula velocidade baseada na duração esperada
            rate = self._calculate_rate(text, duration_seconds)
            
            # Cria comunicação
            communicate = self.edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=rate
            )
            
            # Salva MP3
            await communicate.save(output_path)
            
            # Verifica se arquivo foi criado
            if not Path(output_path).exists():
                raise Exception(f"Falha ao salvar MP3 em {output_path}")
            
            file_size = Path(output_path).stat().st_size
            self.logger.info(f"Edge TTS: Sucesso ({file_size} bytes)")
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "provider": "edge-tts",
                "voice": self.voice,
                "rate": rate
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Edge TTS: {str(e)}")
            raise
    
    def _calculate_rate(self, text: str, 
                        duration_seconds: Optional[int] = None) -> str:
        """
        Calcula a velocidade de fala para ajustar duração.
        
        Args:
            text: Texto a ser falado
            duration_seconds: Duração esperada em segundos
            
        Returns:
            str: Taxa de velocidade (ex: "+10%", "-5%", "0%")
        """
        if not duration_seconds:
            return "0%"  # Velocidade normal
        
        # Estima ~140 palavras por minuto = ~2.33 palavras/segundo
        word_count = len(text.split())
        estimated_seconds = (word_count / 2.33)
        
        # Calcula diferença percentual
        if estimated_seconds > 0:
            rate_percent = ((estimated_seconds - duration_seconds) / estimated_seconds) * 100
            rate_percent = max(-50, min(50, rate_percent))  # Limita entre -50% e +50%
            return f"{rate_percent:+.0f}%"
        
        return "0%"


class GTTSProvider(TTSProvider):
    """Provedor Google TTS (gTTS) com modificação de pitch"""
    
    def __init__(self, lang: str = "pt-br"):
        """
        Inicializa gTTS.
        
        Args:
            lang: Código de idioma (padrão: pt-br)
        """
        self.lang = lang
        self.logger = get_logger("tts.gtts")
        
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            self.logger.info(f"gTTS inicializado (idioma: {lang})")
        except ImportError:
            self.logger.error("gtts não instalado")
            self.gTTS = None
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do gTTS"""
        try:
            if not self.gTTS:
                return False
            
            # Tenta criar objeto gTTS
            tts = self.gTTS(text="teste", lang=self.lang)
            self.logger.info("gTTS: Disponível")
            return True
            
        except Exception as e:
            self.logger.warning(f"gTTS indisponível: {str(e)}")
            return False
    
    async def generate(self, text: str, output_path: str,
                      duration_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera áudio MP3 usando gTTS.
        
        Args:
            text: Texto a converter
            output_path: Caminho para salvar MP3
            duration_seconds: Duração esperada
            
        Returns:
            dict com status e metadata
        """
        try:
            if not self.gTTS:
                raise Exception("gTTS não configurado")
            
            self.logger.info("Gerando áudio com gTTS")
            
            # Cria objeto gTTS
            tts = self.gTTS(text=text, lang=self.lang, slow=False)
            
            # Salva MP3
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            tts.save(output_path)
            
            # Verifica se arquivo foi criado
            if not output_path_obj.exists():
                raise Exception(f"Falha ao salvar MP3 em {output_path}")
            
            file_size = output_path_obj.stat().st_size
            self.logger.info(f"gTTS: Sucesso ({file_size} bytes)")
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "provider": "gtts",
                "lang": self.lang,
                "note": "Para voz masculina grave, use edge-tts"
            }
            
        except Exception as e:
            self.logger.error(f"Erro no gTTS: {str(e)}")
            raise


class TTSManager:
    """
    Gerenciador centralizado de TTS com fallback automático.
    Tenta edge-tts primeiro (melhor qualidade), depois gTTS.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = get_logger("tts.manager")
        self.providers = []
        self._init_providers()
    
    def _init_providers(self):
        """Inicializa provedores de TTS"""
        # Edge TTS como primary
        try:
            edge = EdgeTTSProvider(voice="pt-BR-AntonioNeural")
            self.providers.append(("Edge-TTS", edge))
            self.logger.info("✅ Edge-TTS adicionado como primary")
        except Exception as e:
            self.logger.warning(f"Edge-TTS indisponível: {str(e)}")
        
        # gTTS como fallback
        try:
            gtts = GTTSProvider(lang="pt-br")
            self.providers.append(("gTTS", gtts))
            self.logger.info("✅ gTTS adicionado como fallback")
        except Exception as e:
            self.logger.warning(f"gTTS indisponível: {str(e)}")
        
        if not self.providers:
            self.logger.error("❌ Nenhum provedor de TTS disponível!")
    
    async def generate(self, text: str, output_path: str,
                      duration_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera áudio tentando cada provedor em ordem.
        
        Args:
            text: Texto a converter
            output_path: Caminho para salvar MP3
            duration_seconds: Duração esperada (para sincronização)
            
        Returns:
            dict: {"success": bool, "output_path": str, "provider": str}
        """
        
        if not self.providers:
            return {
                "success": False,
                "error": "Nenhum provedor de TTS disponível",
                "provider": None
            }
        
        for provider_name, provider in self.providers:
            try:
                self.logger.info(f"Tentando {provider_name}...")
                is_available = await provider.is_available()
                
                if not is_available:
                    self.logger.info(f"{provider_name} indisponível, tentando próximo...")
                    continue
                
                result = await provider.generate(text, output_path, duration_seconds)
                
                return {
                    "success": True,
                    "output_path": result["output_path"],
                    "file_size": result["file_size"],
                    "provider": provider_name,
                }
                
            except Exception as e:
                self.logger.warning(f"{provider_name} falhou: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "Todos os provedores de TTS falharam",
            "provider": None
        }
    
    def get_available_providers(self) -> list:
        """Retorna lista de provedores TTS disponíveis"""
        return [name for name, _ in self.providers]
