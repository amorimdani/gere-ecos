# 🎬 MÓDULO 5: EDITOR AGENT - Edição de Vídeo com Sincronização A/V

## Visão Geral

O **Editor Agent** é responsável por transformar conteúdo (áudio + imagens) em um vídeo profissional sincronizado. Implementa sincronização de áudio-vídeo, efeito Ken Burns (zoom + pan), transições suaves e renderização em MP4 de alta qualidade.

### Arquitetura

```
AudioAgent (MP3)
    ↓
EditorAgent
    ├─→ KenBurnsEffect (Zoom + Pan)
    ├─→ TransitionEffect (Fade/Slide)
    └─→ VideoCompositing
        ↓
    FinalVideo (MP4)
```

---

## 📦 Componentes Principais

### 1. **KenBurnsEffect** (Classe)

Implementa o efeito cinematográfico Ken Burns - zoom progressivo com pan suave.

```python
class KenBurnsEffect:
    def __init__(self, duration: float, zoom_factor: float = 1.3):
        """
        Args:
            duration: Duração do efeito em segundos
            zoom_factor: Fator de zoom (1.3 = 30% de zoom)
        """
```

#### Como Funciona:

**Frame 0% (Início):**

```
┌─────────────────────┐
│   Imagem 1.0x       │  Sem zoom
└─────────────────────┘
```

**Frame 50% (Meio):**

```
  ┌──────────────┐
  │ 1.15x zoom   │  Pan + zoom progressivo
  └──────────────┘
```

**Frame 100% (Final):**

```
    ┌───────┐
    │ 1.3x  │  Zoom total + pan final
    └───────┘
```

#### Método Principal:

```python
async def apply_to_image(self, image_path: str, output_path: str) -> VideoClip:
    """
    Transforma imagem estática em VideoClip com Ken Burns

    Returns:
        VideoClip de duração self.duration com efeito aplicado
    """

    # 1. Carrega imagem
    img = Image.open(image_path)
    img_array = np.array(img)

    # 2. Define função de frame
    def make_frame(t):
        frame_number = int(t * fps)

        # Calcula crop region (zoom + pan)
        x1, y1, x2, y2 = calculate_crop_region(frame_number, total_frames)

        # Crop + resize
        cropped = img_array[y1:y2, x1:x2]
        cropped_img = Image.fromarray(cropped)
        cropped_img = cropped_img.resize((1920, 1080))

        return np.array(cropped_img)

    # 3. Cria VideoClip
    clip = VideoClip(make_frame, duration=self.duration)
    return clip
```

#### Parametrização:

```python
# Suave (menos zoom)
kb_subtle = KenBurnsEffect(duration=10.0, zoom_factor=1.1)

# Normal
kb_normal = KenBurnsEffect(duration=10.0, zoom_factor=1.3)

# Dramático (mais zoom)
kb_dramatic = KenBurnsEffect(duration=10.0, zoom_factor=1.5)
```

---

### 2. **TransitionEffect** (Classe)

Gerencia transições entre clipes de vídeo.

```python
class TransitionEffect:
    @staticmethod
    def fade_transition(clip1, clip2, duration=0.5):
        """Fade in/out entre clipes"""

    @staticmethod
    def slide_transition(clip1, clip2, duration=0.5, direction="left"):
        """Slide horizontal entre clipes"""
```

#### Fade Transition:

```
Clip 1:  ████████████░░░░░░  (fade out: 1.0 → 0.0)
Clip 2:  ░░░░░░░░░░████████░  (fade in: 0.0 → 1.0)
         Frames (duration=0.5s)
```

#### Slide Transition:

```
Clip 1:  ████████████░░░░░░
Clip 2:  (slides left)
         ░░░░░░░░░░████████░
         └─ movimento horizontal
```

---

### 3. **EditorAgent** (Agent Principal)

Classe principal que orquestra todo o processo de edição.

