# -*- coding:utf-8 -*-
from asyncio.windows_events import NULL
from discord.ext.commands import CommandNotFound
import sqlite3
import discord
from discord import channel
from discord.ext import commands
import time
import os

from discord.ext.commands.core import Command

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix = '!ㅌ ', intents=intents)
# bot = commands.Bot(command_prefix = '!', help_command= None)
# token = "OTA1NDY3NDg2MjE5MTczOTI4.YYKgTw.Hcp7B-GFjqP4KiLCEZvkOzQo4Ic"
token = "OTA1ODA0MzEzMjY2MzcyNjQ4.YYPaAQ.7BhPAiJ4b5FyW_ChKe2jTbesJtE"

def CurTime():
    day = str(time.localtime().tm_mday)
    hour = str(time.localtime().tm_hour)
    min = str(time.localtime().tm_min)
    sec = str(time.localtime().tm_sec)
    if (len(day) == 1): day = "0" + day
    if (len(hour) == 1): hour = "0" + hour
    if (len(min) == 1): min = "0" + min
    if (len(sec) == 1): sec = "0" + sec
    strTime = str(time.localtime().tm_mon) + "." + day + " " + hour + ":" + min + ":" + sec
    return strTime

def DbLogin(id, name, tag):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    try:
        cur.execute("insert into User_info values(?, ?, ?)", (id, name, tag))
    except:
        return 1

    return 0

def DbInit():
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    cur.execute("DROP TABLE Voice_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Voice_info(id TEXT, before_channel TEXT, after_channel TEXT, time TEXT)")
    cur.execute("DROP TABLE Text_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Text_info(id TEXT, text TEXT, channel TEXT, time TEXT)")
    cur.execute("DROP TABLE User_info")
    cur.execute("CREATE TABLE IF NOT EXISTS User_info(id TEXT, name TEXT, tag TEXT, PRIMARY KEY(id))")
    return 0

def DbModify_text(message):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    cur.execute("INSERT INTO Text_info(id, text, channel, time) VALUES(?, ?, ?, ?)", (message.author.id, message.content, message.channel.name, CurTime()))
    return 0

def DbModify_voice(member, before, after):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()
    
    beChannel = "없음" if before.channel == None else before.channel.name
    afChannel = "없음" if after.channel == None else after.channel.name

    cur.execute("INSERT INTO Voice_info(id, before_channel, after_channel, time) VALUES(?, ?, ?, ?)", (member.id, beChannel, afChannel, CurTime()))
    return 0

def DbSearch_member(name, tag):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    cur.execute("SELECT id from User_info where name=? and tag=?", (name, tag))
    memberId = cur.fetchall()
    return memberId

def DbSearch_member_byid(id):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    cur.execute("SELECT name, tag from User_info where id=?", (id,))
    return cur.fetchall()

def DbSearchText_member(id):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()

    cur.execute("SELECT * from Text_info where id=? order by time desc limit 10", (id,))
    textList = cur.fetchall()
    return textList

def DbSearchVoice_member(id):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()   

    cur.execute("SELECT * from Voice_info where id=? order by time desc limit 10", (id,))
    voiceList = cur.fetchall()
    return voiceList

@bot.event
async def on_ready():
    print(f'부팅 성공:{bot.user.name}!')
    game = discord.Game("Bot Test")
    await bot.change_presence(status = discord.Status.online, activity = game)
    return

@bot.event
async def on_voice_state_update(member, before, after):
    DbReturn = DbLogin(member.id, member.name, member.discriminator)

    DbReturn = DbModify_voice(member, before, after)

    return
    

@bot.event
async def on_message(message):
    # print(message.content)
    # pdb.set_trace()
    if (message.author.name != "태준이"):
        if("!ㅌ" not in message.content):
            DbReturn = DbLogin(message.author.id, message.author.name, message.author.discriminator)
            DbReturn = DbModify_text(message)

    await bot.process_commands(message)
    return
    # return 

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        embed = discord.Embed(description="없는 명령어 입니다.")
        ctx.channel.send(embed=embed)
    raise error

@bot.command()
async def 초기화(ctx):
    for i in ctx.author.roles:
        if (i.name == "STAFF"):
            embed = discord.Embed(description="초기화 중입니다... \n잠시만 기다려주세요...")
            await ctx.send(embed=embed)
            DbInit()
            embed = discord.Embed(description="초기화가 완료되었습니다.")
            await ctx.send(embed=embed)
            return

@bot.command()
# async def 검색(ctx, name, tag):
async def 검색(ctx, *args): 
    for i in ctx.author.roles:
        if (i.name == "STAFF"):
            if len(args) == 2:
                name = args[0]
                tag = args[1]
            else:
                embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
                await ctx.channel.send(embed=embed)
                return

            # pdb.set_trace()
            memberId = DbSearch_member(name, tag)
            # pdb.set_trace()
            if (len(memberId) == 0):
                embed = discord.Embed(name=ctx.author.display_name, 
                                        title=name + "(" + tag + ")" + "님에 대한 기록",
                                        description="없습니다.")
                await ctx.channel.send(embed=embed)
            else:
                textAnswer = ""
                voiceAnswer = ""

                memberId = memberId[0][0]
                textReturn = DbSearchText_member(memberId)
                voiceReturn = DbSearchVoice_member(memberId)
                # pdb.set_trace()


                textFlag = False
                voiceFlag = False
                for j in textReturn:
                    textAnswer += j[3]
                    textAnswer += "\t\t"
                    textAnswer += j[2]
                    textAnswer += "\t\t"
                    textAnswer += j[1] 
                    textAnswer += "\n"
                    textFlag = True

                for j in voiceReturn:
                    voiceAnswer += j[3]
                    voiceAnswer += "\t\t"
                    voiceAnswer += j[1]
                    voiceAnswer += "\t\t->\t\t"
                    voiceAnswer += j[2]
                    voiceAnswer += "\n"
                    voiceFlag = True
                embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                        color=0x00aaaa)
                embed.set_author(name=ctx.author.display_name,
                                    icon_url=ctx.author.avatar_url)
                if (textFlag): embed.add_field(name="채팅 기록", value=textAnswer, inline=False)
                if (voiceFlag): embed.add_field(name="음성 채널 기록", value=voiceAnswer, inline=False)
                await ctx.channel.send(embed=embed)
            return 

@bot.command()
async def 인원정리(ctx):
    for i in ctx.author.roles:
        if (i.name == "STAFF"):
            await ctx.send("인원 정리중...")

            # guild = bot.get_guild(894928878697594920)
            guild = bot.get_guild(875392692014694450)
            ghostList = ""
            for member in guild.members:
                if (member.bot != True):
                    textReturn = DbSearchText_member(member.id)
                    voiceReturn = DbSearchVoice_member(member.id)

                    if (len(textReturn) == 0 and len(voiceReturn) == 0):
                        temp = DbSearch_member_byid(member.id)
                        if (len(temp) == 0):
                            ghostList += member.name
                            ghostList += "\t\t"
                            ghostList += member.discriminator
                            ghostList += "\n"
                        else:
                            ghostList += temp[0][0]
                            ghostList += "\t\t"
                            ghostList += temp[0][1]
                            ghostList += "\n"


            embed = discord.Embed(title="유령회원 목록",
                                    description=ghostList,
                                    color=0x00aaaa)
            embed.set_author(name=ctx.author.display_name,
                                icon_url=ctx.author.avatar_url,
                                )
            
            await ctx.channel.send(embed=embed)

            return


bot.run(os.environ['token'])


