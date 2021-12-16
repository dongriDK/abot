# -*- coding:utf-8 -*-
import discord
import asyncio
import time
import datetime
import mysql.connector
import os
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from discord.ext.commands import CommandNotFound
from discord.ext import tasks

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix = '!ㅌ ', intents=intents)
voiceChannels = {"수다방":"👥＿수다방＿٩( ᐛ )", "스트리밍1":"📺＿스트리밍1", "스트리밍2":"📺＿스트리밍2", "스트리밍3":"📺＿스트리밍3",
                    "스트리밍4":"📺＿스트리밍4",  "스트리밍5":"📺＿스트리밍5",
                    "대기중":"👀＿대기중", "일반1":"⭐＿일반1", "일반2":"🌙＿일반2", "일반3":"🌕＿일반3", "랭크1":"⭐＿랭크1", "랭크2":"🌙＿랭크2",
                    "랭크3":"🌕＿랭크3", "랭크4":"🪐＿랭크4", "랭크5":"🌎＿랭크5", "듀오1":"⭐＿듀오1", "듀오2":"🌙＿듀오2", "기타게임방1":"⭐＿기타게임방1",
                    "기타게임방2":"🌙＿기타게임방2", "히드라전용＊감상":"🎧＿히드라전용＊감상", "하리보전용＊감상":"🎧＿하리보전용＊감상", "회의":"회의＿운영진맨날모여!쫄?",
                    "자유채팅방":"💬＿자유채팅방", "에펙＊구인방":"📝＿에펙＊구인방", "에펙＊닉넴방":"🚀＿에펙＊닉넴방", "에펙＊자랑방":"👑＿에펙＊자랑방",
                    "일상＆게임사진방":"📸＿일상＆게임사진방", "스트리밍채팅방":"💬＿스트리밍채팅방", "히드라＊노래추가":"🎵＿히드라＊노래추가",
                    "하리보＊노래추가":"🎵＿하리보＊노래추가", "채팅방":"운영＿채팅방", "인원기록＆관리":"운영＿인원기록＆관리", "탈주자관리":"운영＿탈주자관리", "인원정리공유":"운영＿인원정리공유",
                    "태준이방":"📡⚡＿태준이방", "신입가입양식":"운영＿신입가입양식", "공지양식":"운영＿양식＿매뉴얼", "잠수":"🌛💤＿잠수＿쿨쿨", "봇사용＊기본":"👾＿봇사용＊기본", "봇사용＊마냥":"🐱＿봇사용＊마냥",
                    "운영진맨날모여!쫄?":"회의＿운영진맨날모여!쫄?", "공지및채널관리":"🟥디렉터：공지및채널관리", "경고＆누적기록":"🟩오피스：경고＆누적기록",
                    "칼부림의그현장":"칼부림의그현장", "탈주자관리":"탈주자관리", "현생휴식유저":"현생휴식유저"}
config = {
    'user' : os.environ["user"],
    'password' : os.environ["password"],
    'host' : os.environ["host"],
    'port' : os.environ["port"],
    'database' : os.environ["database"],
    'raise_on_warnings' : True
}
buttons = [u"\u23EA", u"\u25C0", u"\u25B6", u"\u23E9"]

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

def DbConnect():
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    return con, cur
    
def DbLogin(id, name, tag, con, cur):
    try:
        cur.execute("insert into User_info values(%s, %s, %s, %s, %s)", (id, name, tag, 0, 0))
        con.commit()
    except:
        return 1
    return 0

