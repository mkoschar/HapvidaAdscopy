# HapvidaAds Copy Bot – Deploy no Railway

## Arquivos necessários
- bot.py
- requirements.txt
- Procfile

---

## Passo a passo

### 1. Criar repositório no GitHub
1. Acesse github.com e crie um repositório novo (ex: `hapvida-copy-bot`)
2. Faça upload dos 3 arquivos: `bot.py`, `requirements.txt`, `Procfile`

### 2. Conectar ao Railway
1. Acesse railway.app e faça login
2. Clique em **New Project → Deploy from GitHub repo**
3. Selecione o repositório `hapvida-copy-bot`
4. O Railway vai detectar o Procfile automaticamente

### 3. Configurar variáveis de ambiente
No Railway, vá em **Variables** e adicione:

| Variável | Valor |
|---|---|
| `TELEGRAM_TOKEN` | Token do @HapvidaAdsCopy_bot (gerado no BotFather) |
| `ANTHROPIC_API_KEY` | Sua chave da Anthropic Platform |

### 4. Deploy
Clique em **Deploy**. O Railway vai instalar as dependências e iniciar o bot.

---

## Comandos disponíveis no bot

| Comando | Função |
|---|---|
| `/start` | Apresenta o bot e explica como usar |
| `/briefing` | Envia o template de briefing para preencher |
| `/reset` | Limpa o histórico e inicia nova conversa |

---

## Como o time usa

1. Abre o Telegram e busca **@HapvidaAdsCopy_bot**
2. Digite `/start`
3. Digite `/briefing` para receber o template
4. Preenche e envia
5. Bot retorna 2 variações de copy
6. Time leva para aprovação antes de publicar

---

## Observações

- O bot mantém histórico da conversa por sessão — permite refinamentos ("deixa a versão A mais curta")
- Para resetar e começar novo briefing: `/reset`
- Custo estimado: ~US$ 0,01 por copy gerado (Claude Sonnet)
