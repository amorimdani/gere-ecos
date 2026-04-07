# Skill: Video Editing & Effects with MoviePy

**Description**: Master video composition, editing, effects, and rendering with MoviePy. Use this skill when composing video clips, adding transitions and effects, generating captions, optimizing video export, troubleshooting rendering issues, managing video codec/resolution, or implementing custom video effects.

**Triggers**:

- "How do I edit videos?", "MoviePy", "video composition"
- "Add transitions/effects", "video effects", "visual effects"
- "Generate captions/subtitles", "add text to video"
- "Export video", "video codec", "rendering optimization"
- "Video quality issues", "rendering problems", "FFmpeg errors"
- "Slow video processing", "optimize rendering"

## Video Editing Pipeline

### EditorAgent Architecture

**Location**: `src/agents/editor_agent.py`

**Pipeline Flow**:

```
Image Sequences + Audio → Compose Clips → Add Effects → Add Captions → Render → MP4
```

## MoviePy Fundamentals

### Creating Clips

#### From Images

```python
from moviepy.editor import ImageSequenceClip

# Create clip from image sequence
image_files = ["scene_1.png", "scene_2.png", "scene_3.png"]
clip = ImageSequenceClip(image_files, fps=24)  # 24 frames/sec
```

#### From Audio

```python
from moviepy.editor import AudioFileClip

audio = AudioFileClip("narration.mp3")
duration = audio.duration  # Duração automática
```

#### Composite Clip

```python
from moviepy.editor import CompositeVideoClip

# Combina múltiplos clips
final_clip = CompositeVideoClip([
    bg_clip.set_duration(10),
    text_clip.set_start(2),
    overlay_clip.set_position('center')
])
```

## Common Effects

### 1️⃣ Transitions

#### Fade In/Out

```python
clip = clip.fadein(1).fadeout(1)  # 1 segundo fade
```

#### Speed Changes

```python
clip = clip.speedx(1.5)  # 1.5x velocity
```

#### Zoom

```python
from moviepy.editor import vfx

clip = clip.fx(vfx.resize, height=1080)  # Redimensiona
```

### 2️⃣ Text & Captions

#### Add Title

```python
from moviepy.editor import TextClip, CompositeVideoClip

txt_clip = TextClip(
    "Meu Título",
    fontsize=70,
    color='white',
    font='Arial',
    method='caption',
    size=(1920, 200)
).set_duration(3).set_position('center')

final = CompositeVideoClip([video_clip, txt_clip])
```

#### Auto Captions (Whisper)

```python
# EditorAgent integra Whisper pra legendas automáticas
import openai

def generate_captions(audio_path):
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)

    # Cria arquivo de legendas (SRT format)
    return generate_srt_from_transcript(transcript)
```

### 3️⃣ Audio Integration

#### Set Audio on Video

```python
final_clip = video_clip.set_audio(audio_clip)
```

#### Audio Editing

```python
# Muta/desmuta partes
audio_clip = audio_clip.audio_fadein(1).audio_fadeout(1)

# Ajusta volume
audio_clip = audio_clip.volumex(1.2)  # 20% mais alto
```

## Video Composition Best Practices

### Smart Layering

```python
def compose_video_layers(images, audio, effects_config):
    """
    Camadas:
    1. Background (imagens principais)
    2. Overlay (efeitos visuais)
    3. Texto (títulos/captions)
    4. Audio (narração + música)
    """

    # Base
    bg = ImageSequenceClip(images, fps=24)

    # Overlay com transparência
    overlay = ImageClip("watermark.png").set_opacity(0.3)

    # Texto
    title = TextClip("Video Title", fontsize=50, color='white')

    # Compõe
    final = CompositeVideoClip([
        bg.set_duration(audio.duration),
        overlay.set_duration(audio.duration),
        title.set_start(1).set_duration(3)
    ]).set_audio(audio)

    return final
```

## Rendering & Export

### Basic Export

```python
final_clip.write_videofile(
    "output.mp4",
    fps=30,
    codec='libx264',
    audio_codec='aac',
    threads=4
)
```

### Optimized for YouTube

