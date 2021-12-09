# -*- coding:utf-8 -*-
import sqlite3
from types import prepare_class
import discord
from discord.ext import commands
import time
from discord.ext.commands.core import Command
from discord.ext.commands.errors import CommandInvokeError
from discord.ext.commands import CommandNotFound
import mysql.connector
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix = '!ㅌ ', intents=intents)
voiceChannels = {"수다방":"👥＿수다방＿٩( ᐛ )", "스트리밍1":"📺＿스트리밍1", "스트리밍2":"📺＿스트리밍2", "스트리밍3":"📺＿스트리밍3",
                    "대기중":"👀＿대기중", "일반1":"⭐＿일반1", "일반2":"🌙＿일반2", "일반3":"🌕＿일반3", "랭크1":"⭐＿랭크1", "랭크2":"🌙＿랭크2",
                    "랭크3":"🌕＿랭크3", "랭크4":"🪐＿랭크4", "랭크5":"🌎＿랭크5", "듀오1":"⭐＿듀오1", "듀오2":"🌙＿듀오2", "기타게임방1":"⭐＿기타게임방1",
                    "기타게임방2":"🌙＿기타게임방2", "히드라전용＊감상":"🎧＿히드라전용＊감상", "하리보전용＊감상":"🎧＿하리보전용＊감상", "회의":"회의＿운영진맨날모여!쫄?",
                    "자유채팅방":"💬＿자유채팅방", "에펙＊구인방":"📝＿에펙＊구인방", "에펙＊닉넴방":"🚀＿에펙＊닉넴방", "에펙＊자랑방":"👑＿에펙＊자랑방",
                    "일상＆게임사진방":"📸＿일상＆게임사진방", "스트리밍채팅방":"💬＿스트리밍채팅방", "히드라＊노래추가":"🎵＿히드라＊노래추가",
                    "하리보＊노래추가":"🎵＿하리보＊노래추가", "채팅방":"운영＿채팅방", "인원기록＆관리":"운영＿인원기록＆관리", "탈주자관리":"운영＿탈주자관리",
                    "태준이방":"운영＿태준이방", "신입가입양식":"운영＿신입가입양식", "잠수":"🌛💤＿잠수＿쿨쿨", "봇사용＊기본":"👾＿봇사용＊기본", "봇사용＊마냥":"🐱＿봇사용＊마냥",
                    "운영진맨날모여!쫄?":"회의＿운영진맨날모여!쫄?"}
config = {
    'user' : os.environ["user"],
    'password' : os.environ["password"],
    'host' : os.environ["host"],
    'port' : os.environ["port"],
    'database' : os.environ["database"],
    'raise_on_warnings' : True
}


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
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)
    try:
        cur.execute("insert into User_info values(%s, %s, %s)", (id, name, tag,))
        con.commit()
    except:
        return 1
    return 0

def DbInit():
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    cur.execute("DROP TABLE Voice_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Voice_info(id VARCHAR(128), before_channel TEXT, after_channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("DROP TABLE Text_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Text_info(id VARCHAR(128), text TEXT, channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("DROP TABLE User_info")
    cur.execute("CREATE TABLE IF NOT EXISTS User_info(id VARCHAR(128), name TEXT, tag TEXT, PRIMARY KEY(id)) DEFAULT CHARSET=utf8mb4")
    con.commit()
    return 0

def DbModify_text(message):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)
    try:
        msg = message.channel.name.split("＿")[1]
    except:
        msg = message.channel.name

    cur.execute("INSERT INTO Text_info(id, text, channel, time) VALUES(%s, %s, %s, %s)", (message.author.id, message.content.encode('utf-8'), msg, CurTime()))
    con.commit()
    return 0

def DbModify_voice(member, before, after):
    beChannel = "없음" if before.channel == None else before.channel.name.split("＿")[1]
    afChannel = "없음" if after.channel == None else after.channel.name.split("＿")[1]

    if beChannel != afChannel:
        con = mysql.connector.connect(**config)
        cur = con.cursor(prepared=True)
        
        cur.execute("INSERT INTO Voice_info(id, before_channel, after_channel, time) VALUES(%s, %s, %s, %s)", (member.id, beChannel, afChannel, CurTime()))
        con.commit()
    return 0

def DbSearch_member(name, tag):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    cur.execute("SELECT id from User_info where name=%s and tag=%s", (name, tag))
    memberId = cur.fetchall()
    return memberId

def DbSearch_member_byid(id):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    cur.execute("SELECT name, tag from User_info where id=%s", (id,))
    return cur.fetchall()

def DbSearchText_member(id):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    cur.execute("SELECT * from Text_info where id=%s order by time desc limit 10", (id,))
    textList = cur.fetchall()
    return textList

def DbSearchVoice_member(id):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)   

    cur.execute("SELECT * from Voice_info where id=%s order by time desc limit 10", (id,))
    voiceList = cur.fetchall()
    return voiceList

def DbSearchbellrun(channel, time):
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)   

    # channelName = voiceChannels[channel]
    cur.execute("SELECT User_info.name, Voice_info.before_channel, Voice_info.after_channel, Voice_info.time FROM User_info left join Voice_info on User_info.id = Voice_info.id where Voice_info.time like %s and (Voice_info.before_channel like %s or Voice_info.after_channel like ?) ORDER BY time desc",(time+"%", channel, channel))
    channelList = cur.fetchall()

    return channelList

