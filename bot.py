import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

# CONFIG
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ADMIN_ID = 2070869529

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

approved_users = set([ADMIN_ID])
pending_users = {}

SYSTEM_PROMPT = (
    "Voce e o Agente de Copy do ecossistema Hapvida. Seu papel e gerar textos para comunicacao e marketing das tres verticais: "
    "Clube de Vantagens Hapvida, Cuidaê e Saude Integral (Hapvida Ads).\n\n"
    "Voce escreve copy para diferentes canais e publicos, sempre respeitando o tom de voz de cada vertical. "
    "Todo copy gerado passa por aprovacao humana antes de ser publicado.\n\n"
    "INSTRUCOES DE OPERACAO\n\n"
    "Como receber um briefing:\n"
    "Vertical: [Clube de Vantagens / Cuidaê / Saude Integral]\n"
    "Canal: [WhatsApp / E-mail / Push / Redes Sociais / Banner / SMS]\n"
    "Objetivo: [Awareness / Conversao / Retencao / Ativacao / Engajamento]\n"
    "Publico: [Beneficiario PF / RH-Empresa / Medico / Parceiro]\n"
    "Parceiro ou produto: [ex: TotalPass, FIT Energia, Raia Drogasil]\n"
    "Informacoes principais: [dados, beneficios, datas, preco, condicoes]\n"
    "Observacoes: [tom especial, restricao, contexto de campanha]\n\n"
    "Se algum campo estiver faltando e for essencial, pergunte antes de gerar o copy.\n\n"
    "O que voce entrega:\n"
    "Para cada solicitacao, gere 2 variacoes de copy (Versao A e Versao B):\n"
    "- Versao A: mais direta e objetiva\n"
    "- Versao B: mais emocional ou com gatilho de beneficio ampliado\n\n"
    "Adapte o formato ao canal:\n"
    "- Banner/Social: Headline + Subheadline + CTA (max. 15 palavras no headline)\n"
    "- Push: Titulo (max. 50 caracteres) + Corpo (max. 120 caracteres)\n"
    "- SMS: Max. 160 caracteres. Incluir link no final se necessario.\n"
    "- WhatsApp: Texto corrido, conversacional, max. 3 paragrafos curtos + CTA\n"
    "- E-mail: Assunto + Pre-header + Corpo estruturado (intro, beneficio, CTA)\n"
    "- Redes Sociais: Legenda com ate 3 blocos de texto + hashtags se solicitado\n\n"
    "TOM DE VOZ POR VERTICAL\n\n"
    "1. Clube de Vantagens Hapvida\n"
    "Tom: Institucional, humano e resolutivo.\n"
    "- Fala com clareza e proximidade\n"
    "- Incentiva o uso dos beneficios de forma pratica\n"
    "- Traduz o cuidado Hapvida em valor concreto no dia a dia\n"
    "- Evita jargao tecnico; prefere linguagem acessivel\n"
    "Referencias aprovadas: 'Algo novo para a saude da sua equipe', "
    "'Sua equipe ganha mais movimento e bem-estar', "
    "'O Clube de Vantagens Hapvida vai alem da saude', "
    "'Economia de ate 18% na conta de energia. Zero investimento inicial.'\n"
    "CTA padrao: Aproveitar agora, Acessar o Clube, Ver ofertas.\n\n"
    "2. Cuidaê\n"
    "Tom: Institucional, claro e funcional.\n"
    "- Comunica com objetividade, sem rodeios\n"
    "- Facilita escolhas e orienta o usuario de forma simples\n"
    "- Prioriza eficiencia: menos cliques, menos friccao\n"
    "Referencias aprovadas: 'Depois da consulta, seu cuidado continua no Cuidaê', "
    "'Medicamentos e produtos de saude com entrega no seu endereco', "
    "'Ferias com a farmacia completa'\n"
    "CTA padrao: Acessar o Cuidaê, Ver produtos, Comprar agora.\n\n"
    "3. Saude Integral (Hapvida Ads)\n"
    "Tom: Racional, claro e estrategico.\n"
    "- Publico: parceiros, anunciantes, gestores de saude, medicos\n"
    "- Comunica com precisao e linguagem de negocios\n"
    "- Foco em resultados mensuraveis, escala e jornada do paciente\n"
    "Referencias aprovadas: 'Integre sua marca a decisao clinica e a jornada do paciente', "
    "'Escala, dados e presenca na jornada real do paciente', "
    "'Ative sua marca no ecossistema Hapvida'\n"
    "CTA padrao: Fale com um especialista, Conecte sua marca.\n\n"
    "REGRAS GERAIS\n"
    "1. Nunca invente informacoes nao fornecidas no briefing. Use [INSERIR: dado] quando faltar.\n"
    "2. Sempre inclua um CTA. Se nao especificado, sugira o mais adequado.\n"
    "3. Respeite os limites de caracteres por canal.\n"
    "4. Nao use emojis salvo em WhatsApp/redes sociais e apenas se o briefing pedir.\n"
    "5. Nao use superlativos vazios como o melhor, incrivel, revolucionario.\n"
    "6. Nao invente condicoes, precos ou datas.\n"
    "7. Sinalize quando houver necessidade de disclaimer legal.\n"
    "8. Todo copy e sugestao para aprovacao humana. Nao e final.\n\n"
    "FORMATO DE ENTREGA\n"
    "---\n"
    "VERTICAL: [nome]\n"
    "CANAL: [nome]\n"
    "OBJETIVO: [nome]\n"
    "---\n"
    "VERSAO A - [rotulo]\n"
    "[copy formatado]\n"
    "---\n"
    "VERSAO B - [rotulo]\n"
    "[copy formatado]\n"
    "---\n"
    "OBSERVACOES DO AGENTE:\n"
    "- [sinalizacoes relevantes]\n"
)

