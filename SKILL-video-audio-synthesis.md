# Skill: Video Audio Synthesis & TTS

**Description**: Master audio generation and Text-to-Speech (TTS) processing for video narration. Use this skill when implementing TTS functionality, handling multiple TTS providers, troubleshooting audio quality issues, optimizing audio processing, managing audio caching, implementing voice effects, or debugging narration problems.

**Triggers**:

- "How do I generate audio/narration?"
- "TTS problems", "audio quality issues", "narration sounds bad"
- "Edge-tTS", "gTTS", "pyttsx3", TTS provider"
- "Audio processing", "voice synthesis", "narration optimization"
- "Audio cache", "voice effects", "audio normalization"
- "Why is my audio breaking?", "TTS API failed"

## Audio Generation Pipeline

### TTS Providers (Fallback Chain)

#### 1️⃣ Edge-tTS (Preferred - FREE & Natural)

- **Pros**: Vozes naturais, grátis, sem limite de rate
- **Cons**: Dependencia de internet, latência
- **Voices**: Português BR, EN, ES, etc
- **Usage**:

```python
import edge_tts
import asyncio

async def generate_audio():
    communicate = edge_tts.Communicate(
        text="Seu roteiro de narração",
        voice="pt-BR-AntonioNeural",
        rate=0  # Naturalidade
    )
    await communicate.save("output.mp3")
```

#### 2️⃣ gTTS (Google Text-to-Speech - Backup)

- **Pros**: Simples, multilíngue, confiável
- **Cons**: Vozes robóticas, limite de caracteres
- **Usage**:

```python
from gtts import gTTS

tts = gTTS(text="Seu roteiro", lang='pt-br')
tts.save("output.mp3")
```

#### 3️⃣ pyttsx3 (Local - Fallback Offline)

- **Pros**: Funciona sem internet, rápido
- **Cons**: Vozes básicas/sintetizadas
- **Usage**:

```python
import pyttsx3

engine = pyttsx3.init()
engine.say("Seu roteiro")
engine.save_to_file("output.mp3")
engine.runAndWait()
```

## TTS Manager

### Location

`src/agents/tts_manager.py`

### Key Functions

```python
TTSManager:
  - synthesize(text, voice_style)  # Usa provider preferido
  - validate_quality(audio_file)   # Verifica klips/noise
  - apply_effects(audio_file)      # Normaliza volume/EQ
  - get_provider_status()          # Status de cada provider
  - retry_with_fallback()          # Tenta próximo provider
```

## Audio Quality Control

### Common Issues & Solutions

| Problema               | Causa                        | Solução                               |
| ---------------------- | ---------------------------- | ------------------------------------- |
| Áudio cortado/quebrado | TTS API timeout              | Aumenta timeout ou usa fallback local |
| Narração robótica      | Provider ruim (gTTS)         | Prefere Edge-tTS ou pyttsx3           |
| Volume inconsistente   | Sem normalização             | Usa librosa para normalizar           |
| Ruído/Distorção        | Taxa de amostra incompatível | Resampling para 44.1kHz               |
| Latência alta          | Processamento bloqueante     | Usa async/await em Edge-tTS           |

### Quality Metrics

```python
def validate_audio_quality(audio_path):
    y, sr = librosa.load(audio_path)

    # Detecta silêncios
    S = librosa.feature.melspectrogram(y=y, sr=sr)

    # Calcula RMS (volume)
    rms = librosa.feature.rms(S=S)[0]

    # Detecta clipping (distorção)
    peak = np.max(np.abs(y))

    return {
        'is_valid': peak < 0.95,  # Sem clipping
        'has_silence': np.min(rms) < threshold,
        'volume_level': np.mean(rms)
    }
```

## Audio Processing Pipeline

### Step-by-Step

1. **Generate**: TTS provider cria áudio base
2. **Validate**: Verifica klips/silêncios
3. **Normalize**: Equaliza volume (LUFS -16 para vídeo)
4. **Add Effects**: Opcional - reverb/compressor
5. **Export**: Salva em MP3/WAV 44.1kHz

### Code Example

```python
from src.agents.audio_agent import create_audio_agent

audio_agent = create_audio_agent()
result = audio_agent.execute({
    'script': "Seu roteiro completo aqui...",
    'voice_style': 'pt-BR-AntonioNeural',
    'output_format': 'mp3'
})

if result.success:
    print(f"Audio saved: {result.data['audio_path']}")
else:
    print(f"Error: {result.error}")
```

## Voice Selection

### Portuguese Brazilian Voices (Edge-tTS)

```
pt-BR-AntonioNeural      # Masculina, profissional
pt-BR-FranciscaNeural    # Feminina
```

### Best Practices for Voice

- **Escolha consistente**: Use mesma voz em toda série
- **Velocidade natural**: Rate = 0 (não acelera)
- **Volume constante**: Normaliza todas as narações

## Audio Caching

### Cache Directory

`data/image_cache/` (contém também refs de áudio)

### Cache Index

```json
{
  "roteiro_hash_123": {
    "audio_file": "narration_123.mp3",
    "duration": 600.5,
    "provider": "edge-tts",
    "voice": "pt-BR-AntonioNeural",
    "generated_at": "2026-04-01T10:30:00Z"
  }
}
```

### Reutilizar Áudio Cacheado

```python
# Antes de gerar novo áudio
cached_audio = cache_manager.get_audio(script_hash)
if cached_audio and cache_valid(cached_audio):
    return cached_audio  # Reutiliza
else:
    new_audio = generate_new_audio()
```

## Async Audio Processing

### Para múltiplas narações em paralelo

```python
import asyncio
from src.agents.tts_manager import TTSManager

async def process_multiple_scripts(scripts):
    tts = TTSManager()
    tasks = [
        tts.synthesize_async(script)
        for script in scripts
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Testing Audio Quality

### Test File

`test_audio_quality.py`

### Running Tests

```bash
python test_audio_quality.py
```

### Key Test Scenarios

- ✅ Edge-tTS generation
- ✅ Fallback to gTTS
- ✅ Fallback to local pyttsx3
- ✅ Volume normalization
- ✅ Silence detection
- ✅ Cache validation

## Integration with Video Pipeline

### AudioAgent → EditorAgent

```python
# AudioAgent outputs
{
    'audio_path': 'output/narration.mp3',
    'duration': 600.5,
    'sample_rate': 44100,
    'channels': 2
}

# EditorAgent expects
audio_clip = AudioFileClip(result['audio_path'])
```

## Related Skills

- **video-agents-architecture** - AudioAgent overview
- **video-content-generation** - Provides scripts for narration
- **video-editing-effects** - Integrates audio with video
- **video-pipeline-orchestration** - Orchestrates audio generation
