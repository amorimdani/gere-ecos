# Video Creation Agents & Skills

This file configures custom agents and skills for the Gere Ecos video generation project.

## Available Skills

All skills are automatically invoked based on triggers when working with video generation tasks.

### 1. **Video Pipeline Orchestration**

- **File**: `SKILL-video-pipeline-orchestration.md`
- **Purpose**: Master orchestration of the complete video pipeline (Content → Audio → Visual → Editor → Publisher)
- **Triggers**: Pipeline coordination, scheduling, monitoring, end-to-end workflows
- **Key Topics**: OrchestratorAgent, ScheduleManager, HealthMonitor, error recovery, 3x daily execution

### 2. **Video Agents Architecture**

- **File**: `SKILL-video-agents-architecture.md`
- **Purpose**: Understand and implement the autonomous agent system
- **Triggers**: Agent implementation, BaseAgent class, individual agent workflows
- **Key Topics**: ContentAgent, AudioAgent, VisualAgent, EditorAgent, PublisherAgent, agent lifecycle

### 3. **Video Audio Synthesis & TTS**

- **File**: `SKILL-video-audio-synthesis.md`
- **Purpose**: Master audio generation and Text-to-Speech processing
- **Triggers**: TTS providers, audio quality, voice synthesis, narration optimization
- **Key Topics**: Edge-tTS, gTTS, pyttsx3, audio caching, quality validation, effects

### 4. **Video Editing & Effects with MoviePy**

- **File**: `SKILL-video-editing-effects.md`
- **Purpose**: Master video composition, effects, and rendering
- **Triggers**: Video editing, transitions, effects, captions, rendering optimization
- **Key Topics**: MoviePy, composition, effects, codec optimization, performance tuning

### 5. **YouTube API Publishing & Automation**

- **File**: `SKILL-youtube-api-publishing.md`
- **Purpose**: Master YouTube integration and automated publishing
- **Triggers**: YouTube upload, scheduling, API integration, quota management
- **Key Topics**: OAuth2 auth, video uploads, scheduling, bulk publishing, quota handling

## Project Structure

```
gere-ecos/
├── src/agents/
│   ├── orchestrator_agent.py      # Orquestrador principal
│   ├── content_agent.py            # Geração de conteúdo
│   ├── audio_agent.py              # Síntese de áudio
│   ├── visual_agent.py             # Geração de imagens
│   ├── editor_agent.py             # Edição de vídeos
│   ├── publisher_agent.py          # Publicação YouTube
│   ├── base_agent.py               # Classe base
│   ├── schedule_manager.py         # Agendamento
│   ├── health_monitor.py           # Monitoramento
│   ├── llm_manager.py              # Abstração de LLMs
│   ├── tts_manager.py              # Abstração de TTS
│   ├── image_manager.py            # Cache de imagens
│   └── youtube_manager.py          # API YouTube
├── SKILL-video-pipeline-orchestration.md
├── SKILL-video-agents-architecture.md
├── SKILL-video-audio-synthesis.md
├── SKILL-video-editing-effects.md
├── SKILL-youtube-api-publishing.md
└── AGENTS.md                        # Este arquivo
```

## How Skills Are Triggered

When you ask me questions related to video creation, I automatically invoke the relevant skill based on keywords:

### Pipeline Questions

```
"How do I orchestrate the video pipeline?"
"Why is my video generation failing?"
"How do I schedule 3 videos per day?"
```

→ Invokes: **Video Pipeline Orchestration**

### Agent Implementation

```
"How do I create a new agent?"
"How does the ContentAgent work?"
"Agent lifecycle and architecture"
```

→ Invokes: **Video Agents Architecture**

### Audio/TTS Issues

```
"How do I generate narration?"
"Why is my audio breaking?"
"TTS provider problems"
```

→ Invokes: **Video Audio Synthesis & TTS**

### Video Editing

```
"How do I add effects to the video?"
"How do I optimize video rendering?"
"MoviePy issues"
```

→ Invokes: **Video Editing & Effects with MoviePy**

### YouTube Publishing

```
"How do I upload to YouTube?"
"YouTube API quota exceeded"
"How do I schedule video uploads?"
```

→ Invokes: **YouTube API Publishing & Automation**

## Quick Start Examples

### Generate a Video End-to-End

```python
from src.agents.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()
result = orchestrator.execute_pipeline()
```

### Monitor Pipeline Health

```python
health = orchestrator.health_monitor.get_stats()
print(f"Videos generated today: {health['total_videos']}")
print(f"Success rate: {health['success_rate']}")
```

### Generate Custom Narration

```python
from src.agents.audio_agent import create_audio_agent

audio_agent = create_audio_agent()
result = audio_agent.execute({
    'script': "Your narration text here",
    'voice_style': 'pt-BR-AntonioNeural'
})
```

### Compose Video with MoviePy

```python
from moviepy.editor import ImageSequenceClip, CompositeVideoClip

images = ["scene_1.png", "scene_2.png", "scene_3.png"]
clip = ImageSequenceClip(images, fps=30)
clip = clip.set_audio(audio_clip)
clip.write_videofile("output.mp4")
```

### Upload to YouTube

```python
from src.agents.publisher_agent import create_publisher_agent

publisher = create_publisher_agent()
result = publisher.execute({
    'video_file': 'output/video_final.mp4',
    'title': 'My Video Title',
    'description': 'Video description'
})
```

## Workflow Integration

The skills are designed to work together seamlessly:

1. **Video Pipeline Orchestration** coordinates all agents
2. **Video Agents Architecture** explains how each agent works
3. **Video Audio Synthesis** handles the AudioAgent specifically
4. **Video Editing & Effects** handles the EditorAgent specifically
5. **YouTube API Publishing** handles the PublisherAgent specifically

When you work on multi-step processes, ask me questions at any skill level:

- **High-level**: "Orchestrate a video" → Pipeline skill
- **Mid-level**: "Create narration" → Audio skill
- **Low-level**: "How do I use MoviePy?" → Editing skill

## Key Features of These Skills

✅ **Comprehensive Coverage**: Each pipeline step is documented  
✅ **Real Code Examples**: Actual working code from your project  
✅ **Troubleshooting Guides**: Common issues and solutions  
✅ **Performance Tips**: Optimization strategies  
✅ **Integration Details**: How components connect  
✅ **Testing Instructions**: How to verify functionality

## Next Steps

1. **Use the skills**: Refer to them when you need help with specific tasks
2. **Reference code**: Look at the specific file paths mentioned
3. **Run examples**: Execute the code examples provided
4. **Report issues**: If something doesn't work as documented, let me know

## Related Documentation

- **README.md**: Project overview and setup
- **MODULO_2_CONTENT_AGENT.md**: Content agent details
- **MODULO_3_AUDIO_AGENT.md**: Audio agent details
- **MODULO_4_VISUAL_AGENT.md**: Visual agent details
- **MODULO_5_EDITOR_AGENT.md**: Editor agent details
- **MODULO_6_PUBLISHER_AGENT.md**: Publisher agent details
- **MODULO_7_ORCHESTRATOR_AGENT.md**: Orchestrator agent details

---

**Created**: April 1, 2026  
**Project**: Gere Ecos - Autonomous Video Factory  
**Skills Version**: 1.0
