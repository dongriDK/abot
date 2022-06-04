# -*- coding:utf-8 -*-
import pdb
import discord
import asyncio
import time
import datetime
import mysql.connector
import os
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from discord.ext.commands import CommandNotFound
import requests
import telegram
import json

intents = discord.Intents.all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix = '!ㅌ ', intents=intents)
config = {
    'user' : os.environ["user"],
    'password' : os.environ["password"],
    'host' : os.environ["host"],
    'port' : os.environ["port"],
    'database' : os.environ["database"],
    'raise_on_warnings' : True
}

TELEGRAM_TOKEN = os.environ["telegram_token"]
CHAT_ID = os.environ["chat_id"]
APEX_TOKEN = os.environ["apex_token"]
APEX_URL = os.environ["apex_url"]
TEL_BOT = telegram.Bot(token=TELEGRAM_TOKEN)
taejunRoom = 905813712886198273
DeclarRoom = 926123278584651806
ServerRoom = 875392692014694450
STAFFROLE = 875396480381382706
BOT_DEFAULTROOM = 982617639203524628
cur_year = "2022"
buttons = [u"\u23EA", u"\u25C0", u"\u25B6", u"\u23E9"]

def CurTime():
    # year = str(time.localtime(time.time() + 32400).tm_year)
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

def CurDay():
    mon = str(time.localtime(time.time() + 32400).tm_mon)
    day = str(time.localtime(time.time() + 32400).tm_mday)
    if (len(mon) == 1): mon = "0" + mon
    if (len(day) == 1): day = "0" + day
    strTime = mon + "." + day
    return strTime

def DbConnect():
    con = mysql.connector.connect(**config)
    cur = con.cursor(prepared=True)

    return con, cur
    
def DbLogin(id, tag, con, cur):
    try:
        cur.execute("insert into User_info values(%s, %s, %s, %s)", (id, tag, 0, 0))
        con.commit()
    except:
        return 1
    return 0

