# 📸 MÓDULO 4: VISUAL AGENT - Sistema de Geração de Imagens

## Visão Geral

O **Visual Agent** é responsável por gerar imagens cinéticas profissionais para cada cena do roteiro. Funciona após o ContentAgent (que gera roteiros) e em paralelo com o AudioAgent, produzindo uma imagem **1920x1080** de alta qualidade por cena usando IA generativa.

### Arquitetura

```
ContentAgent (roteiros + cenas)
           ↓
    VisualAgent
      ↙        ↘
ImageManager  Cache
    ↙   ↘
Pollinations.ai  HuggingFace/Stable Diffusion
```

---

## 📦 Componentes Principais

### 1. `image_manager.py` (400+ linhas)

Sistema modular de geração e cache de imagens com fallback automático.

#### Classes:

##### **ImageProvider** (Classe Abstrata)

```python
class ImageProvider(ABC):
    """Interface para provedores de geração de imagens"""

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024
    ) -> dict:
        """Gera imagem a partir de prompt"""
```

**Métodos:**

- `generate_image()`: Implementação do provedor
- `validate_config()`: Verifica credenciais
- `get_name()`: Retorna nome do provedor

---

##### **PollinationsAIProvider** (Online - RECOMENDADO)

Provedor primário usando **Pollinations.ai** (serviço gratuito online).

```python
async def generate_image(self, prompt: str, width: int, height: int) -> dict:
    """
    API: https://image.pollinations.ai/prompt/{prompt}/{width}/{height}
    Resposta: Imagem PNG direta
    """
    url = f"https://image.pollinations.ai/prompt/{prompt}/{width}/{height}"
    response = requests.get(url)
    return {
        "success": response.status_code == 200,
        "image_path": local_path,
        "provider": "Pollinations.ai"
    }
```

**Vantagens:**

- ✅ Sem chave de API necessária
- ✅ Rápido (~3-5 segundos por imagem)
- ✅ Qualidade: Modelo SDXL
- ✅ Sem limites de taxa

**Limitações:**

- ⚠️ Depende de conexão internet
- ⚠️ Serviço pode ter downtime

---

##### **HuggingFaceProvider** (Local - FALLBACK)

Provedor fallback usando **Stable Diffusion v1.5** localmente.

```python
async def generate_image(self, prompt: str, width: int, height: int) -> dict:
    """
    Modelo: runwayml/stable-diffusion-v1-5
    Pipeline: diffusers.StableDiffusionPipeline
    Device: GPU (CUDA) ou CPU
    """
    from diffusers import StableDiffusionPipeline

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5"
    )
    image = pipe(prompt).images[0]
    return {"success": True, "image_path": path}
```

**Vantagens:**

- ✅ Funciona offline
- ✅ Sem limites de uso
- ✅ Controle total

**Limitações:**

- ⚠️ Requer GPU de >4GB VRAM
- ⚠️ Lento em CPU (~5-10 min por imagem)
- ⚠️ Download de modelo (~4.2 GB)
- ⚠️ Qualidade inferior ao SDXL

---

##### **ImageCache** (Sistema de Cache)

Cache inteligente com índice JSON para evitar regeneração.

```python
class ImageCache:
    def __init__(self, cache_dir: str = "data/image_cache"):
        self.cache_dir = Path(cache_dir)
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()

    def get(self, prompt: str) -> Optional[str]:
        """Retorna path da imagem em cache ou None"""
        hash_key = self._hash_prompt(prompt)
        if hash_key in self.index:
            cached_path = self.index[hash_key]["path"]
            if Path(cached_path).exists():
                return cached_path
        return None

    def put(self, prompt: str, image_path: str, metadata: dict):
        """Armazena imagem no cache com metadados"""
        hash_key = self._hash_prompt(prompt)
        self.index[hash_key] = {
            "path": image_path,
            "prompt": prompt,
            "provider": metadata.get("provider"),
            "timestamp": datetime.now().isoformat(),
            "size_bytes": Path(image_path).stat().st_size
        }
        self._save_index()
```

**Estrutura de Cache:**

```
data/image_cache/
├── cache_index.json           # Índice de prompts
├── a1b2c3d4e5f6g7h8i9j.png   # Imagem cached (nome = hash MD5)
└── ...
```

