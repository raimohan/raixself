import discord
from discord.ext import commands
import aiohttp
import json
import asyncio
import os
import sys
import urllib.parse
import random

# ==========================================
# ⚙️ CONFIGURATION & GLOBALS
# ==========================================

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ config.json not found! Please create it.")
        sys.exit()

def save_config(conf):
    with open('config.json', 'w') as f:
        json.dump(conf, f, indent=4)

config = load_config()
owner_id = str(config.get('userid', ''))
bot = commands.Bot(command_prefix=config.get('prefix', '.'), self_bot=True, help_command=None)

# State Trackers
afk_reason = None
smart_afk = False
auto_responders = {}
automag_tasks = {}
sniped_messages = {}
ai_memory = []
system_prompt = "You are a helpful, concise AI assistant integrated into a Discord selfbot."

# Logging & Alert Trackers
log_settings = {"msg_logging": False, "mention": False, "keyword": False, "roleping": False}
hooks = {}
keywords = []
rolepings = []
greet_msg = None

# ==========================================
# 🟢 EVENTS
# ==========================================

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"👑 Nanku Connected as: {bot.user.name}")

@bot.event
async def on_message_delete(message):
    # Ignore your own account's deletions so you don't snipe your own command
    if message.author == bot.user:
        return
        
    # By removing "if message.guild:", this now universally catches DMs, GCs, and Server messages
    sniped_messages[message.channel.id] = message

@bot.event
async def on_message(message):
    global afk_reason

    if message.author != bot.user:
        # AFK Auto-reply
        if afk_reason and bot.user.mentioned_in(message):
            await message.channel.send(f"[AFK] I am currently AFK: {afk_reason}")
            
        # Auto-Responder logic
        if message.content in auto_responders:
            await message.channel.send(auto_responders[message.content])

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    wc_id = config.get('welcome_channel')
    wc_msg = config.get('welcome_msg')
    if not wc_id or not wc_msg:
        return
    channel = bot.get_channel(int(wc_id))
    if not channel:
        return
    formatted = wc_msg.replace("{user_m}", member.mention).replace("{server}", member.guild.name)
    try:
        await channel.send(formatted)
    except Exception as e:
        print(f"⚠️ Welcome message error: {e}")


# ==========================================
# ⚙️ CONFIG SECTION
# ==========================================

@bot.command()
async def restart(ctx): 
    await ctx.message.delete()
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def setup1(ctx, upi): 
    await ctx.message.delete(); config['upi_id'] = upi; save_config(config); await ctx.send(f"✅ UPI set to `{upi}`")

@bot.command()
async def setupi2(ctx, upi): 
    await ctx.message.delete(); config['upi2'] = upi; save_config(config); await ctx.send("✅ UPI 2 set")

@bot.command()
async def setqr(ctx, qr): 
    await ctx.message.delete(); config['qr'] = qr; save_config(config); await ctx.send("✅ QR set")

@bot.command()
async def setqr2(ctx, qr): 
    await ctx.message.delete(); config['qr2'] = qr; save_config(config); await ctx.send("✅ QR 2 set")

@bot.command()
async def setsvrlink(ctx, link): 
    await ctx.message.delete(); config['svrlink'] = link; save_config(config); await ctx.send("✅ Server link set")

@bot.command()
async def setuserid(ctx, uid): 
    await ctx.message.delete(); config['userid'] = uid; save_config(config); await ctx.send("✅ User ID set")

@bot.command()
async def setaddy(ctx, addy): 
    await ctx.message.delete(); config['ltc_address'] = addy; save_config(config); await ctx.send("✅ LTC Addy set")

@bot.command()
async def setaddy2(ctx, addy): 
    await ctx.message.delete(); config['ltc_address2'] = addy; save_config(config); await ctx.send("✅ LTC Addy 2 set")

@bot.command()
async def setbinid(ctx, bid): 
    await ctx.message.delete(); config['binance_id'] = bid; save_config(config); await ctx.send("✅ Binance ID set")

@bot.command()
async def setltckey(ctx, key): 
    await ctx.message.delete(); config['ltckey'] = key; save_config(config); await ctx.send("✅ LTC Key set")


# ==========================================
# 📖 STYLED HELP MENU (SELFBOT SAFE)
# ==========================================