def DbInit():
    con, cur = DbConnect()
    cur.execute("DROP TABLE Voice_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Voice_info(id varchar(128), be_channel TEXT, af_channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("DROP TABLE Text_info")
    cur.execute("CREATE TABLE IF NOT EXISTS Text_info(id VARCHAR(128), text TEXT, channel TEXT, time TEXT) DEFAULT CHARSET=utf8mb4")
    cur.execute("update user_info set ttime=0, ttext=0")
    con.commit()
    return 0

def DbModify_text(message, con, cur):
    cur.execute("INSERT INTO Text_info(id, text, channel, time) VALUES(%s, %s, %s, %s)", (message.author.id, message.content.encode('utf-8'), message.channel.id, CurTime()))
    cur.execute("UPDATE user_info SET ttext=ttext+1 where id=%s", (message.author.id,))
    con.commit()
    return 0

def DbModify_voice(member, before, after, con, cur):
    retValue = 0
    totalSeconds = 0

    beChannel = "없음" if before.channel == None else before.channel.id
    afChannel = "없음" if after.channel == None else after.channel.id

    if beChannel != afChannel:
        newTime = CurTime()
        if (beChannel != "없음"):
            cur.execute("SELECT time FROM voice_info where id=%s and af_channel=%s ORDER BY time desc limit 1", (member.id, beChannel))
            ret = cur.fetchall()
            try:
                oldTime = ret[0][0].decode()
            except:
                if(len(ret) == 0):
                    return 0, 0, 0
                oldTime = CurTime()

            oldSec = time.mktime(datetime.datetime.strptime("2022." + oldTime, '%Y.%m.%d %H:%M:%S').timetuple())
            newSec = time.mktime(datetime.datetime.strptime("2022." + newTime, '%Y.%m.%d %H:%M:%S').timetuple())

            totalSeconds = newSec - oldSec

            if (totalSeconds < 10):
                retValue = 1

            try:
                bef_cat_id = before.channel.category.id
            except:
                bef_cat_id = 0

            if (bef_cat_id == 875392692014694452 or bef_cat_id == 875416181077577809 or bef_cat_id == 875457125063733289 or bef_cat_id == 875392692014694451):
                cur.execute("UPDATE user_info SET ttime=ttime+%s where id=%s", (totalSeconds, member.id,))
                con.commit()

        cur.execute("INSERT INTO Voice_info(id, be_channel, af_channel, time) VALUES(%s, %s, %s, %s)", (member.id, beChannel, afChannel, newTime))
        con.commit()

    return retValue, beChannel, totalSeconds

def DbSearchTime_byid(id, con, cur):
    cur.execute("SELECT jointime from user_info where id=%s", (id,))

    return cur.fetchall()

def DbSearchText_member(id, con, cur, flag):
    if flag:
        cur.execute("SELECT * from Text_info where id=%s order by time desc limit 12", (id,))
    else:
        cur.execute("SELECT * from Text_info where id=%s order by time desc", (id,))
    textList = cur.fetchall()

    return textList

def DbSearchVoice_member(id, con, cur, flag):
    if flag:
        cur.execute("SELECT * from Voice_info where id=%s order by time desc limit 10", (id,))
    else:
        cur.execute("SELECT * from Voice_info where id=%s order by time desc", (id,))
    voiceList = cur.fetchall()

    return voiceList

# def DbSearchid_bytag(tag, con, cur):
    # cur.execute("SELECT id from user_info where tag=%s )

def DbSearchbellrun(channel, time, con, cur):
    # cur.execute("SELECT User_info.name, Voice_info.before_channel, Voice_info.after_channel, Voice_info.time FROM User_info left join Voice_info on User_info.id = Voice_info.id where Voice_info.time like %s and (Voice_info.before_channel like %s or Voice_info.after_channel like ?) ORDER BY time desc",(time+"%", channel, channel))
    cur.execute("SELECT * from voice_info where time like %s and (be_channel=%s or af_channel=%s) order by time desc",(time+"%", channel, channel))
    channelList = cur.fetchall()

    return channelList

def DbSearchVoiceRank(con, cur):
    cur.execute("SELECT * FROM user_info order by ttime desc limit 100")
    voiceList = cur.fetchall()

    return voiceList

def DbSearchTextRank(con, cur):
    cur.execute("SELECT * FROM user_info order by ttext desc limit 100")
    textList = cur.fetchall()

    return textList

def DbSearchtexttime(id, flag, con, cur):
    if (flag == 1):
        cur.execute("SELECT ttext FROM user_info WHERE id=%s", (id,))
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
            ttext = ttime[0][1]
        except:
            ttext = 0
        return ttime1, ttext

def FindChannelName(name):
    channels = bot.get_guild(ServerRoom).channels
    
    for i in channels:
        if name in i.name:
            return i.id
    return 0

async def SendMessage(channel, msg):
    channelg = bot.get_channel(channel)
    await channelg.send(msg)

def MakeEmbed(text):
    embed = discord.Embed(description=text)
    return embed

# tag : 1 = user, 2 = channel, 3 = role
def MakeMention(id, tag):
    if tag == 1:
        return "<@!" + str(id) + ">"
    elif tag == 2:
        return "<#" + str(id) + ">"
    elif tag == 3:
        return "<@&" + str(id) + ">"
    elif tag == 4:
        return "@" + str(id)
    

def MakePageList(channel, list_, flag, arg, arg1):
    showlist = 30
    disc_list = []
    pages = []
    total_len = len(list_)
    total_page = total_len // showlist + 1 if total_len / showlist > total_len // showlist else total_len // showlist
    for i in range(total_page):
        disc_list.append("")
        pages.append("")
        
    count = 0
    page = 0 
    if flag == 1: # 벨튀
        for i in list_:
            disc_list[page] += i[3].decode()
            disc_list[page] += " ㅤ"

            if i[1].decode() != "없음":
                disc_list[page] += MakeMention(i[1].decode(), 2)
            else:
                disc_list[page] += "없음"

            disc_list[page] += " -> "

            if i[2].decode() != "없음":
                disc_list[page] += MakeMention(i[2].decode(), 2)
            else:
                disc_list[page] += "없음"

            disc_list[page] += " ㅤ"
            disc_list[page] += MakeMention(i[0].decode(), 1)
            disc_list[page] += "\n"
            count += 1
            if (count % showlist == 0 or count == total_len):
                pages[page] = discord.Embed(title = channel + " 입장 기록 " + str(page + 1) + "/" + str(total_page), 
                                            description = disc_list[page], 
                                            color = 0x00aaaa)
                page += 1
    else:
        for i in list_:
            disc_list[page] += i
            count += 1

            if (count % showlist == 0 or count == total_len):
                if (flag == 2): # 채팅만
                    embed = discord.Embed(title = "채팅과 음성 2시간 미만 유저 " + str(page + 1) + "/" + str(total_page),
                                                description = "총 `" + str(total_len) + "`명\n" + disc_list[page],
                                                color = 0x00aaaa)
                    # embed.add_field(name="휴식회원", value = arg, inline = False)
                    pages[page] = embed
                elif (flag == 3): # 인원정리
                    embed = discord.Embed(title = "유령회원 목록 " + str(page + 1) + "/" + str(total_page),
                                            description = "총 `" + str(total_len) + "`명\n" + disc_list[page],
                                            color = 0x00aaaa)
                    # embed.add_field(name="휴식회원", value = arg, inline = False)
                    pages[page] = embed
                elif (flag == 4): # 음성 순위
                    pages[page] = discord.Embed(title = "음성채널 거주 시간 Top 100",
                                                description = disc_list[page],
                                                color = 0x00aaaa)
                elif (flag == 5): # 채팅 순위
                    pages[page] = discord.Embed(title = "채팅 Top 100",
                                                description = disc_list[page],
                                                color = 0x00aaaa)
                elif (flag == 6): # 채팅 검색
                    pages[page] = discord.Embed(title = channel + "님의 전체 채팅 기록 " + str(page + 1) + "/" + str(total_page) ,
                                                description = disc_list[page],
                                                color = 0x00aaaa)
                elif (flag == 7): # 음성 검색
                    pages[page] = discord.Embed(title = channel + "님의 전체 음성 기록 " + str(page + 1) + "/" + str(total_page),
                                                description = disc_list[page],
                                                color = 0x00aaaa)
                page += 1

    return pages

async def Pages(ctx, pages):
    current = 0
    msg = await ctx.send(embed=pages[current])
    for button in buttons:
        await msg.add_reaction(button)

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            embed = pages[current]
            await msg.clear_reactions()
            embed.set_footer(text="Timed Out.")
            return 0

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

async def ParsingJson(name, data, channel):
    try:
        data["Error"]
        await channel.send("`" + name + "` 플레이어에 대한 검색 결과가 없습니다.\n>>> 1. 스팀에서 플레이하는 경우 스팀 계정에 연결된 오리진 계정 이름을 사용하세요.\n2. 한글 닉네임은 검색이 불가합니다.")
        return 0
    except:
        pass

    info = data["global"]

    level = info["level"]
    rank = info["rank"]
    rankscore = rank["rankScore"]
    rankimg = rank["rankImg"]
    ladderPos = rank["ladderPosPlatform"]


    embed = discord.Embed(title = "Apex Legends 티어 검색", color=0x00aaaa)
    embed.set_thumbnail(url = rankimg)
    embed.add_field(name = "ID", value = name)
    embed.add_field(name = "Level", value = level)
    embed.add_field(name="RankScore", value = rankscore, inline = False)
    if ladderPos != -1:
        ladderPos = "#" + str(ladderPos)
        embed.add_field(name="Ladder", value=ladderPos, inline=False)

    return embed


def WhiteList(ctx):
    # if (ctx.author.name == "노우리"):
    #     return False
    for i in ctx.author.roles:
        if (i.name == "ADMIN"):
            return True
    return False

@bot.event
async def on_ready():
    print(f'부팅 성공:{bot.user.name}!')
    game = discord.Game("탐지")
    await bot.change_presence(status = discord.Status.online, activity = game)

    return 0

# 보이스 상태 변경 시 오출
@bot.event
async def on_voice_state_update(member, before, after):
    con, cur = DbConnect()
    DbReturn = DbLogin(member.id, member.discriminator, con, cur)
    retValue, beChannel, retTime = DbModify_voice(member, before, after, con, cur)
    if (retValue == 1 and beChannel != "없음"):
        runChannel_id = bot.get_channel(before.channel.id)
        runChannel_members = runChannel_id.members
        if len(runChannel_members) > 0:
            await SendMessage(taejunRoom, MakeMention(beChannel, 2) + "에서 " + MakeMention(member.id, 1) + " " + "`" + str(retTime) + "`" + "초 벨튀 탐지")

    return 0
    
# 메시지 생성 시 호출
@bot.event
async def on_message(message):
    con, cur = DbConnect()
    if (message.author.name != "태준이" and message.author.name != "InFi-EYE"):
        if("!ㅌ" not in message.content):
            DbReturn = DbLogin(message.author.id, message.author.discriminator, con, cur)
            DbModify_text(message, con, cur)
            # 휴식 신청 
            if message.channel.id == 926118022245142538 and (message.author.id != 581632092148989993 and message.author.id != 389659172158832644 and message.author.id != 364855162663075850):
                await message.delete()
                picture_url = ""
                if len(message.attachments) == 1:
                    picture_url = message.attachments[0].url
                    # await SendMessage(DeclarRoom, picture_url)
                msg = "**신고자** ㅤ: ㅤ" + MakeMention(message.author.id, 1) + "```" + message.content + "```"
                await SendMessage(DeclarRoom, msg + "\n" + picture_url)
            if(message.channel.id == BOT_DEFAULTROOM):
                if(message.content.startswith("!전적 ")):
                    msg = message.content.split(" ")
                    try:
                        name = msg[1]
                    except:
                        await message.channel.send("검색할 아이디를 입력하세요.")
                        await bot.process_commands(message)
                    
                    res = requests.get(APEX_URL + name + APEX_TOKEN)
                    json_data = json.loads(res.text)
                    embed = await ParsingJson(name, json_data, message.channel)
                    if (embed != 0):
                        await message.channel.send(embed = embed)

    await bot.process_commands(message)
    return 0

# @bot.event
# async def delete_message(message):
#     if message.author.id == "159985870458322944":

# 별명 변경 시 호출
@bot.event
async def on_member_update(before, after):
    beNick = before.display_name
    afNick = after.display_name
    if(beNick != afNick):
        msg = MakeMention(after.id, 1) + " ㅤ`" + beNick + "` -> `" + afNick + "` 별명 변경."
        await SendMessage(taejunRoom, msg)

# 프로필 변경 시 호출
@bot.event
async def on_user_update(before, after):
    con, cur = DbConnect()
    beName = before.display_name
    afName = after.display_name
    beDis = before.discriminator
    afDis = after.discriminator
    if (beName != afName):
        msg = MakeMention(after.id, 1) + " ㅤ`" + beName + "` -> `" + afName + "` 디스코드 아이디 변경"
        if (beDis != afDis):
            msg = MakeMention(after.id, 1) + " ㅤ`" + beName + "` " + "`" + beDis + "` -> `" + afDis + "` 디스코드 태그 변경"
        await SendMessage(taejunRoom, msg)

@bot.event
async def on_member_join(member):
    con, cur = DbConnect()
    cur.execute("SELECT count from user_info where id=%s", (member.id,))
    count = cur.fetchall()
    if len(count) == 0:
        print("join new", member)
        cur.execute("INSERT INTO user_info(id, tag, ttext, ttime, count, jointime) VALUES(%s, %s, %s, %s, %s, %s)", (member.id, member.discriminator, 0, 0, 1, CurDay()))
        con.commit()
    elif count[0][0] >= 3:
        print("join exc", member)
        channel = bot.get_channel(taejunRoom)
        ret = MakeMention(STAFFROLE, 3) + " ㅤ" + MakeMention(member.id, 1) + " ㅤ`" + str(member.name) + "` `" + str(member.discriminator) + "` 서버 재입장 3회 탐지"
        await channel.send(ret)
        cur.execute("UPDATE user_info SET count=count+1 where id=%s", (member.id,))
        con.commit()
    else:
        print("join again", member)
        cur.execute("UPDATE user_info SET count=count+1 where id=%s", (member.id,))
        con.commit()

@bot.event
async def on_member_remove(member):
    con, cur = DbConnect()
    cur.execute("SELECT count from user_info where id=%s", (member.id,))
    count = cur.fetchall()
    print(count)
    if count[0][0] >= 2:
        print("remove if", member)
        channel = bot.get_channel(taejunRoom)
        ret = MakeMention(STAFFROLE, 3) + " ㅤ" + MakeMention(member.id, 1) + " ㅤ`" + str(member.name) + "` `" + str(member.discriminator) + "` 서버 재입장 후 탈퇴"
        await channel.send(ret)
    else:
        print("remove else", member)
        cur.execute("UPDATE user_info SET count=count+1 where id=%s", (member.id,))
        con.commit()

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
        TEL_BOT.sendMessage(chat_id=CHAT_ID, text=str(ctx) + " " + str(error)+" 없는 명령어")
        await ctx.channel.send(embed=MakeEmbed("없는 명령어입니다."))

    elif isinstance(error, CommandInvokeError):
        TEL_BOT.sendMessage(chat_id=CHAT_ID, text=str(ctx) + " " + str(error)+"없는 채널")
        await ctx.channel.send(embed=MakeEmbed("없는 채널입니다."))
    raise error

@bot.command()
async def 초기화(ctx):
    if WhiteList(ctx):
        embed = discord.Embed(description="초기화 중입니다... \n잠시만 기다려주세요...")
        msg = await ctx.send(embed=embed)
        DbInit()
        await msg.delete()
        embed = discord.Embed(description="초기화가 완료되었습니다.")
        await ctx.send(embed=embed)
    return 0

@bot.command()
async def 검색(ctx, *args): 
    con, cur = DbConnect()
    if WhiteList(ctx):
        if len(args) == 2:
            name = args[0]
            tag = args[1]
        elif len(args) == 1:
            if "#" in args[0]:
                splittext = args[0].split("#")
                name = splittext[0]
                tag = splittext[1]
            else:
                embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
                await ctx.channel.send(embed=embed)
                return
                
        else:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return

        name = name.replace(" ", "")
        allMember = bot.get_guild(ServerRoom).members
        flag = False
        for i in allMember:
            if name in i.name.replace(" ", "") and tag in i.discriminator:
                memberId = i.id
                flag = True
        if not flag:
            # here
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return    

        textAnswer = ""
        voiceAnswer = ""

        textReturn = DbSearchText_member(memberId, con, cur, True)
        voiceReturn = DbSearchVoice_member(memberId, con, cur, True)
        ttime, ttext = DbSearchtexttime(memberId, 3, con, cur)
        jointime = DbSearchTime_byid(memberId, con, cur)
        if len(textReturn) == 0 and len(voiceReturn) == 0:
            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    description="없습니다.")
            await ctx.channel.send(embed=embed)
            return    
        
        textFlag = False
        voiceFlag = False
        textAnswer += "총 채팅 수 : `" + str(ttext) + "`\n"
        for j in textReturn:
            textAnswer += j[3].decode()
            textAnswer += " ㅤ"
            textAnswer += MakeMention(j[2].decode(), 2)
            textAnswer += " ㅤ"
            textAnswer += j[1].decode()
            textAnswer += "\n"
            textFlag = True
        voiceAnswer += "음성채널 누적 시간 : `" + str(datetime.timedelta(seconds=int(ttime))) + "`\n"
        for j in voiceReturn:
            voiceAnswer += j[3].decode()
            voiceAnswer += " ㅤ"
            if j[1].decode() != "없음":
                voiceAnswer += MakeMention(j[1].decode(), 2)
            else:
                voiceAnswer += "없음"
            voiceAnswer += " -> "
            if j[2].decode() != "없음":
                voiceAnswer += "<#" + j[2].decode() + ">"
            else:
                voiceAnswer += "없음"

            voiceAnswer += "\n"
            voiceFlag = True

        embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                color=0x00aaaa)
        embed.add_field(name="서버 입장", value = "`" + str(jointime[0][0].decode()) + "`\n", inline=False)
        if (textFlag): embed.add_field(name="채팅 기록", value=textAnswer, inline=False)
        if (voiceFlag): embed.add_field(name="음성 채널 기록", value=voiceAnswer, inline=False)
        await ctx.channel.send(embed=embed)

    return 0

