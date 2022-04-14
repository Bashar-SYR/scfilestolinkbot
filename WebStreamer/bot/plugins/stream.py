
# (c) @SyrianCrackers


import asyncio
import urllib.parse
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def get_media_file_size(m):
    media = m.video or m.audio or m.document
    if media and media.file_size:
        return media.file_size
    else:
        return None


def get_media_file_name(m):
    media = m.video or m.document or m.audio
    if media and media.file_name:
        return urllib.parse.quote_plus(media.file_name)
    else:
        return None


@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.edited, group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"New user joined \n\nUser: [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started your bot."
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="Sorry bro, you are banned from using me. Contact @BasharSYR for more info.",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="""• Join my update channel first, then hit /start to use me ;D""",
                reply_markup=InlineKeyboardMarkup(
                    [[ InlineKeyboardButton("Join update channel", url=f"https://t.me/{Var.UPDATES_CHANNEL}") ]]
                ),
                parse_mode="HTML"
            )
            return
        except Exception:
            await c.send_message(
                chat_id=m.chat.id,
                text="Something wrong, contact the owner for more info.",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        file_name = get_media_file_name(m)
        file_size = humanbytes(get_media_file_size(m))
        stream_link = "https://{}/{}/{}".format(Var.FQDN, log_msg.message_id, file_name) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}/{}".format(Var.FQDN,
                                    Var.PORT,
                                    log_msg.message_id,
                                    file_name)

        msg_text ="""
Your link is generated!\n
<b>📂 File name:</b> {}\n
<b>📦 File size:</b> {}\n
<b>📥 Direct download link:</b> {}\n
• <u>Note</u>: Link expires in 24H\n
© @SyrianCrackers"""

        await log_msg.reply_text(text=f"**Requested by:** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User id:** `{m.from_user.id}`\n**Download link:** {stream_link}", disable_web_page_preview=True, parse_mode="Markdown", quote=True)
        await m.reply_text(
            text=msg_text.format(file_name, file_size, stream_link),
            parse_mode="HTML", 
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Download now 📥", url=stream_link)]]),
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Got floodwait of {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄ser id:** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video) & ~filters.edited, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = "https://{}/{}".format(Var.FQDN, log_msg.message_id) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}".format(Var.FQDN,
                                    Var.PORT,
                                    log_msg.message_id)
        await log_msg.reply_text(
            text=f"**Channel name:** `{broadcast.chat.title}`\n**Channel id:** `{broadcast.chat.id}`\n**Request url:** https://t.me/{(await bot.get_me()).username}?start=BasharSYR_{str(log_msg.message_id)}",
            # text=f"**Channel name:** `{broadcast.chat.title}`\n**Channel id:** `{broadcast.chat.id}`\n**Request url:** https://t.me/FxStreamBot?start=BasharSYR_{str(log_msg.message_id)}",
            quote=True,
            parse_mode="Markdown"
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Download link 📥", url=f"https://t.me/{(await bot.get_me()).username}?start=BasharSYR_{str(log_msg.message_id)}")]])
            # [[InlineKeyboardButton("Download link 📥", url=f"https://t.me/FxStreamBot?start=BasharSYR_{str(log_msg.message_id)}")]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"Got floodwait of {str(w.x)}s from {broadcast.chat.title}\n\n**Channel id:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#Error traceback:** `{e}`", disable_web_page_preview=True, parse_mode="Markdown")
        print(f"Can't edit broadcast message!\nError: {e}")