```python
class EditorAgent(BaseAgent):
    """
    Input:
    {
        "audio_path": "output/audio_123.mp3",
        "scenes": [
            {
                "scene_number": 1,
                "image_path": "output/images/scene_1.png",
                "duration": 10.0,
                "visual_prompt": "..."
            }
        ],
        "video_title": "Estoicismo: A Filosofia de Calma",
        "theme": "estoicismo",
        "use_ken_burns": True,
        "add_transitions": True
    }

    Output:
    {
        "success": true,
        "data": {
            "output_filename": "output/video_12345.mp4",
            "file_size_mb": 125.5,
            "duration_seconds": 600.0,
            "resolution": "1920x1080",
            "fps": 30,
            "theme": "estoicismo"
        }
    }
    """

    async def execute(self, payload: dict) -> dict:
        """Pipeline principal"""

        # 1. Calcula timing das cenas
        timings = await self._calculate_scene_timings(
            payload["audio_path"],
            payload["scenes"]
        )

        # 2. Cria clipes com efeitos
        clips = await self._create_video_clips(
            timings,
            use_ken_burns=payload.get("use_ken_burns", True)
        )

        # 3. Aplica transições
        if payload.get("add_transitions"):
            clips = await self._apply_transitions(clips)

        # 4. Combina com áudio
        final = await self._combine_clips_with_audio(
            clips,
            payload["audio_path"]
        )

        # 5. Renderiza
        await self._render_video(final, payload.get("output_filename"))

        return {
            "success": True,
            "data": {...}
        }
```

---

## 🚀 Como Usar

### Instalação de Dependências

```bash
# Essencial (já em requirements.txt)
pip install moviepy ffmpeg-python Pillow numpy

# Se não tiver FFmpeg instalado:
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

---

### Uso Básico

```python
from agents import create_editor_agent

# 1. Cria agent
editor = create_editor_agent()

# 2. Prepara payload
payload = {
    "audio_path": "output/audio_123.mp3",
    "scenes": [
        {
            "scene_number": 1,
            "image_path": "output/images/scene_1.png",
            "visual_prompt": "Philosopher thinking"
        },
        {
            "scene_number": 2,
            "image_path": "output/images/scene_2.png",
            "visual_prompt": "Ancient library"
        }
    ],
    "video_title": "Estoicismo Explicado",
    "theme": "estoicismo",
    "use_ken_burns": True,
    "add_transitions": True
}

# 3. Executa
result = await editor.run(payload)

# 4. Acessa resultado
if result["success"]:
    video_data = result["data"]
    print(f"✅ Vídeo criado: {video_data['output_filename']}")
    print(f"   Tamanho: {video_data['file_size_mb']:.2f} MB")
    print(f"   Duração: {video_data['duration_seconds']:.1f}s")
```

---

### Pipeline Completo (Content → Audio → Visual → Video)

```python
from agents import (
    create_content_agent,
    create_audio_agent,
    create_visual_agent,
    create_editor_agent
)

# 1. Content
content_agent = create_content_agent()
content_result = await content_agent.run({"theme": "estoicismo"})
content = content_result["data"]

# 2. Audio
audio_agent = create_audio_agent()
audio_result = await audio_agent.run({
    "script": content["script"],
    "video_title": content["title"]
})
audio = audio_result["data"]

# 3. Visual
visual_agent = create_visual_agent()
visual_result = await visual_agent.run({
    "scenes": content["scenes"],
    "theme": content["theme"]
})
visual = visual_result["data"]

# 4. Video (NEW!)
editor_agent = create_editor_agent()
video_result = await editor_agent.run({
    "audio_path": audio["output_filename"],
    "scenes": visual["scenes"],
    "video_title": content["title"],
    "theme": content["theme"],
    "use_ken_burns": True,
    "add_transitions": True
})

if video_result["success"]:
    print("✅✅ Vídeo final criado!")
    print(f"   {video_result['data']['output_filename']}")
```

---

### Customização: Sem Ken Burns

```python
# Se preferir imagens estáticas (prequilo)
payload = {
    ...
    "use_ken_burns": False,  # Desativa efeito
    "add_transitions": True   # Mantém transições
}

result = await editor.run(payload)
```

---

### Customização: Múltiplas Transições

```python
# Para adicionar suporte a outras transições:
# Estender TransitionEffect com novos métodos

# Exemplo: Dissolve (similar a fade)
# Exemplo: Wipe (terceira imagem entra)
# Exemplo: Zoom out/in
```

---

## ⚙️ Configuração

### Variáveis

```python
# Em editor_agent.py:
TARGET_WIDTH = 1920      # Resolução horizontal
TARGET_HEIGHT = 1080     # Resolução vertical
TARGET_FPS = 30          # Frames por segundo
```

### Estrutura de Saída

```
output/
├── video_20260331_143021.mp4    # Vídeo final
├── video_20260331_143022.mp4    # Próximo vídeo
└── ...

