"""
Editor Agent - Integração de Áudio + Imagens em Vídeo Sincronizado
Responsável por: Sincronização A/V, Ken Burns Effect, Transições, Rendering
"""

from __future__ import annotations
import sys
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

import numpy as np
from PIL import Image
import moviepy.editor as mpy

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentStatus
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


@dataclass
class SceneTimings:
    """Informações de timing de uma cena"""
    scene_number: int
    image_path: str
    start_time: float
    duration: float
    audio_start: float
    text_overlay: str = ""
    transition: str = "fade"  # fade, dissolve, slide


class KenBurnsEffect:
    """Gerador de efeito Ken Burns (zoom + pan) em imagens estáticas"""
    
    def __init__(self, duration: float, zoom_factor: float = 1.25, scene_number: int = 1):
        """
        Args:
            duration: Duração do efeito em segundos
            zoom_factor: Fator de zoom (1.2 = zoom de 20%)
            scene_number: Usado para variar a direção do efeito deterministicamente
        """
        self.duration = duration
        self.zoom_factor = zoom_factor
        self.scene_number = scene_number
    
    def calculate_crop_region(
        self,
        frame_number: int,
        total_frames: int,
        original_width: int,
        original_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Calcula região de crop para frame específico (simula zoom + pan)
        """
        progress = frame_number / max(total_frames - 1, 1)
        
        # Tipos de movimento baseados no número da cena
        move_type = self.scene_number % 4
        
        if move_type == 0: # Zoom In + Center
            current_zoom = 1.0 + (self.zoom_factor - 1.0) * progress
            start_x, start_y = 0, 0
        elif move_type == 1: # Zoom Out + Center
            current_zoom = self.zoom_factor - (self.zoom_factor - 1.0) * progress
            start_x, start_y = 0, 0
        elif move_type == 2: # Pan Right to Left
            current_zoom = self.zoom_factor
            start_x = (original_width - (original_width / current_zoom)) * (1 - progress)
            start_y = (original_height - (original_height / current_zoom)) / 2
        else: # Pan Left to Right
            current_zoom = self.zoom_factor
            start_x = (original_width - (original_width / current_zoom)) * progress
            start_y = (original_height - (original_height / current_zoom)) / 2

        zoomed_width = int(original_width / current_zoom)
        zoomed_height = int(original_height / current_zoom)
        
        if move_type < 2:
            x1 = int((original_width - zoomed_width) / 2)
            y1 = int((original_height - zoomed_height) / 2)
        else:
            x1 = int(start_x)
            y1 = int(start_y)
            
        x2 = x1 + zoomed_width
        y2 = y1 + zoomed_height
        
        # Clamp
        x1 = max(0, min(x1, original_width - zoomed_width))
        y1 = max(0, min(y1, original_height - zoomed_height))
        x2 = min(x2, original_width)
        y2 = min(y2, original_height)
        
        return (x1, y1, x2, y2)
    
    def apply_to_image(self, image_path: str) -> mpy.VideoClip:
        """
        Aplica Ken Burns effect a uma imagem estática
        """
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        original_height, original_width = img_array.shape[:2]
        
        fps = 30
        total_frames = int(self.duration * fps)
        
        def make_frame(t):
            frame_number = int(t * fps)
            frame_number = min(frame_number, total_frames - 1)
            
            x1, y1, x2, y2 = self.calculate_crop_region(
                frame_number, total_frames, original_width, original_height
            )
            
            cropped = img_array[y1:y2, x1:x2]
            cropped_img = Image.fromarray(cropped)
            # 1080p Target
            cropped_img = cropped_img.resize((1920, 1080), Image.Resampling.LANCZOS)
            
            return np.array(cropped_img)
        
        clip = mpy.VideoClip(make_frame, duration=self.duration)
        clip.fps = fps
        return clip


class TransitionEffect:
    """Gerenciador de transições entre clipes"""
    
    @staticmethod
    def apply_fade(clips: List[mpy.VideoClip], duration: float = 0.6) -> mpy.VideoClip:
        """Aplica crossfade entre uma lista de clipes"""
        return mpy.concatenate_videoclips(clips, method="compose", padding=-duration)


class EditorAgent(BaseAgent):
    """
    Agent responsável por edição de vídeo
    Pipeline: Audio + Imagens → Vídeo Sincronizado com Ken Burns e Legendas
    """
    
    TARGET_WIDTH = 1920
    TARGET_HEIGHT = 1080
    TARGET_FPS = 30
    
    def __init__(self):
        super().__init__(agent_name="EditorAgent", max_retries=2)
        self.config = Config()
        self.file_manager = FileManager()
    
    async def execute(self, payload: dict) -> dict:
        """
        Executa edição de vídeo completa
        """
        try:
            audio_path = payload.get("audio_path")
            scenes = payload.get("scenes", [])
            video_title = payload.get("video_title", "Video")
            theme = payload.get("theme", "")
            use_ken_burns = payload.get("use_ken_burns", True)
            add_transitions = payload.get("add_transitions", True)
            add_subtitles = payload.get("add_subtitles", True)
            output_filename = payload.get("output_filename")
            
            if not audio_path or not scenes:
                return {"success": False, "error": "Missing audio_path or scenes"}
            
            if not Path(audio_path).exists():
                return {"success": False, "error": f"Audio file not found: {audio_path}"}
            
            scenes = self._ensure_scene_images(scenes, theme)
            
            logger.info(f"🎬 Iniciando edição de vídeo: {video_title} (High Quality)")
            
            # Calcula timings
            timings = await self._calculate_scene_timings(audio_path, scenes)
            
            # Cria clipes de vídeo
            video_clips = await self._create_video_clips(
                timings,
                use_ken_burns=use_ken_burns,
                add_subtitles=add_subtitles
            )
            
            # Aplica transições
            if add_transitions and len(video_clips) > 1:
                final_video_clip = TransitionEffect.apply_fade(video_clips)
                logger.info(f"✅ Transições aplicadas")
            else:
                final_video_clip = mpy.concatenate_videoclips(video_clips)
            
            # Sincroniza áudio
            final_video = await self._combine_clips_with_audio(
                [final_video_clip],
                audio_path
            )
            
            # Renderiza
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = str(Path(self.config.output_dir) / f"video_{timestamp}.mp4")
            
            await self._render_video(final_video, output_filename)
            
            output_path = Path(output_filename)
            file_size_mb = output_path.stat().st_size / 1024 / 1024
            
            return {
                "success": True,
                "data": {
                    "output_filename": str(output_path),
                    "file_size_mb": file_size_mb,
                    "duration_seconds": final_video.duration,
                    "resolution": f"{self.TARGET_WIDTH}x{self.TARGET_HEIGHT}",
                    "fps": self.TARGET_FPS,
                    "title": video_title
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Erro na edição de vídeo: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _ensure_scene_images(self, scenes: list, theme: str) -> list:
        output_dir = Path(self.config.output_dir) / "scenes"
        output_dir.mkdir(parents=True, exist_ok=True)
        for i, scene in enumerate(scenes, 1):
            image_path = scene.get("image_path")
            if not image_path or not Path(str(image_path)).exists():
                placeholder_path = output_dir / f"placeholder_scene_{i:02d}.png"
                if not placeholder_path.exists():
                    img = Image.new("RGB", (self.TARGET_WIDTH, self.TARGET_HEIGHT), color=(20, 20, 20))
                    img.save(placeholder_path)
                scene["image_path"] = str(placeholder_path)
        return scenes
    
    async def _calculate_scene_timings(self, audio_path: str, scenes: list) -> List[SceneTimings]:
        audio_clip = mpy.AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        audio_clip.close()
        
        num_scenes = len(scenes)
        scene_duration = total_duration / num_scenes
        
        timings = []
        for i, scene in enumerate(scenes):
            start_time = i * scene_duration
            timings.append(SceneTimings(
                scene_number=i + 1,
                image_path=scene.get("image_path", ""),
                start_time=start_time,
                duration=scene_duration,
                audio_start=start_time,
                text_overlay=scene.get("script", "") # Usa o roteiro para legendas
            ))
        return timings
    
    async def _create_video_clips(
        self,
        timings: List[SceneTimings],
        use_ken_burns: bool = True,
        add_subtitles: bool = True
    ) -> List[mpy.VideoClip]:
        clips = []
        for timing in timings:
            if use_ken_burns:
                kb = KenBurnsEffect(duration=timing.duration, scene_number=timing.scene_number)
                clip = kb.apply_to_image(timing.image_path)
            else:
                clip = mpy.ImageClip(timing.image_path).set_duration(timing.duration)
                clip = clip.resize((self.TARGET_WIDTH, self.TARGET_HEIGHT))
            
            if add_subtitles and timing.text_overlay:
                clip = self._add_subtitles_to_clip(clip, timing.text_overlay)
                
            clips.append(clip)
        return clips

    def _add_subtitles_to_clip(self, clip: mpy.VideoClip, text: str) -> mpy.VideoClip:
        """Adiciona legenda estilizada ao clipe"""
        try:
            # Quebra texto em linhas curtas
            words = text.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > 40:
                    lines.append(" ".join(current_line))
                    current_line = []
            if current_line:
                lines.append(" ".join(current_line))
            
            wrapped_text = "\n".join(lines[:3]) # Limita a 3 linhas
            
            txt_clip = mpy.TextClip(
                wrapped_text,
                fontsize=50,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=1.5,
                method='caption',
                size=(self.TARGET_WIDTH * 0.8, None),
                align='center'
            )
            txt_clip = txt_clip.set_position(('center', self.TARGET_HEIGHT * 0.75)).set_duration(clip.duration)
            
            return mpy.CompositeVideoClip([clip, txt_clip])
        except Exception as e:
            logger.warning(f"Erro ao adicionar legenda (provavelmente ImageMagick faltando): {e}")
            return clip
    
    async def _combine_clips_with_audio(self, clips: List[mpy.VideoClip], audio_path: str) -> mpy.VideoClip:
        audio = mpy.AudioFileClip(audio_path)
        video = clips[0] if len(clips) == 1 else mpy.concatenate_videoclips(clips)
        
        # Sincronização fina
        if abs(video.duration - audio.duration) > 0.1:
            video = video.set_duration(audio.duration)
            
        return video.set_audio(audio)
    
    async def _render_video(self, clip: mpy.VideoClip, output_path: str) -> None:
        clip.write_videofile(
            str(output_path),
            fps=self.TARGET_FPS,
            codec='libx264',
            audio_codec='aac',
            bitrate="8000k", # Aumentado para melhor qualidade
            preset='slow',   # Melhor compressão
            ffmpeg_params=['-pix_fmt', 'yuv420p'],
            logger=None
        )
        
        # Valida arquivo gerado
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise Exception(f"Arquivo de vídeo não foi criado ou está vazio: {output_path}")
        
        file_size_mb = output_path.stat().st_size / 1024 / 1024
        logger.info(f"✅ Renderização concluída: {output_path.name} ({file_size_mb:.1f} MB)")


def create_editor_agent() -> EditorAgent:
    """Factory function para criar EditorAgent"""
    return EditorAgent()
