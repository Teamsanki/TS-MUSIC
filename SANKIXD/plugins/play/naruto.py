import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from SANKIXD import app
from SANKIXD.core.call import SANKI
from SANKIXD.utils.logger import play_logs
from SANKIXD.utils.stream.stream import stream

FIREBASE_URL = "https://social-bite-skofficial-default-rtdb.firebaseio.com/files.json"
API_KEY = "sk_n56p50uxd5m"

@app.on_message(filters.command("naruto", prefixes=["/", "!", ".", "#"]) & filters.group)
async def naruto_play(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Episode number dena zaroori hai!\nExample: `/naruto 10`")

    episode_no = message.command[1]  # episode number
    mystic = await message.reply_text(f"🔎 Naruto Episode {episode_no} fetch kiya jaa raha hai...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FIREBASE_URL) as resp:
                if resp.status != 200:
                    return await mystic.edit_text("❌ Firebase se data fetch nahi ho raha.")
                data = await resp.json()

        # Firebase ke data se episode search
        episode_key = f"naruto_{episode_no}"
        if episode_key not in data:
            return await mystic.edit_text(f"⚠️ Episode {episode_no} Firebase me nahi mila.")
        
        episode_data = data[episode_key]
        video_url = episode_data.get("url")
        if not video_url:
            return await mystic.edit_text("❌ Episode ka URL missing hai.")

        try:
            await stream(
                _={},
                mystic=mystic,
                user_id=message.from_user.id,
                details={"title": f"Naruto Episode {episode_no}", "link": video_url, "path": video_url},
                chat_id=message.chat.id,
                user_name=message.from_user.first_name,
                group_id=message.chat.id,
                video=True,
                streamtype="firebase",
                forceplay=True
            )
        except NoActiveGroupCall:
            await mystic.edit_text("❌ VC me koi active group call nahi mila. Pehle VC start karo.")
            return
        except Exception as e:
            await mystic.edit_text(f"⚠️ Error: {type(e).__name__}")
            return

        await mystic.delete()
        return await play_logs(message, streamtype="Firebase Naruto Episode")

    except Exception as e:
        return await mystic.edit_text(f"⚠️ Error: {e}")
