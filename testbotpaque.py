import discord
from discord import channel
from discord.ext import commands, tasks
from random import randint
import sqlite3

conn=sqlite3.connect('/home/ubuntu/paques/dbPaques.db')
cursor = conn.cursor()


client = commands.Bot(command_prefix='!')
client.remove_command('help')
joueA="chercher des œufs."
channels=[765930952328347690,768017888341917706,773215994481999893,769104471505502248,788190890010738708,772769708722094100,772771789365444608,796062293656993854,772771412188069918,772769352336408596,779035262499684382,770652712186019870,772768947052347392,775313799326203914,821742781223534623,786165301665595413,772040589671530518]
oeufs=0
nbpts=0
nombreOeufT1=0
nombreOeufT2=0
nombreOeufT3=0

'''
80% de T1
15% de T2
5% de T3
'''

def embedClassement():
    embed=discord.Embed(color=0xfefcdd,title="10 Meilleurs scores :")

    cursor.execute("SELECT * FROM users ORDER BY score DESC LIMIT 10")
    top=cursor.fetchall()

    for i in range(len(top)):

        if i==0:
            embed.add_field(name=":trophy: **{0}**er :".format(i+1), value="{0} avec {1} points".format(top[i][0],top[i][1]), inline=False)
        else:
            embed.add_field(name="**{0}**e :".format(i+1), value="{0} avec {1} points".format(top[i][0],top[i][1]), inline=True)
    return embed


def embedT1(auteur):
    global nbpts
    embed=discord.Embed()
    if nbpts==1:
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/796875325622583296/828647896126586880/1test.png")
    elif nbpts==2:
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/796875325622583296/828647897419350066/2test.png")
    else:
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/796875325622583296/828644841675292792/3test.png")

    embed.add_field(name="{0} a claim l'œuf !".format(auteur), value="Il gagne {0}pts !".format(nbpts), inline=False)
    embed.set_footer(text="Event Paques")
    return embed


async def apparitionOeuf(channel):
    global oeufs
    global nbpts
    global nombreOeufT1, nombreOeufT2, nombreOeufT3

    channel = client.get_channel(channel)
    tierOeuf = randint(1,100)
    numOeuf = str(randint(0,5))

    if tierOeuf <= 80:
        print("Tier 1")
        nbpts=1
        oeufs = await channel.send(file=discord.File('/home/ubuntu/paques/oeufT1_'+numOeuf+'.png'))
        nombreOeufT1=nombreOeufT1+1

    elif 80 < tierOeuf <= 95 :
        print("Tier 2")
        nbpts=2
        oeufs = await channel.send(file=discord.File('/home/ubuntu/paques/oeufT2_'+numOeuf+'.png'))
        nombreOeufT2=nombreOeufT2+1

    elif tierOeuf > 95 :
        print("Tier 3")
        nbpts=3
        oeufs = await channel.send(file=discord.File('/home/ubuntu/paques/oeufT3_'+numOeuf+'.png'))
        #ajouter un randint entre le nombre chaque oeuf du tier
        nombreOeufT3=nombreOeufT3+1

    print("Nb tier1 : ", nombreOeufT1, "Nb tier2 :", nombreOeufT2, "Nb tier3 :", nombreOeufT3)


async def fonctionClaim(ctx):
    global nbpts
    global oeufs
    embedclaim=await ctx.send(embed=embedT1(ctx.author))
    await embedclaim.delete(delay=10)

    if oeufs !=0:
        await oeufs.delete()
        oeufs=0

    cursor.execute("SELECT score FROM users WHERE idUser = '{0}'".format(ctx.author))
    alreadyExist=cursor.fetchone()
    if alreadyExist==None:
        cursor.execute("INSERT INTO users (idUser, score) VALUES ('{0}', {1})".format(ctx.author,nbpts))
        print(ctx.author,"créé")
    else:
        cursor.execute("UPDATE users SET score = score + {0} WHERE idUser ='{1}'".format(nbpts,ctx.author))
    conn.commit()
    nbpts=0

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name=joueA))
    randomEgg.start()

@tasks.loop(minutes=1.0)
async def randomEgg():
    if oeufs==0:
        random = randint(0,5)
        if  random == 0 :
            channel = channels[randint(0,len(channels)-1)]
            await apparitionOeuf(channel)
        else:
            print("pas d'oeuf")

@client.command()
async def help(ctx) :
    await ctx.send("saucisse")

@client.command()
async def top(ctx) :
    await ctx.send(embed=embedClassement())

@client.command()
async def score(ctx) :
    await ctx.message.delete()
    cursor.execute("SELECT score FROM users WHERE idUser = '{0}'".format(ctx.author))
    score=cursor.fetchone()

    embed=discord.Embed()
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/816053639100497920/828684907453612092/logopaque.png")
    embed.add_field(name="Ton score est de {0} pts !".format(score[0]), value="*Waouh.*", inline=False)
    embed.set_footer(text="Event Paques")
    textscore = await ctx.send(embed=embed)

    await textscore.delete(delay=10)

@client.command(aliases=['c'])
async def claim(ctx):
    await ctx.message.delete()
    if oeufs !=0:
        if ctx.channel.id == oeufs.channel.id :
            await fonctionClaim(ctx)
        else:
            pasdoeuf=await ctx.send("Il n'y a pas d'oeuf à claim !")
            await pasdoeuf.delete(delay=10)
    else:
        pasdoeuf=await ctx.send("Il n'y a pas d'oeuf à claim !")
        await pasdoeuf.delete(delay=10)



#commande pour drop un oeuf
@client.command()
async def drop(ctx,salon:int) :
    if ctx.author.id==182503482803093513 or ctx.author.id==271254899243745281:
        await ctx.message.delete()
        await apparitionOeuf(salon)

@drop.error
async def drive_error(ctx,error) :
    if ctx.author.id==182503482803093513 or ctx.author.id==271254899243745281:
        if isinstance(error, commands.MissingRequiredArgument):
            global oeufs
            if oeufs != 0:
                await oeufs.delete()
            channel = channels[randint(0,len(channels)-1)]
            await apparitionOeuf(channel)
        else: raise error


client.run('token')