@bot.command()
async def 인원정리(ctx):
    con, cur = DbConnect()
    if WhiteList(ctx):
        msg = await ctx.send("인원 정리중...")
        ghostList = []
        newjoinList = ""
        rest = ""
        flag = False
        guild = bot.get_guild(875392692014694450)
        for member in guild.members:
            # for roles in member.roles:
            #     if roles.id == 893155020499988490:
            #         rest += member.mention
            #         rest += " ㅤ"
            #         flag = True
            #         break
            
            if flag:
                flag = False
                continue

            if (member.bot != True):
                print(member)
                ttime, ttext = DbSearchtexttime(member.id, 3, con, cur)

                if (ttext == 0 and ttime == 0):
                    try:
                        jointime = DbSearchTime_byid(member.id, con, cur)[0][0].decode()
                    except:
                        print(member, "인원정리 except")
                        jointime = "00.00"
                    
                    curday = CurDay()
                    curday = curday[1:].split(".") if curday[0] == "0" else curday.split(".")
                    jointime1 = jointime[1:].split(".") if jointime[0] == "0" else jointime.split(".")

                    ghost = ""
                    ghost += member.mention
                    ghost += " (" + member.name + "#" + member.discriminator + ") "
                    ghost += " ㅤ**"
                    ghost += jointime
                    ghost += "**\n"
                    if (jointime1[0] != "0"):
                        if ((datetime.datetime(int(cur_year), int(curday[0]), int(curday[1])) - datetime.datetime(int(cur_year), int(jointime1[0]), int(jointime1[1]))).days < 15):
                            newjoinList += ghost
                        else:
                            ghostList.append(ghost)
                    else:
                        ghostList.append(ghost)

        if len(ghostList) == 0:
            await msg.delete()
            await SendMessage(taejunRoom, "인원정리 대상이 없습니다.")
        else:
            pages = MakePageList(member, ghostList, 3, rest, newjoinList)
            await msg.delete()
            embed = discord.Embed(title="신입회원", description = newjoinList)
            await ctx.send(embed=embed)
            await Pages(ctx, pages) 


    return 0

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
            retChannel = FindChannelName(channel)
            if retChannel == 0:
                await ctx.channel.send(embed=MakeEmbed("채널 이름 검색이 안됨"))
            DbReturn = DbSearchbellrun(retChannel, time, con, cur)

            if len(DbReturn) == 0:
                await ctx.channel.send(embed=MakeEmbed("결과가 없습니다."))
            else:
                pages = MakePageList(channel, DbReturn, 1, 0, 0)
                await Pages(ctx, pages)

    return 0