@bot.command()
async def help(ctx):
    await ctx.message.delete()

    page1 = (
        "```ansi\n"
        "\u001b[1;35m👑 Nanku - HELP MENU (1/5)\u001b[0m\n\n"
        "\u001b[1;33m[⚙️ Config Section]\u001b[0m\n"
        "  .setup1 <upi> | .setupi2 <upi> - Set Upi 1/2\n"
        "  .setqr <qr>   | .setqr2 <qr>   - Set Qr 1/2\n"
        "  .setsvrlink <link>             - Set Server Link\n"
        "  .setuserid <id>                - Set User Id\n"
        "  .setaddy <addy> | .setaddy2    - Set Ltc Addy 1/2\n"
        "  .setbinid <id>                 - Set Binance Id\n"
        "  .setltckey <key>               - Set Ltc Key\n\n"
        "\u001b[1;33m[📂 General Section]\u001b[0m\n"
        "  .allcmds        - Show All Cmds\n"
        "  .csrv <c> <t>   - Server Clone\n"
        "  .snipe          - Snipe Msg\n"
        "  .srvinfo        - Server Info\n"
        "  .selfbot        - Selfbot Info\n"
        "  .user_info      - User Info\n"
        "  .yt <search>    - YT Search\n\n"
        "\u001b[1;33m[🤖 AI & 🌙 AFK Section]\u001b[0m\n"
        "  .ai <msg>       - Talk With AI\n"
        "  .resetai        - Reset AI Memory\n"
        "  .afk <reason>   - AFK\n"
        "  .unafk          - Remove AFK\n"
        "  .smartafk       - Smart AFK\n"
        "```"
    )

    page2 = (
        "```ansi\n"
        "\u001b[1;35m👑 Nanku - HELP MENU (2/5)\u001b[0m\n\n"
        "\u001b[1;33m[⭐ Vouch Section]\u001b[0m\n"
        "  .vouch <prod>   - Vouch\n"
        "  .exch           - Exchange Vouch\n"
        "  .i2cvouch       - I2C Vouch\n"
        "  .c2ivouch       - C2I Vouch\n\n"
        "\u001b[1;33m[🧮 Calculate Section]\u001b[0m\n"
        "  .math <eq>      - Calculate\n"
        "  .i2c / .c2i     - INR <-> Crypto\n"
        "  .u2l / .l2u     - USD <-> LTC\n\n"
        "\u001b[1;33m[🖼️ User & 💸 Crypto Section]\u001b[0m\n"
        "  .avatar <user>  - Get Avatar\n"
        "  .leaveallgroups - Leave Groups\n"
        "  .closealldms    - Close DMs\n"
        "  .upi / .qr      - Get Payment Info\n"
        "  .send <addy> <amt> - Send LTC\n"
        "  .bal / .mybal   - Check Balances\n"
        "  .txidltc <id>   - Check LTC TXID\n"
        "  .txidbtc <id>   - Check BTC TXID\n"
        "```"
    )

    page3 = (
        "```ansi\n"
        "\u001b[1;35m👑 Nanku - HELP MENU (3/5)\u001b[0m\n\n"
        "\u001b[1;33m[💬 Message Section]\u001b[0m\n"
        "  .spam <amt> <msg> - Spam Msg\n"
        "  .clear <amt>      - Clear Msgs\n"
        "  .dm / .dmall      - Direct Message\n"
        "  .massdmfriends    - DM All Friends\n\n"
        "\u001b[1;33m[🤖 Auto Sender Section]\u001b[0m\n"
        "  .addar / .removear - AutoRespond\n"
        "  .am / .am_stop     - AutoMessage\n\n"
        "\u001b[1;33m[🛡️ Moderation & 🎙️ VC Section]\u001b[0m\n"
        "  .ban / .kick / .nuke - Mod Tools\n"
        "  .banid / .unbanid    - ID Bans\n"
        "  .joinvc / .leavevc   - VC Controls\n"
        "  .vckick / .vcmute    - VC Mod\n"
        "```"
    )

    page4 = (
        "```ansi\n"
        "\u001b[1;35m👑 Nanku - HELP MENU (4/5)\u001b[0m\n\n"
        "\u001b[1;33m[🤡 Fun & Interaction]\u001b[0m\n"
        "  .rizz / .joke / .neko / .hug / .slap\n\n"
        "\u001b[1;33m[🔍 Checker & Alerts]\u001b[0m\n"
        "  .checkpromo <code >  - Check Promo\n"
        "  .checktoken <token> - Check Token\n"
        "  .checktrail <token> - Check Trial\n"
        "  .setlitchook <url>  - LTC Webhook\n"
        "  .setmaghook <url>   - Log Webhook\n"
        "  .setmentionhook     - Mention Webhook\n"
        "  .setgreet / .cleargreet - DM Greeting\n\n"
        "\u001b[1;33m[🎉 Welcome Section]\u001b[0m\n"
        "  .setwelcomechannel <id> - Set Channel\n"
        "  .setwelcomemsg <msg>    - Set Message\n"
        "  .clearwelcome           - Disable\n"
        "```"
    )

    page5 = (
        "```ansi\n"
        "\u001b[1;35m👑 Nanku - HELP MENU (5/5)\u001b[0m\n\n"
        "\u001b[1;33m[🃏 Rich Presence (RPC) Section]\u001b[0m\n"
        "  .setrpcname <txt>       - Set Name\n"
        "  .setrpcdetails <txt>    - Set Details\n"
        "  .setrpcstate <txt>      - Set State\n"
        "  .setrpclargeimage <url> - Set Large Img\n"
        "  .setrpclargetext <txt>  - Large Img Tooltip\n"
        "  .setrpcsmallimage <url> - Set Small Img\n"
        "  .setrpcsmalltext <txt>  - Small Img Tooltip\n"
        "  .setrpcappid <id>       - Set App Id\n"
        "  .applyrpc               - Apply/Activate RPC\n"
        "  .stopactivity           - Clear RPC/Status\n"
        "```"
    )

    for page in [page1, page2, page3, page4, page5]:
        await ctx.send(page)
        await asyncio.sleep(0.5)




# ==========================================
# 📂 GENERAL SECTION
# ==========================================

@bot.command()
async def allcmds(ctx): 
    await ctx.invoke(bot.get_command('help'))

@bot.command()
async def snipe(ctx):
    # 1. Fetch the deleted message for the current chat FIRST
    msg = sniped_messages.get(ctx.channel.id)
    
    # 2. Delete your command message
    try:
        await ctx.message.delete()
    except:
        pass 
        
    # 3. Send the sniped message
    if msg: 
        chat_type = "Server" if ctx.guild else "DM/GC"
        await ctx.send(f"🔫 **Sniped in {chat_type}:** `{msg.author.name}`: {msg.content}")
    else: 
        await ctx.send("⚠️ No recently deleted messages found in this chat.")

@bot.command()
async def srvinfo(ctx): 
    await ctx.message.delete()
    await ctx.send(f"🛡️ **Server:** `{ctx.guild.name}` | 👥 **Members:** `{ctx.guild.member_count}`")

@bot.command()
async def selfbot(ctx): 
    await ctx.message.delete()
    await ctx.send("🤖 Running **Nanku**")

@bot.command()
async def user_info(ctx, user_input: str): 
    await ctx.message.delete()
    
    # Strip mention tags if the user was pinged instead of just providing the ID
    clean_id = user_input.replace("<@", "").replace(">", "").replace("!", "")
    
    try:
        # Check cache first
        user = bot.get_user(int(clean_id))
        
        # If not cached, force an API fetch
        if not user:
            user = await bot.fetch_user(int(clean_id))
            
        await ctx.send(f"👤 **User:** `{user.name}` | 🆔 **ID:** `{user.id}`")
        
    except ValueError:
        await ctx.send("⚠️ Please provide a valid numerical User ID or mention.")
    except discord.NotFound:
        await ctx.send("⚠️ User not found. The ID might be invalid or deleted.")
    except discord.HTTPException as e:
        await ctx.send(f"⚠️ API Error: `{e}`")

@bot.command()
async def yt(ctx, *, search): 
    await ctx.message.delete()
    await ctx.send(f"📺 https://www.youtube.com/results?search_query={urllib.parse.quote(search)}")

