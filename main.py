import discord
import os
import json
import requests
import openai

from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents
from openai import OpenAI

#TODO Add Comment
load_dotenv()

# Create bot with specific intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

#Enable all intents and create client
bot = commands.Bot(command_prefix='!', intents=intents)

#TODO Add Comment
IGNORE_PREFIX = '$'
CHANNELS = ['1199945205663674409',
           '1117152162674393251']


#Indicator of succesful connection
@bot.event
async def on_ready():
  print('Online as {0.user}'.format(bot))


#TODO Add Comment
@bot.event
async def on_message(message):
  # Ignore messages from bots or that start with the IGNORE_PREFIX
  if message.author.bot or message.content.startswith(IGNORE_PREFIX):
    return

  if bot.user is None:
    return

  # Check if the message is in allowed channels or mentions the bot
  if message.channel.id not in CHANNELS and bot.user.id not in [
      user.id for user in message.mentions
  ]:
    return

  # Indicate typing while processing
  async with message.channel.typing():
    messages = []
    async for msg in message.channel.history(limit=10):
      messages.insert(0, msg)

    conversation = []

    conversation.append({
        'role': 'system',
        'content': 'NimBot is a friendly Discord chatbot.'
    })

    for msg in messages:
      if msg.author.bot and msg.author.id != bot.user.id:
        continue
      if msg.content.startswith(IGNORE_PREFIX):
        continue

      # Sanitize username
      username = ''.join(e for e in msg.author.name
                         if e.isalnum() or e in ['_'])

      role = 'assistant' if msg.author.id == bot.user.id else 'user'

      # Append the message to the conversation list with the correct structure
      conversation.append({
          'role': role,
          'name': username,
          'content': msg.content
      })

    try:
      # Use OpenAI API to get response
      client = OpenAI()
      response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                messages=conversation)
      response_message = response.choices[0].message.content

    except Exception as e:
      print(f'OpenAI Error: {e}')
      await message.reply(
          "I'm having some trouble with the OpenAI API. Try again in a moment."
      )
      return

    # Split and send response in chunks to avoid max message length limit
    chunk_size = 2000
    if response_message is not None:
      for i in range(0, len(response_message), chunk_size):
        await message.reply(response_message[i:i + chunk_size])


#TODO Add Comment
def get_repos(username):
  data = {"type": "all", "sort": "full_name", "direction": "asc"}

  username = username.split(" ")

  if len(username) != 2:
    return ("Invalid username.")

  username = username[1]
  retstring = "\n" + username + "'s repositories:\n"

  output = requests.get(
      "https://api.github.com/users/{}/repos".format(username),
      data=json.dumps(data))
  output = json.loads(output.text)

  for reponame in output:
    retstring += ("- " + reponame["name"] + "\n")

  return retstring


#Run the bot
bot.run(os.environ['TOKEN'])
