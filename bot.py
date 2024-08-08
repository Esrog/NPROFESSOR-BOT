import os
import math
import logging
import datetime
import pytz
import logging.config

from pyrogram.errors import BadRequest, Unauthorized
from pyrogram import Client, types

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, UPTIME, WEB_SUPPORT, LOG_MSG
from utils import temp, repo, license, copyright, version
from typing import Union, Optional, AsyncGenerator

from plugins import web_server 
from aiohttp import web

# Configure logging
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)
logger = logging.getLogger(name)

class Bot(Client):

    def init(self):
        super().init(
            name="Professor-Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats        
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.id = me.id
        self.name = me.first_name
        self.mention = me.mention
        self.username = me.username
        self.log_channel = LOG_CHANNEL
        self.uptime = UPTIME
        curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        logger.info(LOG_MSG.format(me.first_name, date, time, repo, version, license, copyright))
        try:
            await self.send_message(LOG_CHANNEL, text=LOG_MSG.format(me.first_name, date, time, repo, version, license, copyright), disable_web_page_preview=True)   
        except Exception as e:
            logger.warning(f"Bot Isn't Able To Send Message To LOG_CHANNEL \n{e}")
        if WEB_SUPPORT:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", 8080).start()
            logger.info("Web Response Is Running......🕸️")
            
    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Is Restarting ⟳...")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:                       
        current = offset
        while current < limit:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff)))
            for message in messages:
                yield message
                current += 1

Bot().run()