```python
final_clip.write_videofile(
    "output_youtube.mp4",
    fps=30,
    codec='libx264',
    preset='medium',  # ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow
    audio_codec='aac',
    bitrate="8000k",  # 8 Mbps (YouTube HD)
    threads=8
)
```

### Parameters Explained

| Parâmetro   | Valores              | Impacto                              |
| ----------- | -------------------- | ------------------------------------ |
| **fps**     | 24/30/60             | Mais fps = arquivo maior             |
| **preset**  | ultrafast...veryslow | Mais slow = melhor qualidade         |
| **bitrate** | 4000k/8000k/16000k   | Qualidade vs tamanho                 |
| **codec**   | libx264/libx265      | x265 = menor arquivo, mais lento     |
| **threads** | 4/8/16               | Mais threads = renderiza mais rápido |

## Performance Optimization

### Memory Management

```python
# Problema: Vídeos longos causam OutOfMemory
# Solução: Processa em chunks

def render_in_chunks(clips, output_path, chunk_duration=300):
    """Renderiza vídeo em chunks (5 min cada)"""
    total_duration = sum(c.duration for c in clips)

    for start in range(0, int(total_duration), chunk_duration):
        end = min(start + chunk_duration, total_duration)
        chunk = composite[start:end]
        chunk.write_videofile(f"chunk_{start}.mp4")
```

### Rendering Speed

```python
# Dicas para acelerar renderização
final_clip.write_videofile(
    output,
    preset='ultrafast',      # Sacrifica qualidade por velocidade
    codec='mpeg4',           # Mais rápido que libx264
    verbose=False,           # Não printa logs
    logger=None
)
```

## Common Issues & Troubleshooting

| Problema                  | Causa                            | Solução                                 |
| ------------------------- | -------------------------------- | --------------------------------------- |
| **OutOfMemory**           | Vídeo muito longo/resolução alta | Aumenta chunk_size, reduz fps           |
| **FFmpeg error**          | FFmpeg não instalado             | Instala: `apt install ffmpeg` (Linux)   |
| **Rendering lento**       | Codec pesado + muitos efeitos    | Usa preset='ultrafast', reduz threads   |
| **Audio dessincronizado** | Mismatch de duração              | Valida audio.duration == video.duration |
| **Qualidade ruim**        | Bitrate baixo                    | Aumenta para 8000k+                     |
| **Arquivo grande**        | Codec ineficiente                | Usa libx265, reduz fps de 60 para 30    |

## Advanced: Custom Effects

### Create Custom Vignette

```python
import numpy as np
from moviepy.editor import VideoClip

def vignette_effect(get_frame, t, intensity=0.5):
    """Adiciona vinheta (escurecimento nas bordas)"""
    frame = get_frame(t)

    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]

    # Cria gradiente radial
    mask = np.sqrt((X - w/2)**2 + (Y - h/2)**2)
    mask = 1 - (mask / np.max(mask)) * intensity

    return (frame * mask[:,:,None]).astype(np.uint8)

# Aplicar
clip_with_vignette = clip.fl(vignette_effect, intensity=0.4)
```

## Integration with Pipeline

### EditorAgent Input

```json
{
  "image_sequences": ["scene_1.png", "scene_2.png", ...],
  "audio_file": "narration.mp3",
  "metadata": {
    "title": "Video Title",
    "description": "Video description",
    "fps": 30
  },
  "effects_config": {
    "add_subtitles": true,
    "add_watermark": true,
    "duration": 600
  }
}
```

### EditorAgent Output

```json
{
  "video_file": "output/video_final.mp4",
  "duration": 600.5,
  "resolution": "1920x1080",
  "codec": "libx264",
  "file_size": "250MB"
}
```

## Testing & Quality Checks

### Verify Video

```python
import cv2

def check_video_quality(video_path):
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration = frame_count / fps

    print(f"Duration: {duration}s | FPS: {fps} | Resolution: {width}x{height}")

    cap.release()
```

## Related Skills

- **video-agents-architecture** - EditorAgent overview
- **video-audio-synthesis** - Audio integration
- **video-pipeline-orchestration** - Orchestrates editing
- **youtube-api-publishing** - Takes output from editor