@bot.command()
async def 채팅만(ctx):
    con, cur = DbConnect()
    if WhiteList(ctx):
        msg = await ctx.send("채팅, 음성기록 정리중...")
        guild = bot.get_guild(875392692014694450)
        chatList = []
        newjoinList = ""
        rest = ""
        flag = False
        for member in guild.members:
            for roles in member.roles:
                if roles.id == 893155020499988490:
                    rest += member.mention
                    rest += " ㅤ"
                    flag = True
                    continue
            
            if flag:
                flag = False
                continue

            if (member.bot != True):
                # print(member)
                ttime, ttext = DbSearchtexttime(member.id, 3, con, cur)
                if ((ttime > 0 and ttime < 7200) or (ttext != 0 and ttime == 0)):
                    try:
                        jointime = DbSearchTime_byid(member.id, con, cur)[0][0].decode()
                    except:
                        print(member, "채팅만 except")
                        jointime = "00.00"

                    curday = CurDay()
                    curday = curday[1:].split(".") if curday[0] == "0" else curday.split(".")
                    jointime1 = jointime[1:].split(".") if jointime[0] == "0" else jointime.split(".")
                
                    chat = ""
                    chat += member.mention
                    chat += " (" + member.name + "#" + member.discriminator + ") "
                    chat += " ㅤ**"
                    chat += str(ttext)
                    chat += "** ㅤ`"
                    chat += str(datetime.timedelta(seconds=int(ttime)))
                    chat += "` ㅤ"
                    chat += jointime
                    chat += "\n"
                    if (jointime1[0] != "0"):
                        if ((datetime.datetime(int(cur_year), int(curday[0]), int(curday[1])) - datetime.datetime(int(cur_year), int(jointime1[0]), int(jointime1[1]))).days < 15):
                            newjoinList += chat
                        else:
                            chatList.append(chat)
                    else:
                        print(member)
                        chatList.append(chat)

        pages = MakePageList(0, chatList, 2, rest, newjoinList)
        await msg.delete()
        embed = discord.Embed(title="신입회원", description = newjoinList)
        await ctx.send(embed=embed)
        await Pages(ctx, pages)
        

