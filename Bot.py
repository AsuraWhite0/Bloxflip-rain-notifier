import discord
import json
from fake_useragent import UserAgent
from discord.ext import commands, tasks
import asyncio
import tls_client
import requests

bot_token = "bot token here" # discord token
channel_id = 123 # channel id to send rain notifier
Rolepingid = 123 # role id for ping once it rain
embed_title = "i love moon" # your embed title here
footer_text = "i love moon" # your footer embed text here
footer_icon = "" # your footer embed icon url here
color_embed = "0, 0, 0" # your color embed here(using rgb). exe 255,255,255 for white color. Do not Put like color_embed = "(255,255,255)" put only number inside it.
#ex : color_embed = "255, 255, 255" dont forgot those space
r, g, b = map(int, color_embed.split(", "))

# cf bypass method from @endoyko_  i love him :))
class cf_bypass:
    def __init__(self):
        self.ua = UserAgent()
        session = tls_client.Session(client_identifier="safari_15_6_1")
        self.session = session 
        self.headers = {
            "Referer": "https://bloxflip.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.generate_fake_user_agent()
        }

    def generate_fake_user_agent(self):
        return self.ua.random
    def get(self, url):
        response = self.session.get(url, headers=self.headers)
        return response

bypass = cf_bypass()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is online now sir')
    try:
        synced = await client.tree.sync()
        print(f'{len(synced)}')
    except Exception as e:
        print(f"{e}")
    rain_notifier.start()

def active():
    try:
        response = bypass.get("https://api.bloxflip.com/chat/history")
        data = json.loads(response.text)
        return data.get('rain', None)
    except (json.JSONDecodeError, Exception) as e:
        print(f"{e}")
        return None


def get_host_id(username):
    try:
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username]})
        response.raise_for_status()
        data = response.json()
        if data['data']:
            return data['data'][0]['id'], data['data'][0]['name']
    except (requests.RequestException, IndexError, KeyError):
        pass
    return None, username

async def send_discord_message(channel, content, embed):
    try:
        message = await channel.send(content=content, embed=embed)
        return message
    except Exception as e:
        print(f"{e}")
        return None

def getpfpurl(user_id):
    try:
        response = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=75x75&format=Png&isCircular=false")
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['imageUrl']
    except (requests.RequestException, IndexError, KeyError):
        return "https://www.roblox.com/images/RobloxDefaultAvatar.png"

@tasks.loop(seconds=1)
async def rain_notifier():
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"{channel_id} not found in server")
        return
    while True:
        rain = active()
        if rain is not None and rain.get('active', False):
            break
        await asyncio.sleep(1)
    user_id, host_username = get_host_id(rain['host'])
    avatar_url = getpfpurl(user_id) if user_id else getpfpurl(1)

    prize = f"{rain['prize']:,}".rstrip('0').rstrip('.')

    embed = discord.Embed(title=f"{embed_title}", color=discord.Color.from_rgb(r, g, b))
    embed.add_field(name="Hoster :", value=f"> {host_username}", inline=False)
    embed.add_field(name="RainAmount :", value=f"> {prize}R$", inline=False)
    embed.add_field(name="CashoutPer :", value="> Pending...", inline=False)
    embed.add_field(name="PlayerJoining:", value="> 1", inline=False)
    embed.add_field(name="Finished :", value="> False", inline=False)
    embed.add_field(name="Click Below to join faster", value="> [CLICK HERE TO JOIN FAST](https://bloxflip.com/)", inline=False)
    embed.set_footer(text=f"{footer_text}", icon_url=f"{footer_icon}")
    embed.set_thumbnail(url=avatar_url)
    embed.set_author(name="==> waiting for result.....<==", icon_url="https://images-ext-1.discordapp.net/external/9QdxoeY7eahqzko8-ZA22vU9fvUmdLwn4nfH6hs7MRg/https/images-ext-1.discordapp.net/external/SlykflAfUQwR8J7ltEDLOziBiegBrjzu8tZFUwd7bmU/%253Fsize%253D64/https/cdn.discordapp.com/emojis/1225744553173061654.gif")


    content = f"<@&{Rolepingid}>"
    message = await send_discord_message(channel, content, embed)
    if message is None:
        return

    rain_active = True
    playercount = set(rain['players']) if 'players' in rain else set()
    playerCheck = playercount.copy()

    while rain_active:
        await asyncio.sleep(1)
        current_rain = active()
        if current_rain is None or not current_rain.get('active', False):
            rain_active = False
            try:
                joined_count = len(playercount)
                if joined_count > 0:
                    prizeforeach = round(rain['prize'] / joined_count, 2)
                else:
                    prizeforeach = 0
                prizeforeach = f"{prizeforeach:,}".rstrip('0').rstrip('.')

                embed = discord.Embed(title=f"{embed_title}", color=discord.Color.from_rgb(r, g, b))
                embed.add_field(name="Hoster:", value=f"> {host_username}", inline=False)
                embed.add_field(name="RainAmount:", value=f"> {prize}R$", inline=False)
                embed.add_field(name="CashoutPer:", value=f"> {prizeforeach}R$", inline=True)
                embed.add_field(name="Playersjoined:", value=f"> {joined_count}", inline=False)
                embed.add_field(name="Finished:", value="> True", inline=False)
                embed.set_footer(text=f"{footer_text}", icon_url=f"{footer_icon}")
                embed.set_thumbnail(url=avatar_url)
                embed.set_author(name="==>RAINS RESULT<==", icon_url="https://images-ext-1.discordapp.net/external/3axdiDQWWMOHD5xHp_TbdK17sROoeKfnRt_3o39xeRk/%3Fsize%3D64%2522%2C/https/cdn.discordapp.com/emojis/1225690243382906910.webp")

                await message.edit(embed=embed)

            except Exception as e:
                print(f"{e}")
            finally:
                return

        current_players = set(current_rain.get('players', []))
        newplayers = current_players - playerCheck
        playercount.update(newplayers)

        if len(playercount) > 1:
            embed.set_field_at(index=3, name="Playersjoining :", value=f"> {len(playercount)}", inline=False)
            await message.edit(embed=embed)
client.run(bot_token)
