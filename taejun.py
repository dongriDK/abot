# -*- coding:utf-8 -*-
# import pdb
# from discord import channel
import sqlite3
import discord
import time
import os
from discord.ext import commands
from discord.ext.commands.core import Command
from discord.ext.commands.errors import CommandInvokeError
from discord.ext.commands import CommandNotFound

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix = '!ㅌ ', intents=intents)
# bot = commands.Bot(command_prefix = '!', help_command= None)
# token = "OTA1NDY3NDg2MjE5MTczOTI4.YYKgTw.Hcp7B-GFjqP4KiLCEZvkOzQo4Ic"
token = "OTA1ODA0MzEzMjY2MzcyNjQ4.YYPaAQ.Ubr4QPer_-EiBuM4X22Kks2SvQA"
voiceChannels = {"수다방":"👥＿수다방＿٩( ᐛ )", "스트리밍1":"📺＿스트리밍1", "스트리밍2":"📺＿스트리밍2", "스트리밍3":"📺＿스트리밍3",
                    "대기중":"👀＿대기중", "일반1":"⭐＿일반1", "일반2":"🌙＿일반2", "일반3":"🌕＿일반3", "랭크1":"⭐＿랭크1", "랭크2":"🌙＿랭크2",
                    "랭크3":"🌕＿랭크3", "랭크4":"🪐＿랭크4", "랭크5":"🌎＿랭크5", "듀오1":"⭐＿듀오1", "듀오2":"🌙＿듀오2", "기타게임방1":"⭐＿기타게임방1",
                    "기타게임방2":"🌙＿기타게임방2", "히드라전용감상":"🎧＿히드라전용＊감상", "하리보전용감상":"🎧＿하리보전용＊감상", "회의":"회의＿운영진맨날모여!쫄?"}

def CurTime():
    mon = str(time.localtime(time.time() + 32400).tm_mon)
    day = str(time.localtime(time.time() + 32400).tm_mday)
    hour = str(time.localtime(time.time() + 32400).tm_hour)
    min = str(time.localtime(time.time() + 32400).tm_min)
    sec = str(time.localtime(time.time() + 32400).tm_sec)
    if (len(mon) == 1): mon = "0" + mon
    if (len(day) == 1): day = "0" + day
    if (len(hour) == 1): hour = "0" + hour
    if (len(min) == 1): min = "0" + min
    if (len(sec) == 1): sec = "0" + sec
    strTime = mon + "." + day + " " + hour + ":" + min + ":" + sec
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
    beChannel = "없음" if before.channel == None else before.channel.name
    afChannel = "없음" if after.channel == None else after.channel.name

    # beChannel = beChannel.split("_")
    beChannel = "".join(beChannel.split("_"))
    afChannel = "".join(afChannel.split("_"))

    if beChannel != afChannel:
        con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
        cur = con.cursor()
        
        # DbSearch_bellrun(member, cur)


        cur.execute("INSERT INTO Voice_info(id, before_channel, after_channel, time) VALUES(?, ?, ?, ?)", (member.id, beChannel, afChannel, CurTime()))
    return 0

# def DbSearch_bellrun(member, cur):
#     cur.execute("SELECT time from Voice_info where id=? order by id desc limit 1", (member.id,))
#     memberTime = cur.fetchall()

#     beforeTime = int(memberTime[0][0].split(":")[1]) * 60 + int(memberTime[0][0].split(":")[2])
#     curTime = CurTime()
#     afterTime = int(curTime.split(":")[1]) * 60 + int(curTime.split(":")[2])
#     if ((afterTime - beforeTime) < 6):


#         print("A")
#     return 1

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