@bot.command()
async def 음성순위(ctx): # 음성채널 거주 시간 순위
    con, cur = DbConnect()
    if (WhiteList(ctx)):
        voiceRankList = []
        Return = DbSearchVoiceRank(con, cur)
        # print(voiceRankReturn[0])
        rank = 1
        for i in Return:
            id = int(i[0].decode())
            user = bot.get_user(id)
            voice = ""
            voice += str(rank)
            voice += ".ㅤ "
            voice += MakeMention(id, 1)
            try:
                voice += "ㅤ (" + user.name + "#" + user.discriminator
            except:
                voice += "ㅤ (검색안됨"
            voice += ")ㅤ `"
            voice += str(datetime.timedelta(seconds=int(i[3])))
            voice += "`\n"
            voiceRankList.append(voice)
            rank += 1
        pages = MakePageList(0, voiceRankList, 4, 0, 0)

        await Pages(ctx, pages)

@bot.command()
async def 채팅순위(ctx):
    con, cur = DbConnect()
    if (WhiteList(ctx)):
        textRankList = []
        Return = DbSearchTextRank(con, cur)
        rank = 1
        for i in Return:
            id = int(i[0].decode())
            user = bot.get_user(id)
            text = ""
            text += str(rank)
            text += ".ㅤ "
            text += MakeMention(id, 1)
            try:
                text += "ㅤ (" + user.name + "#" + user.discriminator
            except:
                text += "ㅤ (검색안됨"
            text += ")ㅤ `"
            text += str(i[2])
            text += "`\n"
            textRankList.append(text)
            rank += 1
        pages = MakePageList(0, textRankList, 5, 0,0)

        await Pages(ctx, pages)

