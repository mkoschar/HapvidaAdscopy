"""

WELCOME_MESSAGE = """
👋 Olá! Sou o *HapvidaAds Copy Bot*.

Seu acesso está sendo verificado. Aguarde a aprovação do administrador.
"""

WELCOME_APPROVED = """
👋 Olá! Sou o *HapvidaAds Copy Bot*.

Gero copy para as três verticais do ecossistema Hapvida:
- Clube de Vantagens
- Cuidaê
- Saúde Integral (Hapvida Ads)

*Como usar:*
1. Digite /briefing para receber o template
2. Preencha e envie
3. Receba 2 variações de copy prontas para aprovação

Digite /briefing para começar.
"""

# ─── HELPERS ─────────────────────────────────────────────

def is_approved(user_id: int) -> bool:
    return user_id in approved_users

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str, full_name: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprovar", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Recusar", callback_data=f"reject_{user_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"🔔 *Novo acesso solicitado*\n\n"
        f"Nome: {full_name}\n"
        f"Username: @{username if username else 'sem username'}\n"
        f"ID: `{user_id}`"
    )
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ─── HANDLERS ────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if is_approved(user_id):
        await update.message.reply_text(WELCOME_APPROVED, parse_mode="Markdown")
    else:
        pending_users[user_id] = {
            "username": user.username,
            "full_name": user.full_name
        }
        await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
        await notify_admin(context, user_id, user.username or "", user.full_name)

async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_approved(update.effective_user.id):
        await update.message.reply_text("⏳ Seu acesso ainda não foi aprovado. Aguarde.")
        return
    await update.message.reply_text(BRIEFING_TEMPLATE, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_approved(user_id):
        await update.message.reply_text("⏳ Seu acesso ainda não foi aprovado. Aguarde.")
        return

    user_message = update.message.text

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

        if len(reply) > 4096:
            for i in range(0, len(reply), 4096):
                await update.message.reply_text(reply[i:i+4096])
        else:
            await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao gerar copy: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_approved(update.effective_user.id):
        await update.message.reply_text("⏳ Seu acesso ainda não foi aprovado. Aguarde.")
        return
    context.user_data["history"] = []
    await update.message.reply_text("🔄 Conversa reiniciada. Digite /briefing para começar um novo copy.")

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data
    action, user_id_str = data.split("_", 1)
    user_id = int(user_id_str)

    user_info = pending_users.get(user_id, {})
    full_name = user_info.get("full_name", "Usuário")

    if action == "approve":
        approved_users.add(user_id)
        await query.edit_message_text(f"✅ *{full_name}* aprovado com sucesso.", parse_mode="Markdown")
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Seu acesso foi aprovado! Digite /briefing para começar.",
        )
    elif action == "reject":
        pending_users.pop(user_id, None)
        await query.edit_message_text(f"❌ Acesso de *{full_name}* recusado.", parse_mode="Markdown")
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Seu acesso ao bot não foi aprovado. Entre em contato com o administrador.",
        )

# ─── MAIN ─────────────────────────────────────────────────

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