def DbSearchbellrun(channel, time):
    con = sqlite3.connect("Test.db", isolation_level = None, timeout = 10)
    cur = con.cursor()   

    channelName = voiceChannels[channel]
    cur.execute("SELECT User_info.name, Voice_info.before_channel, Voice_info.after_channel, Voice_info.time FROM User_info left join Voice_info on User_info.id = Voice_info.id where Voice_info.time like ? and (Voice_info.before_channel like ? or Voice_info.after_channel like ?) ORDER BY time desc",(time+"%", channelName, channelName))
    channelList = cur.fetchall()

    return channelList

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
        embed = discord.Embed(description="없는 명령어입니다.")
        await ctx.channel.send(embed=embed)

    elif isinstance(error, CommandInvokeError):
        embed = discord.Embed(description="없는 채널입니다.")
        await ctx.channel.send(embed=embed)
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
    print("BBB")
    for i in ctx.author.roles:
        print(ctx.author.roles)
        if (i.name == "STAFF"):
            if len(args) == 2:
                name = args[0]
                tag = args[1]
            else:
                embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
                await ctx.channel.send(embed=embed)
                return
            print(name, tag)
            memberId = DbSearch_member(name, tag)
            print(memberId)
            if (len(memberId) == 0):
                embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
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
                    textAnswer += " "
                    textAnswer += j[2]
                    textAnswer += " ㅤ"
                    textAnswer += j[1] 
                    textAnswer += "\n"
                    textFlag = True

                for j in voiceReturn:
                    voiceAnswer += j[3]
                    voiceAnswer += "ㅤ"
                    voiceAnswer += j[1]
                    voiceAnswer += " -> "
                    voiceAnswer += j[2]
                    voiceAnswer += "\n"
                    voiceFlag = True

                embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                        color=0x00aaaa)
                # embed.set_author(name=ctx.author.display_name,
                #                     icon_url=ctx.author.avatar_url)
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
                            ghostList += "\t"
                            ghostList += member.discriminator
                            ghostList += "\n"
                        else:
                            ghostList += temp[0][0]
                            ghostList += "\t"
                            ghostList += temp[0][1]
                            ghostList += "\n"


            embed = discord.Embed(title="유령회원 목록",
                                    description=ghostList,
                                    color=0x00aaaa)
            # embed.set_author(name=ctx.author.display_name,
            #                     icon_url=ctx.author.avatar_url,
            #                     )
            
            await ctx.channel.send(embed=embed)
                # allmembers.append(member.id)
                # print(member.id, member.name, member.discriminator)

            return

@bot.command()
async def 벨튀(ctx, *args):
    try:
        channel = args[0]
    except:
        channel = ""
    try:
        time = args[1]
    except:
        time = ""

    if channel == "" or time == "":
        embed = discord.Embed(description="!ㅌ 벨튀 [채널이름] [날짜]\n ex) !ㅌ 벨튀 랭크1 11.15")
        await ctx.channel.send(embed=embed)
    else:
        VoiceList = ""
        DbReturn = DbSearchbellrun(channel, time)
        for i in DbReturn:
            VoiceList += i[3]
            VoiceList += "ㅤ"
            VoiceList += i[1]
            VoiceList += " -> "
            VoiceList += i[2]
            VoiceList += "ㅤ"
            VoiceList += i[0]
            VoiceList += "\n"
        embed = discord.Embed(title=channel + " 입장 기록",
                                description=VoiceList,
                                color=0x00aaaa)
        # embed.set_author(name=ctx.author.display_name,
        #                 icon_url=ctx.author.avatar_url,
        #                 )
        await ctx.channel.send(embed=embed)

    return 
    # guild = bot.get_guild(875392692014694450)
    # import pdb
    # pdb.set_trace()
    
# @bot.command()
# async def 
# @bot.command(aliases=['안녕', '안녕하세요', 'ㅎㅇ'])
# async def 하이(ctx):
#     await ctx.send("안녕하세요")

# @bot.command()
# async def 자비스(ctx, *, text):
#     await ctx.send(text)

# @bot.command()
# async def hi(ctx):
#     await ctx.send("하이")


bot.run(os.environ["token"])