@bot.command()
async def 채팅검색(ctx, *args):
    con, cur = DbConnect()
    if WhiteList(ctx):
        if len(args) == 2:
            name = args[0]
            tag = args[1]
        elif len(args) == 1:
            if "#" in args[0]:
                splittext = args[0].split("#")
                name = splittext[0]
                tag = splittext[1]
            else:
                embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
                await ctx.channel.send(embed=embed)
                return
        else:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return

        name = name.replace(" ", "")
        allMember = bot.get_guild(ServerRoom).members
        flag = False
        for i in allMember:
            if name in i.name.replace(" ", "") and tag in i.discriminator:
                memberId = i.id
                flag = True
        if not flag:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return    

        textAnswer = ""

        textReturn = DbSearchText_member(memberId, con, cur, False)
        ttime, ttext = DbSearchtexttime(memberId, 3, con, cur)
        if len(textReturn) == 0:
            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    description="없습니다.")
            await ctx.channel.send(embed=embed)
            return    
        
        textAnswerList = []
        textAnswer = "총 채팅 수 : `" + str(ttext) + "`\n"
        for j in textReturn:
            textAnswer = ""
            textAnswer += j[3].decode()
            textAnswer += " ㅤ"
            textAnswer += MakeMention(j[2].decode(), 2)
            textAnswer += " ㅤ"
            textAnswer += j[1].decode()
            textAnswer += "\n"
            textAnswerList.append(textAnswer)

        member = name + "#" + tag
        pages = MakePageList(member, textAnswerList, 6, "A", 0)
        await Pages(ctx, pages) 

        return

