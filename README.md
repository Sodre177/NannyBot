# NannyBot

NannyBot is a very simple discord bot which allows one to run custom scripts and shell commands specified in the config file from discord, as well as view the tail of log files or get the entire logfile sent.

This is a fully setup bot, ready to use aside from configuration. An example configuration file is provided, simply copy that to "nanny.conf", enter the required details, and run the bot!

The original use for NannyBot is managing self-hosted discord bots. By setting pull and restart scripts, you can redeploy and view logs from inside discord. However, NannyBot may be used to run any shell commands and read any log files, so the possibilities are endless.

As an example of use, the following is my personal configuration file for one of my bots.

```inf
[General]
token = ----
prefix = ~~
authorised_users = [299175087389802496]

app_scripts = {"ls" : "ls", "pull" : "../scripts/pull.sh", "kill" : "pkill -f "main.py", "restart" : "../scripts/restart.sh"}
app_logfiles = {"paralog" : "../logs/paralog.log", "debuglog" : "../logs/debuglog.log"}
```
