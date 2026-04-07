# Fábrica de Vídeos Autônoma - Ecos de Sabedoria

📚 **Conceito**: Gerador automático de vídeos de qualidade profissional focados em Estoicismo, Cristianismo, Filosofia e Lições de Vida. Publica automaticamente 3 vídeos por dia no YouTube.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Arquitetura](#arquitetura)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A aplicação implementa uma arquitetura baseada em **Agentes Autônomos** que orquestram cada etapa do processo de geração de vídeos:

1. **Agente de Conteúdo**: Gera roteiros com 10 minutos de duração
2. **Agente de Áudio**: Converte roteiro em narração (TTS)
3. **Agente Visual**: Gera imagens para cada cena
4. **Agente Editor**: Edita vídeo com efeitos e legendas
5. **Agente Publisher**: Publica no YouTube
6. **Agente Orquestrador**: Executa 3 vezes por dia via cron

### 🚀 Diferenciais

✅ **Custo Zero**: Usa apenas APIs gratuitas com fallbacks automáticos  
✅ **Resiliente**: Try/Catch em todas as etapas com recuperação automática  
✅ **Escalável**: Arquitetura modular baseada em agentes  
✅ **Monitorador**: Dashboard Streamlit com logs em tempo real

---

## 🛠️ Requisitos

### Sistema Operacional

- Windows 10+ / macOS / Linux
- Python 3.10+
- FFmpeg instalado no sistema

### Modelos Locais (Opcionais)

- Ollama com modelo local (fallback para LLM)
- Whisper local (para legendas)

### Credenciais Necessárias

1. **Google Gemini API** - Para roteiros
2. **YouTube API** - Para publicação
3. Opcional: **Ollama local** - Para fallback

---

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/gere-ecos.git
cd gere-ecos
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Instalar FFmpeg

```bash
# Windows (com Chocolatey)
choco install ffmpeg

# macOS (com Homebrew)
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt-get install ffmpeg
```

### 5. Configurar Ollama (Opcional)

```bash
# Download: https://ollama.ai
ollama pull llama2
ollama serve  # Em outro terminal
```

---

## ⚙️ Configuração

### 1. Copiar Arquivo de Configuração

```bash
cp .env.example .env
```

### 2. Obter Google Gemini API Key

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave e adicione ao `.env`:

```env
GOOGLE_API_KEY=sua_chave_aqui
```

### 3. Configurar YouTube API

1. Acesse: https://console.cloud.google.com
2. Crie um novo projeto
3. Ative YouTube Data API v3
4. Crie credenciais OAuth 2.0 (Desktop Application)
5. Baixe o JSON e copie ID e Secret para `.env`:

```env
YOUTUBE_CLIENT_ID=seu_id_aqui
YOUTUBE_CLIENT_SECRET=seu_secret_aqui
```

### 4. Configurar Ollama (Opcional)

Se usando Ollama como fallback:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 5. Configurar Aplicação

```env
DEBUG=False
LOG_LEVEL=INFO
VIDEOS_PER_DAY=3
VIDEO_DURATION_MINUTES=10
```

---

## 🚀 Uso

### 1. Iniciar a Aplicação

```bash
python main.py
```

A interface Streamlit abrirá automaticamente em: `http://localhost:8501`

### 2. Verificar Credenciais

- Acesse a aba "⚙️ Configuração"
- Verifique o status de cada API
- Adicione/atualize credenciais conforme necessário

### 3. Iniciar Geração

- Clique no botão "▶️ Iniciar Fábrica de Vídeos"
- Acompanhe o progresso na aba "📊 Monitoramento"

### 4. Verificar Vídeos Publicados

- Os vídeos são salvos em `output/`
- Logs em `logs/`
- Registro em `data/videos_publicados.txt`

---

## 📁 Estrutura do Projeto

```
gere-ecos/
├── src/
│   ├── agents/              # Agentes autônomos
│   │   ├── content_agent.py
│   │   ├── audio_agent.py
│   │   ├── visual_agent.py
│   │   ├── editor_agent.py
│   │   ├── publisher_agent.py
│   │   └── orchestrator_agent.py
│   ├── config/              # Configuração centralizada
│   │   ├── config.py
│   │   └── logger.py
│   ├── utils/               # Funções auxiliares
│   │   └── __init__.py
│   └── ui/                  # Interface Streamlit
│       └── streamlit_app.py
├── output/                  # Vídeos gerados
├── logs/                    # Arquivos de log
├── data/                    # Dados e registros
├── main.py                  # Entry point
├── requirements.txt         # Dependências
├── .env                     # Variáveis de ambiente
└── README.md               # Este arquivo
```

---

## 🏗️ Arquitetura

### Padrão de Agentes

Cada agente é uma classe independente com responsabilidade única:

```python
class Agent:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    async def execute(self, payload):
        """Executa a tarefa do agente"""
        try:
            # Lógica
            return resultado
        except Exception as e:
            self.logger.error(str(e))
            # Fallback
```

### Sistema de Fallback

Cada LLM possui fallback automático:

```
1. Tenta Google Gemini API
   ↓ (erro/quota)
2. Tenta Ollama Local
   ↓ (erro/indisponível)
3. Usa prompt pré-gerado
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install --upgrade -r requirements.txt
```

### Erro: "Google API quota exceeded"

- O sistema fará fallback para Ollama automaticamente
- Configure Ollama localmente

### Erro: "YouTube authentication failed"

- Verifique se o token está válido em `.env`
- Faça novo login em: `https://console.cloud.google.com`

### Erro: "FFmpeg not found"

- Instale FFmpeg conforme descrito em [Instalação](#instalação)

### Erro: "Ollama connection refused"

- Certifique-se de que Ollama está rodando: `ollama serve`
- Verifique `OLLAMA_BASE_URL` em `.env`

### Logs muito grandes

- Os logs mais antigos são compactados automaticamente
- Verifique em `logs/`

### Vídeos não sendo publicados

1. Verifique credenciais YouTube
2. Chec limitações de quota da conta
3. Consulte `logs/` para detalhes

---

## 📊 Monitoramento

### Command Line

```bash
# Ver logs em tempo real
tail -f logs/app_*.log

# Contar vídeos publicados
wc -l data/videos_publicados.txt
```

### Interface Streamlit

- Aba "📊 Monitoramento": Vídeos publicados e logs
- Aba "⚙️ Configuração": Status das APIs
- Aba "⏰ Agendador": Próximas execuções

---

## 🔐 Segurança

⚠️ **IMPORTANTE**: Nunca comitir arquivo `.env` em repositório!

```bash
# Adicionar ao .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "output/" >> .gitignore
echo "logs/" >> .gitignore
```

---

## 📈 Próximos Passos

Após confirmar esta estrutura, os próximos módulos a implementar serão:

1. **Agente de Conteúdo** - Roteiros e brainstorming
2. **Agente de Áudio** - TTS e narração
3. **Agente Visual** - Geração de imagens
4. **Agente Editor** - Montagem e legendas
5. **Agente Publisher** - Upload ao YouTube
6. **Agente Orquestrador** - Cronograma automático

---

## 📝 Licença

Este projeto é de uso pessoal. Usar responsavelmente.

---

## 🤝 Suporte

Para dúvidas ou problemas:

1. Consulte os logs em `logs/`
2. Verifique o `.env` e credenciais
3. Execute testes de conexão na aba "🛠️ Utilitários"

---

**Desenvolvido com ❤️ para criadores de conteúdo**

Última atualização: Março de 2026