@bot.command()
async def csrv(ctx, copy_id: int, target_id: int):
    await ctx.message.delete()
    source = bot.get_guild(copy_id)
    target = bot.get_guild(target_id)
    if not source or not target:
        await ctx.send("⚠️ Source or Target server not found.")
        return
    await ctx.send(f"⚙️ Cloning **{source.name}**...")
    try:
        for c in target.channels:
            try: await c.delete(); await asyncio.sleep(0.5)
            except: pass
        for c in source.categories:
            try: await target.create_category(name=c.name); await asyncio.sleep(0.5)
            except: pass
        for c in source.text_channels:
            try: await target.create_text_channel(name=c.name); await asyncio.sleep(0.5)
            except: pass
        await ctx.send("✅ Server basic clone complete!")
    except Exception:
        await ctx.send("⚠️ Clone encountered errors.")


# ==========================================
# 🤖 AI SECTION (Groq LLaMA)
# ==========================================

@bot.command()
async def ai(ctx, *, msg):
    await ctx.message.delete()
    groq_key = config.get('groq_key')
    if not groq_key:
        await ctx.send("⚠️ Groq API key is missing from config.json")
        return
    ai_memory.append({"role": "user", "content": msg})
    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}] + ai_memory[-10:]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data['choices'][0]['message']['content']
                    ai_memory.append({"role": "assistant", "content": reply})
                    if len(reply) > 1900: reply = reply[:1900] + "... [Truncated]"
                    await ctx.send(f"🧠 **AI:** {reply}")
                else: 
                    err_text = await resp.text()
                    await ctx.send(f"⚠️ Groq API Error (`{resp.status}`): `{err_text[:100]}`")
    except Exception as e:
        await ctx.send(f"⚠️ Request failed: `{e}`")

@bot.command()
async def resetai(ctx):
    await ctx.message.delete()
    global ai_memory; ai_memory = []
    await ctx.send("✅ 🧠 AI Memory wiped.")

@bot.command()
async def setprompt(ctx, *, prompt):
    await ctx.message.delete()
    global system_prompt; system_prompt = prompt
    await ctx.send(f"✅ 🧠 System prompt updated.")

@bot.command()
async def resetprompt(ctx):
    await ctx.message.delete()
    global system_prompt
    system_prompt = "You are a helpful, concise AI assistant integrated into a Discord selfbot."
    await ctx.send("✅ 🧠 System prompt reset to default.")

@bot.command()
async def showprompt(ctx):
    await ctx.message.delete()
    await ctx.send(f"🧠 **Current AI Prompt:** `{system_prompt}`")


# ==========================================
# 🌙 AFK SECTION
# ==========================================

@bot.command()
async def afk(ctx, *, reason="I am away"):
    global afk_reason
    afk_reason = reason
    await ctx.message.delete()
    await ctx.send(f"✅ AFK set: {reason}")

@bot.command()
async def unafk(ctx):
    global afk_reason
    afk_reason = None
    await ctx.message.delete()
    await ctx.send("✅ AFK removed.")


# ==========================================
# ⭐ VOUCH & CALCULATE SECTION
# ==========================================

@bot.command()
async def vouch(ctx, *, product="item"):
    await ctx.message.delete()
    await ctx.send(f"✅ +1 Vouch | Fast & smooth transaction for `{product}`!")

@bot.command()
async def exch(ctx):
    await ctx.message.delete()
    await ctx.send("✅ +1 Vouch | Successful exchange completed smoothly!")

@bot.command()
async def i2cvouch(ctx, inr: float, ltc: float):
    await ctx.message.delete()
    await ctx.send(f"✅ +1 Vouch | Successfully bought `{ltc} LTC` for `₹{inr} INR`!")

@bot.command()
async def c2ivouch(ctx, ltc: float, inr: float):
    await ctx.message.delete()
    await ctx.send(f"✅ +1 Vouch | Successfully sold `{ltc} LTC` for `₹{inr} INR`!")

@bot.command()
async def math(ctx, *, equation):
    await ctx.message.delete()
    try: await ctx.send(f"🧮 **Result:** `{eval(equation)}`")
    except Exception as e: await ctx.send(f"⚠️ Math Error: `{e}`")


# ==========================================
# 🪙 CRYPTO SECTION (CoinGecko + Tatum)
# ==========================================

async def fetch_crypto_price(coin_id, vs_currency="usd"):
    cg_key = config.get('coingecko_key', '')
    headers = {"x-cg-demo-api-key": cg_key} if cg_key else {}
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get(coin_id, {}).get(vs_currency)
    return None

@bot.command()
async def btc(ctx):
    await ctx.message.delete()
    price = await fetch_crypto_price("bitcoin")
    await ctx.send(f"🪙 | **Live BTC Price:** `${price:,.2f} USD`" if price else "⚠️ Fetch failed.")

@bot.command()
async def sol(ctx):
    await ctx.message.delete()
    price = await fetch_crypto_price("solana")
    await ctx.send(f"🪙 | **Live SOL Price:** `${price:,.2f} USD`" if price else "⚠️ Fetch failed.")

@bot.command()
async def usdt(ctx):
    await ctx.message.delete()
    price = await fetch_crypto_price("tether")
    await ctx.send(f"🪙 | **Live USDT Price:** `${price:,.3f} USD`" if price else "⚠️ Fetch failed.")

@bot.command()
async def xrp(ctx):
    await ctx.message.delete()
    price = await fetch_crypto_price("ripple")
    await ctx.send(f"🪙 | **Live XRP Price:** `${price:,.4f} USD`" if price else "⚠️ Fetch failed.")

@bot.command()
async def ltc(ctx):
    await ctx.message.delete()
    price = await fetch_crypto_price("litecoin")
    await ctx.send(f"🪙 | **Live LTC Price:** `${price:,.2f} USD`" if price else "⚠️ Fetch failed.")

@bot.command()
async def u2l(ctx, usd_amount: float):
    await ctx.message.delete()
    price = await fetch_crypto_price("litecoin")
    if price: await ctx.send(f"🧮 | **{usd_amount} USD** ≈ **{usd_amount/price:.6f} LTC**")
    else: await ctx.send("⚠️ Conversion failed.")

@bot.command()
async def l2u(ctx, ltc_amount: float):
    await ctx.message.delete()
    price = await fetch_crypto_price("litecoin")
    if price: await ctx.send(f"🧮 | **{ltc_amount} LTC** ≈ **${ltc_amount*price:.2f} USD**")
    else: await ctx.send("⚠️ Conversion failed.")

