import asyncio
import random
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Master Bot Initialize
app = Client(
    "Master_Bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.MASTER_BOT_TOKEN
)

# MongoDB Database Initialize
mongo_client = AsyncIOMotorClient(config.MONGO_URI)
db = mongo_client[config.DB_NAME]
forward_states_collection = db["forward_states"]
user_bots_collection = db["user_bots"]
destinations_collection = db["destinations"]

forward_steps = {}  
running_minibots = {}
user_bots_cache = {} 
DATABASE_CHAT_ID = config.DATABASE_CHANNEL_ID 
stop_signals = {} 

# --- RECOVERY SYSTEM (MONGODB) ---
async def save_job_state(user_id, source_chat_id, start_id, end_id, current_idx, dest_chat):
    await forward_states_collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "source_chat_id": source_chat_id,
                "start_id": start_id,
                "end_id": end_id,
                "current_idx": current_idx,
                "dest_chat": dest_chat
            }
        },
        upsert=True
    )

async def clear_job_state(user_id):
    await forward_states_collection.delete_one({"_id": user_id})

# --- ADVANCED FORWARDING ENGINE (GLOBAL SCOPE) ---
async def run_forwarding_process(c, status_msg, uid, dest_chat_id, f_data):
    if "start_id" not in f_data:
        job_state = f_data
        source_chat_id = job_state["source_chat_id"]
        start_id = job_state["start_id"]
        base_end_id = job_state["end_id"]
        resume_from = job_state.get("current_idx", start_id)
        caption_text = job_state.get("caption", "")
    else:
        source_chat_id = f_data["source_chat_id"]
        start_id = f_data["start_id"]
        base_end_id = f_data["end_id"]
        resume_from = start_id
        caption_text = f_data.get("caption", "")

    actual_end_id = base_end_id
    print(f"🎯 Fixed End ID set to: {actual_end_id}")

    stop_token = f"stop_{uid}"
    stop_signals[uid] = True 
    
    stop_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⏹️ Stop Process", callback_data=stop_token)]])
    status = await status_msg.edit_text("🔄 <b>Forwarding shuru/resume ho rahi hai...</b>", reply_markup=stop_keyboard)
    
    batch_topics = {} 
    seen_topics_tracker = {} 
    
    bot_url = "https://t.me/course_hub2bot"
    total_msgs = (actual_end_id - resume_from) + 1
    
    sleep_time = 4.0  # TQDA SOLID FIX: Dhire-dhire aur aaram se message bhejne ke liye 4.0 seconds kiya gaya है
    current_batch_name = None

    print(f"\n🚀 [Forwarding Job Started/Resumed] ID {resume_from} to {actual_end_id}...")
    
    for idx, m_id in enumerate(range(resume_from, actual_end_id + 1), start=1):
        await save_job_state(uid, source_chat_id, start_id, actual_end_id, m_id, dest_chat_id)
        
        if not stop_signals.get(uid, False):
            print(f"⏹️ [Forwarding Interrupted] Process explicitly stopped by user ID {uid}...")
            try:
                await status.edit_text("⏹️ <b>Forwarding paused/stopped by user!</b>")
            except Exception:
                pass
            return

        try:
            remaining_msgs = total_msgs - idx
            estimated_seconds = remaining_msgs * sleep_time
            time_remaining_str = format_seconds(int(estimated_seconds))

            if idx % 15 == 0 or idx == 1 or idx == total_msgs:
                try:
                    await status.edit_text(
                        f"🔄 <b>Forwarding in Progress...</b>\n\n"
                        f"📈 <b>Progress:</b> {idx}/{total_msgs} messages processed\n"
                        f"⏱️ <b>Time Remaining:</b> ~ {time_remaining_str}\n"
                        f"💤 <b>Sleep Interval:</b> {sleep_time}s",
                        reply_markup=stop_keyboard
                    )
                except Exception:
                    pass

            msg = None
            for _ in range(4): # Try attempts badhayein hain
                try:
                    msg = await c.get_messages(source_chat_id, m_id)
                    break
                except Exception as e:
                    if "FLOOD_WAIT" in str(e):
                        secs = int(re.search(r"_(\d+)", str(e)).group(1))
                        await asyncio.sleep(secs + 2)
                    else:
                        await asyncio.sleep(1.0)
                        
            # --- TQDA SOLID FIX: MEDIA & FILES RETENTION ---
            if not msg:
                await asyncio.sleep(0.1)
                continue

            if msg.service is not None:
                await asyncio.sleep(0.1)
                continue

            # Check karta hai ki agar post par video, document, audio, photo mein se kuch bhi nahi hai aur caption/text bhi khali hai, tabhi skip karein.
            if msg.document is None and msg.video is None and msg.audio is None and msg.media is None and msg.photo is None and not msg.text:
                await asyncio.sleep(0.1)
                continue

            # BATCH DETECTION LOGIC
            if msg.caption:
                b_match = re.search(r'(?:batch\s*name|batch)\s*:\s*(.+)', msg.caption, re.IGNORECASE)
                if b_match:
                    found = b_match.group(1).strip().split('\n')[0]
                    detected_batch = found.replace("-", "").strip()
                else:
                    detected_batch = current_batch_name if current_batch_name else "Default Batch"
            else:
                detected_batch = current_batch_name if current_batch_name else "Default Batch"

            if detected_batch != current_batch_name:
                if current_batch_name and current_batch_name in batch_topics:
                    await send_chunked_summary(c, dest_chat_id, current_batch_name, batch_topics[current_batch_name])
                
                current_batch_name = detected_batch
                batch_text_msg = f"<b>📌 Batch Name: {current_batch_name}</b>"
                try:
                    pinned_text_obj = await c.send_message(dest_chat_id, batch_text_msg, parse_mode=ParseMode.HTML)
                    await c.pin_chat_message(chat_id=dest_chat_id, message_id=pinned_text_obj.id, disable_notification=True)
                except Exception:
                    pass

            if current_batch_name not in batch_topics:
                batch_topics[current_batch_name] = []
                seen_topics_tracker[current_batch_name] = set()
            
            topic_keywords = ["Topic name :", "Topic :", "Topic:"]
            t_name = None

            for kw in topic_keywords:
                if msg.caption and kw in msg.caption:
                    t_name = msg.caption.split(kw)[1].split("\n")[0].strip()
                    break
            
            orig_caption = f"<a href='{bot_url}'>{msg.caption}</a>" if msg.caption else ""
            user_caption = f"\n\n{caption_text}" if caption_text else ""
            final_caption = f"{orig_caption}{user_caption}"
            
            while True:
                try:
                    new_msg = await msg.copy(dest_chat_id, caption=final_caption, parse_mode=ParseMode.HTML)
                    
                    if t_name and t_name not in seen_topics_tracker[current_batch_name]:
                        seen_topics_tracker[current_batch_name].add(t_name)
                        batch_topics[current_batch_name].append((t_name, new_msg.link))
                        
                    break
                except asyncio.exceptions.TimeoutError:
                    await asyncio.sleep(5)
                except Exception as e:
                    error_str = str(e)
                    if "FLOOD_WAIT" in error_str:
                        seconds_to_wait = int(re.search(r"_(\d+)", error_str).group(1))
                        await asyncio.sleep(seconds_to_wait + 2)
                    else:
                        break
                        
            await asyncio.sleep(sleep_time)
        except Exception: 
            continue
        
    if current_batch_name and current_batch_name in batch_topics:
        await send_chunked_summary(c, dest_chat_id, current_batch_name, batch_topics[current_batch_name])
    
    await status.edit_text("🎉 <b>Task Done & All Summaries Sent ✅</b>")
    c.forward_steps.pop(uid, None)
    stop_signals.pop(uid, None)
    await clear_job_state(uid)

