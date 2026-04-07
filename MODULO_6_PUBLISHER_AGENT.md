# 📤 MÓDULO 6: PUBLISHER AGENT - Publicação no YouTube

## Visão Geral

O **Publisher Agent** é responsável por publicar vídeos na plataforma YouTube. Implementa autenticação OAuth 2.0, upload com retry automático, metadados completos e registro de histórico de publicações.

### Arquitetura

```
EditorAgent (MP4 final)
    ↓
PublisherAgent
    ├─→ YouTubeManager
    │   ├─→ OAuth Authentication
    │   ├─→ Video Upload (com retry)
    │   ├─→ Metadata Setting
    │   └─→ Thumbnail Upload (opcional)
    │
    ├─→ Validation
    ├─→ Publishing
    └─→ Logging
        ↓
    YouTube Platform
    + videos_publicados.json
```

---

## 📦 Componentes Principais

### 1. **YouTubeManager** (Classe)

Gerencia toda interação com YouTube API v3.

```python
class YouTubeManager:
    """
    Gerenciador de YouTube API v3

    Recursos:
    - Autenticação OAuth com refresh automático
    - Upload de vídeos com retry
    - Metadados completos
    - Thumbnail customizado
    - Agendamento de publicação
    """

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    async def authenticate() -> bool:
        """
        Autentica no YouTube
        Fluxo:
        1. Tenta carregar token salvo
        2. Se expirado, faz refresh
        3. Se nenhum, inicia OAuth
        """

    async def upload_video(
        video_path: str,
        metadata: VideoMetadata,
        schedule_time: Optional[datetime]
    ) -> Tuple[bool, str]:
        """
        Upload de vídeo
        Returns: (sucesso, video_id)
        """

    async def get_channel_info() -> Dict:
        """Obtém informações do canal"""

    async def list_recent_videos(max_results: int) -> list:
        """Lista vídeos recentes"""
```

---

### 2. **VideoMetadata** (Dataclass)

Estrutura de metadados de vídeo.

```python
@dataclass
class VideoMetadata:
    title: str                          # Título do vídeo
    description: str                    # Descrição (até 5000 caracteres)
    tags: list                          # Tags (até 500 caracteres total)
    category_id: str = "22"             # 22 = People & Blogs
    privacy_status: str = "private"     # private, unlisted, public
    made_for_kids: bool = False         # Adequado para crianças?
    thumbnail_path: Optional[str] = None # Imagem customizada
```

#### Categorias Disponíveis:

| ID  | Categoria             | Uso                  |
| --- | --------------------- | -------------------- |
| 22  | People & Blogs        | Padrão para maioria  |
| 23  | Shorts                | Vídeos curtos (<60s) |
| 26  | Howto & Style         | Tutoriais            |
| 28  | Science & Technology  | Educacional          |
| 29  | Nonprofits & Activism | Social               |

---

### 3. **PublisherAgent** (Agent Principal)

Agent que orquestra publicação de vídeos.

```python
class PublisherAgent(BaseAgent):
    """
    Agent de publicação

    Pipeline:
    1. Valida vídeo
    2. Autentica YouTube
    3. Prepara metadados
    4. Faz upload
    5. Registra no histórico
    """

    async def execute(payload: dict) -> dict:
        """
        Input:
        {
            "video_path": "output/video_123.mp4",
            "title": "Estoicismo: A Filosofia de Calma",
            "description": "Um guia completo...",
            "tags": ["estoicismo", "filosofia"],
            "theme": "estoicismo",
            "privacy_status": "unlisted",  # Opcional
            "schedule_time": "2026-04-01T09:00:00"  # Opcional (fmt ISO)
        }

        Output:
        {
            "success": true,
            "data": {
                "video_id": "dQw4w9WgXcQ",
                "url": "https://youtu.be/dQw4w9WgXcQ",
                "title": "...",
                "privacy_status": "unlisted",
                "upload_time_seconds": 120
            }
        }
        """

    async def get_published_videos() -> list:
        """Retorna vídeos publicados"""

    async def get_channel_stats() -> dict:
        """Obtém estatísticas do canal"""
```

