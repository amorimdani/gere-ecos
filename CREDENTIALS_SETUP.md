# ⚠️ Configuração de Credenciais

Este projeto requer dois arquivos de configuração com credenciais:
- `credentials.json` - Credenciais do Google OAuth
- `.env` - Variáveis de ambiente

## 📋 Estrutura Necessária

### 1. `credentials.json` (Google OAuth)

Crie o arquivo `credentials.json` na raiz do projeto com a seguinte estrutura:

```json
{
  "installed": {
    "client_id": "seu_client_id.apps.googleusercontent.com",
    "project_id": "seu_project_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "seu_client_secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Como obter:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a API do YouTube
4. Crie credenciais OAuth 2.0 (Desktop App)
5. Baixe o JSON e renomeie para `credentials.json`

### 2. `.env` (Variáveis de Ambiente)

Configure baseado em `.env.example`:

```bash
GOOGLE_API_KEY=sua_chave_api
OLLAMA_BASE_URL=http://localhost:11434
YOUTUBE_CLIENT_ID=seu_client_id
YOUTUBE_CLIENT_SECRET=seu_client_secret
OPENAI_API_KEY=opcional
```

## 🔒 Segurança

- ✅ Ambos os arquivos estão no `.gitignore`
- ✅ NÃO será feito commit destas credenciais
- ✅ Cada desenvolvedor deve ter seus próprios arquivos

## ✅ Verificar Configuração

```bash
# Teste o ambiente
python main.py
```

---

Para dúvidas, consulte a documentação do projeto.