@bot.command()
async def i2c(ctx, inr_amount: float):
    await ctx.message.delete()
    price = await fetch_crypto_price("litecoin", "inr")
    if price: await ctx.send(f"🧮 | **₹{inr_amount} INR** ≈ **{inr_amount/price:.6f} LTC**")

@bot.command()
async def c2i(ctx, ltc_amount: float):
    await ctx.message.delete()
    price = await fetch_crypto_price("litecoin", "inr")
    if price: await ctx.send(f"🧮 | **{ltc_amount} LTC** ≈ **₹{ltc_amount*price:.2f} INR**")

@bot.command()
async def addy(ctx): 
    await ctx.message.delete(); await ctx.send(f"🔗 | **Address 1:** `{config.get('ltc_address', 'Not Set')}`")

@bot.command()
async def addy2(ctx): 
    await ctx.message.delete(); await ctx.send(f"🔗 | **Address 2:** `{config.get('ltc_address2', 'Not Set')}`")

@bot.command()
async def bal(ctx, address: str):
    await ctx.message.delete()
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Fetch LTC Balance from LitecoinSpace (Fast, free, no rate limits)
            async with session.get(f"https://litecoinspace.org/api/address/{address}") as resp:
                if resp.status != 200:
                    await ctx.send("⚠️ Invalid Litecoin address or API error.")
                    return
                data = await resp.json()

            # Calculate total balance (Confirmed + Mempool Unconfirmed)
            chain_stats = data.get('chain_stats', {})
            mempool_stats = data.get('mempool_stats', {})

            confirmed_sat = chain_stats.get('funded_txo_sum', 0) - chain_stats.get('spent_txo_sum', 0)
            unconfirmed_sat = mempool_stats.get('funded_txo_sum', 0) - mempool_stats.get('spent_txo_sum', 0)
            
            total_litoshi = confirmed_sat + unconfirmed_sat
            balance_ltc = total_litoshi / 100000000.0

            # 2. Fetch current Litecoin USD price
            price = await fetch_crypto_price("litecoin")
            
            if price is not None:
                usd_balance = balance_ltc * price
                await ctx.send(
                    f"💸 | **Balance:** `{usd_balance:.2f}$` (`{balance_ltc:.4f} LTC`)\n"
                    f"🔗 | **Address:** `{address}`"
                )
            else:
                await ctx.send(f"💸 | **Balance:** `{balance_ltc:.4f} LTC` (USD Price unavailable)\n🔗 | **Address:** `{address}`")

    except Exception as e:
        await ctx.send("⚠️ Error fetching balance. Check address format.")


@bot.command()
async def mybal(ctx): 
    await ctx.invoke(bot.get_command('bal'), address=config.get('ltc_address'))

@bot.command()
async def mybal2(ctx): 
    await ctx.invoke(bot.get_command('bal'), address=config.get('ltc_address2'))

@bot.command()
async def send(ctx, address: str, amount_input: str):
    await ctx.message.delete()
    if str(ctx.author.id) != owner_id: return
    try:
        clean_amt = float(amount_input.replace('$', ''))
        price = await fetch_crypto_price("litecoin")
        converted_ltc = round(clean_amt / price, 8)
        
        url = 'https://api.tatum.io/v3/litecoin/transaction'
        payload = {
            "fromAddress": [{"address": config.get('ltc_address'), "privateKey": config.get('ltckey')}],
            "to": [{"address": address, "value": converted_ltc}],
            "fee": "0.00005", "changeAddress": config.get('ltc_address')
        }
        headers = {'Content-Type': 'application/json', 'x-api-key': config.get('apikey')}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                if 'txId' in data:
                    await ctx.send(f"✅ | Sent `{clean_amt}$` To `{address}`\n🔗 | https://live.blockcypher.com/ltc/tx/{data['txId']}")
                else:
                    await ctx.send("⚠️ Transaction failed. Insufficient funds or invalid API key.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")


# ==========================================
# ⛓️ CRYPTO TXID CHECKER (TEXT FORMAT)
# ==========================================

import aiohttp
import datetime

@bot.command(aliases=['txltc', 'ltctx'])
async def txidltc(ctx, txid: str):
    await ctx.message.delete()
    if "/" in txid:
        txid = txid.rstrip("/").split("/")[-1]
    txid = txid.strip()

    url = f"https://litecoinspace.org/api/tx/{txid}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    status_info = data.get('status', {})
                    confirmed = status_info.get('confirmed', False)
                    block_height = status_info.get('block_height', 'Unconfirmed')
                    block_time = status_info.get('block_time', 'Pending')
                    
                    readable_time = "Pending Confirmation"
                    if confirmed and block_time != 'Pending':
                        readable_time = datetime.datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S UTC')

                    msg = (
                        "🪙 **Litecoin TXID Status**\n"
                        f"🔗 **Transaction ID:** `{txid}`\n"
                        f"✅ **Status:** {'`Confirmed`' if confirmed else '⏳ `Unconfirmed`'}\n"
                        f"📦 **Block Height:** `{block_height}`\n"
                        f"🕒 **Block Time:** `{readable_time}`\n"
                        f"🌐 **Explorer:** <https://litecoinspace.org/tx/{txid}>"
                    )
                    await ctx.send(msg)
                else:
                    await ctx.send("❌ **Invalid LTC TXID or Transaction Not Found.**")
    except Exception as e:
        await ctx.send(f"⚠️ Error checking LTC TXID: `{e}`")


@bot.command(aliases=['txbtc', 'btctx'])
async def txidbtc(ctx, txid: str):
    await ctx.message.delete()
    if "/" in txid:
        txid = txid.rstrip("/").split("/")[-1]
    txid = txid.strip()

    url = f"https://mempool.space/api/tx/{txid}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    status_info = data.get('status', {})
                    confirmed = status_info.get('confirmed', False)
                    block_height = status_info.get('block_height', 'Unconfirmed')

                    msg = (
                        "🪙 **Bitcoin TXID Status**\n"
                        f"🔗 **Transaction ID:** `{txid}`\n"
                        f"✅ **Status:** {'`Confirmed`' if confirmed else '⏳ `Unconfirmed`'}\n"
                        f"📦 **Block Height:** `{block_height}`\n"
                        f"🌐 **Explorer:** <https://mempool.space/tx/{txid}>"
                    )
                    await ctx.send(msg)
                else:
                    await ctx.send("❌ **Invalid BTC TXID or Transaction Not Found.**")
    except Exception as e:
        await ctx.send(f"⚠️ Error checking BTC TXID: `{e}`")


