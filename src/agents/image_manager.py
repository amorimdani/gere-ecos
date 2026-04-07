"""
Image Manager - Gerenciador de geração de imagens com fallback automático
Implementa Pollinations.ai com fallback para HuggingFace Stable Diffusion
"""

import sys
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import asyncio
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


class ImageProvider(ABC):
    """Interface para provedores de geração de imagem"""
    
    @abstractmethod
    async def generate(self, prompt: str, output_path: str, 
                      width: int = 512, height: int = 512) -> Dict[str, Any]:
        """Gera imagem a partir de prompt"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Verifica disponibilidade do provedor"""
        pass


class PollinationsAIProvider(ImageProvider):
    """Provedor Pollinations.ai (API Gratuita)"""
    
    def __init__(self):
        """Inicializa Pollinations.ai"""
        self.base_url = "https://image.pollinations.ai/prompt"
        self.logger = get_logger("image.pollinations")
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do Pollinations.ai"""
        try:
            import requests
            # Testa com imagem pequena
            response = requests.head(
                f"{self.base_url}/test",
                timeout=5
            )
            is_available = response.status_code < 500
            
            if is_available:
                self.logger.info("Pollinations.ai: Disponível")
            return is_available
            
        except Exception as e:
            self.logger.warning(f"Pollinations.ai indisponível: {str(e)}")
            return False
    
    async def generate(self, prompt: str, output_path: str,
                      width: int = 512, height: int = 512) -> Dict[str, Any]:
        """
        Gera imagem usando Pollinations.ai.
        
        Args:
            prompt: Descrição da imagem
            output_path: Caminho para salvar PNG
            width: Largura (recomendado 512 ou 768)
            height: Altura (recomendado 512 ou 768)
            
        Returns:
            dict com status e metadata
        """
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            self.logger.info(f"Gerando imagem com Pollinations.ai")
            
            # Constrói URL com prompt encodado
            safe_prompt = prompt.replace(" ", "%20")
            url = f"{self.base_url}/{safe_prompt}/{width}/{height}"
            
            # Faz requisição
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
            
            # Salva imagem
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Verifica se arquivo foi criado
            if not output_path_obj.exists():
                raise Exception(f"Falha ao salvar imagem em {output_path}")
            
            file_size = output_path_obj.stat().st_size
            self.logger.info(f"Pollinations.ai: Sucesso ({file_size} bytes)")
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "provider": "Pollinations.ai",
                "width": width,
                "height": height,
                "prompt": prompt
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Pollinations.ai: {str(e)}")
            raise


class HuggingFaceProvider(ImageProvider):
    """Provedor HuggingFace com Stable Diffusion local"""
    
    def __init__(self):
        """Inicializa HuggingFace/Stable Diffusion"""
        self.logger = get_logger("image.huggingface")
        self.pipeline = None
        self.device = "cpu"  # Muda para "cuda" se GPU disponível
        
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
                self.logger.info("GPU detectada, usando CUDA")
        except ImportError:
            self.logger.warning("torch não instalado")
        
        self._init_pipeline()
    
    def _init_pipeline(self):
        """Inicializa pipeline de Stable Diffusion"""
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            self.logger.info("Carregando Stable Diffusion (primeira vez pode demorar)...")
            
            # Carrega modelo
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_auth_token=False
            ).to(self.device)
            
            self.logger.info("✅ Stable Diffusion carregado")
            
        except ImportError:
            self.logger.warning("diffusers/torch não instalados")
            self.pipeline = None
        except Exception as e:
            self.logger.error(f"Erro ao carregar Stable Diffusion: {str(e)}")
            self.pipeline = None
    
    async def is_available(self) -> bool:
        """Verifica disponibilidade do HuggingFace/SD"""
        if self.pipeline is None:
            return False
        
        self.logger.info("HuggingFace Stable Diffusion: Disponível")
        return True
    
    async def generate(self, prompt: str, output_path: str,
                      width: int = 512, height: int = 512) -> Dict[str, Any]:
        """
        Gera imagem usando Stable Diffusion local.
        
        Args:
            prompt: Descrição da imagem
            output_path: Caminho para salvar PNG
            width: Largura (recomendado 512 ou 768)
            height: Altura (recomendado 512 ou 768)
            
        Returns:
            dict com status e metadata
        """
        try:
            if self.pipeline is None:
                raise Exception("Stable Diffusion não carregado")
            
            self.logger.info(f"Gerando imagem com Stable Diffusion")
            
            # Dimensões devem ser múltiplos de 8
            width = (width // 8) * 8
            height = (height // 8) * 8
            
            # Gera imagem
            with torch.no_grad():
                image = self.pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=30,
                    guidance_scale=7.5
                ).images[0]
            
            # Salva imagem
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            # Verifica se arquivo foi criado
            if not output_path_obj.exists():
                raise Exception(f"Falha ao salvar imagem em {output_path}")
            
            file_size = output_path_obj.stat().st_size
            self.logger.info(f"Stable Diffusion: Sucesso ({file_size} bytes)")
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "provider": "HuggingFace/Stable Diffusion",
                "width": width,
                "height": height,
                "prompt": prompt,
                "steps": 30
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Stable Diffusion: {str(e)}")
            raise


class ImageCache:
    """Cache de imagens para evitar regeneração"""
    
    def __init__(self, cache_dir: str):
        """
        Inicializa cache de imagens.
        
        Args:
            cache_dir: Diretório para armazenar cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index_path = self.cache_dir / "cache_index.json"
        self.logger = get_logger("image.cache")
        self.index = self._load_index()
    
    def _hash_prompt(self, prompt: str) -> str:
        """Gera hash do prompt para chave de cache"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _load_index(self) -> Dict[str, Any]:
        """Carrega índice de cache"""
        try:
            if self.cache_index_path.exists():
                with open(self.cache_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar índice de cache: {str(e)}")
        
        return {}
    
    def _save_index(self):
        """Salva índice de cache"""
        try:
            with open(self.cache_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"Erro ao salvar índice de cache: {str(e)}")
    
    def get(self, prompt: str) -> Optional[str]:
        """
        Obtém imagem em cache se existir.
        
        Args:
            prompt: Prompt da imagem
            
        Returns:
            Caminho da imagem em cache ou None
        """
        hash_key = self._hash_prompt(prompt)
        
        if hash_key in self.index:
            cached_path = self.index[hash_key]["path"]
            if Path(cached_path).exists():
                self.logger.info(f"Cache hit para: {prompt[:50]}...")
                return cached_path
            else:
                # Remove do índice se arquivo não existe
                del self.index[hash_key]
                self._save_index()
        
        return None
    
    def set(self, prompt: str, path: str, metadata: Dict[str, Any] = None):
        """
        Adiciona imagem ao cache.
        
        Args:
            prompt: Prompt da imagem
            path: Caminho do arquivo
            metadata: Metadata adicional
        """
        hash_key = self._hash_prompt(prompt)
        
        self.index[hash_key] = {
            "prompt": prompt,
            "path": path,
            "created_at": __import__('datetime').datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self._save_index()
        self.logger.info(f"Adicionado ao cache: {prompt[:50]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_size = sum(
            Path(entry["path"]).stat().st_size 
            for entry in self.index.values() 
            if Path(entry["path"]).exists()
        )
        
        return {
            "cached_images": len(self.index),
            "total_size_mb": total_size / 1024 / 1024,
            "cache_dir": str(self.cache_dir)
        }


class ImageManager:
    """
    Gerenciador centralizado de geração de imagens com fallback automático.
    Tenta Pollinations.ai primeiro, depois HuggingFace Stable Diffusion.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = get_logger("image.manager")
        self.providers = []
        self.cache = ImageCache(os.path.join(self.config.data_dir, "image_cache"))
        self._init_providers()
    
    def _init_providers(self):
        """Inicializa provedores de imagem"""
        # Pollinations.ai como primary
        try:
            pollinations = PollinationsAIProvider()
            self.providers.append(("Pollinations.ai", pollinations))
            self.logger.info("✅ Pollinations.ai adicionado como primary")
        except Exception as e:
            self.logger.warning(f"Pollinations.ai indisponível: {str(e)}")
        
        # HuggingFace como fallback
        try:
            huggingface = HuggingFaceProvider()
            self.providers.append(("HuggingFace/SD", huggingface))
            self.logger.info("✅ HuggingFace/Stable Diffusion adicionado como fallback")
        except Exception as e:
            self.logger.warning(f"HuggingFace/SD indisponível: {str(e)}")
        
        if not self.providers:
            self.logger.error("❌ Nenhum provedor de imagem disponível!")
    
    async def generate(self, prompt: str, output_path: str,
                      width: int = 512, height: int = 512,
                      use_cache: bool = True) -> Dict[str, Any]:
        """
        Gera imagem tentando cada provedor em ordem, com cache.
        
        Args:
            prompt: Descrição da imagem
            output_path: Caminho para salvar imagem
            width: Largura de imagem
            height: Altura de imagem
            use_cache: Se deve usar cache
            
        Returns:
            dict: {"success": bool, "output_path": str, "provider": str}
        """
        
        # Verifica cache primeiro
        if use_cache:
            cached_path = self.cache.get(prompt)
            if cached_path:
                return {
                    "success": True,
                    "output_path": cached_path,
                    "file_size": Path(cached_path).stat().st_size,
                    "provider": "CACHE",
                    "from_cache": True
                }
        
        if not self.providers:
            return {
                "success": False,
                "error": "Nenhum provedor de imagem disponível",
                "provider": None
            }
        
        for provider_name, provider in self.providers:
            try:
                self.logger.info(f"Tentando {provider_name}...")
                is_available = await provider.is_available()
                
                if not is_available:
                    self.logger.info(f"{provider_name} indisponível, tentando próximo...")
                    continue
                
                result = await provider.generate(prompt, output_path, width, height)
                
                # Adiciona ao cache
                if use_cache and result["success"]:
                    self.cache.set(prompt, result["output_path"], {
                        "width": width,
                        "height": height,
                        "provider": provider_name
                    })
                
                return {
                    "success": True,
                    "output_path": result["output_path"],
                    "file_size": result["file_size"],
                    "provider": provider_name,
                    "from_cache": False
                }
                
            except Exception as e:
                self.logger.warning(f"{provider_name} falhou: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "Todos os provedores de imagem falharam",
            "provider": None
        }
    
    def get_available_providers(self) -> list:
        """Retorna lista de provedores disponíveis"""
        return [name for name, _ in self.providers]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return self.cache.get_stats()