data/
├── video_editing_log.json        # Log de edição
└── ...
```

---

## 📊 Performance

### Tempos de Renderização

| Cenário                 | Tempo    | Notas           |
| ----------------------- | -------- | --------------- |
| 10 cenas, sem Ken Burns | 2-3 min  | Rápido          |
| 10 cenas, com Ken Burns | 8-12 min | Intel i7/i9     |
| Com transições          | +20%     | Sobreposição    |
| 4K (3840x2160)          | +200%    | Não recomendado |

### Tamanho de Arquivo

| Configuração  | Tamanho     | Duração     |
| ------------- | ----------- | ----------- |
| 1080p, 10 min | ~120-150 MB | Codec H.264 |
| 1080p, 30 min | ~360-450 MB | -           |

### Requisitos de Hardware

- **Processador:** Intel i5 ou melhor
- **RAM:** 8 GB mínimo (16 GB recomendado)
- **Disco:** 500 MB espaço livre
- **GPU:** Opcional (acelera renderização)

---

## 🔧 Troubleshooting

### Problema: "FFmpeg not found"

**Solução:**

```bash
# Windows (Chocolatey)
choco install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Linux (apt)
sudo apt install ffmpeg
```

### Problema: "Movie file not found"

**Solução:** Verifique paths absolutos:

```python
import os
audio_path = os.path.abspath(audio_path)
image_path = os.path.abspath(image_path)
```

### Problema: "Out of memory during rendering"

**Solução:**

- Reduza resolução (1280x720 em vez de 1920x1080)
- Diminua FPS (24 em vez de 30)
- Processe cenas em lotes menores

### Problema: "Rendering muito lento"

**Solução:**

- Desative Ken Burns: `use_ken_burns=False`
- Desative transições: `add_transitions=False`
- Considere usar GPU (se disponível)

---

## 🎯 Recuros Avançados

### Ken Burns Customizado

```python
from agents import KenBurnsEffect

# Mais dramático
kb = KenBurnsEffect(
    duration=15.0,
    zoom_factor=1.5  # 50% de zoom
)

clip = kb.apply_to_image("image.png", None)
```

### Transições Customizadas

```python
from agents import TransitionEffect

# Slide from right
combined = TransitionEffect.slide_transition(
    clip1, clip2,
    duration=1.0,
    direction="right"
)
```

---

## 🆚 Comparação de Efeitos

| Efeito                 | Tempo    | Qualidade  | Impacto           |
| ---------------------- | -------- | ---------- | ----------------- |
| Sem efeitos            | 2 min    | Normal     | Imagens estáticas |
| Ken Burns              | 10 min   | Alta       | Movimento natural |
| Transições             | +0.2 min | Alta       | Suave entre cenas |
| Ken Burns + Transições | 12 min   | Muito Alta | Cinematográfico   |

---

## ✅ Checklist de Funcionalidades

- ✅ Sincronização áudio-vídeo
- ✅ Ken Burns effect (zoom + pan)
- ✅ Fade transitions entre clipes
- ✅ Slide transitions
- ✅ Renderização MP4 (codec H.264)
- ✅ Resolução 1920x1080
- ✅ 30 FPS
- ✅ Tratamento robusto de erros
- ✅ Logging detalhado
- ✅ Suporte a múltiplas cenas

---

## 📈 Próximos Passos

**Módulo 6: Publisher Agent** (upload para YouTube)

```python
# Fluxo:
ContentAgent → AudioAgent → VisualAgent → EditorAgent → PublisherAgent
(MOD. 2)    (MOD. 3)    (MOD. 4)   (MOD. 5)  (MOD. 6)
```

---

## 📚 Referências

- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [FFmpeg Guide](https://ffmpeg.org/documentation.html)
- [Ken Burns Effect](https://en.wikipedia.org/wiki/Ken_Burns_effect)
- [PIL/Pillow Image Processing](https://python-pillow.org/)
- [NumPy Array Operations](https://numpy.org/doc/stable/)
