# Skill: Video Agents Architecture

**Description**: Understand and work with the autonomous agent system for video creation. Use this skill when implementing new agents, understanding the BaseAgent architecture, creating custom agent behaviors, debugging agent-specific issues, managing agent lifecycle, or optimizing individual agent performance.

**Triggers**:

- "How do I create a new agent?"
- "Agent architecture", "BaseAgent", "agent workflow"
- "How does [agent_name] work?"
- "Debug agent failures", "agent performance", "agent lifecycle"
- "Implement custom agent behavior"

## Agent Architecture Overview

### BaseAgent (Foundation)

All agents inherit from `BaseAgent` in `base_agent.py`:

```python
class BaseAgent(BaseClass):
    - agent_name: str
    - execute(): Main execution method (override in subclasses)
    - validate_input(): Input validation
    - log_execution(): Logging and monitoring
    - get_stats(): Performance metrics
```

### The Five Agents Pipeline

#### 1️⃣ ContentAgent

- **Purpose**: Gera roteiros de vídeo sobre Filosofia/Estoicismo
- **Input**: Tema, duração desejada
- **Output**: Roteiro estruturado de ~10 minutos
- **LLM Used**: Google Gemini API (fallback: Ollama local)
- **File**: `src/agents/content_agent.py`
- **Key Methods**:
  - `generate_script()` - Cria roteiro estruturado
  - `extract_scenes()` - Divide em cenas
  - `estimate_duration()` - Calcula duração real

#### 2️⃣ AudioAgent

- **Purpose**: Converte roteiro em narração profissional
- **Input**: Roteiro (texto)
- **Output**: Arquivo de áudio (WAV/MP3)
- **TTS Used**: Edge-tTS, gTTS, pyttsx3 local
- **File**: `src/agents/audio_agent.py`
- **Key Methods**:
  - `synthesize_speech()` - Gera narração
  - `validate_audio_quality()` - Verifica qualidade
  - `apply_effects()` - Adiciona efeitos/equalização

#### 3️⃣ VisualAgent

- **Purpose**: Gera imagens para cada cena do vídeo
- **Input**: Descrição de cena, contexto temático
- **Output**: Imagens PNG/JPG
- **Image Gen**: Diffusers (Stable Diffusion local ou API)
- **File**: `src/agents/visual_agent.py`
- **Key Methods**:
  - `generate_image()` - Cria imagem por cena
  - `cache_images()` - Implementa cache de imagens
  - `validate_aesthetic()` - Valida qualidade/consistência

#### 4️⃣ EditorAgent

- **Purpose**: Edita vídeo final com imagens, áudio e efeitos
- **Input**: Sequências de imagens + áudio + metadados
- **Output**: Vídeo MP4 final
- **Video Lib**: MoviePy
- **File**: `src/agents/editor_agent.py`
- **Key Methods**:
  - `compose_clips()` - Monta clips
  - `add_effects()` - Adiciona transições/efeitos
  - `add_captions()` - Gera legendas (OpenAI Whisper)
  - `export_video()` - Renderiza vídeo final

#### 5️⃣ PublisherAgent

- **Purpose**: Publica vídeo finalizado no YouTube
- **Input**: Vídeo MP4 + metadados (título, descrição, tags)
- **Output**: URL do vídeo publicado
- **API Used**: YouTube Data API v3
- **File**: `src/agents/publisher_agent.py`
- **Key Methods**:
  - `upload_video()` - Faz upload
  - `set_metadata()` - Define título/descrição/tags
  - `schedule_publish()` - Agenda publicação
  - `update_stats()` - Registra estatísticas

## Agent State Management

### Input/Output Contracts

Each agent follows this pattern:

```python
# Input: ScheduleEntry (time) → OrchestratorAgent
# Processing: Agent.execute()
# Output: AgentResult(success: bool, data: dict, error: Optional[str])
```

### Error Handling Pattern

```python
try:
    result = agent.execute()
except Exception as e:
    log_error(e)
    return fallback_result()  # Use secondary method
```

## Subagent Specialization

### Managers/Support Classes

- **LLMManager** (`llm_manager.py`): Abstrai chamadas a diferentes LLMs
- **TTSManager** (`tts_manager.py`): Abstrai providers de TTS
- **ImageManager** (`image_manager.py`): Gerencia geração/cache de imagens
- **YouTubeManager** (`youtube_manager.py`): Encapsula YouTube API

## Common Agent Patterns

### Adding a New Agent

1. **Inherit from BaseAgent**: `class NewAgent(BaseAgent)`
2. **Implement execute()**: Callback principal
3. **Add input validation**: Valida contrato de entrada
4. **Implement retry logic**: Try/catch com fallbacks
5. **Log everything**: Use logger para debugging
6. **Register in OrchestratorAgent**: Adiciona ao pipeline

### Agent Communication

Agentes se comunicam via **files/storage** (não compartilham memória):

```python
# AgentA output
output_path = f"data/agent_outputs/{scene_id}.json"
save_json(scene_metadata, output_path)

# AgentB input
scene_data = load_json(output_path)
```

## Performance Optimization

| Aspecto      | Estratégia                                                         |
| ------------ | ------------------------------------------------------------------ |
| **Memory**   | Processa streams/chunks ao invés de carregar tudo em RAM           |
| **Speed**    | Paraleliza agentes independentes (Visual/Audio podem rodar juntos) |
| **Cache**    | Implementa cache em image_manager.py e reutiliza assets            |
| **Fallback** | Cada agente tem 2-3 métodos alternativos (APIs diferentes)         |

## Testing Individual Agents

### ContentAgent Test

```bash
python -m src.agents.test_content_agent
```

### AudioAgent Test

```bash
python -m src.agents.test_audio_agent
```

### VisualAgent Test

```bash
python -m src.agents.test_visual_agent
```

## Related Skills

- **video-pipeline-orchestration** - Coordenação entre agentes
- **video-content-generation** - ContentAgent deep dive
- **video-audio-synthesis** - AudioAgent deep dive
- **video-editing-effects** - EditorAgent deep dive
- **youtube-api-publishing** - PublisherAgent deep dive