**Exemplo de índice:**

```json
{
  "a1b2c3d4e5f6": {
    "path": "data/image_cache/a1b2c3d4e5f6.png",
    "prompt": "mystical forest with glowing trees",
    "provider": "Pollinations.ai",
    "timestamp": "2024-01-15T14:30:00",
    "size_bytes": 1524284
  }
}
```

---

##### **ImageManager** (Orquestrador)

Gerencia provedores, fallback e cache.

```python
class ImageManager:
    def __init__(self):
        self.cache = ImageCache()
        self.providers = [
            PollinationsAIProvider(),    # Primary
            HuggingFaceProvider()        # Fallback
        ]

    async def generate_image(
        self,
        prompt: str,
        width: int = 1920,
        height: int = 1080,
        use_cache: bool = True
    ) -> dict:
        """
        Fluxo:
        1. Verifica cache (se use_cache=True)
        2. Tenta Pollinations.ai
        3. Se falhar, tenta HuggingFace
        4. Armazena em cache se bem-sucedido
        5. Retorna resultado ou erro
        """

        # 1. Check cache
        if use_cache:
            cached_path = self.cache.get(prompt)
            if cached_path:
                return {
                    "success": True,
                    "image_path": cached_path,
                    "from_cache": True,
                    "provider": "ImageCache"
                }

        # 2. Try providers
        for provider in self.providers:
            try:
                result = await provider.generate_image(prompt, width, height)
                if result["success"]:
                    # 4. Cache it
                    self.cache.put(prompt, result["image_path"],
                                  {"provider": result["provider"]})
                    return result
            except Exception as e:
                logger.warning(f"{provider.get_name()} failed: {e}")
                continue

        return {"success": False, "error": "All providers failed"}

    def get_available_providers(self) -> List[str]:
        """Lista provedores disponíveis"""
        return [p.get_name() for p in self.providers if p.validate_config()]
```

---

### 2. `visual_agent.py` (350+ linhas)

Agent que processa cenas e gera imagens utilizando o ImageManager.

#### Classes:

##### **VisualAgent**

Agent responsável por gerar uma imagem por cena.

```python
class VisualAgent(BaseAgent):
    """
    Gera imagens para cenas de forma sequencial
    Input: Lista de cenas com prompts
    Output: Cenas atualizadas com caminhos de imagens
    """

    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    IMAGE_STYLE = "cinematic, 4K, professional, dramatic lighting"

    async def execute(self, payload: dict) -> dict:
        """
        Payload esperado:
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration": 10,
                    "visual_prompt": "a person reading a book",
                    "theme": "estoicismo"
                }
            ],
            "theme": "estoicismo",
            "use_cache": True
        }
        """

        scenes = payload.get("scenes", [])
        theme = payload.get("theme", "")
        use_cache = payload.get("use_cache", True)

        # Gera imagens em paralelo
        results = await self._generate_scene_images(
            scenes, theme, use_cache
        )

        return {
            "scenes": results,
            "statistics": self._calculate_stats(results),
            "cache_stats": self.image_manager.get_cache_stats()
        }

    async def _generate_scene_images(
        self,
        scenes: list,
        theme: str,
        use_cache: bool
    ) -> list:
        """Gera imagens em paralelo usando asyncio.gather()"""

        tasks = [
            self._generate_single_image(i, scene, theme, use_cache)
            for i, scene in enumerate(scenes, 1)
        ]

        # Executa tudo em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _generate_single_image(
        self,
        scene_number: int,
        scene: dict,
        theme: str,
        use_cache: bool
    ) -> dict:
        """Gera uma única imagem com tratamento de erro"""

        try:
            # Enriquece prompt com contexto
            enriched_prompt = self._enrich_prompt(
                scene.get("visual_prompt", ""),
                theme
            )

            logger.info(f"Gerando imagem {scene_number}: {enriched_prompt}")

            # Gera imagem
            image_result = await self.image_manager.generate_image(
                enriched_prompt,
                self.IMAGE_WIDTH,
                self.IMAGE_HEIGHT,
                use_cache
            )

            if image_result["success"]:
                file_size_mb = (
                    Path(image_result["image_path"]).stat().st_size / 1024 / 1024
                )

                scene.update({
                    "image_generated": True,
                    "image_path": image_result["image_path"],
                    "image_filename": Path(image_result["image_path"]).name,
                    "image_provider": image_result.get("provider", "Unknown"),
                    "image_from_cache": image_result.get("from_cache", False),
                    "image_size_mb": file_size_mb
                })

                status = "📦 CACHE" if image_result.get("from_cache") else "🆕 NEW"
                logger.info(f"[{scene_number}] {status} OK")
            else:
                raise Exception(image_result.get("error", "Unknown error"))

        except Exception as e:
            logger.error(f"Erro ao gerar imagem {scene_number}: {str(e)}")
            scene.update({
                "image_generated": False,
                "image_error": str(e)
            })

        return scene

    def _enrich_prompt(self, base_prompt: str, theme: str) -> str:
        """Enriquece prompt base com contexto de tema e estilo"""

        theme_context = {
            "estoicismo": "Stoic philosophy, wisdom, inner peace,",
            "cristianismo": "Christian faith, spirituality, divine light,",
            "filosofia": "Philosophical concept, wisdom, meditation,",
            "licoes_de_vida": "Life lesson, inspirational, human connection,"
        }

        context = theme_context.get(theme, "")

        prompt = f"{context} {base_prompt}, {self.IMAGE_STYLE}"

        # Limita a 1000 caracteres
        return prompt[:1000]

    def _calculate_stats(self, scenes: list) -> dict:
        """Calcula estatísticas de geração"""

        total = len(scenes)
        generated = sum(1 for s in scenes if s.get("image_generated", False))
        cached = sum(1 for s in scenes if s.get("image_from_cache", False))
        failed = total - generated

        total_size = sum(
            s.get("image_size_mb", 0)
            for s in scenes
            if s.get("image_generated", False)
        )

        return {
            "total_scenes": total,
            "total_generated": generated,
            "total_cached": cached,
            "total_failed": failed,
            "total_size_mb": total_size,
            "success_rate": f"{(generated/total)*100:.1f}%" if total > 0 else "0%"
        }
```