def DbInit():
    con, cur = DbConnect()

    cur.execute("DROP TABLE Voice_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Voice_info(id VARCHAR(128), before_channel TEXT, after_channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("DROP TABLE Text_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Text_info(id VARCHAR(128), text TEXT, channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("DROP TABLE User_info")
    cur.execute("CREATE TABLE IF NOT EXISTS User_info(id VARCHAR(128), name TEXT, tag TEXT, ttext MEDIUMINT(9) DEFAULT '0', ttime MEDIUMINT(9) DEFAULT '0', PRIMARY KEY(id)) DEFAULT CHARSET=utf8mb4")
    con.commit()
    return 0

def DbModify_text(message, con, cur):
    try:
        msg = message.channel.name.split("＿")[1]
        if (msg == "공지양식"):
            return 0
    except:
        if (":" in message.channel.name):
            return 0
            # msg = message.channel.name.split(":")[1]
        msg = message.channel.name
    cur.execute("INSERT INTO Text_info(id, text, channel, time) VALUES(%s, %s, %s, %s)", (message.author.id, message.content.encode('utf-8'), msg, CurTime()))
    cur.execute("UPDATE user_info SET ttext=ttext+1 where id=%s", (message.author.id,))
    con.commit()
    return 0

def DbModify_voice(member, before, after, con, cur):
    retValue = 0
    beChannel = "없음" if before.channel == None else before.channel.name.split("＿")[1]
    afChannel = "없음" if after.channel == None else after.channel.name.split("＿")[1]
    if ("(" in beChannel):
        beChannel = beChannel.split("(")[0][:-1]
    if ("(" in afChannel):
        afChannel = afChannel.split("(")[0][:-1]

    if beChannel != afChannel:
        newTime = CurTime()

        if (beChannel != "없음"):
            year = str(time.localtime(time.time() + 32400).tm_year)

            cur.execute("SELECT time FROM voice_info where id=%s and after_channel=%s ORDER BY time desc limit 1", (member.id, beChannel))
            ret = cur.fetchall()
            try:
                oldTime = ret[0][0].decode()
            except:
                oldTime = CurTime()
            oldTime = year + "." + oldTime
            new_Time = year + "." + newTime

            oldSec = time.mktime(datetime.datetime.strptime(oldTime, '%Y.%m.%d %H:%M:%S').timetuple())
            newSec = time.mktime(datetime.datetime.strptime(new_Time, '%Y.%m.%d %H:%M:%S').timetuple())

            totalSeconds = newSec - oldSec

            if (totalSeconds < 20):
                retValue = 1

            cur.execute("UPDATE user_info SET ttime=ttime+%s where id=%s", (totalSeconds, member.id,))
            con.commit()

        cur.execute("INSERT INTO Voice_info(id, before_channel, after_channel, time) VALUES(%s, %s, %s, %s)", (member.id, beChannel, afChannel, newTime))
        con.commit()

    return retValue

def DbSearch_member(name, tag, con, cur):
    # cur.execute("SELECT id from User_info where name=%s and tag=%s", (name, tag))
    cur.execute("SELECT id from login where name=%s and tag=%s", (name, tag))
    memberId = cur.fetchall()

    return memberId

def DbSearch_member_byid(id, con, cur):
    cur.execute("SELECT name, tag from User_info where id=%s", (id,))

    return cur.fetchall()

def DbSearchText_member(id, con, cur):
    cur.execute("SELECT * from Text_info where id=%s order by time desc limit 10", (id,))
    textList = cur.fetchall()

    return textList

def DbSearchVoice_member(id, con, cur):
    cur.execute("SELECT * from Voice_info where id=%s order by time desc limit 10", (id,))
    voiceList = cur.fetchall()

    return voiceList

def DbSearchbellrun(channel, time, con, cur):
    cur.execute("SELECT User_info.name, Voice_info.before_channel, Voice_info.after_channel, Voice_info.time FROM User_info left join Voice_info on User_info.id = Voice_info.id where Voice_info.time like %s and (Voice_info.before_channel like %s or Voice_info.after_channel like ?) ORDER BY time desc",(time+"%", channel, channel))
    channelList = cur.fetchall()

    return channelList

def DbSearchtime(id, flag, con, cur):
    if (flag == 1):
        cur.execute("SELECT ttime FROM user_info WHERE id=%s", (id,))
        ttime = cur.fetchall()
        try:
            ttime = ttime[0][0]
        except:
            ttime = 0

        return ttime

    if (flag == 2):
        cur.execute("SELECT ttext FROM user_info WHERE id=%s", (id,))
        textime = cur.fetchall()
        return textime[0][0] 
    
    if (flag == 3):
        cur.execute("SELECT ttime, ttext FROM user_info WHERE id=%s", (id,))
        ttime = cur.fetchall()
        try:
            ttime1 = ttime[0][0]
        except:
            ttime1 = 0
        try:
            ttime2 = ttime[0][1]
        except:
            ttime2 = 0
        return ttime1, ttime2

async def SendMessage(channel, msg):
    channel = bot.get_channel(894545802247159808)
    await channel.send(msg)

def MakePageList(channel, list_, flag):
    disc_list = []
    pages = []
    total_len = len(list_)
    total_page = total_len // 20 + 1 if total_len / 20 > total_len // 20 else total_len // 20
    for i in range(total_page):
        disc_list.append("")
        pages.append("")
    count = 0
    page = 0 
    if flag == 1: # 벨튀
        for i in list_:
            disc_list[page] += i[3].decode()
            disc_list[page] += " ㅤ"
            try:
                becha = voiceChannels[i[1].decode()]
            except:
                becha = "없음"
            disc_list[page] += becha
            disc_list[page] += " -> "
            try:
                afcha = voiceChannels[i[2].decode()]
            except:
                afcha = "없음"
            disc_list[page] += afcha
            disc_list[page] += " ㅤ"
            disc_list[page] += i[0].decode()
            disc_list[page] += "\n"
            count += 1
            if (count % 20 == 0 or count == total_len):
                pages[page] = discord.Embed(title = channel + " 입장 기록 " + str(page + 1) + "/" + str(total_page), 
                                            description="총 " + str(total_len) + "명\n" + disc_list[page], 
                                            color=0x00aaaa)
                page += 1
    else:
        for i in list_:
            disc_list[page] += i
            count += 1
            if (count % 20 == 0 or count == total_len):
                if (flag == 2): # 채팅만2
                    pages[page] = discord.Embed(title = "채팅과 음성 30분 미만 유저 " + str(page + 1) + "/" + str(total_page),
                                                description="총 " + str(total_len) + "명\n" + disc_list[page],
                                                color=0x00aaaa)
                elif (flag == 3): # 인원정리
                    pages[page] = discord.Embed(title = "유령회원 목록 " + str(page + 1) + "/" + str(total_page),
                                                description="총 " + str(total_len) + "명\n" + disc_list[page],
                                                color=0x00aaaa)
                page += 1

    return pages

async def Pages(ctx, pages):
    current = 0
    msg = await ctx.send(embed=pages[current])
    for button in buttons:
        await msg.add_reaction(button)

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=90.0)

        except asyncio.TimeoutError:
            embed = pages[current]
            await msg.clear_reactions()
            embed.set_footer(text="Timed Out.")

        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
            elif reaction.emoji == u"\u25C0":
                if current > 0:
                    current -= 1
            elif reaction.emoji == u"\u25B6":
                if current < len(pages) -1:
                    current += 1
            elif reaction.emoji == u"\u23E9":
                current = len(pages) -1

            for button in buttons:
                await msg.remove_reaction(button, ctx.author)
            if current != previous_page:
                await msg.edit(embed=pages[current])
    return

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
    con, cur = DbConnect()
    DbReturn = DbLogin(member.id, member.name, member.discriminator, con, cur)
    retValue = DbModify_voice(member, before, after, con, cur)
    # if (retValue == 1):
    #     await SendMessage(1, member.name + "벨튀 탐지")

    return 0
    
@bot.event
async def on_message(message):
    con, cur = DbConnect()
    if (message.author.name != "태준이"):
        if("!ㅌ" not in message.content):
            DbReturn = DbLogin(message.author.id, message.author.name, message.author.discriminator, con, cur)
            DbModify_text(message, con, cur)

    await bot.process_commands(message)
    return 0

# @bot.event
# async def on_message_delete(message):
#     # embed = discord.Embed(description=message.content + " 삭제됨")
#     channel = bot.get_channel(894545802247159808)
#     await channel.send("'" + message.content + "'" + " 메시지 삭제됨")

# @bot.event
# async def on_message_edit(before, after):
#     channel = bot.get_channel(894545802247159808)
#     await channel.send("'" + before.content + "'" + " -> " + "'" + after.content + "'" + "메시지 변경됨")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        embed = discord.Embed(description="없는 명령어입니다.")
        await ctx.channel.send(embed=embed)

    elif isinstance(error, CommandInvokeError):
        embed = discord.Embed(description="없는 채널입니다.")
        await ctx.channel.send(embed=embed)
    raise error


@bot.event
async def on_member_join(member):
    con, cur = DbConnect()
    cur.execute("SELECT count from login where id=%s", (member.id,))
    count = cur.fetchall()
    if len(count) == 0:
        cur.execute("INSERT INTO login(id, name, tag, count) VALUES(%s, %s, %s, %s)", (member.id, member.name, member.discriminator, 1))
        con.commit()
        print(member)
    elif count[0][0] >= 2:
        channel = bot.get_channel(894545802247159808)
        ret = str(member.name) + " " + str(member.discriminator) + "서버 재입장 3회 탐지"
        await channel.send(ret)
        await channel.send(ret)
        await channel.send(ret)
    else:
        cur.execute("UPDATE login SET count=count+1 where id=%s", (member.id,))
        con.commit()

@bot.command()
async def test(ctx):
    if WhiteList(ctx):
        print(bot.get_all_channels())
#         guild = bot.get_guild(875392692014694450)
#         for member in guild.members:
#             if(member.bot != True):
#                 print(member)
#                 con, cur = DbConnect()
#                 try:
#                     cur.execute("INSERT INTO login(id, name, tag, count) VALUES(%s, %s, %s, %s)", (member.id, member.name, member.discriminator, 1))
#                     con.commit()
#                 except:
#                     print("error", member)
#                     pass
                

@bot.command()
async def 초기화(ctx):
    if WhiteList(ctx):
        embed = discord.Embed(description="초기화 중입니다... \n잠시만 기다려주세요...")
        msg = await ctx.send(embed=embed)
        DbInit()
        await msg.delete()
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
    con, cur = DbConnect()
    if WhiteList(ctx):
        if len(args) == 2:
            name = args[0]
            tag = args[1]
        else:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return

        memberId = DbSearch_member(name, tag, con, cur)
        try:
            memberId = memberId[0][0].decode()
        except:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            # embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
            #                         description="없습니다.")
            await ctx.channel.send(embed=embed)
            return    

        textAnswer = ""
        voiceAnswer = ""

        textReturn = DbSearchText_member(memberId, con, cur)
        voiceReturn = DbSearchVoice_member(memberId, con, cur)
        ttime, ttext = DbSearchtime(memberId, 3, con, cur)

        if len(textReturn) == 0 and len(voiceReturn) == 0:
            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    description="없습니다.")
            await ctx.channel.send(embed=embed)
            return    
        
        textFlag = False
        voiceFlag = False
        textAnswer += "총 채팅 수 : " + str(ttext) + "\n"
        for j in textReturn:
            textAnswer += j[3].decode()
            textAnswer += " ㅤ"
            try:
                textAnswer += voiceChannels[j[2].decode()]
            except:
                textAnswer += j[2].decode()
            textAnswer += " ㅤ"
            textAnswer += j[1].decode()
            textAnswer += "\n"
            textFlag = True
        voiceAnswer += "음성채널 누적 시간 : " + str(datetime.timedelta(seconds=int(ttime))) + "\n"
        for j in voiceReturn:
            voiceAnswer += j[3].decode()
            voiceAnswer += " ㅤ"
            try:
                becha = voiceChannels[j[1].decode()] + " "
            except:
                becha = "없음"
            voiceAnswer += becha
            voiceAnswer += " -> "
            try:
                afcha = voiceChannels[j[2].decode()] + " "
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
    con, cur = DbConnect()
    if WhiteList(ctx):
        msg = await ctx.send("인원 정리중...")
        ghostList = []
        guild = bot.get_guild(875392692014694450)
        for member in guild.members:
            if (member.bot != True):
                textReturn = DbSearchText_member(member.id, con, cur)
                voiceReturn = DbSearchVoice_member(member.id, con, cur)

                if (len(textReturn) == 0 and len(voiceReturn) == 0):
                    ghost = ""
                    temp = DbSearch_member_byid(member.id, con, cur)
                    if (len(temp) == 0):
                        ghost += member.name
                        ghost += " ㅤ"
                        ghost += member.discriminator
                        ghost += "\n"
                        ghostList.append(ghost)
                    else:
                        ghost += temp[0][0].decode()
                        ghost += " ㅤ"
                        ghost += temp[0][1].decode()
                        ghost += "\n"
                        ghostList.append(ghost)

        pages = MakePageList(member, ghostList, 3)
        await msg.delete()
        await Pages(ctx, pages) 

        return
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 벨튀(ctx, *args):
    con, cur = DbConnect()
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
            DbReturn = DbSearchbellrun(channel, time, con, cur)

        pages = MakePageList(channel, DbReturn, 1)

        await Pages(ctx, pages)

    return 
    
    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return

