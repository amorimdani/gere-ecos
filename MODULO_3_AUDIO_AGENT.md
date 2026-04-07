<!-- MÓDULO 3: AGENTE DE ÁUDIO -->

# 🎙️ Módulo 3: Agente de Áudio

## ✅ Componentes Criados

### 1. **TTSManager** (`tts_manager.py`)

Gerenciador de Text-to-Speech com fallback automático:

#### Provedores Implementados:

1. **EdgeTTSProvider** (PRIMARY)
   - Microsoft Edge Neural Voices
   - Voz: `pt-BR-AntonioNeural` (masculina, grave, profissional)
   - Qualidade: Excelente
   - Velocidade ajustável automaticamente

2. **GTTSProvider** (FALLBACK)
   - Google TTS (via gTTS)
   - Fallback quando Edge-TTS falha
   - Qualidade: Boa
   - Sem custo

#### Sistema de Fallback:

```
TRY Microsoft Edge-TTS
  ├─ ✅ Sucesso → Usa Edge-TTS
  ├─ ❌ Indisponível → Fallback automático
  └─ ❌ Não instalado → Fallback automático

FALLBACK Google gTTS
  ├─ ✅ Sucesso → Usa gTTS
  └─ ❌ Erro → Erro estruturado
```

### 2. **AudioAgent** (`audio_agent.py`)

Agente principal de geração de áudio:

#### Funcionalidades:

- ✅ Converte roteiros em MP3
- ✅ Remove marcações de cenas automaticamente
- ✅ Sincroniza com duração esperada do vídeo
- ✅ Retry automático (3 tentativas)
- ✅ Extrai metadata do áudio gerado

#### Pipeline de Geração:

```
1. Recebe roteiro do ContentAgent
   ↓
2. Limpa script (remove [CENA], [HOOK], etc)
   ↓
3. Calcula velocidade para sincronização
   ↓
4. Tenta Edge-TTS → Fallback gTTS
   ↓
5. Gera MP3 em output/
   ↓
6. Extrai metadata (duração, velocidade)
   ↓
7. Retorna dict estruturado
```

#### AudioAgentWithPydub:

Versão estendida com ajustes advanced:

- Modificação de velocidade (speed_factor)
- Modificação de pitch (semitons)
- Processamento avançado com pydub

### 3. **Test Suite**

#### `test_audio_agent.py`

- ✅ Teste de geração de áudio simples
- ✅ Teste com múltiplos temas
- ✅ Verificação de provedores disponíveis
- ✅ Teste de limpeza de scripts

#### `test_pipeline.py`

- ✅ Pipeline completo: Conteúdo → Áudio
- ✅ Teste com todos os 4 temas
- ✅ Orquestrador de testes
- ✅ Resumo e estatísticas

## 📊 Estrutura de Dados

### Input do AudioAgent

```python
{
    "script": "[roteiro completo com marcações]",
    "video_title": "Título do vídeo",
    "expected_duration_minutes": 10,
    "output_filename": "audio_output.mp3"  # opcional
}
```

### Response do AudioAgent

```python
{
    "success": True,
    "audio_path": "/path/to/audio_output.mp3",
    "output_filename": "audio_output.mp3",
    "file_size": 5242880,  # bytes
    "tts_provider": "Edge-TTS",  # ou "gTTS"
    "script_length": 1250,  # palavras
    "expected_duration_minutes": 10,
    "actual_duration_seconds": 598.5,
    "timestamp": "2026-03-31T10:30:45"
}
```

## 🚀 Como Usar

### Importação

```python
from agents import create_audio_agent

agent = create_audio_agent()
```

### Uso Básico (com roteiro)

```python
import asyncio

async def generate_audio():
    payload = {
        "script": "Sua narração aqui...",
        "video_title": "Meu Vídeo",
        "expected_duration_minutes": 10
    }

    result = await agent.run(payload)

    if result["success"]:
        audio = result["data"]
        print(f"Áudio salvo em: {audio['audio_path']}")
    else:
        print(f"Erro: {result['error']}")

asyncio.run(generate_audio())
```

### Uso Integrado (Conteúdo + Áudio)