def DbSearchChatList():
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    cur.execute("SELECT User_info.name, user_info.tag, count(text_info.text) FROM User_info left join text_info on User_info.id = text_info.id GROUP BY text_info.id ORDER BY user_info.name")
    chatList = cur.fetchall()

    return chatList

def WhiteList(ctx):
    # if (ctx.author.name == "노우리"):
    #     return False
    for i in ctx.author.roles:
        if (i.name == "STAFF"):
            return True
    return False

@bot.event
async def on_ready():
    print(f'부팅 성공:{bot.user.name}!')
    game = discord.Game("탐지")
    await bot.change_presence(status = discord.Status.online, activity = game)

    return 0

@bot.event
async def on_voice_state_update(member, before, after):
    DbReturn = DbLogin(member.id, member.name, member.discriminator)
    DbModify_voice(member, before, after)

    return 0
    
@bot.event
async def on_message(message):
    if (message.author.name != "태준이"):
        if("!ㅌ" not in message.content):
            DbReturn = DbLogin(message.author.id, message.author.name, message.author.discriminator)
            DbModify_text(message)

    await bot.process_commands(message)
    return 0

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
    if WhiteList(ctx):
        embed = discord.Embed(description="초기화 중입니다... \n잠시만 기다려주세요...")
        await ctx.send(embed=embed)
        DbInit()
        embed = discord.Embed(description="초기화가 완료되었습니다.")
        await ctx.send(embed=embed)
        return
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 검색(ctx, *args): 
    if WhiteList(ctx):
        if len(args) == 2:
            name = args[0]
            tag = args[1]
        else:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return

        memberId = DbSearch_member(name, tag)
        if (len(memberId) == 0):
            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    description="없습니다.")
            await ctx.channel.send(embed=embed)
        else:
            textAnswer = ""
            voiceAnswer = ""

            memberId = memberId[0][0].decode()
            textReturn = DbSearchText_member(memberId)
            voiceReturn = DbSearchVoice_member(memberId)

            textFlag = False
            voiceFlag = False
            for j in textReturn:
                textAnswer += j[3].decode()
                textAnswer += " "
                textAnswer += voiceChannels[j[2].decode()]
                textAnswer += " ㅤ"
                textAnswer += j[1].decode()
                textAnswer += "\n"
                textFlag = True

            for j in voiceReturn:
                voiceAnswer += j[3].decode()
                voiceAnswer += "ㅤ"
                try:
                    becha = voiceChannels[j[1].decode()]
                except:
                    becha = "없음"
                voiceAnswer += becha
                voiceAnswer += " -> "
                try:
                    afcha = voiceChannels[j[2].decode()]
                except:
                    afcha = "없음"
                voiceAnswer += afcha
                voiceAnswer += "\n"
                voiceFlag = True

            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    color=0x00aaaa)
            if (textFlag): embed.add_field(name="채팅 기록", value=textAnswer, inline=False)
            if (voiceFlag): embed.add_field(name="음성 채널 기록", value=voiceAnswer, inline=False)
            await ctx.channel.send(embed=embed)
        return
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 인원정리(ctx):
    if WhiteList(ctx):
        await ctx.send("인원 정리중...")

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
                        ghostList += "ㅤ"
                        ghostList += member.discriminator
                        ghostList += "\n"
                    else:
                        ghostList += temp[0][0].decode()
                        ghostList += "ㅤ"
                        ghostList += temp[0][1].decode()
                        ghostList += "\n"


        embed = discord.Embed(title="유령회원 목록",
                                description=ghostList,
                                color=0x00aaaa)            
        await ctx.channel.send(embed=embed)

        return
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 벨튀(ctx, *args):
    if WhiteList(ctx):
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
                VoiceList += i[3].decode()
                VoiceList += "ㅤ"
                try:
                    becha = voiceChannels[i[1].decode()]
                except:
                    becha = "없음"
                VoiceList += becha
                VoiceList += " -> "
                try:    
                    afcha = voiceChannels[i[2].decode()]
                except:
                    afcha = "없음"
                VoiceList += afcha
                VoiceList += "ㅤ"
                VoiceList += i[0].decode()
                VoiceList += "\n"
            embed = discord.Embed(title=channel + " 입장 기록",
                                    description=VoiceList,
                                    color=0x00aaaa)
            await ctx.channel.send(embed=embed)
        return 
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 채팅만(ctx):
    if WhiteList(ctx):
        await ctx.send("채팅 기록 정리중...")
        guild = bot.get_guild(875392692014694450)
        chatList = ""
        for member in guild.members:
            if (member.bot != True):
                textReturn = DbSearchText_member(member.id)
                voiceReturn = DbSearchVoice_member(member.id)
                if (len(textReturn) != 0 and len(voiceReturn) == 0):
                    temp = DbSearch_member_byid(member.id)
                    if (len(temp) == 0):
                        chatList += member.name
                        chatList += "ㅤ"
                        chatList += member.discriminator
                        chatList += "\n"
                    else:
                        chatList += temp[0][0].decode()
                        chatList += "ㅤ"
                        chatList += temp[0][1].decode()
                        chatList += "\n"

        embed = discord.Embed(title="채팅만 친 유저",
                                        description=chatList,
                                        color=0x00aaaa)            
        await ctx.channel.send(embed=embed)
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return
bot.run(os.environ["token"])


