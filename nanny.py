import discord
import asyncio
import os
import subprocess
import json

from botconf import Conf

#Initialise and load settings
CONF_FILE = "nanny.conf"

conf = Conf(CONF_FILE)
TOKEN = conf.get("token")
PREFIX = conf.get("prefix")
AUTHORISED = conf.getintlist("authorised_users")
HELP_STR = conf.get("custom_help_string") if conf.get("custom_help_string") else "Available Commands:"

SCRIPTS = json.loads(conf.get("app_scripts"))
LOGFILES = json.loads(conf.get("app_logfiles"))

client = discord.Client()


#Command decorator
cmds = {}

def cmd(cmdName, helpStr="No help provided for this command"):
    def decor(func):
        cmds[cmdName] = [func, helpStr]
        return func
    return decor


#Utility
async def execute(command):
    p1 = subprocess.Popen(command, shell = True, stdin=None, stdout=subprocess.PIPE)
    out,err = p1.communicate()
    p1.stdout.close()
    return out.decode('utf-8')

async def tail(filename, n):
    command = 'tail -n '+str(n)+' '+filename
    out = await execute(command)
    return out


async def reply(message, content): 
    await client.send_message(message.channel, content)

#Commands

@cmd("help", "Usage: help [command name]\n\nShows detailed help on the requested command, or lists all the commands.")
async def cmd_help(message, params):
    msg = ""
    if params == "":
        msg = HELP_STR + "\n"
        for cmd in sorted(cmds):
            msg += " `{}` ".format(cmd)
    else:
        params = params.split(' ')
        for cmd in params:
            if cmd in cmds:
                msg += "```{}```\n".format(cmds[cmd][1])
            else:
                msg += "I couldn't find a command named `{}`. Please make sure you have spelled the command correctly. \n".format(cmd)
    await reply(message, msg)

@cmd("sendlog", "Usage: sendlog <logname>\n\nAttempts to send the logfile <logname> specified in the config file.")
async def cmd_sendlog(message, params):
    params = params.split(' ')
    if params[0] == "":
        await reply(message, "Available logfiles: "+ ", ".join(sorted(LOGFILES)))
        return
    if params[0] not in LOGFILES:
        await reply(message, "This is not a valid logfile!")
        return
    try:
        await reply(message, "Sending your logfile now, hold on!")
        client.send_file(message.channel, LOGFILES[params[0]])
    except:
        await reply(message, "Oh dear, I couldn't send your logfile. Maybe it is too large or doesn't exist?")
    return


@cmd("logtail", "Usage: logtail <number of lines> <logname>\n\nSends the last <number> lines of the logfile <logname> specified in the config file.")
async def cmd_logtail(message, params):
    params = params.split(' ')
    if len(params) < 2:
        await reply(message, "Available logfiles: "+ ", ".join(sorted(LOGFILES)))
        return
    if params[1] not in LOGFILES:
        await reply(message, "This is not a valid logfile!")
        return
    if not params[0].isdigit():
        await reply(message, cmds["logtail"][1])
        return
    try:
        logs = await tail(LOGFILES[params[1]], params[0])
        await reply(message, "Here are your logs:\n```{}```".format(logs))
    except:
        await reply(message, "Oh dear, I couldn't send your logs for some reason. Maybe they don't exist or the message is too large?")
    return


@cmd("show", "Usage: show <cmdname>\n\nShows the script or command associated to <cmdname> in the configfile.")
async def cmd_show(message, params):
    params = params.split(' ')
    if params[0] == "":
        await reply(message, "Available scripts/commands: "+ ", ".join(sorted(SCRIPTS)))
        return
    if params[0] not in SCRIPTS:
        await reply(message, "I don't know about this command/script!")
        return
    await reply(message, SCRIPTS[params[0]])
    return

async def exec_script(message, params):
    cmd_message = message.content[len(PREFIX):]
    cmd = cmd_message.strip().split(' ')[0].lower()
    if cmd not in SCRIPTS:
        await reply(message, "I don't know how I got here, something's wrong. Forgetting this ever happened")
        return
    try:
        await reply(message, "Running your command now")
        out = await execute(SCRIPTS[cmd] + " " + params)
        try:
            if out:
                await reply(message, "Output:\n```{}```".format(out))
            else:
                await reply(message, "The command produced no output")
        except:
            await reply(message, "I ran your command but couldn't print the output! Perhaps it was too long.")
    except:
        await reply(message, "Something went wrong running your command, check the console for details!")

for cmd in SCRIPTS:
    if cmd not in cmds:
        cmds[cmd] = [exec_script, "This is a custom command! Use show <cmdname> to see details."]
    else:
        print("Tried to add command {} but the name was already in use!".format(cmd))





#Discord Event Handling

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("Logged into", len(client.servers), "servers")


@client.event
async def on_message(message):
    PREFIX = conf.get("PREFIX") 
    if not message.content.startswith(PREFIX):
        return
    if message.content == (PREFIX):
        return
    if int(message.author.id) not in AUTHORISED:
        return
    cmd_message = message.content[len(PREFIX):]
    cmd = cmd_message.strip().split(' ')[0].lower()
    params = ' '.join(cmd_message.strip().split(' ')[1:])
    await cmd_parser(message, cmd, params)
    return

async def cmd_parser(message, cmd, params):
    if cmd in cmds:
        try:
            await cmds[cmd][0](message, params)
            return
        except:
            traceback.print_exc()
            try:
                await reply(message, "Something went wrong. The error has been logged")
            except:
                print("Something unexpected happened and I can't print the error. Dying now.")
            return
    else:
        return


client.run(TOKEN)