#### Fluxo Interno:

```
1. Validação
   ├─ Arquivo existe?
   ├─ Credenciais existem?
   └─ Metadados válidos?
       ↓
2. Autenticação
   ├─ Token salvo?
   ├─ Token expirado?
   └─ Iniciar OAuth?
       ↓
3. Preparação
   ├─ Gera descrição
   ├─ Formata tags
   └─ Valida categoria
       ↓
4. Upload
   ├─ Resumable upload
   ├─ Retry automático (backoff exponencial)
   └─ Progresso
       ↓
5. Pós-upload
   ├─ Thumbnail (opcional)
   ├─ Registro em histórico
   └─ Logging
```

---

## 🚀 Setup Inicial

### Passo 1: Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto
3. Nome: "Géré Ecos" (ou similar)

### Passo 2: Ativar YouTube Data API v3

1. Vá para "APIs & Services" → "Library"
2. Busque "YouTube Data API v3"
3. Clique "Enable"

### Passo 3: Criar Credenciais OAuth

1. Vá para "APIs & Services" → "Credentials"
2. Clique "Create Credentials" → "OAuth client ID"
3. Tipo: "Desktop application"
4. Baixe o JSON
5. Renomeie para `credentials.json`
6. Salve na **raiz do projeto** (`c:\Projetos\gere-ecos\credentials.json`)

### Passo 4: Autorizar no Primeiro Uso

```bash
python src/agents/test_publisher_agent.py
```

- Abrirá navegador
- Faça login com sua conta Google/YouTube
- Autorize o acesso
- Token salvo automaticamente em `data/youtube_token.json`

---

## 📝 Como Usar

### Uso Básico

```python
from agents import create_publisher_agent

# 1. Cria agent
publisher = create_publisher_agent()

# 2. Prepara payload
payload = {
    "video_path": "output/video_123.mp4",
    "title": "Estoicismo: A Filosofia de Calma",
    "description": "Um guia sobre estoicismo...",
    "tags": ["estoicismo", "filosofia", "sabedoria"],
    "theme": "estoicismo",
    "privacy_status": "unlisted",  # Publicado mas não listado
}

# 3. Publica
result = await publisher.run(payload)

# 4. Acessa resultado
if result["success"]:
    video_id = result["data"]["video_id"]
    url = result["data"]["url"]
    print(f"✅ Publicado: {url}")
```

---

### Pipeline Completo (C→A→V→E→P)

```python
from agents import (
    create_content_agent,
    create_audio_agent,
    create_visual_agent,
    create_editor_agent,
    create_publisher_agent
)

# 1. Content
content = await create_content_agent().run({"theme": "estoicismo"})

# 2. Audio
audio = await create_audio_agent().run({
    "script": content["data"]["script"],
    "video_title": content["data"]["title"]
})

# 3. Visual
visual = await create_visual_agent().run({
    "scenes": content["data"]["scenes"],
    "theme": content["data"]["theme"]
})

# 4. Editor
video = await create_editor_agent().run({
    "audio_path": audio["data"]["output_filename"],
    "scenes": visual["data"]["scenes"],
    "video_title": content["data"]["title"],
    "theme": content["data"]["theme"]
})

# 5. Publisher (NEW!)
published = await create_publisher_agent().run({
    "video_path": video["data"]["output_filename"],
    "title": content["data"]["title"],
    "description": "Um vídeo sobre estoicismo...",
    "tags": content["data"]["metadata"]["tags"],
    "theme": content["data"]["theme"],
    "privacy_status": "unlisted"
})

if published["success"]:
    print(f"✅ Vídeo publicado: {published['data']['url']}")
```

---

### Linha de Comando (CLI)

```bash
# Produzir 1 vídeo (sem publicar)
python src/agents/test_pipeline_v4_full_factory.py --theme estoicismo

# Produzir e publicar
python src/agents/test_pipeline_v4_full_factory.py --theme filosofia --publish

# Publicar como "public" (visível para todos)
python src/agents/test_pipeline_v4_full_factory.py \
  --theme cristianismo \
  --publish \
  --privacy public

# Produzir 4 vídeos (1 por tema)
python src/agents/test_pipeline_v4_full_factory.py --count 4

# Ajuda
python src/agents/test_pipeline_v4_full_factory.py --help
```