async def load_previous_states():
    global user_bots_cache
    async for bot_doc in user_bots_collection.find():
        uid = bot_doc["_id"]
        token = bot_doc["token"]
        user_bots_cache[uid] = {
            "id": bot_doc["id"],
            "username": bot_doc["username"],
            "name": bot_doc["name"],
            "token": token
        }
        
        # Auto-initialize child-bot runtime in background on Master Bot startup
        try:
            session_id = token.split(':')[0]
            session_name = f"childbot_{session_id}"
            
            child_client = Client(
                session_name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                bot_token=token
            )
            
            child_client.temp_dest = {}
            child_client.forward_steps = {}
            
            dest_doc = await destinations_collection.find_one({"_id": uid})
            if dest_doc:
                child_client.temp_dest[uid] = dest_doc["dest_id"]

            # Re-binding start command handler for auto-reconnection
            @child_client.on_message(filters.command("start"))
            async def child_start(c, msg):
                uid = msg.from_user.id
                dest_stat = "❌ Not Set"
                if uid in c.temp_dest:
                    dest_stat = f"✅ Set (ID: <code>{c.temp_dest[uid]}</code>)"
                    
                start_, emj = (
                    f"╭────────────────────────────\n"
                    f"│ 🤖 <b>Namaste! Welcome {msg.from_user.first_name}</b>\n"
                    f"│ 🚀 <i>Aapka Personal Child Bot Active Hai!</i>\n"
                    f"╰────────────────────────────\n\n"
                    f"🎯 <b>Destination Status:</b> {dest_stat}\n\n"
                    f"<b>⚙️ Step-by-Step Instructions:</b>\n\n"
                    f"<b>1️⃣ Destination Channel Setup:</b>\n"
                    f"• Channel me bot ko Admin banayein.\n"
                    f"• Channel ki post forward karke reply mein likhein 👉 <code>/setchannel</code>\n\n"
                    f"<b>2️⃣ Forwarding Shuru Karein:</b>\n"
                    f"• Type karein 👉 <code>/forward</code>\n\n"
                    f"<b>🗑️ Management Commands:</b>\n"
                    f"• <code>/removedest</code> - Destination channel reset karein.", "✨"
                )
                
                keyb_child = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎯 Set Channel", callback_data="c_setch"), InlineKeyboardButton("🚀 Forward", callback_data="c_fwd")],
                    [InlineKeyboardButton("🗑️ Remove Destination", callback_data="c_rmdest")]
                ])
                
                await msg.reply_text(start_, parse_mode=ParseMode.HTML, reply_markup=keyb_child)

            @child_client.on_callback_query(filters.regex("c_setch"))
            async def c_setch(c, q):
                await q.answer("Destination post forward karke reply mein /setchannel likhein.", show_alert=True)

            @child_client.on_callback_query(filters.regex("c_fwd"))
            async def c_fwd(c, q):
                await q.answer("Forwarding shuru karne ke liye /forward type karein.", show_alert=True)

            @child_client.on_callback_query(filters.regex("c_rmdest"))
            async def c_rmdest(c, q):
                await destinations_collection.delete_one({"_id": q.from_user.id})
                c.temp_dest.pop(q.from_user.id, None)
                await q.answer("✅ Destination channel successfully reset ho gaya hai!", show_alert=True)
                await q.message.edit_text("🎯 <b>Destination channel successfully reset ho gaya hai!</b> Naya set karne ke liye /start dobara run karein.", parse_mode=ParseMode.HTML)

            @child_client.on_message(filters.command("removedest"))
            async def child_remove_dest_cmd(c, msg):
                uid = msg.from_user.id
                await destinations_collection.delete_one({"_id": uid})
                c.temp_dest.pop(uid, None)
                await msg.reply_text("🎯 <b>Destination channel successfully reset/remove ho gaya hai.</b> Naya channel set karne ke liye <code>/setchannel</code> bhejein.", parse_mode=ParseMode.HTML)

            # Re-binding setchannel command handler
            @child_client.on_message(filters.command("setchannel"))
            async def child_setchannel(c, msg):
                reply_msg = msg.reply_to_message
                dest_chat_id = None
                uid = msg.from_user.id
                
                if reply_msg:
                    if reply_msg.forward_from_chat:
                        dest_chat_id = reply_msg.forward_from_chat.id
                    elif reply_msg.text or reply_msg.caption:
                        text = (reply_msg.text or reply_msg.caption).strip()
                        if text.startswith("-100") or text.startswith("-"):
                            try: dest_chat_id = int(text)
                            except: pass
                        else:
                            chat_id, _ = await get_details_from_link(c, text)
                            dest_chat_id = chat_id
                else:
                    cmd_args = msg.text.split(" ", 1)
                    if len(cmd_args) > 1:
                        text = cmd_args[1].strip()
                        if text.startswith("-100") or text.startswith("-"):
                            try: dest_chat_id = int(text)
                            except: pass
                        else:
                            chat_id, _ = await get_details_from_link(c, text)
                            dest_chat_id = chat_id

                if dest_chat_id:
                    try:
                        chat_member = await c.get_chat_member(dest_chat_id, "me")
                        if chat_member.status.value not in ["administrator", "owner"]:
                            await msg.reply_text(
                                "❌ <b>Admin Error!</b> Yeh Child Bot destination channel/group mein <b>Admin nahi hai</b>.\n\n"
                                "Kripya bot ko channel ka admin banayein aur delete/pin messages ki permission dein, phir se <code>/setchannel</code> karein.",
                                parse_mode=ParseMode.HTML
                            )
                            return
                            
                        chat_info = await c.get_chat(dest_chat_id)
                        channel_name = chat_info.title
                        c.temp_dest[uid] = dest_chat_id
                        
                        await destinations_collection.update_one(
                            {"_id": uid},
                            {"$set": {"dest_id": dest_chat_id}},
                            upsert=True
                        )
                        
                        await msg.reply_text(
                            f"✅ <b>Success: {channel_name}</b>\n🆔 ID: <code>{dest_chat_id}</code>\n\n"
                            "🎯 Destination channel set ho chuka hai! Ab aap <code>/forward</code> command bhej sakte hain.",
                            parse_mode=ParseMode.HTML
                        )
                    except Exception as e:
                        await msg.reply_text(f"⚠️ <b>Verification Error:</b> Bot admin nahi hai ya link galat hai. Details: <code>{e}</code>", parse_mode=ParseMode.HTML)
                else:
                    await msg.reply_text(
                        "🎯 <b>Destination Channel ID/Link Setup:</b>\n"
                        "Kripya destination post ko forward karke is bot ko reply mein <code>/setchannel</code> likhein, ya seedha ID bhejein (Ex: <code>/setchannel -100xxxxxxxx</code>).",
                        parse_mode=ParseMode.HTML
                    )

            # Re-binding forward command handler
            @child_client.on_message(filters.command("forward"))
            async def child_forward(c, msg):
                uid = msg.from_user.id
                dest_chat_id = c.temp_dest.get(uid)
                    
                if not dest_chat_id:
                    await msg.reply_text("🎯 Pehle <code>/setchannel</code> command se destination channel set karein aur bot ko wahan admin banayein.", parse_mode=ParseMode.HTML)
                    return
                    
                job_state = await forward_states_collection.find_one({"_id": uid})
                
                if job_state:
                    choice_text = f"📑 <b>Purana Pending Task Mila!</b>\nAapki purani forwarding process ruki hui hai. Aap kya karna chahte hain?"
                    choice_keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("▶️ Resume Job", callback_data="resume_job")],
                        [InlineKeyboardButton("🆕 New Task (Start Fresh)", callback_data="new_task")]
                    ])
                    await msg.reply_text(choice_text, parse_mode=ParseMode.HTML, reply_markup=choice_keyboard)
                else:
                    c.forward_steps[uid] = {"step": "source", "dest_chat": dest_chat_id, "data": {}}
                    await msg.reply_text("🔗 <b>First Link (Source Post Link)</b> bhejein (Jahan se forward karna hai Ex: <code>https://t.me/channel/123</code>):")

            @child_client.on_callback_query(filters.regex("resume_job"))
            async def resume_job_callback(c, query):
                uid = query.from_user.id
                job_state = await forward_states_collection.find_one({"_id": uid})
                if not job_state:
                    await query.answer("⚠️ Koi purana saved task nahi mila.", show_alert=True)
                    await query.message.edit_text("⚠️ <b>Purana task nahi mila.</b> Naya task shuru karne ke liye dobara <code>/forward</code> bhejein.", parse_mode=ParseMode.HTML)
                    return
                
                await query.answer("▶️ Forwarding resuming from saved state...", show_alert=True)
                await query.message.edit_text("🔄 <b>Purana task resume ho raha hai...</b>")
                await run_forwarding_process(c, query.message, uid, job_state["dest_chat"], job_state)

            @child_client.on_callback_query(filters.regex("new_task"))
            async def new_task_callback(c, query):
                uid = query.from_user.id
                await clear_job_state(uid)
                dest_chat_id = c.temp_dest.get(uid)
                c.forward_steps[uid] = {"step": "source", "dest_chat": dest_chat_id, "data": {}}
                await query.answer("🆕 Starting fresh task setup...", show_alert=True)
                await query.message.edit_text("🔗 <b>First Link (Source Post Link)</b> bhejein (Jahan se forward karna hai Ex: <code>https://t.me/channel/123</code>):")

            @child_client.on_message(filters.text & filters.private & ~filters.command(["start", "setchannel", "forward", "removedest"]))
            async def child_steps_handler(c, msg):
                uid = msg.from_user.id
                if uid not in c.forward_steps: 
                    return
                
                step = c.forward_steps[uid]["step"]
                data = c.forward_steps[uid]["data"]
                text = msg.text.strip()
                # ✅ Yahan se 'await auto_delete(msg)' hata diya gaya hai taaki links screen par safe rahein.

                if step == "source":
                    chat_id, msg_id = await get_details_from_link(c, text)
                    if not chat_id:
                        await msg.reply_text("⚠️ <b>Invalid Source Link!</b> Kripya source channel ki valid post link bhejein.")
                        return
                        
                    data.update({"source_chat_id": chat_id, "start_id": msg_id})
                    c.forward_steps[uid]["step"] = "end_link"
                    await msg.reply_text("🔢 <b>Last Link (End Message Link)</b> bhejein (Jahan tak forward karna hai):")

                elif step == "end_link":
                    if text.isdigit():
                        msg_id = int(text)
                    else:
                        _, msg_id = await get_details_from_link(c, text)
                        
                    if not msg_id:
                        try: 
                            msg_id = int(text)
                        except:
                            await msg.reply_text("⚠️ <b>Invalid Last Link!</b> Kripya last message ki link ya sirf message ID number mein bhejein.")
                            return
                            
                    c.forward_steps[uid]["data"]["end_id"] = msg_id
                    c.forward_steps[uid]["step"] = "caption"
                    await msg.reply_text("📝 <b>Caption</b> bhejein (ya <code>skip</code> likhein):", parse_mode=ParseMode.HTML)

                elif step == "caption":
                    c.forward_steps[uid]["data"]["caption"] = text if text.lower() != 'skip' else ""
                    await msg.reply_text("✅ <b>Setup Ready!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Start Forwarding", callback_data="run_fwd")]]))

        @child_client.on_callback_query(filters.regex("run_fwd"))
        async def child_run_fwd_setup(c, query):
            uid = query.from_user.id
            if uid not in c.forward_steps:
                await query.answer("❌ Session Expired!", show_alert=True)
                return
            
            f_step_data = c.forward_steps[uid]
            f_data = f_step_data["data"]
            dest_chat = f_step_data["dest_chat"]
            
            await run_forwarding_process(c, query.message, uid, dest_chat, f_data)

        @child_client.on_callback_query(filters.regex(r"^stop_\d+$"))
        async def stop_forwarding_job(c, query):
            uid = query.from_user.id
            if uid in stop_signals:
                stop_signals[uid] = False
                await query.answer("⏹️ Forwarding process stopping instantly...", show_alert=True)
            else:
                await query.answer("❌ No active forwarding process found for you.", show_alert=True)

        await child_client.start()
        bot_info = await child_client.get_me()
        
        user_bots_cache[user_id] = {
            "id": bot_info.id,
            "username": bot_info.username,
            "name": bot_info.first_name,
            "token": token
        }
        
        await user_bots_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "id": bot_info.id,
                    "username": bot_info.username,
                    "name": bot_info.first_name,
                    "token": token
                }
            },
            upsert=True
        )
        
        running_minibots[user_id] = child_client

        try:
            await target_msg.forward(chat_id=DATABASE_CHAT_ID)
            await client.send_message(
                chat_id=DATABASE_CHAT_ID,
                text=f"🤖 <b>Naya Child Bot Register & Start Hua!</b>\n"
                     f"User: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> (ID: <code>{user_id}</code>)\n"
                     f"Bot Name: {bot_info.first_name}\n"
                     f"Username: @{bot_info.username}\n"
                     f"Bot ID: <code>{bot_info.id}</code>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

        await auto_delete(message)
        if target_msg != message:
            await auto_delete(target_msg)

        await status_msg.edit_text(
            f"✅ <b>Child-Bot (Mini-Bot) Successfully Registered & Started!</b>\n\n"
            f"🤖 <b>Bot Name:</b> {bot_info.first_name}\n"
            f"🔗 <b>Username:</b> @{bot_info.username}\n"
            f"🆔 <b>Bot ID:</b> <code>{bot_info.id}</code>\n\n"
            f"Ab aap apne mini bot @{bot_info.username} par jayein aur <code>/start</code> command send karein.",
            parse_mode=ParseMode.HTML
        )
    
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Initialization Failed:</b> Kripya token check karein ya dobara koshish karein.\nError: <code>{e}</code>", parse_mode=ParseMode.HTML)

# --- HELPERS ---
async def auto_delete(message):
    try: await message.delete()
    except: pass

async def get_details_from_link(client, link):
    try:
        link = link.strip().replace("https://t.me/", "")
        if "c/" in link:
            parts = link.split("c/")[-1].split("/")
            chat_id = int("-100" + parts[0])
            msg_id = int(parts[1])
        else:
            parts = [p for p in link.split("/") if p]
            chat_identifier = parts[-2]
            msg_id = int(parts[-1])
            
            if chat_identifier.isdigit():
                chat_id = int("-100" + chat_identifier)
            elif chat_identifier.startswith("-"):
                chat_id = int(chat_identifier)
            else:
                chat_info = await client.get_chat(chat_identifier)
                chat_id = chat_info.id
        
        msg = await client.get_messages(chat_id, msg_id)
        if msg:
            return msg.chat.id, msg.id
        return None, None
    except Exception: 
        return None, None

def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

async def send_chunked_summary(client, chat_id, b_name, topic_list):
    if not topic_list: 
        return
    chunk_size = 40
    for i in range(0, len(topic_list), chunk_size):
        chunk = topic_list[i:i + chunk_size]
        part_num = (i // chunk_size) + 1
        s_txt = f"✨ <b>{b_name} - Summary (Part {part_num}):</b>\n\n"
        
        for name, link in chunk:
            s_txt += f"• <a href='{link}'>{name}</a>\n"
        
        while True:
            try:
                await client.send_message(chat_id, s_txt, parse_mode=ParseMode.HTML)
                break
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    secs = int(e.value) if hasattr(e, "value") else 45
                    await asyncio.sleep(secs + 2)
                else:
                    await asyncio.sleep(3)

# --- MASTER BOT COMMANDS ---

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user = message.from_user
    emojis = ["🚀", "🔥", "✨", "🤖", "💎", "⚡", "🎯"]
    msg = await message.reply_text(random.choice(emojis))
    await asyncio.sleep(0.5)
    await msg.delete()
    
    try:
        await client.send_message(
            chat_id=DATABASE_CHAT_ID,
            text=f"👤 <b>Naya User Master Bot Par Aaya:</b>\n"
                 f"Name: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                 f"Username: @{user.username if user.username else 'N/A'}\n"
                 f"ID: <code>{user.id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass
    
    start_text = (
        f"╭────────────────────────────\n"
        f"│ ✨ <b>Namaste! Welcome {user.first_name}</b>\n"
        f"│ 🚀 <i>Premium Auto-Forwarder is active & healthy!</i>\n"
        f"╰────────────────────────────\n\n"
        f"<b>⚙️ Step-by-Step Instructions:</b>\n\n"
        f"<b>1️⃣ Apna Personal Child-Bot Banayein (Add Bot):</b>\n"
        f"• BotFather se apne naye bot ka message/token yahan <b>forward</b> karein.\n"
        f"• <i>Zaroori Note:</i> Forward kiye gaye message par <b>reply (long press karke)</b> dein aur likhein 👉 <code>/addbot</code>\n\n"
        f"<b>2️⃣ Destination Channel Setup:</b>\n"
        f"• Apne channel me bot ko Admin banayein.\n"
        f"• Channel ki post forward karke reply mein likhein 👉 <code>/setchannel</code>\n\n"
        f"<b>3️⃣ Forwarding Shuru Karein:</b>\n"
        f"• Type karein 👉 <code>/forward</code>\n\n"
        f"<b>ℹ️ Management Commands:</b>\n"
        f"• <code>/mybot</code> - Check your added child-bot\n"
        f"• <code>/resumejob</code> - Purana kaam wahin se shuru karein agar bot band hua ho.\n"
        f"• <code>/removebot</code> - Added bot remove karein.\n"
        f"• <code>/removedest</code> - Destination channel reset karein."
    )
    
    keyb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Bot Instructions", callback_data="a_help"), InlineKeyboardButton("🎯 Set Channel", callback_data="s_help")],
        [InlineKeyboardButton("🔗 Support Channel", url="https://t.me/telegram")]
    ])
    
    await message.reply_text(start_text, parse_mode=ParseMode.HTML, reply_markup=keyb)

@app.on_callback_query(filters.regex("a_help"))
async def a_help(c, q):
    await q.answer("1. Forward token message from BotFather here.\n2. Reply to that forwarded message with /addbot", show_alert=True)

@app.on_callback_query(filters.regex("s_help"))
async def s_help(c, q):
    await q.answer("Forward post from target channel and reply /setchannel", show_alert=True)

# --- BOT MANAGEMENT COMMANDS ---
@app.on_message(filters.command("mybot") & filters.private)
async def mybot_command(client, message):
    user_id = message.from_user.id
    if user_id in user_bots_cache:
        bot_info = user_bots_cache[user_id]
        await message.reply_text(
            f"🤖 <b>Aapka Added Bot:</b>\n"
            f"• <b>Bot Name:</b> {bot_info['name']}\n"
            f"• <b>Username:</b> @{bot_info['username']}\n"
            f"• <b>Bot ID:</b> <code>{bot_info['id']}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text("⚠️ <b>Aapne abhi tak koi bot add nahi kiya hai.</b> Kripya <code>/addbot</code> command use karein.", parse_mode=ParseMode.HTML)

@app.on_message(filters.command("removebot") & filters.private)
async def remove_bot_cmd(client, message):
    uid = message.from_user.id
    if uid in running_minibots:
        try:
            await running_minibots[uid].stop()
        except:
            pass
        running_minibots.pop(uid, None)
    
    if uid in user_bots_cache:
        user_bots_cache.pop(uid, None)
        await user_bots_collection.delete_one({"_id": uid})
        await clear_job_state(uid)
        await destinations_collection.delete_one({"_id": uid})
        await message.reply_text("🗑️ <b>Aapka bot successfully delete aur stop kar diya gaya hai.</b> Naya bot add karne ke liye <code>/addbot</code> use karein.", parse_mode=ParseMode.HTML)
    else:
        await message.reply_text("⚠️ Aapne koi bot add hi nahi kiya hai remove karne ke liye.", parse_mode=ParseMode.HTML)

@app.on_message(filters.command("removedest") & filters.private)
async def remove_dest_cmd(client, message):
    uid = message.from_user.id
    await destinations_collection.delete_one({"_id": uid})
    if uid in running_minibots:
        running_minibots[uid].temp_dest.pop(uid, None)
    await message.reply_text("🎯 <b>Destination channel successfully reset/remove ho gaya hai.</b> Naya channel set karne ke liye <code>/setchannel</code> bhejein.", parse_mode=ParseMode.HTML)

@app.on_message(filters.command("resumejob") & filters.private)
async def resume_job_cmd(client, message):
    uid = message.from_user.id
    job_state = await forward_states_collection.find_one({"_id": uid})
    if not job_state:
        await message.reply_text("⚠️ Aapka koi bhi purana data pending ya saved nahi mila.", parse_mode=ParseMode.HTML)
        return
    await message.reply_text("🔄 Data recovery mode chal raha hai. Kripya apne child-bot par jayein aur `/forward` run karein.", parse_mode=ParseMode.HTML)

print("🤖 Premium Master Bot is Live & Database Connected...")

print("🤖 Initing previous runtime connections...")
loop = asyncio.get_event_loop()
loop.run_until_complete(load_previous_states())

app.run()
