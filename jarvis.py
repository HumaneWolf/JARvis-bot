from configparser import ConfigParser
from dataclasses import dataclass
import discord
from discord.ext import commands
import logging
import sqlite3
import sys
from typing import List


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s; \t%(levelname)s; \t%(message)s')


# Load configuration
config = ConfigParser()
config.read('config.ini')


@dataclass
class Counter:
    counter_type: str
    name: str
    value: int


# Open database and create table
db = sqlite3.connect('datastore.db')
c = db.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS counters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT NOT NULL,
        name TEXT NOT NULL,
        counter BIGINT DEFAULT 0,
        
        UNIQUE (class, name)
    );
''')
db.commit()


def add_count(counter_type: str, name: str, value: int = 1):
    name = name.title()
    c = db.cursor()
    c.execute('INSERT OR IGNORE INTO counters (class, name) VALUES (?, ?);', (counter_type, name))
    c.execute('UPDATE counters SET counter=counter+? WHERE class=? AND name=?', (value, counter_type, name))
    c.execute('SELECT counter FROM counters WHERE class=? AND name=?', (counter_type, name))
    db.commit()
    return c.fetchone()[0]


def get_all() -> List[Counter]:
    c = db.cursor()
    result = []
    for row in c.execute('SELECT class, name, counter FROM counters ORDER BY counter DESC;'):
        result.append(Counter(row[0], row[1], row[2]))
    return result


# Create bot and commands
bot = commands.Bot(command_prefix='!')

@bot.command()
async def pun(ctx: commands.Context, name: str, count: int = 1):
    if ctx.author.bot:
        return
    if not ctx.guild:
        return
    if str(ctx.author.id) != config['BOT']['ownerid']:
        count = 1
    new_count = add_count('pun', name, count)
    await ctx.send(f'PUN JAR: Added {count} for {name}, their new total is now {new_count}')


@bot.command()
async def badjoke(ctx: commands.Context, name: str, count: int = 1):
    if ctx.author.bot:
        return
    if not ctx.guild:
        return
    if str(ctx.author.id) != config['BOT']['ownerid']:
        count = 1
    new_count = add_count('bad joke', name, count)
    await ctx.send(f'BAD JOKE JAR: Added {count} for {name}, their new total is now {new_count}')


@bot.command()
async def groan(ctx: commands.Context, name: str, count: int = 1):
    if ctx.author.bot:
        return
    if not ctx.guild:
        return
    if str(ctx.author.id) != config['BOT']['ownerid']:
        count = 1
    new_count = add_count('groan', name, count)
    await ctx.send(f'GROAN JAR: Added {count} for {name}, their new total is now {new_count}')


@bot.command()
async def jars(ctx: commands.Context):
    if ctx.author.bot:
        return
    if not ctx.guild:
        return
    embed = discord.Embed(title='Active Jars', type='rich', color=int(0x00FF00))
    for counter in get_all():
        embed.add_field(name=f'{counter.name}:', value=f'{counter.value} {counter.counter_type}s')
    await ctx.send(embed=embed)


# Run bot
logging.info('Almost ready')
bot.run(config['DISCORD']['token'])
