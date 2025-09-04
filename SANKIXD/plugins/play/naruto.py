import aiohttp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.exceptions import NoActiveGroupCall

from SANKIXD import app
from SANKIXD.utils.stream.stream import stream
from SANKIXD.utils.logger import play_logs

FIREBASE_URL = "https://social-bite-skofficial-default-rtdb.firebaseio.com/files.json"
API_KEY = "sk_n56p50uxd5m"


# ---------- Step 1: Show episodes as inline buttons ----------
@app.on_message(filters.command("naruto", prefixes=["/", "!", ".", "#"]) & filters.group)
async def naruto_list(client, message):
    mystic = await message.reply_text("🔎 Fetching Naruto episodes...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(FIREBASE_URL) as resp:
            if resp.status != 200:
                return await mystic.edit_text("❌ Firebase se data fetch nahi ho raha.")
            data = await resp.json()
    
    if not data:
        return await mystic.edit_text("⚠️ Firebase me koi episode nahi hai.")

    buttons = []
    for key, ep in sorted(data.items()):
        ep_name = ep.get("name", f"Episode {key}")
        buttons.append([InlineKeyboardButton(ep_name, callback_data=f"naruto_play|{key}")])

    await mystic.edit_text(
        "📺 Naruto Episodes:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ---------- Step 2: Play episode in VC ----------
@app.on_callback_query(filters.regex(r"naruto_play\|"))
async def play_naruto_episode(client, callback):
    ep_key = callback.data.split("|")[1]
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name
    chat_id = callback.message.chat.id

    await callback.answer("▶️ Playing episode...", show_alert=True)

    # Fetch episode URL from Firebase
    async with aiohttp.ClientSession() as session:
        async with session.get(FIREBASE_URL) as resp:
            data = await resp.json()

    if ep_key not in data:
        return await callback.message.edit_text("⚠️ Episode not found in Firebase.")

    ep_data = data[ep_key]
    video_url = ep_data.get("url")
    if not video_url:
        return await callback.message.edit_text("❌ Episode URL missing.")

    try:
        await stream(
            _={},  # localization not required
            mystic=callback.message,
            user_id=user_id,
            details={"title": ep_data.get("name", "Naruto Episode"), "link": video_url, "path": video_url},
            chat_id=chat_id,
            user_name=user_name,
            group_id=chat_id,
            video=True,
            streamtype="firebase",
            forceplay=True  # use string session account for VC
        )
    except NoActiveGroupCall:
        return await callback.message.edit_text("❌ VC me koi active group call nahi hai. Pehle VC join karo.")
    except Exception as e:
        return await callback.message.edit_text(f"⚠️ Error: {type(e).__name__}")

    await callback.message.edit_text(f"▶️ Playing: {ep_data.get('name', 'Naruto Episode')} in VC!")
    await play_logs(callback.message, streamtype="Firebase Naruto Episode")