---

## 🚀 Como Usar

### Instalação de Dependências

```bash
# Essencial (Pollinations.ai - online)
pip install requests Pillow

# Opcional (Stable Diffusion local - CUDA)
pip install diffusers torch transformers

# Com GPU (mais rápido)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### Uso Básico

```python
from agents import create_visual_agent

# Cria agent
visual_agent = create_visual_agent()

# Prepara payload
payload = {
    "scenes": [
        {"scene_number": 1, "visual_prompt": "philosopher in contemplation"},
        {"scene_number": 2, "visual_prompt": "ancient library with scrolls"}
    ],
    "theme": "filosofia",
    "use_cache": True
}

# Executa
result = await visual_agent.run(payload)

# Acessa resultados
if result["success"]:
    scenes = result["data"]["scenes"]
    stats = result["data"]["statistics"]
    print(f"✅ {stats['total_generated']} imagens geradas")
```

---

### Pipeline Completo

```python
from agents import (
    create_content_agent,
    create_audio_agent,
    create_visual_agent
)

# 1. Gera conteúdo
content_agent = create_content_agent()
content_result = await content_agent.run({"theme": "estoicismo"})
content = content_result["data"]

# 2. Gera áudio
audio_agent = create_audio_agent()
audio_result = await audio_agent.run({
    "script": content["script"],
    "video_title": content["title"]
})

# 3. Gera visual
visual_agent = create_visual_agent()
visual_result = await visual_agent.run({
    "scenes": content["scenes"],
    "theme": content["theme"],
    "use_cache": True
})

print("✅ Pipeline Content → Audio → Visual concluído!")
```

---

## ✅ Checklist de Funcionalidades

- ✅ Geração de imagens online (Pollinations.ai)
- ✅ Fallback local (Stable Diffusion)
- ✅ Cache inteligente com índice JSON
- ✅ Processamento paralelo com asyncio
- ✅ Enriquecimento de prompts por tema
- ✅ Tratamento robusto de erros
- ✅ Logging detalhado
- ✅ Testes unitários e de integração
- ✅ Suporte a múltiplas resoluções
- ✅ Metadata e estatísticas

---

## 📈 Próximos Passos

**Módulo 5: Editor Agent** vai integrar Content → Audio → Visual em vídeos finalizados.