@bot.command()
async def 음성검색(ctx, *args):
    con, cur = DbConnect()
    if WhiteList(ctx):
        if len(args) == 2:
            name = args[0]
            tag = args[1]
        elif len(args) == 1:
            if "#" in args[0]:
                splittext = args[0].split("#")
                name = splittext[0]
                tag = splittext[1]
            else:
                embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
                await ctx.channel.send(embed=embed)
                return
                
        else:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return

        name = name.replace(" ", "")
        allMember = bot.get_guild(ServerRoom).members
        flag = False
        for i in allMember:
            if name in i.name.replace(" ", "") and tag in i.discriminator:
                memberId = i.id
                flag = True
        if not flag:
            embed = discord.Embed(description="ID와 TAG를 한번 더 확인해 주세요.")
            await ctx.channel.send(embed=embed)
            return    

        voiceAnswer = ""

        voiceReturn = DbSearchVoice_member(memberId, con, cur, False)
        ttime, ttext = DbSearchtexttime(memberId, 3, con, cur)
        if len(voiceReturn) == 0:
            embed = discord.Embed(title=name + "(" + tag + ")" + "님에 대한 기록",
                                    description="없습니다.")
            await ctx.channel.send(embed=embed)
            return    
        
        voiceAnswerList = []
        voiceAnswer = "음성채널 누적 시간 : `" + str(datetime.timedelta(seconds=int(ttime))) + "`\n"
        for j in voiceReturn:
            voiceAnswer = ""
            voiceAnswer += j[3].decode()
            voiceAnswer += " ㅤ"
            if j[1].decode() != "없음":
                voiceAnswer += MakeMention(j[1].decode(), 2)
            else:
                voiceAnswer += "없음"
            voiceAnswer += " -> "
            if j[2].decode() != "없음":
                voiceAnswer += "<#" + j[2].decode() + ">"
            else:
                voiceAnswer += "없음"

            voiceAnswer += "\n"
            voiceAnswerList.append(voiceAnswer)

        member = name + "#" + tag
        pages = MakePageList(member, voiceAnswerList, 7, "A", 0)
        await Pages(ctx, pages) 

        return

@bot.command()
async def test(ctx):
    req = requests.get("https://discord.com/api/path/to/the/endpoint")
    print(req.headers)

# @bot.command()
# async def updateUser(ctx):
#     print(dir(telegram))
    # con, cur = DbConnect()
    # if WhiteList(ctx):
    #     guild = bot.get_guild(875392692014694450)

    #     for member in guild.members:
    #         if (member.bot != True):
    #             print(member)
    #             cur.execute("INSERT INTO user_info(id, tag, ttext, ttime, count, jointime) VALUES(%s, %s, %s, %s, %s, %s)", (member.id, member.discriminator, "0", "0", "1", "00.00"))
    #             con.commit()


bot.run(os.environ["token"])


