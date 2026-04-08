# 🚀 Guia: Rodando Gere Ecos no GitHub Codespaces

## O que é GitHub Codespaces?
- ✅ Máquina virtual **gratuita** fornecida pelo GitHub
- ✅ 60 horas/mês grátis
- ✅ Ambiente completo de desenvolvimento (VS Code na nuvem)
- ✅ Não trava seu notebook
- ✅ Acesso via navegador

---

## 📋 PASSO 1: Acessar o Codespaces

### 1.1 Ir para seu repositório
1. Abra: https://github.com/amorimdani/gere-ecos
2. Clique no botão verde **"Code"** (canto superior direito)
3. Selecione a aba **"Codespaces"**
4. Clique em **"Create codespace on main"**

**OU** use este link direto:
```
https://github.com/codespaces/new?repo=amorimdani/gere-ecos
```

### 1.2 Aguardar o carregamento
- Espere 1-2 minutos enquanto a máquina é criada
- VS Code abrirá no navegador automaticamente
- Você verá um terminal na base da tela

---

## ✅ PASSO 2: Configurar o Ambiente

Copie e cole **CADA COMANDO** no terminal do Codespaces:

### 2.1 Criar ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2.2 Instalar dependências
```bash
pip install -r requirements.txt
```

### 2.3 Configurar credenciais
Copie o arquivo `credentials.json` do seu computador:

1. No seu computador, abra: `c:\Projetos\gere-ecos\credentials.json`
2. Copie **TODO o conteúdo**
3. No Codespaces, crie um novo arquivo:
   - Clique em **Explorer** (ícone de pasta na esquerda)
   - Clique com botão direito na raiz (gere-ecos)
   - Selecione **"New File"**
   - Nome: `credentials.json`
   - Cole o conteúdo copiado

### 2.4 Criar arquivo `.env`
1. Crie novo arquivo: `.env`
2. Cole o conteúdo abaixo:
```
GOOGLE_API_KEY=sua_chave_aqui
OLLAMA_BASE_URL=http://localhost:11434
YOUTUBE_CLIENT_ID=seu_client_id
YOUTUBE_CLIENT_SECRET=seu_client_secret
DEBUG=False
LOG_LEVEL=INFO
VIDEOS_PER_DAY=3
```

3. Substitua pelos valores reais do seu `.env` local

---

## 🧪 PASSO 3: Testar o Projeto

### 3.1 Rodar um teste simples
```bash
python test_minimalista.py
```

### 3.2 Rodar o pipeline completo (DEMORA!)
```bash
python main.py
```

### 3.3 Rodar o orquestrador
```bash
python run_orchestrator_once.py
```

---

## 💡 PASSO 4: Trabalhar no Codespaces

### Editor de Código
- Left Panel: **Explorer** (navegue os arquivos)
- Edite arquivos normalmente

### Terminal
- Abra novo terminal: `Ctrl + Shift + ~` (til)
- Execute quantos comandos precisar

### Git (opcional)
O Codespaces já tem git configurado. Você pode:

```bash
# Ver status
git status

# Fazer commit
git add .
git commit -m "Minha mensagem"

# Fazer push
git push
```

---

## 📱 PASSO 5: Atalhos Úteis

| Atalho | O que faz |
|--------|-----------|
| `Ctrl + ~` | Abrir/fechar terminal |
| `Ctrl + Shift + P` | Command Palette |
| `Ctrl + B` | Mostrar/esconder sidebar |
| `Ctrl + /` | Comentar linha |
| `F5` | Debug (se configurado) |

---

## ⚠️ Limitações & Dicas

### Limitações
- ❌ 60 horas/mês (depois paga)
- ❌ Máquina durme após 30 min inativo
- ❌ Sem acesso a webcam/microfone

### Dicas
- ✅ **Pause o Codespace** quando não usar (economiza horas):
  - Vai em: https://github.com/codespaces
  - Clique nos 3 pontos (...) → Stop codespace
  
- ✅ **Máximo 4 Codespaces simultâneos** (você só tem 1)
  
- ✅ **Use VS Code Extensions**: Codespaces suporta as mesmas extensões

---

## 🆘 Resolver Problemas

### Codespace travou
```bash
# Feche a aba do navegador
# Volte para: https://github.com/codespaces
# Clique STOP
# Clique CREATE CODESPACE novamente
```

### Erro de import Python
```bash
# Verifique a ativação do venv
source .venv/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

### Falta credentials.json
```bash
# Crie manualmente (Passo 2.3)
# OU
# git clone do seu PC para copiar o arquivo
```

---

## 🎯 Fluxo Resumido

```
1. Abra: github.com/amorimdani/gere-ecos
   ↓
2. Code → Codespaces → Create
   ↓
3. Aguarde 1-2 min (VS Code abrirá)
   ↓
4. Terminal:
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ↓
5. Copie credentials.json (crie manualmente)
   ↓
6. Crie arquivo .env
   ↓
7. Execute:
   $ python main.py
   ↓
8. Pronto para desenvolver!
```

---

## 📞 Próximas Ações

### Quando estiver no Codespaces:
- ✅ Faça uma mudança de teste
- ✅ Teste o projeto
- ✅ Faça um git push
- ✅ Veja a mudança refletida no GitHub

### Se precisar de ajuda:
- Abra o **GitHub Copilot Chat** no Codespaces:
  - Atalho: `Ctrl + Shift + I`
  - Descreva o erro/dúvida
  - IA ajudará direto no Codespaces!

---

## ✨ Vantagens Resumidas

| Notebook Local | Codespaces ☁️ |
|---|---|
| ❌ Trava | ✅ Rápido (16GB RAM) |
| ❌ Disk cheio | ✅ Espaço ilimitado |
| ❌ Às vezes lento | ✅ Máquina potente |
| ❌ Deixa quente | ✅ Sem calor |
| ✅ Sempre disponível | ⚠️ 60h/mês |

---

**Pronto? Vamos lá! Depois volte aqui para confirmar que funcionou! 🚀**
