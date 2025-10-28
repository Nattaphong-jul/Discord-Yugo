from discord.ext import commands
import discord
import random
from discord import channel, voice_client
from discord import FFmpegPCMAudio
import time
from datetime import datetime
import pandas as pd
import csv
import os
import shutil
import random
import ai_channel_manager

with open("token.txt", "r") as  file:
    Token = file.read()
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
script_dir = os.path.dirname(os.path.abspath(__file__))
client = commands.Bot(command_prefix= "-", intents=intents)
print(f"running on:{script_dir}")

import aiohttp

async def llama(prompt: str, model: str = "yugo-3b") -> str:
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "repeat_penalty": 1.05
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            return data.get("response", "").strip()


@client.event
async def on_ready():
    print("Yugo is ready")
    try:
        # Sync the commands with Discord (in case you add new commands)
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_message(message):

    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Mention respond
    if client.user in message.mentions or message.guild is None:
        if len(str(message.content)) == len(str(client.user.id)) + 3:
            async with message.channel.typing():
                reply = await llama(message.content.replace(f"<@{client.user.id}>", "Hi Yugo").strip())

            await message.channel.send(reply)
        else:
            async with message.channel.typing():
                reply = await llama(message.content.replace(f"<@{client.user.id}>", "").strip())

            await message.channel.send(reply)

    elif ai_channel_manager.is_ai_channel(message.channel.id) and not message.attachments:
        async with message.channel.typing():
            reply = await llama(message.content.replace(f"<@{client.user.id}>", "").strip())

        await message.channel.send(reply)

    # Process the command
    await client.process_commands(message)

@client.tree.command(name="aimode", description="Switch between AI mode for Yugo in this channel")
async def aimode(interaction: discord.Interaction):
    channel = interaction.channel
    channel_id = str(getattr(channel, "id", None))
    channel_name = getattr(channel, "name", None) or str(channel)

    if channel_id is None:
        await interaction.response.send_message("Cannot toggle AI mode in this channel 😵", ephemeral=True)
        return

    result = ai_channel_manager.toggle_channel(channel_name, channel_id)

    if result == "enabled":
        await interaction.response.send_message("AI mode enabled ✨", ephemeral=True)
    else:
        await interaction.response.send_message("AI mode disabled", ephemeral=True)

client.run(Token)