```python
from agents import create_content_agent, create_audio_agent

async def full_pipeline():
    # Gera conteúdo
    content_agent = create_content_agent()
    content_result = await content_agent.run({"theme": "estoicismo"})
    content = content_result["data"]

    # Gera áudio a partir do roteiro
    audio_agent = create_audio_agent()
    audio_payload = {
        "script": content["script"],
        "video_title": content["title"],
        "expected_duration_minutes": int(content["metadata"]["estimated_duration_minutes"])
    }

    audio_result = await audio_agent.run(audio_payload)

    return {
        "content": content,
        "audio": audio_result["data"]
    }

asyncio.run(full_pipeline())
```

## 🧪 Testando

### Teste de Áudio Simples

```bash
python src/agents/test_audio_agent.py
```

**Esperado:**

- ✅ Detecta provedores TTS
- ✅ Gera áudio para tema específico
- ✅ Testa limpeza de scripts
- ✅ Salva arquivo MP3

### Teste de Pipeline Completo

```bash
python src/agents/test_pipeline.py
```

**Esperado:**

- ✅ Gera conteúdo + áudio integrado
- ✅ Testa múltiplos temas
- ✅ Mostra estatísticas
- ✅ Salva resultados em JSON

## 🛠️ Tratamento de Erros

O sistema é resiliente:

| Erro                   | Comportamento                 |
| ---------------------- | ----------------------------- |
| edge-tts não instalado | Fallback automático para gTTS |
| Microsoft não responde | Fallback automático para gTTS |
| gTTS falha             | Erro estruturado com detalhes |
| Script vazio           | Erro de validação             |
| Falha ao salvar        | Erro com caminho              |

## 📝 Características de Sincronização

O AudioAgent calcula automaticamente a velocidade de fala:

1. **Conta palavras no script**
2. **Estima duração padrão** (~2.33 palavras/segundo)
3. **Compara com duração esperada**
4. **Ajusta velocidade** entre -50% e +50%

**Exemplo:**

- Script: 1300 palavras
- Duração esperada: 10 minutos (600 segundos)
- Velocidade padrão criaria: ~558 segundos
- Ajuste necessário: +7.5% de velocidade

## 🔊 Vozes Disponíveis

### Edge-TTS (Recomendado)

```
Portuguesa:
- pt-PT-DuarteNeural (masculina)
- pt-PT-RaquelNeural (feminina)

Brasileira:
- pt-BR-AntonioNeural (masculina grave - PADRÃO)
- pt-BR-FranciscaNeural (feminina)
```

Para usar outra voz:

```python
from agents.tts_manager import EdgeTTSProvider

provider = EdgeTTSProvider(voice="pt-BR-FranciscaNeural")
```

## 🔄 Pipeline Completo até Agora

```
1. ContentAgent
   ↓ (roteiro + cenas)

2. AudioAgent ← VOCÊ ESTÁ AQUI
   ↓ (MP3 gerado)

3. VisualAgent (próximo)
   ↓ (imagens das cenas)

4. EditorAgent
   ↓ (vídeo montado)

5. PublisherAgent
   ↓ (publicado no YouTube)

6. OrchestratorAgent
   (3x/dia automático)
```

## 📦 Dependências

### Necessário

```txt
edge-tts           # Microsoft TTS
gtts               # Google TTS fallback
pydantic           # Validação
```

### Opcional

```txt
pydub              # Para ajustes avançados
librosa            # Para modificação de pitch
```

## ⚡ Performance

**Tempo de Geração:**

- Edge-TTS: ~5-10 segundos por vídeo
- gTTS: ~3-5 segundos por vídeo

**Tamanho de Arquivo:**

- MP3 128kbps: ~1 MB por minuto
- MP3 192kbps: ~1.5 MB por minuto

**Exemplo:**

- Vídeo de 10 minutos
- Tamanho: ~10 MB (MP3 128kbps)
- Tempo de geração: ~8 segundos (Edge-TTS)

## 📁 Arquivos Gerados

```
output/
├── audio_estoicismo_20260331_103045.mp3
├── audio_cristianismo_20260331_103055.mp3
└── audio_filosofia_20260331_103105.mp3

data/
└── conteudo_gerado.log

```

## ✨ Próximo Módulo

**Módulo 4: Agente Visual** (após confirmação)

- Geração de imagens com Pollinations.ai
- Fallback HuggingFace Stable Diffusion
- Uma imagem por cena
- Cache automático

---

**Status**: ✅ Módulo 3 Completo
