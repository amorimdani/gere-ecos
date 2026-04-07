"""
Visual Agent - Responsável por gerar imagens para cada cena do vídeo
Uma imagem por cena, otimizada para vídeo 1080p
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from agents.image_manager import ImageManager
from config.logger import get_logger

logger = get_logger(__name__)


class VisualAgent(BaseAgent):
    """
    Agente responsável por:
    1. Receber cenas do ContentAgent
    2. Gerar uma imagem por cena com prompts otimizados
    3. Usar Pollinations.ai com fallback para Stable Diffusion
    4. Aplicar cache automático
    5. Otimizar para 1080p (100% de retenção visual)
    """
    
    # Configurações de imagem
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    IMAGE_STYLE = "hyper-realistic, cinematic lighting, 8k, highly detailed, professional photography, masterpiece, dramatic atmosphere"
    NEGATIVE_PROMPT = "blurry, low quality, distorted, text, watermark, bad anatomy, low resolution"

    def __init__(self):
        super().__init__(agent_name="VisualAgent", max_retries=3)
        self.image_manager = ImageManager(self.config)
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o pipeline de geração de imagens.
        """
        scenes = payload.get("scenes")
        if not scenes:
            raise ValueError("Scenes são obrigatórias no payload")
        
        theme = payload.get("theme", "tema_desconhecido")
        use_cache = payload.get("use_cache", True)
        
        self.log_info(f"Gerando imagens para {len(scenes)} cenas ({theme}) - Cache: {'ON' if use_cache else 'OFF'}")
        
        enhanced_scenes = await self._generate_scene_images(
            scenes=scenes,
            theme=theme,
            use_cache=use_cache
        )
        
        stats = self._calculate_stats(enhanced_scenes)
        self.log_info(f"Imagens geradas: {stats['total_generated']} (cache: {stats['total_cached']})")
        
        return {
            "scenes": enhanced_scenes,
            "theme": theme,
            "statistics": stats,
            "cache_stats": self.image_manager.get_cache_stats(),
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_scene_images(self, scenes: List[Dict[str, Any]], theme: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        tasks = []
        for i, scene in enumerate(scenes, 1):
            tasks.append(self._generate_single_image(i, scene, theme, use_cache))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for scene, result in zip(scenes, results):
            if isinstance(result, Exception):
                self.log_error(f"Erro ao gerar imagem: {str(result)}")
                scene["image_path"] = None
                scene["image_generated"] = False
            else:
                scene.update(result)
        return scenes

    async def _generate_single_image(self, scene_number: int, scene: Dict[str, Any], theme: str, use_cache: bool = True) -> Dict[str, Any]:
        visual_prompt = scene.get("visual_prompt") or scene.get("title", "Cena")
        enriched_prompt = self._enrich_prompt(visual_prompt, theme)
        enriched_prompt = f"[Scene {scene_number}] {enriched_prompt}"
        
        output_filename = f"scene_{scene_number:02d}_{theme.replace(' ', '_')}.png"
        output_path = os.path.join(self.config.output_dir, "scenes", output_filename)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        result = await self.image_manager.generate(
            prompt=enriched_prompt,
            output_path=output_path,
            width=self.IMAGE_WIDTH,
            height=self.IMAGE_HEIGHT,
            use_cache=use_cache
        )
        
        if result["success"]:
            return {
                "image_path": result["output_path"],
                "image_filename": output_filename,
                "image_size_mb": result["file_size"] / 1024 / 1024,
                "image_provider": result["provider"],
                "image_generated": True,
                "image_prompt": enriched_prompt,
                "image_from_cache": result.get("from_cache", False)
            }
        return {"image_path": None, "image_generated": False}

    def _enrich_prompt(self, prompt: str, theme: str) -> str:
        """Enriquece prompt visual com estilo e contexto."""
        theme_context = {
            "estoicismo": "stoic philosophy, ancient Rome, marble statues, moody lighting, profound silence",
            "cristianismo": "divine light, biblical landscapes, ethereal atmosphere, sacred art style",
            "filosofia": "contemplative mood, library, classical academy, soft lighting, intellectual depth",
            "licoes_de_vida": "emotional storytelling, cinematic realism, warm lighting, inspiring composition"
        }
        context = theme_context.get(theme.lower().replace(" ", "_"), "professional cinematography, high contrast")
        return f"{prompt}. {context}, {self.IMAGE_STYLE}. --no {self.NEGATIVE_PROMPT}"
    
    def _calculate_stats(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(scenes)
        generated = sum(1 for s in scenes if s.get("image_generated", False))
        cached = sum(1 for s in scenes if s.get("image_from_cache", False))
        return {
            "total_scenes": total,
            "total_generated": generated,
            "total_cached": cached,
            "success_rate": f"{(generated/total)*100:.1f}%" if total > 0 else "0%"
        }


class BatchVisualAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="BatchVisualAgent", max_retries=1)
        self.visual_agent = VisualAgent()
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        videos = payload.get("videos", [])
        tasks = [self.visual_agent.execute(video) for video in videos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {"results": results}


def create_visual_agent() -> VisualAgent:
    return VisualAgent()


def create_batch_visual_agent() -> BatchVisualAgent:
    return BatchVisualAgent()
