import discord
from discord.ext import commands
from discord import Interaction, app_commands
import yt_dlp
import asyncio


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True


class Client(commands.Bot):
    async def on_ready(self):
        print('-------------')
        print('BOT IS ONLINE')
        print('-------------')

        #Forces code to activate '/' commands
        try:
            guild = discord.Object(id=1344903102968500274)
            synced = await self.tree.sync(guild=guild)
            print(f'Synched {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands: {e}')
    
    #Wag mo na lang po pansinin Sir hihi
    async def on_message(self,message):
        if 'chrysander' in message.content:
            await message.channel.send("**POTANG INA MO CHRYSANDER**")




max_bot = Client(command_prefix='!', intents=intents) #Arono required daw eh
guild_id = discord.Object(id=1344903102968500274) #Guild ID for slash commands



#This handles concurrent execution
async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query,ydl_opts))

#This function searches
def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)
    
#song que variable
song_ques = {}

#Slash commands
@max_bot.tree.command(name='mplay', description='Play some music', guild=guild_id)
@app_commands.describe(song_query="Search Query")
async def play(interaction: discord.Interaction, song_query: str):
    embed = discord.Embed(title=song_query, description="Currently Playing", color=discord.Colour.green())
    await interaction.response.send_message(embed=embed)

    voice_channel = interaction.user.voice.channel

    #pag walang tao sa VC
    if interaction.user.voice.channel is None:
        embed = discord.Embed(description="Asan ka bro? **Mauna** ka kasi")
        await interaction.followup.edit_message(embed=embed)
        return
    
    
    #checks if bot is in VC
    voice_client = interaction.guild.voice_client

    #checks if bot is in same channel as user
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    #sets what kind of video to stream
    ydl_options = {
        "format": "bestaudio[abr<=96]/bestaudio",
        "noplaylist": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    query = "ytsearch:" + song_query
    results = await search_ytdlp_async(query, ydl_options)
    tracks = results.get("entries", [])

    if tracks is None:
        await interaction.followup.send("No results found.")
        return
    
    first_track = tracks[0]
    audio_url = first_track["url"]
    title = first_track.get("title", "untitled")

    ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -c:a libopus -b:a 96k",
        }
    
    source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="C:\\ffmpeg\\ffmpeg.exe")

    voice_client.play(source)




max_bot.run('SECRET PU HIHI')