---

## 🔐 Status de Privacidade

| Status     | Visível       | Listado | Uso             |
| ---------- | ------------- | ------- | --------------- |
| `private`  | ❌            | ❌      | Desenvolvimento |
| `unlisted` | ✅ (com link) | ❌      | Teste           |
| `public`   | ✅            | ✅      | Produção        |

---

## 📊 Performance e Quotas

### Limites do YouTube API

- **Upload diário:** ~500 vídeos
- **Taxa de requisições:** 10,000 credits/dia
- **Tamanho máximo:** 256 GB por vídeo
- **Duração máxima:** 12 horas

### Performance Esperada

```
Tamanho do vídeo: 125 MB
Conexão: 10 Mbps
├─ Tempo de upload: ~100s
├─ Retry (se falho): +20s
├─ Metadados: ~5s
└─ Total: ~125s (~2 minutos)
```

---

## 📝 Arquivo de Log

Todos os vídeos publicados são registrados em `data/videos_publicados.json`:

```json
{
  "created_at": "2026-03-31T14:00:00",
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "url": "https://youtu.be/dQw4w9WgXcQ",
      "title": "Estoicismo: A Filosofia de Calma",
      "theme": "estoicismo",
      "file_size_mb": 125.5,
      "upload_time_seconds": 120,
      "privacy_status": "unlisted",
      "published_at": "2026-03-31T14:05:00"
    }
  ],
  "total_videos": 1,
  "last_published": "2026-03-31T14:05:00"
}
```

---

## 🆚 Comparação de Status

```
DESENVOLVIMENTO:
  • privacy_status: "private"
  • Visível: Apenas você
  • Sem link direto

TESTE:
  • privacy_status: "unlisted"
  • Compartilhando via link
  • Não aparece em buscas

PRODUÇÃO:
  • privacy_status: "public"
  • Todos podem ver
  • Aparece em buscas
```

---

## ✅ Checklist de Funcionalidades

- ✅ Autenticação OAuth 2.0
- ✅ Upload com retry automático
- ✅ Metadados completos
- ✅ Thumbnail customizado
- ✅ Agendamento de publicação
- ✅ Registro em histórico
- ✅ Obtenção de estatísticas do canal
- ✅ Fallback gracioso
- ✅ Tratamento robusto de erros
- ✅ Logging detalhado

---

## 🧪 Testes

```bash
# Validar setup
python src/agents/test_publisher_agent.py

# Pipeline completo (produção + publicação)
python src/agents/test_pipeline_v4_full_factory.py --publish
```

---

## 🔧 Troubleshooting

### Problema: "Credentials not found"

**Solução:**

1. Acesse Google Cloud Console
2. Crie OAuth credentials (Desktop)
3. Baixe JSON
4. Salve como `credentials.json` na raiz

### Problema: "Invalid token"

**Solução:**

```bash
# Delete token e faça login novamente
rm data/youtube_token.json
python src/agents/test_publisher_agent.py  # Re-autentica
```

### Problema: "Upload timeout"

**Solução:**

- Verifique conexão internet
- Reduza tamanho do vídeo (comprima em 1280x720)
- Tente novamente (retry automático ativa em 5s)

### Problema: "Quota exceeded"

**Solução:**

- YouTube API tem limite diário (10,000 credits)
- Espere até próximo dia
- Ou aumente quota no Google Cloud Console

---

## 📈 Próximos Passos

**Módulo 7: Orchestrator Agent** (agendamento automático)

```
Fábrica Completa:
Content (MOD 2) → Audio (MOD 3) → Visual (MOD 4)
             ↓
         Editor (MOD 5) → Publisher (MOD 6)
             ↑
    Orchestrator (MOD 7) - Executa 3x/dia automaticamente
```

---

## 📚 Referências

- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/desktop)
- [Video Upload Guide](https://developers.google.com/youtube/v3/guides/uploading_a_video)
- [Metadata Reference](https://developers.google.com/youtube/v3/docs/videos)
