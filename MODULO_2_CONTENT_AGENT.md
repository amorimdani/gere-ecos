<!-- MÓDULO 2: AGENTE DE CONTEÚDO -->

# 📝 Módulo 2: Agente de Conteúdo

## ✅ Componentes Criados

### 1. **BaseAgent** (`base_agent.py`)

Classe abstrata que define interface comum para todos os agentes:

- ✅ Sistema de Retry com backoff exponencial
- ✅ Tratamento de erros centralizado
- ✅ Status tracking (IDLE, RUNNING, SUCCESS, FAILED)
- ✅ Logging integrado
- ✅ Async/await support

### 2. **LLMManager** (`llm_manager.py`)

Gerenciador de LLMs com fallback automático:

#### Provedores Implementados:

1. **GoogleGeminiProvider**
   - API: Google Gemini Pro
   - Primary provider
   - Auto-fallback em quota exceeded

2. **OllamaProvider**
   - Modelo local (Llama2, Mistral, etc)
   - Fallback quando Gemini falha
   - Sem dependência de internet

#### Sistema de Fallback:

```
Tenta Google Gemini
    ↓ (erro/quota/offline)
Tenta Ollama Local
    ↓ (erro/indisponível)
Retorna erro detalhado
```

### 3. **ContentAgent** (`content_agent.py`)

Agente principal de geração de conteúdo:

#### Temas Pré-Configurados:

- 🏛️ **Estoicismo**: Marco Aurélio, Epicteto, Controle da Razão
- ✝️ **Cristianismo**: Fé, Graça, Jesus, Perdão
- 💭 **Filosofia**: Sócrates, Platão, Sabedoria, Verdade
- 🎯 **Lições de Vida**: Crescimento, Sucesso, Relacionamentos

#### Pipeline de Geração:

1. **Escolha de Tema** (aleatório ou especificado)
2. **Geração de Roteiro** (exatamente 10 minutos)
   - Abertura com HOOK impactante
   - Ganchos de retenção a cada minuto
   - 3 histórias/exemplos práticos
   - Plot twist no meio
   - CTA ao final

3. **Geração de Título e Tags**
   - Título magnético (60-70 caracteres)
   - Descrição otimizada SEO (150-200 palavras)
   - 15 tags relevantes

4. **Divisão em Cenas**
   - Automática do roteiro
   - 5 cenas por padrão
   - Estrutura: Hook → Desenvolvimento → Plot Twist → Conclusão

5. **Prompts Visuais por Cena**
   - Cada cena tem prompt para geração de imagem
   - Estilo cinematic 4K
   - Otimizado para Stable Diffusion

### 4. **Test Suite** (`test_content_agent.py`)

- ✅ Teste com tema específico (Estoicismo)
- ✅ Teste com tema aleatório
- ✅ Verificação de provedores disponíveis
- ✅ Salva resultado em JSON

## 📊 Estrutura de Dados

### Resposta do ContentAgent

```python
{
    "theme": "Estoicismo",
    "theme_key": "estoicismo",
    "script": "Abertura impactante...[roteiro completo]...CTA",
    "title": "3 Segredos Estoicos que Vão Mudar Sua Vida (Revelado!)",
    "description": "[150-200 palavras]",
    "tags": ["estoicismo", "filosofia", "autoajuda", ...],
    "scenes": [
        {
            "title": "[HOOK] - Abertura Impactante",
            "script": "[texto da cena]",
            "visual_prompt": "Abertura dramática com tema estoicismo",
            "style": "cinematic, dramatic, 4K"
        },
        ...
    ],
    "metadata": {
        "generated_at": "2026-03-31T10:30:45",
        "llm_provider": "Gemini",  # ou "Ollama"
        "word_count": 1250,
        "estimated_duration_minutes": 9.6,
        "scene_count": 5
    }
}
```

## 🚀 Como Usar

### Importação

```python
from agents import create_content_agent

agent = create_content_agent()
```

### Uso Básico (com tema específico)

```python
import asyncio

async def generate():
    payload = {"theme": "estoicismo"}
    result = await agent.run(payload)

    if result["success"]:
        content = result["data"]
        print(content["title"])
        print(content["script"])
    else:
        print(f"Erro: {result['error']}")

asyncio.run(generate())
```

### Uso com Tema Aleatório

```python
payload = {}  # Deixa vazio para tema aleatório
result = await agent.run(payload)
```

## 🧪 Testando

```bash
# No diretório do projeto
python src/agents/test_content_agent.py
```

**Esperado:**

- ✅ Detecta provedores disponíveis
- ✅ Gera conteúdo com tema específico
- ✅ Gera conteúdo com tema aleatório
- ✅ Salva resultado em `output/conteudo_teste.json`

## 🛠️ Tratamento de Erros

O sistema é resiliente:

| Erro                           | Comportamento                   |
| ------------------------------ | ------------------------------- |
| Google API Key não configurado | Fallback automático para Ollama |
| Google quota exceeded          | Fallback automático para Ollama |
| Ollama offline                 | Retorna erro claro              |
| Ambos indisponíveis            | Retorna erro estruturado        |
| Erro ao gerar JSON             | Fallback para parsing manual    |

## 📝 Integração com UI Streamlit

Já preparada para adicionar botão na UI:

```python
# Em tabs de "Monitoramento"
if st.button("🎬 Gerar Conteúdo Teste"):
    with st.spinner("Gerando..."):
        result = await agent.run({})
        if result["success"]:
            st.success(f"✅ {result['data']['title']}")
```

## 🔄 Pipeline Completo

```
ContentAgent
    ↓
LLMManager (Google Gemini ou Ollama)
    ↓
Script de 10 minutos gerado
    ↓
Título + Tags
    ↓
5 Cenas com tipos visuais
    ↓
Retorna JSON estruturado
    ↓
Próximo: Agente de Áudio (audio_agent.py)
```

## 📦 Dependências Adicionadas

```txt
google-generativeai==0.3.0  # Para Google Gemini
```

Já estava:

- `ollama==0.0.36`
- `pydantic==2.4.2`

## ✨ Diferenciais

✅ **Zero-Cost Fallback**: Tenta Gemini, cai para Ollama  
✅ **Retry Automático**: 3 tentativas com backoff  
✅ **Async/Await**: Não bloqueia UI  
✅ **Vídeos de 10 minutos**: Exatamente dimensionados  
✅ **Ganchos de Retenção**: A cada minuto  
✅ **Plot Twist**: Engajamento garantido  
✅ **Cenas Pré-divididas**: Pronto para editor  
✅ **Prompts Visuais**: Para geração de imagens

## 🎯 Próximo Módulo

**Módulo 3: Agente de Áudio**

- Converter roteiro em MP3
- edge-tts (PT-BR voice)
- Fallback para gTTS
- Sincronização com vídeo

---

**Status**: ✅ Módulo 2 Completo
