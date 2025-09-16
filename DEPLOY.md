# 🚀 Personal AI Assistant - Deploy Guide (Railway)

Este guia explica como fazer deploy do Personal AI Assistant no Railway.

## 📋 Pré-requisitos

1. **Conta no Railway**: [railway.app](https://railway.app)
2. **Chave OpenAI**: [platform.openai.com](https://platform.openai.com)
3. **Configuração de Email** (opcional): SMTP credentials

## 🔧 Configuração no Railway

### 1. Deploy Inicial

1. **Fork/Clone o repositório**
2. **Conecte ao Railway**:
   ```bash
   railway login
   railway init
   railway link
   ```

3. **Deploy automático**:
   ```bash
   railway up
   ```

### 2. Configurar Variáveis de Ambiente

No Railway Dashboard, configure as seguintes variáveis:

#### ✅ **Obrigatórias**
```env
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-key-here
SECRET_KEY=your-super-secret-key-here-change-in-production
```

#### 🔧 **Opcionais - OpenAI**
```env
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

#### 📧 **Opcionais - Email (recomendado)**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_USE_TLS=true
FROM_EMAIL=noreply@yourdomain.com
```

#### 🌐 **Opcionais - CORS e Domínios**
```env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MATERIALS_LINK=https://yourdomain.com/materials
```

### 3. Configurar Banco de Dados

Railway fornece PostgreSQL automaticamente. Não precisa configurar `DATABASE_URL` - é injetado automaticamente.

### 4. Domínio Customizado (Opcional)

1. No Railway Dashboard: **Settings > Domains**
2. Adicione seu domínio personalizado
3. Configure DNS CNAME: `your-app.railway.app`

## 📁 Estrutura de Deploy

### Arquivos Criados:
- ✅ `Procfile` - Comando de inicialização + release hook
- ✅ `railway.json` - Configuração Railway
- ✅ `requirements.txt` - Dependencies mínimas e compatíveis
- ✅ `.env.production` - Template de variáveis
- ✅ `init_db.py` - Script de inicialização do banco
- ✅ `.gitignore` - Segurança de arquivos

### Como funciona:
1. **Build**: Railway usa Nixpacks para build automático
2. **Release**: `python init_db.py` (criação automática de tabelas)
3. **Start**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Health Check**: `/health` endpoint
5. **Database**: PostgreSQL automático via Railway + SQLite local

## 🔍 Monitoramento

### Endpoints de Monitoramento:
- **Health Check**: `https://your-app.railway.app/health`
- **API Docs**: `https://your-app.railway.app/docs`
- **API Root**: `https://your-app.railway.app/`

### Logs:
```bash
railway logs --follow
```

## 🛠️ Deploy do Frontend

### Opção 1: Vercel (Recomendado)
1. Fork o repositório
2. Conecte no Vercel
3. Configure build settings:
   - **Build Command**: `cp frontend/* .`
   - **Output Directory**: `.`
4. Configure variáveis:
   ```env
   NEXT_PUBLIC_API_URL=https://your-api.railway.app
   ```

### Opção 2: Netlify
1. Deploy da pasta `frontend/`
2. Configure redirects em `_redirects`:
   ```
   /api/* https://your-api.railway.app/:splat 200
   /* /index.html 200
   ```

### Opção 3: Railway (Monorepo)
1. Crie serviço separado
2. Configure `frontend/` como root
3. Use servidor estático

## 🔐 Segurança

### Variáveis Sensíveis:
- ❌ **NÃO** commite `.env` files
- ✅ Use Railway Environment Variables
- ✅ Gere `SECRET_KEY` forte:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

### HTTPS:
- ✅ Railway fornece HTTPS automático
- ✅ Redireciona HTTP → HTTPS

## 📈 Scaling

### Railway Pricing:
- **Hobby**: $5/mês - Adequado para MVP
- **Pro**: $20/mês - Para produção

### Otimizações:
- ✅ Dependencies mínimas (sem pandas)
- ✅ Health checks configurados
- ✅ Restart policy automático

## 🐛 Troubleshooting

### Problemas Comuns:

1. **Build fails com pandas**:
   - ✅ Removido do requirements.txt

2. **CORS errors**:
   - ✅ Configure `ALLOWED_ORIGINS`
   - ✅ Verifique domínios frontend

3. **OpenAI errors**:
   - ✅ App funciona sem OpenAI (fallback)
   - ✅ Configure `OPENAI_API_KEY` quando possível

4. **Email não funciona**:
   - ✅ App funciona sem email
   - ✅ Configure SMTP quando necessário

### Debug Commands:
```bash
# Logs em tempo real
railway logs --follow

# Status do deploy
railway status

# Variáveis de ambiente
railway variables

# Restart do serviço
railway redeploy
```

## 🚀 Deploy Checklist

### Antes do Deploy:
- [ ] Conta Railway criada
- [ ] Chave OpenAI obtida
- [ ] Domínio configurado (opcional)
- [ ] SMTP configurado (opcional)

### Durante o Deploy:
- [ ] Repository connected
- [ ] Environment variables set
- [ ] Database connected (automático)
- [ ] Health check passing

### Após o Deploy:
- [ ] API funcionando: `/health`
- [ ] Frontend funcionando
- [ ] CORS configurado
- [ ] Monitoramento ativo

## 📞 Suporte

Em caso de problemas:

1. **Railway Docs**: [docs.railway.app](https://docs.railway.app)
2. **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
3. **GitHub Issues**: Abra issue no repositório

---

## 🎯 URLs de Exemplo

Após deploy, você terá:

- **API Backend**: `https://personal-ai-assistant-production.railway.app`
- **Frontend**: `https://your-frontend.vercel.app`
- **Docs**: `https://personal-ai-assistant-production.railway.app/docs`

O projeto estará live e pronto para receber usuários! 🎉