# ==========================================
# 🛒 INR / UPI SECTION
# ==========================================

@bot.command()
async def upi(ctx): 
    await ctx.message.delete(); await ctx.send(f"💸 **UPI ID 1:** `{config.get('upi_id', 'Not Set')}`")

@bot.command()
async def upi2(ctx): 
    await ctx.message.delete(); await ctx.send(f"💸 **UPI ID 2:** `{config.get('upi2', 'Not Set')}`")

@bot.command()
async def qr(ctx):
    await ctx.message.delete()
    try: await ctx.send(file=discord.File('qr.png'))
    except: await ctx.send("⚠️ `qr.png` missing from folder.")

@bot.command()
async def qr2(ctx):
    await ctx.message.delete()
    try: await ctx.send(file=discord.File('qr2.png'))
    except: await ctx.send("⚠️ `qr2.png` missing from folder.")


# ==========================================
# 🏃 ACTIVITY SECTION
# ==========================================

@bot.command()
async def stream(ctx, *, title):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Streaming(name=title, url="https://twitch.tv/discord"))
    await ctx.send(f"✅ Status set to Streaming: **{title}**")

@bot.command()
async def play(ctx, *, title):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Game(name=title))
    await ctx.send(f"✅ Status set to Playing: **{title}**")

@bot.command()
async def watch(ctx, *, title):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=title))
    await ctx.send(f"✅ Status set to Watching: **{title}**")

@bot.command()
async def listen(ctx, *, title):
    await ctx.message.delete()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=title))
    await ctx.send(f"✅ Status set to Listening: **{title}**")

@bot.command()
async def stopactivity(ctx):
    await ctx.message.delete()
    await bot.change_presence(activity=None)
    await ctx.send("✅ Activity cleared.")


# ==========================================
# 🃏 CUSTOM RICH PRESENCE (RPC) SECTION
# ==========================================
# Large/small image fields accept either a Discord Developer Portal
# "Rich Presence Asset" key, or a direct http(s):// image/gif URL
# (auto-converted via Discord's external asset proxy). Note: RPC images
# always render as a static thumbnail in the client — gifs will not animate.

def resolve_asset(value):
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        return "mp:" + urllib.parse.quote(value, safe='')
    return value  # treat as a literal Developer Portal asset key

@bot.command()
async def setrpcname(ctx, *, text: str):
    await ctx.message.delete()
    config['rpc_name'] = text
    save_config(config)
    await ctx.send(f"✅ RPC name set to: `{text}`")

@bot.command()
async def setrpcdetails(ctx, *, text: str):
    await ctx.message.delete()
    config['rpc_details'] = text
    save_config(config)
    await ctx.send(f"✅ RPC details line set to: `{text}`")

@bot.command()
async def setrpcstate(ctx, *, text: str):
    await ctx.message.delete()
    config['rpc_state'] = text
    save_config(config)
    await ctx.send(f"✅ RPC state line set to: `{text}`")

@bot.command()
async def setrpclargeimage(ctx, *, url: str):
    await ctx.message.delete()
    config['rpc_large_image'] = url
    save_config(config)
    await ctx.send("✅ RPC large image set.")

@bot.command()
async def setrpclargetext(ctx, *, text: str):
    await ctx.message.delete()
    config['rpc_large_text'] = text
    save_config(config)
    await ctx.send(f"✅ RPC large image tooltip set to: `{text}`")

@bot.command()
async def setrpcsmallimage(ctx, *, url: str):
    await ctx.message.delete()
    config['rpc_small_image'] = url
    save_config(config)
    await ctx.send("✅ RPC small image set.")

@bot.command()
async def setrpcsmalltext(ctx, *, text: str):
    await ctx.message.delete()
    config['rpc_small_text'] = text
    save_config(config)
    await ctx.send(f"✅ RPC small image tooltip set to: `{text}`")

@bot.command()
async def setrpcappid(ctx, app_id: str):
    await ctx.message.delete()
    config['rpc_app_id'] = app_id
    save_config(config)
    await ctx.send(f"✅ RPC Application Id set to: `{app_id}`")

@bot.command()
async def applyrpc(ctx):
    await ctx.message.delete()

    assets = {}
    if config.get('rpc_large_image'):
        assets['large_image'] = resolve_asset(config['rpc_large_image'])
    if config.get('rpc_large_text'):
        assets['large_text'] = config['rpc_large_text']
    if config.get('rpc_small_image'):
        assets['small_image'] = resolve_asset(config['rpc_small_image'])
    if config.get('rpc_small_text'):
        assets['small_text'] = config['rpc_small_text']

    app_id = None
    if config.get('rpc_app_id'):
        try:
            app_id = int(config['rpc_app_id'])
        except ValueError:
            app_id = None

    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name=config.get('rpc_name') or "Custom Status",
        details=config.get('rpc_details') or None,
        state=config.get('rpc_state') or None,
        application_id=app_id,
        assets=assets or None,
    )
    try:
        await bot.change_presence(activity=activity)
        await ctx.send("✅ Custom RPC applied. Use `.stopactivity` to clear it.")
    except Exception as e:
        await ctx.send(f"⚠️ RPC apply failed: `{e}`")


# ==========================================
# 💬 MESSAGE MANAGEMENT
# ==========================================

@bot.command()
async def spam(ctx, amount: int, *, msg):
    await ctx.message.delete()
    for _ in range(amount):
        await ctx.send(msg)
        await asyncio.sleep(0.7)

@bot.command()
async def clear(ctx, amount: int):
    await ctx.message.delete()
    async for message in ctx.channel.history(limit=amount):
        if message.author == bot.user:
            try: await message.delete(); await asyncio.sleep(0.5)
            except: pass

@bot.command()
async def dm(ctx, user: discord.User, *, msg: str):
    await ctx.message.delete()
    try: await user.send(msg); await ctx.send(f"✅ Sent DM to **{user.name}**")
    except: await ctx.send("⚠️ Could not send DM.")

