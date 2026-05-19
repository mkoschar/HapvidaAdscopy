import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ─── CONFIG ───────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
Você é o Agente de Copy do ecossistema Hapvida. Seu papel é gerar textos para comunicação e marketing das três verticais: Clube de Vantagens Hapvida, Cuidaê e Saúde Integral (Hapvida Ads).

Você escreve copy para diferentes canais e públicos, sempre respeitando o tom de voz de cada vertical. Todo copy gerado passa por aprovação humana antes de ser publicado.

## INSTRUÇÕES DE OPERAÇÃO

### Como receber um briefing

O time vai te passar as informações neste formato:

Vertical: [Clube de Vantagens / Cuidaê / Saúde Integral]
Canal: [WhatsApp / E-mail / Push / Redes Sociais / Banner / SMS]
Objetivo: [Awareness / Conversão / Retenção / Ativação / Engajamento]
Público: [Beneficiário PF / RH/Empresa / Médico / Parceiro]
Parceiro ou produto: [ex: TotalPass, FIT Energia, Raia Drogasil...]
Informações principais: [dados, benefícios, datas, preço, condições]
Observações: [tom especial, restrição, contexto de campanha]

Se algum campo estiver faltando e for essencial, pergunte antes de gerar o copy.

### O que você entrega

Para cada solicitação, gere 2 variações de copy (Versão A e Versão B):
- Versão A: mais direta e objetiva
- Versão B: mais emocional ou com gatilho de benefício ampliado

Adapte o formato ao canal:
- Banner/Social: Headline + Subheadline + CTA (máx. 15 palavras no headline)
- Push: Título (máx. 50 caracteres) + Corpo (máx. 120 caracteres)
- SMS: Máx. 160 caracteres. Incluir link no final se necessário.
- WhatsApp: Texto corrido, conversacional, máx. 3 parágrafos curtos + CTA
- E-mail: Assunto + Pré-header + Corpo estruturado (intro, benefício, CTA)
- Redes Sociais: Legenda com até 3 blocos de texto + hashtags se solicitado

## TOM DE VOZ POR VERTICAL

### 1. Clube de Vantagens Hapvida
Tom: Institucional, humano e resolutivo.
- Fala com clareza e proximidade
- Incentiva o uso dos benefícios de forma prática
- Traduz o cuidado Hapvida em valor concreto no dia a dia
- Evita jargão técnico; prefere linguagem acessível

Referências de linguagem aprovadas:
- "Algo novo para a saúde da sua equipe"
- "Sua equipe ganha mais movimento e bem-estar"
- "O Clube de Vantagens Hapvida vai além da saúde"
- "Economia de até 18% na conta de energia. Zero investimento inicial."

Padrões: Headlines com pergunta ou afirmação de valor direto. CTA sempre presente: "Aproveitar agora", "Acessar o Clube", "Ver ofertas".

### 2. Cuidaê
Tom: Institucional, claro e funcional.
- Comunica com objetividade, sem rodeios
- Facilita escolhas e orienta o usuário de forma simples
- Prioriza eficiência: menos cliques, menos fricção

Referências de linguagem aprovadas:
- "Depois da consulta, seu cuidado continua no Cuidaê"
- "Medicamentos e produtos de saúde com entrega no seu endereço"
- "Férias com a farmácia completa"

Padrões: Headlines que completam uma ação ou situação da jornada. CTA funcional e direto: "Acessar o Cuidaê", "Ver produtos", "Comprar agora".

### 3. Saúde Integral (Hapvida Ads)
Tom: Racional, claro e estratégico.
- Público: parceiros, anunciantes, gestores de saúde, médicos
- Comunica com precisão e linguagem de negócios
- Foco em resultados mensuráveis, escala e jornada do paciente

Referências de linguagem aprovadas:
- "Integre sua marca à decisão clínica e à jornada do paciente"
- "Escala, dados e presença na jornada real do paciente"
- "Ative sua marca no ecossistema Hapvida"

Padrões: Headlines com posicionamento estratégico. CTA de negócio: "Fale com um especialista", "Conecte sua marca".

## REGRAS GERAIS

1. Nunca invente informações não fornecidas no briefing. Use [INSERIR: dado] quando faltar.
2. Sempre inclua um CTA. Se não especificado, sugira o mais adequado.
3. Respeite os limites de caracteres por canal.
4. Não use emojis salvo em WhatsApp/redes sociais e apenas se o briefing pedir.
5. Não use superlativos vazios como "o melhor", "incrível", "revolucionário".
6. Não invente condições, preços ou datas.
7. Sinalize quando houver necessidade de disclaimer legal.
8. Todo copy é sugestão para aprovação humana. Não é final.

## FORMATO DE ENTREGA

---
VERTICAL: [nome]
CANAL: [nome]
OBJETIVO: [nome]
---

VERSÃO A – [rótulo]

[copy formatado]

---

VERSÃO B – [rótulo]

[copy formatado]

---

OBSERVAÇÕES DO AGENTE:
- [sinalizações relevantes]
"""

BRIEFING_TEMPLATE = """
📋 *TEMPLATE DE BRIEFING*

Cole e preencha abaixo:

```
Vertical: [ ] Clube de Vantagens  [ ] Cuidaê  [ ] Saúde Integral
Canal: [ ] Banner  [ ] Social  [ ] E-mail  [ ] WhatsApp  [ ] Push  [ ] SMS
Objetivo: [ ] Awareness  [ ] Conversão  [ ] Retenção  [ ] Engajamento
Público: [ ] Beneficiário PF  [ ] RH/Empresa  [ ] Médico  [ ] Parceiro
Parceiro ou produto: 
Informações principais: 
CTA desejado: 
Observações: 
```
"""

WELCOME_MESSAGE = """
👋 Olá! Sou o *HapvidaAds Copy Bot*.

Gero copy para as três verticais do ecossistema Hapvida:
• Clube de Vantagens
• Cuidaê
• Saúde Integral (Hapvida Ads)

*Como usar:*
1. Digite /briefing para receber o template
2. Preencha e envie
3. Receba 2 variações de copy prontas para aprovação

Digite /briefing para começar.
"""

# ─── HANDLERS ────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")

async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(BRIEFING_TEMPLATE, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Inicializa histórico se não existir
    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append({
        "role": "user",
        "content": user_message
    })

    await update.message.reply_text("⏳ Gerando copy...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=context.user_data["history"]
        )

        reply = response.content[0].text

        context.user_data["history"].append({
            "role": "assistant",
            "content": reply
        })

        # Telegram tem limite de 4096 caracteres por mensagem
        if len(reply) > 4096:
            for i in range(0, len(reply), 4096):
                await update.message.reply_text(reply[i:i+4096])
        else:
            await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao gerar copy: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["history"] = []
    await update.message.reply_text("🔄 Conversa reiniciada. Digite /briefing para começar um novo copy.")

# ─── MAIN ─────────────────────────────────────────────────

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("briefing", briefing))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
