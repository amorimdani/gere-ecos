"""
LLM Manager - Gerenciar múltiplos LLMs com fallback automático
Implementa Google Gemini com fallback para Ollama local
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Interface para provedores de LLM"""
    
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Gera texto baseado no prompt"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Verifica se o provedor está disponível"""
        pass


class GoogleGeminiProvider(LLMProvider):
    """Provedor Google Gemini API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Modelo atualizado ("gemini-pro" foi descontinuado)
        self.model_name = "gemini-1.5-flash"
        self.logger = get_logger("llm.gemini")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.logger.info("Google Gemini inicializado")
        except ImportError:
            self.logger.warning("google-generativeai não instalado")
            self.client = None
        except Exception as e:
            self.logger.error(f"Erro ao configurar Gemini: {str(e)}")
            self.client = None
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do Gemini"""
        try:
            if not self.client:
                return False
            # Teste rápido com prompt vazio
            response = self.client.generate_content("test")
            return response is not None
        except Exception as e:
            self.logger.warning(f"Gemini indisponível: {str(e)}")
            return False
    
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Gera texto usando Google Gemini"""
        try:
            if not self.client:
                raise Exception("Gemini não configurado")
            
            self.logger.info(f"Gerando com Gemini (tokens: {max_tokens})")
            
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            )
            
            if response.text:
                self.logger.info("Gemini: Sucesso")
                return response.text
            else:
                raise Exception("Resposta vazia do Gemini")
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                self.logger.warning(f"Quota excedida no Gemini: {error_msg}")
            else:
                self.logger.error(f"Erro no Gemini: {error_msg}")
            raise


class OllamaProvider(LLMProvider):
    """Provedor Ollama Local"""
    
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
        self.logger = get_logger("llm.ollama")
        self.client = None
        
        try:
            import ollama
            self.client = ollama
            self.logger.info(f"Ollama inicializado (modelo: {model_name})")
        except ImportError:
            self.logger.warning("ollama não instalado")
        except Exception as e:
            self.logger.error(f"Erro ao configurar Ollama: {str(e)}")
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do Ollama"""
        try:
            if not self.client:
                return False
            
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            is_available = response.status_code == 200
            
            if is_available:
                self.logger.info("Ollama disponível")
            return is_available
            
        except Exception as e:
            self.logger.warning(f"Ollama indisponível: {str(e)}")
            return False
    
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Gera texto usando Ollama local"""
        try:
            if not self.client:
                raise Exception("Ollama não configurado")
            
            self.logger.info(f"Gerando com Ollama (modelo: {self.model_name})")
            
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False,
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            )
            
            if response and "response" in response:
                self.logger.info("Ollama: Sucesso")
                return response["response"].strip()
            else:
                raise Exception("Resposta vazia do Ollama")
                
        except Exception as e:
            self.logger.error(f"Erro no Ollama: {str(e)}")
            raise


class LLMManager:
    """
    Gerenciador centralizado de LLMs com fallback automático.
    Tenta Google Gemini primeiro, depois Ollama.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = get_logger("llm.manager")
        self.providers = []
        self._init_providers()
    
    def _init_providers(self):
        """Inicializa provedores de LLM"""
        # Google Gemini como primary
        if self.config.google.api_key:
            try:
                gemini = GoogleGeminiProvider(self.config.google.api_key)
                self.providers.append(("Gemini", gemini))
                self.logger.info("✅ Google Gemini adicionado como primary")
            except Exception as e:
                self.logger.warning(f"Gemini indisponível: {str(e)}")
        else:
            self.logger.warning("⚠️ Google API Key não configurada")
        
        # Ollama como fallback
        try:
            ollama = OllamaProvider(
                self.config.ollama.base_url,
                self.config.ollama.model
            )
            self.providers.append(("Ollama", ollama))
            self.logger.info("✅ Ollama adicionado como fallback")
        except Exception as e:
            self.logger.warning(f"Ollama indisponível: {str(e)}")
        
        if not self.providers:
            self.logger.error("❌ Nenhum provedor de LLM disponível!")
    
    async def generate(self, prompt: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Gera texto tentando cada provedor em ordem.
        
        Args:
            prompt: Prompt para o LLM
            max_tokens: Número máximo de tokens
            
        Returns:
            dict: {"success": bool, "text": str, "provider": str, "error": str}
        """
        
        if not self.providers:
            return {
                "success": False,
                "error": "Nenhum provedor de LLM disponível",
                "provider": None
            }
        
        for provider_name, provider in self.providers:
            try:
                self.logger.info(f"Tentando {provider_name}...")
                is_available = await provider.is_available()
                
                if not is_available:
                    self.logger.info(f"{provider_name} indisponível, tentando próximo...")
                    continue
                
                result = await provider.generate(prompt, max_tokens)
                
                return {
                    "success": True,
                    "text": result,
                    "provider": provider_name,
                    "tokens_used": len(result.split())
                }
                
            except Exception as e:
                self.logger.warning(f"{provider_name} falhou: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "Todos os provedores falharam",
            "provider": None
        }
    
    def get_available_providers(self) -> list:
        """Retorna lista de provedores disponíveis"""
        return [name for name, _ in self.providers]