@bot.command()
async def dmall(ctx, *, msg: str):
    await ctx.message.delete()
    count = 0
    for member in ctx.guild.members:
        if member != bot.user and not member.bot:
            try: await member.send(msg); count += 1; await asyncio.sleep(1.0)
            except: pass
    await ctx.send(f"✅ Mass DM complete to `{count}` members.")


# ==========================================
# 🤖 AUTO SENDER & RESPONDER
# ==========================================

@bot.command()
async def addar(ctx, *, args):
    await ctx.message.delete()
    try:
        trigger, response = args.split(',', 1)
        auto_responders[trigger.strip()] = response.strip()
        await ctx.send(f"✅ Added AR for: `{trigger.strip()}`")
    except ValueError:
        await ctx.send("⚠️ Format: `.addar trigger , response`")

@bot.command()
async def removear(ctx, *, trigger):
    await ctx.message.delete()
    if trigger in auto_responders:
        del auto_responders[trigger]
        await ctx.send(f"✅ Removed AR: `{trigger}`")

@bot.command()
async def ar_list(ctx):
    await ctx.message.delete()
    if not auto_responders: return await ctx.send("📋 No ARs set.")
    resp = "📋 **Active Auto-Responders:**\n"
    for t, r in auto_responders.items(): resp += f"• `{t}` ➔ `{r}`\n"
    await ctx.send(resp)

@bot.command()
async def am(ctx, time_sec: int, channel_id: int, *, text: str):
    await ctx.message.delete()
    channel = bot.get_channel(channel_id)
    if not channel: return
    if channel_id in automag_tasks: automag_tasks[channel_id].cancel()

    async def automag_loop():
        try:
            while True:
                await channel.send(text)
                await asyncio.sleep(time_sec)
        except asyncio.CancelledError: pass

    automag_tasks[channel_id] = asyncio.create_task(automag_loop())
    await ctx.send(f"✅ AutoMag started in <#{channel_id}>.")

@bot.command()
async def am_stop(ctx, channel_id: int):
    await ctx.message.delete()
    if channel_id in automag_tasks:
        automag_tasks[channel_id].cancel()
        del automag_tasks[channel_id]
        await ctx.send(f"🛑 Stopped AutoMag in <#{channel_id}>.")


# ==========================================
# 🛡️ MODERATION SECTION
# ==========================================

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try: await member.ban(reason=reason); await ctx.send(f"✅ Banned **{member}**")
    except: await ctx.send("⚠️ Error banning.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try: await member.kick(reason=reason); await ctx.send(f"✅ Kicked **{member}**")
    except: await ctx.send("⚠️ Error kicking.")

@bot.command()
async def nuke(ctx):
    await ctx.message.delete()
    try:
        channel = ctx.channel; pos = channel.position
        new_channel = await channel.clone()
        await new_channel.edit(position=pos)
        await channel.delete()
        await new_channel.send("💥 Channel nuked!")
    except: pass

@bot.command()
async def hide(ctx):
    await ctx.message.delete()
    try: await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False); await ctx.send("🔒 Channel hidden.")
    except: pass

@bot.command()
async def unhide(ctx):
    await ctx.message.delete()
    try: await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True); await ctx.send("🔓 Channel unhidden.")
    except: pass


# ==========================================
# 🎙️ VC SECTION (24/7 SPOOF)
# ==========================================

@bot.command()
async def joinvc(ctx, channel_id: int = None):
    await ctx.message.delete()
    channel = bot.get_channel(channel_id) if channel_id else (ctx.author.voice.channel if ctx.author.voice else None)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        return await ctx.send("⚠️ Invalid Voice Channel.")
    try:
        await ctx.guild.change_voice_state(channel=channel, self_mute=True, self_deaf=False)
        await ctx.send(f"✅ Joined VC indefinitely: **{channel.name}**")
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")

@bot.command()
async def leavevc(ctx):
    await ctx.message.delete()
    try:
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send("✅ Left the voice channel.")
    except Exception as e:
        await ctx.send(f"⚠️ Error leaving VC: `{e}`")


# ==========================================
# 🤡 FUN & INTERACTION SECTION (Local Folder + Tenor Fallback)
# ==========================================

# Fallback Tenor Links (Used ONLY if local folder is empty or upload fails)
FALLBACK_MEDIA = {
    "hug": [
        "https://tenor.com/view/anime-hug-warm-hug-cuddle-gif-22530182"
    ],
    "slap": [
        "https://tenor.com/view/slap-anime-gif-22442232"
    ],
    "neko": [
        "https://tenor.com/view/catgirl-anime-neko-cute-gif-19272318"
    ],
    "fuck": [
        "https://tenor.com/view/anime-kiss-make-out-gif-24422200"
    ],
    "boobs": [
        "https://tenor.com/view/anime-waifu-gif-22442232"
    ]
}

def get_local_media(category):
    """
    Checks gifs/<category>/ for local image files (.gif, .png, .jpg).
    Returns path to file if found, otherwise returns None.
    """
    folder_path = os.path.join("gifs", category)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        valid_exts = ('.gif', '.png', '.jpg', '.jpeg', '.webp')
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
        if files:
            return os.path.join(folder_path, random.choice(files))
    return None

async def send_interaction(ctx, category, text_content=""):
    """
    Attempts to send a local GIF file attachment first.
    If no local file exists or upload fails, sends Tenor URL fallback.
    """
    local_file = get_local_media(category)

    if local_file:
        try:
            await ctx.send(content=text_content if text_content else None, file=discord.File(local_file))
            return
        except Exception as e:
            print(f"Failed to upload local file {local_file}: {e}")

    # Fallback to Tenor URL
    fallback_url = random.choice(FALLBACK_MEDIA.get(category, FALLBACK_MEDIA["neko"]))
    full_msg = f"{text_content}\n{fallback_url}" if text_content else fallback_url
    await ctx.send(full_msg.strip())


@bot.command()
async def rizz(ctx, user: discord.User = None):
    await ctx.message.delete()
    target = user or ctx.author
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://vinuxd.vercel.app/api/pickup", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                data = await resp.json() if resp.status == 200 else {}
                line = data.get('pickup', 'Are you a magician? Because everyone else disappears.')
                await ctx.send(f"😏 {target.mention}, {line}")
    except: 
        await ctx.send(f"😏 {target.mention}, Are you a magician? Because everyone else disappears.")