@bot.command()
async def 채팅만(ctx):
    con, cur = DbConnect()
    if WhiteList(ctx):
        msg = await ctx.send("채팅, 음성기록 정리중...")
        guild = bot.get_guild(875392692014694450)
        chatList = []
        for member in guild.members:
            if (member.bot != True):
                textReturn = DbSearchText_member(member.id, con, cur)
                voiceReturn = DbSearchtime(member.id, 1, con, cur)
                if (len(textReturn) != 0 and voiceReturn < 1800):
                    chat = ""
                    chat += member.name
                    chat += " ㅤ"
                    chat += member.discriminator
                    chat += " ㅤ"
                    chat += str(datetime.timedelta(seconds=int(voiceReturn)))
                    chat += "\n"
                    chatList.append(chat)
        pages = MakePageList(0, chatList, 2)

        await msg.delete()
        await Pages(ctx, pages)

    # else:
    #     if (ctx.author.name == "노우리"):
    #         embed = discord.Embed(description="우리님은 뭐다? 태준이 권한이 없다~",
    #                                 color=0x00aaaa)
    #         await ctx.channel.send(embed=embed)
    #     return



# @bot.command()
# async def 채팅만(ctx):
#     con, cur = DbConnect()
#     if WhiteList(ctx):
#         msg = await ctx.send("채팅기록 정리중...")
#         guild = bot.get_guild(875392692014694450)
#         chatList = ""
#         for member in guild.members:
#             if (member.bot != True):
#                 textReturn = DbSearchText_member(member.id, con, cur)
#                 voiceReturn = DbSearchVoice_member(member.id, con, cur)

#                 if (len(textReturn) != 0 and len(voiceReturn) == 0):
#                     chatList += member.name
#                     chatList += " ㅤ"
#                     chatList += member.discriminator
#                     chatList += "\n"

#         embed = discord.Embed(title="채팅만 쓴 유저",
#                                         description=chatList,
#                                         color=0x00aaaa)
#         await msg.delete()            
#         await ctx.channel.send(embed=embed)
    

bot.run(os.environ["token"])


