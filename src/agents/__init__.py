"""
Agentes da Fábrica de Vídeos Autônoma
"""

from .base_agent import BaseAgent, AgentStatus
from .llm_manager import LLMManager, GoogleGeminiProvider, OllamaProvider
from .content_agent import ContentAgent, create_content_agent
from .tts_manager import TTSManager, EdgeTTSProvider, GTTSProvider
from .audio_agent import AudioAgent, AudioAgentWithPydub, create_audio_agent, create_audio_agent_with_pydub
from .image_manager import (
    ImageManager,
    ImageProvider,
    PollinationsAIProvider,
    HuggingFaceProvider,
    ImageCache,
)
from .visual_agent import VisualAgent, BatchVisualAgent, create_visual_agent
from .editor_agent import EditorAgent, KenBurnsEffect, TransitionEffect, create_editor_agent
from .youtube_manager import YouTubeManager, VideoMetadata
from .publisher_agent import PublisherAgent, create_publisher_agent
from .schedule_manager import ScheduleManager, Scheduler, ScheduleEntry
from .health_monitor import HealthMonitor, HealthStatus
from .orchestrator_agent import OrchestratorAgent, create_orchestrator_agent

__all__ = [
    "BaseAgent",
    "AgentStatus",
    "LLMManager",
    "GoogleGeminiProvider",
    "OllamaProvider",
    "ContentAgent",
    "create_content_agent",
    "TTSManager",
    "EdgeTTSProvider",
    "GTTSProvider",
    "AudioAgent",
    "AudioAgentWithPydub",
    "create_audio_agent",
    "create_audio_agent_with_pydub",
    "ImageManager",
    "ImageProvider",
    "PollinationsAIProvider",
    "HuggingFaceProvider",
    "ImageCache",
    "VisualAgent",
    "BatchVisualAgent",
    "create_visual_agent",
    "EditorAgent",
    "KenBurnsEffect",
    "TransitionEffect",
    "create_editor_agent",
    "YouTubeManager",
    "VideoMetadata",
    "PublisherAgent",
    "create_publisher_agent",
    "ScheduleManager",
    "Scheduler",
    "ScheduleEntry",
    "HealthMonitor",
    "HealthStatus",
    "OrchestratorAgent",
    "create_orchestrator_agent",
]