@bot.command()
async def joke(ctx):
    await ctx.message.delete()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://official-joke-api.appspot.com/random_joke", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                data = await resp.json()
                await ctx.send(f"🤡 **Joke:** {data.get('setup')}\n> *{data.get('punchline')}*")
    except: 
        await ctx.send("🤡 **Joke:** Why don't scientists trust atoms?\n> *Because they make up everything!*")

@bot.command()
async def neko(ctx):
    await ctx.message.delete()
    await send_interaction(ctx, category="neko")

@bot.command()
async def hug(ctx, user: discord.User = None):
    await ctx.message.delete()
    target = f" hugs {user.mention}" if user else ""
    await send_interaction(ctx, category="hug", text_content=f"🫂 {ctx.author.mention}{target}")

@bot.command()
async def slap(ctx, user: discord.User = None):
    await ctx.message.delete()
    target = f" slaps {user.mention}" if user else ""
    await send_interaction(ctx, category="slap", text_content=f"👋 {ctx.author.mention}{target}!")

@bot.command(aliases=['hass', 'hentai'])
async def boobs(ctx):
    await ctx.message.delete()
    await send_interaction(ctx, category="boobs")

@bot.command(aliases=['sex', 'f'])
async def fuck(ctx, user: discord.User = None):
    await ctx.message.delete()
    target = f" with {user.mention}" if user else ""
    await send_interaction(ctx, category="fuck", text_content=f"🔥 {ctx.author.mention}{target}")


# ==========================================
# 🔍 CHECKER SECTION (Token & Promo)
# ==========================================

@bot.command(aliases=['ct', 'checkt'])
async def checktoken(ctx, token: str):
    await ctx.message.delete()
    
    # Strip quotes if passed in arguments
    token = token.strip('"\'')
    
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com/api/v9/users/@me", headers=headers) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    
                    username = f"{user_data.get('username')}#{user_data.get('discriminator', '0')}" if user_data.get('discriminator') != '0' else user_data.get('username')
                    user_id = user_data.get('id')
                    email = user_data.get('email') or "N/A"
                    phone = user_data.get('phone') or "N/A"
                    mfa = "Enabled" if user_data.get('mfa_enabled') else "Disabled"
                    
                    nitro_types = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
                    nitro_str = nitro_types.get(user_data.get('premium_type', 0), "None")

                    msg = (
                        f"✅ **Token Valid!**\n"
                        f"👤 **User:** `{username}` (`{user_id}`)\n"
                        f"📧 **Email:** `{email}`\n"
                        f"📱 **Phone:** `{phone}`\n"
                        f"🔒 **2FA:** `{mfa}`\n"
                        f"🚀 **Nitro:** `{nitro_str}`"
                    )
                    await ctx.send(msg)
                elif resp.status in (401, 403):
                    await ctx.send("❌ **Invalid Token!** (Token is invalid, expired, or account is locked)")
                else:
                    await ctx.send(f"⚠️ API returned status code `{resp.status}`.")
    except Exception as e:
        await ctx.send(f"⚠️ Error checking token: `{e}`")


@bot.command(aliases=['cp', 'promo'])
async def checkpromo(ctx, code: str):
    await ctx.message.delete()
    
    # Extract code if a full URL was pasted (e.g. promotions.discord.gg/XYZ)
    if "/" in code:
        code = code.rstrip("/").split("/")[-1]
    code = code.strip()

    url = f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=true&with_subscription_plan=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    uses = data.get('uses', 0)
                    max_uses = data.get('max_uses', 1)
                    redeemed = data.get('redeemed', False)
                    
                    promotion = data.get('promotion', {})
                    title = promotion.get('outbound_title') or data.get('store_listing', {}).get('sku', {}).get('name') or "Nitro / Gift Promo"
                    
                    if redeemed or uses >= max_uses:
                        await ctx.send(f"❌ **Already Redeemed / Used Code:** `{code}`")
                    else:
                        await ctx.send(
                            f"✅ **Valid Promo Code!**\n"
                            f"🎁 **Type:** `{title}`\n"
                            f"📊 **Uses:** `{uses}/{max_uses}`\n"
                            f"🔗 **Code:** `{code}`"
                        )
                elif resp.status == 404:
                    await ctx.send(f"❌ **Invalid or Expired Code:** `{code}`")
                else:
                    await ctx.send(f"⚠️ Error checking promo (Status `{resp.status}`).")
    except Exception as e:
        await ctx.send(f"⚠️ Error checking promo: `{e}`")


@bot.command(aliases=['ctrial', 'ntrial', 'checktrail', 'trial'])
async def checktrial(ctx, token: str):
    await ctx.message.delete()
    
    # Clean token quotes
    token = token.strip('"\'')
    
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            # 1. Fetch Basic Account Info
            async with session.get("https://discord.com/api/v9/users/@me", headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send("❌ **Invalid Token!**")
                    return
                user_data = await resp.json()

            username = f"{user_data.get('username')}#{user_data.get('discriminator', '0')}" if user_data.get('discriminator') != '0' else user_data.get('username')
            user_id = user_data.get('id')
            
            nitro_types = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
            nitro_type = nitro_types.get(user_data.get('premium_type', 0), "None")

            # 2. Check Payment Methods (Required for claiming Trial promos)
            payment_methods = []
            async with session.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers) as resp:
                if resp.status == 200:
                    methods = await resp.json()
                    for pm in methods:
                        p_type = pm.get('type')
                        if p_type == 1:
                            payment_methods.append("Credit Card")
                        elif p_type == 2:
                            payment_methods.append("PayPal")
                        else:
                            payment_methods.append("Other")

            payment_str = ", ".join(payment_methods) if payment_methods else "None"

            # 3. Check Active Subscriptions for Trial Information
            has_active_trial = False
            async with session.get("https://discord.com/api/v9/users/@me/billing/subscriptions", headers=headers) as resp:
                if resp.status == 200:
                    subs = await resp.json()
                    for sub in subs:
                        if sub.get('trial_period_end') or sub.get('trial_id'):
                            has_active_trial = True
                            break

            # Evaluate Trial Eligibility / Status
            if has_active_trial:
                trial_status = "⚡ Active Trial Running"
            elif payment_methods and nitro_type == "None":
                trial_status = "✅ Ready for Trial (Payment Attached)"
            elif nitro_type != "None":
                trial_status = "⚠️ Has Active Nitro (Cannot claim standard trials)"
            else:
                trial_status = "❌ Needs Payment Method to Claim Trial"

            msg = (
                f"🧪 **Nitro Trial Token Check:**\n"
                f"👤 **User:** `{username}` (`{user_id}`)\n"
                f"🚀 **Nitro Status:** `{nitro_type}`\n"
                f"💳 **Payment Method:** `{payment_str}`\n"
                f"🎁 **Trial Readiness:** `{trial_status}`"
            )
            await ctx.send(msg)

    except Exception as e:
        await ctx.send(f"⚠️ Error checking trial token: `{e}`")