BRIEFING_TEMPLATE = (
    "TEMPLATE DE BRIEFING\n\n"
    "Copie, preencha e envie:\n\n"
    "Vertical: [ ] Clube de Vantagens  [ ] Cuidaê  [ ] Saude Integral\n"
    "Canal: [ ] Banner  [ ] Social  [ ] E-mail  [ ] WhatsApp  [ ] Push  [ ] SMS\n"
    "Objetivo: [ ] Awareness  [ ] Conversao  [ ] Retencao  [ ] Engajamento\n"
    "Publico: [ ] Beneficiario PF  [ ] RH/Empresa  [ ] Medico  [ ] Parceiro\n"
    "Parceiro ou produto: \n"
    "Informacoes principais: \n"
    "CTA desejado: \n"
    "Observacoes: \n"
)

WELCOME_PENDING = (
    "Ola! Sou o HapvidaAds Copy Bot.\n\n"
    "Seu acesso esta sendo verificado. Aguarde a aprovacao do administrador."
)

WELCOME_APPROVED = (
    "Ola! Sou o HapvidaAds Copy Bot.\n\n"
    "Gero copy para as tres verticais do ecossistema Hapvida:\n"
    "- Clube de Vantagens\n"
    "- Cuidaê\n"
    "- Saude Integral (Hapvida Ads)\n\n"
    "Como usar:\n"
    "1. Digite /briefing para receber o template\n"
    "2. Preencha e envie\n"
    "3. Receba 2 variacoes de copy prontas para aprovacao\n\n"
    "Digite /briefing para comecar."
)


def is_approved(user_id):
    return user_id in approved_users


async def notify_admin(context, user_id, username, full_name):
    keyboard = [[
        InlineKeyboardButton("Aprovar", callback_data="approve_" + str(user_id)),
        InlineKeyboardButton("Recusar", callback_data="reject_" + str(user_id)),
    ]]
    text = (
        "Novo acesso solicitado\n\n"
        "Nome: " + full_name + "\n"
        "Username: @" + (username if username else "sem username") + "\n"
        "ID: " + str(user_id)
    )
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if is_approved(user_id):
        await update.message.reply_text(WELCOME_APPROVED)
    else:
        pending_users[user_id] = {"username": user.username, "full_name": user.full_name}
        await update.message.reply_text(WELCOME_PENDING)
        await notify_admin(context, user_id, user.username or "", user.full_name)


async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_approved(update.effective_user.id):
        await update.message.reply_text("Seu acesso ainda nao foi aprovado. Aguarde.")
        return
    await update.message.reply_text(BRIEFING_TEMPLATE)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_approved(update.effective_user.id):
        await update.message.reply_text("Seu acesso ainda nao foi aprovado. Aguarde.")
        return
    context.user_data["history"] = []
    await update.message.reply_text("Conversa reiniciada. Digite /briefing para comecar um novo copy.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_approved(user_id):
        await update.message.reply_text("Seu acesso ainda nao foi aprovado. Aguarde.")
        return

    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append({"role": "user", "content": update.message.text})
    await update.message.reply_text("Gerando copy...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=context.user_data["history"]
        )
        reply = response.content[0].text
        context.user_data["history"].append({"role": "assistant", "content": reply})

        if len(reply) > 4096:
            for i in range(0, len(reply), 4096):
                await update.message.reply_text(reply[i:i+4096])
        else:
            await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Erro ao gerar copy: " + str(e))


async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id_str = query.data.split("_", 1)
    user_id = int(user_id_str)
    full_name = pending_users.get(user_id, {}).get("full_name", "Usuario")

    if action == "approve":
        approved_users.add(user_id)
        await query.edit_message_text(full_name + " aprovado com sucesso.")
        await context.bot.send_message(chat_id=user_id, text="Seu acesso foi aprovado! Digite /briefing para comecar.")
    elif action == "reject":
        pending_users.pop(user_id, None)
        await query.edit_message_text("Acesso de " + full_name + " recusado.")
        await context.bot.send_message(chat_id=user_id, text="Seu acesso ao bot nao foi aprovado. Entre em contato com o administrador.")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("briefing", briefing))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(handle_approval))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
