import discord
import typing
import wavelink
from discord.ext import commands
import random


def get_track_embed(search, playing):
    random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    title = f"🎶 Now Playing 🎶 \n\n {search}"
    if not playing:
        title = f"➕ Queued ➕ \n\n {search}"
    embed = discord.Embed(title=title, color=random_color, url=search.uri)

    if search.thumbnail is not None:
        embed.set_image(url=search.thumbnail)
    return embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.position = 0
        self.playingTextChannel = 0
        bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        print('---------- Music.py create_nodes() -----------')
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="lavalink.herokuapp.com", port=80, password="Uniqlo2143!", region="us")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog is now ready!")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> is now ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        try:
            self.queue.pop(0)
        except:
            pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if str(reason) == "FINISHED" and len(self.queue) != 0:
            next_track = self.queue[0]
            channel = self.bot.get_channel(self.playingTextChannel)

            try:
                await player.play(next_track)
            except:
                return await channel.send(embed=discord.Embed(title=f"Something went wrong"))

            await channel.send(get_track_embed(next_track, True))

    @commands.command(name="join", aliases=["connect", "summon"])
    async def join_command(self, ctx: commands.Context, channel: typing.Optional[discord.VoiceChannel]):
        if channel is None:
            channel = ctx.author.voice.channel

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is not None:
            if player.is_connected():
                return await ctx.send("Bot is already connected to a voice channel")

        await channel.connect(cls=wavelink.Player)
        mbed = discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(name="leave", alises=["disconnect"])
    async def leave_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("bot is not connected to any voice channel")

        await player.disconnect()
        mbed = discord.Embed(title="Disconnected", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(name="play")
    async def play_command(self, ctx: commands.Context, *, search: str):
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.is_playing():
            self.queue.append(search)
            print("Queuing", search)
            await ctx.send(embed=get_track_embed(search, False))
        else:
            await vc.play(search)
            print("Playing", search)

            await ctx.send(embed=get_track_embed(search, True))

    @commands.command(name="stop")
    async def stop_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("Bot is not connected to any voice channel")

        self.queue.clear()

        if player.is_playing:
            await player.stop()
            mbed = discord.Embed(title="Playback Stopped", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Nothing Is playing right now")

    @commands.command(name="pause")
    async def pause_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("Bot is not connected to any voice channel")

        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                mbed = discord.Embed(title="Playback Paused", color=discord.Color.from_rgb(255, 255, 255))
                return await ctx.send(embed=mbed)
            else:
                return await ctx.send("Nothing is playing right now")
        else:
            return await ctx.send("Playback is already paused")

    @commands.command(name="resume")
    async def resume_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("Bot is not connected to any voice channel")

        if player.is_paused():
            await player.resume()
            mbed = discord.Embed(title="Playback resumed", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Playback is not paused")

    @commands.command(name="volume")
    async def volume_command(self, ctx: commands.Context, to: int):
        if to > 100:
            return await ctx.send("Volume should be between 0 and 100")
        elif to < 1:
            return await ctx.send("Volume should be between 0 and 100")

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        await player.set_volume(to)
        mbed = discord.Embed(title=f"Changed volume to {to}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(name="playnow", aliases=["pn"])
    async def play_now_command(self, ctx: commands.Context, *, search: str):
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.play(search)

        await ctx.send(embed=get_track_embed(search, True))

    @commands.command(name="nowplaying", aliases=["now_playing", "np"])
    async def now_playing_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.reply("Bot is not connected to any voice channel")

        if player.is_playing():
            mbed = discord.Embed(
                title=f"Now Playing: {player.track}",
                color=discord.Color.from_rgb(255, 255, 255)
            )

            t_sec = int(player.track.length)
            hour = int(t_sec / 3600)
            min = int((t_sec % 3600) / 60)
            sec = int((t_sec % 3600) % 60)
            length = f"{hour}hr {min}min {sec}sec" if not hour == 0 else f"{min}min {sec}sec"

            mbed.add_field(name="Artist", value=player.track.info['author'], inline=False)
            mbed.add_field(name="Length", value=f"{length}", inline=False)

            return await ctx.send(embed=mbed)
        else:
            await ctx.send("Nothing is playing right now")

    @commands.command(name="skip")
    async def skip_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if len(self.queue) == 0:
            await ctx.reply("The queue is empty")
        else:
            next_track = self.queue[0]
            await player.play(next_track)
            await ctx.reply(embed=get_track_embed(next_track, True))

    @commands.command(name="queue", aliases=["q"])
    async def queue_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        title = ""
        if player.is_playing():
            title += f"🎶 Now playing {player.track} 🎶 \n\n"
        title += "⏯ Current queue"
        response = ""
        if len(self.queue) == 0:
            response += "No songs in queue"
        else:
            for i in range(len(self.queue)):
                response += f"\n {i + 1}. {self.queue[i]} \n"

        random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        embed = discord.Embed(title=title, description=response, color=random_color)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Music(client))