# ==========================================
# 🧩 PATCH: MISSING COMMANDS IMPLEMENTATION
# ==========================================

# --- AFK Section Patch ---
@bot.command()
async def smartafk(ctx, *, reason="I am away"):
    global afk_reason, smart_afk
    afk_reason = reason
    smart_afk = True
    await ctx.message.delete()
    await ctx.send(f"✅ Smart AFK set: `{reason}`")


# --- Image & User Section Patch ---
@bot.command()
async def avatar(ctx, user: discord.User = None):
    await ctx.message.delete()
    target = user or ctx.author
    avatar_url = target.avatar.url if target.avatar else target.default_avatar.url
    await ctx.send(f"🖼️ **Avatar for {target.name}:**\n{avatar_url}")

@bot.command()
async def leaveallgroups(ctx):
    await ctx.message.delete()
    count = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.GroupChannel):
            try:
                await channel.leave()
                count += 1
                await asyncio.sleep(1)
            except: pass
    await ctx.send(f"✅ Left `{count}` group chats.")

@bot.command()
async def closealldms(ctx):
    await ctx.message.delete()
    count = 0
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
            try:
                await channel.close()
                count += 1
                await asyncio.sleep(0.5)
            except: pass
    await ctx.send(f"✅ Closed `{count}` DMs.")


# --- Message Section Patch ---
@bot.command()
async def massdmfriends(ctx, *, msg: str):
    await ctx.message.delete()
    count = 0
    for friend in bot.user.friends:
        try:
            await friend.send(msg)
            count += 1
            await asyncio.sleep(1.5)
        except: pass
    await ctx.send(f"✅ Mass DM sent to `{count}` friends.")


# --- Moderation Section Patch ---
@bot.command()
async def banid(ctx, user_id: int):
    await ctx.message.delete()
    try:
        await ctx.guild.ban(discord.Object(id=user_id))
        await ctx.send(f"✅ Banned User ID: `{user_id}`")
    except Exception as e:
        await ctx.send(f"⚠️ Ban ID failed: `{e}`")

@bot.command()
async def unbanid(ctx, user_id: int):
    await ctx.message.delete()
    try:
        await ctx.guild.unban(discord.Object(id=user_id))
        await ctx.send(f"✅ Unbanned User ID: `{user_id}`")
    except Exception as e:
        await ctx.send(f"⚠️ Unban ID failed: `{e}`")

@bot.command()
async def chnl(ctx, *, name: str):
    await ctx.message.delete()
    try:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f"✅ Created channel: `{name}`")
    except Exception as e:
        await ctx.send(f"⚠️ Channel creation failed: `{e}`")

@bot.command()
async def role(ctx, *, name: str):
    await ctx.message.delete()
    try:
        await ctx.guild.create_role(name=name)
        await ctx.send(f"✅ Created role: `{name}`")
    except Exception as e:
        await ctx.send(f"⚠️ Role creation failed: `{e}`")


# --- VC Section Patch ---
@bot.command()
async def vckick(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        await member.move_to(None)
        await ctx.send(f"✅ Kicked **{member.name}** from VC.")
    except Exception as e:
        await ctx.send(f"⚠️ VC Kick failed: `{e}`")

@bot.command()
async def vcmute(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        await member.edit(mute=True)
        await ctx.send(f"✅ Muted **{member.name}** in VC.")
    except Exception as e:
        await ctx.send(f"⚠️ VC Mute failed: `{e}`")

@bot.command()
async def vcunmute(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        await member.edit(mute=False)
        await ctx.send(f"✅ Unmuted **{member.name}** in VC.")
    except Exception as e:
        await ctx.send(f"⚠️ VC Unmute failed: `{e}`")


# --- Checker & Alert Section Patch ---
@bot.command()
async def setlitchook(ctx, webhook: str):
    await ctx.message.delete()
    hooks['ltc'] = webhook
    await ctx.send("✅ LTC Webhook set.")

@bot.command()
async def setmaghook(ctx, webhook: str):
    await ctx.message.delete()
    hooks['msglog'] = webhook
    await ctx.send("✅ Log Webhook set.")

@bot.command()
async def setmentionhook(ctx, webhook: str):
    await ctx.message.delete()
    hooks['mention'] = webhook
    await ctx.send("✅ Mention Webhook set.")

@bot.command()
async def setgreet(ctx, *, text: str):
    await ctx.message.delete()
    global greet_msg
    greet_msg = text
    await ctx.send(f"✅ Greet message set: `{text}`")

@bot.command()
async def cleargreet(ctx):
    await ctx.message.delete()
    global greet_msg
    greet_msg = None
    await ctx.send("✅ Greet message cleared.")


# --- Welcome Section Patch ---
@bot.command()
async def setwelcomechannel(ctx, channel_id: int = None):
    await ctx.message.delete()
    channel = bot.get_channel(channel_id) if channel_id else ctx.channel
    if not channel or not isinstance(channel, discord.TextChannel):
        return await ctx.send("⚠️ Invalid Text Channel.")
    config['welcome_channel'] = channel.id
    save_config(config)
    await ctx.send(f"✅ Welcome channel set to: **#{channel.name}**")

@bot.command()
async def setwelcomemsg(ctx, *, message: str):
    await ctx.message.delete()
    config['welcome_msg'] = message
    save_config(config)
    await ctx.send(f"✅ Welcome message set:\n{message}")

@bot.command()
async def clearwelcome(ctx):
    await ctx.message.delete()
    config['welcome_channel'] = None
    config['welcome_msg'] = None
    save_config(config)
    await ctx.send("✅ Welcome message disabled.")


# ==========================================
# 🏁 RUN BOT
# ==========================================
if __name__ == '__main__':
    bot.run(config.get('token', ''))