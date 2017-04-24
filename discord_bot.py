import discord
import asyncio
import urllib.request
import json
import settings

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith(u'!ку'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith(u'!статка') \
            or message.content.startswith(u'!стата'):
        base_text = ''
        if not message.mentions:
            name = message.author.display_name.split('*', 1)[0]
            base_url = "http://thunderskill.com/ru/stat/"
            url = "http://thunderskill.com/ru/stat/" + name + "/export/json"
            with urllib.request.urlopen(url) as url_link:
                data = json.loads(url_link.read().decode())
                base_text = u'{0.author.mention} | ' + base_url + name \
                            + '\n' \
                            + '(**РБ**) ' + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                            + '(**СБ**) ' + str("%.2f" % data['stats']['s']['kpd']) + '; ' \
                            + '(**АБ**) ' + str("%.2f" % data['stats']['a']['kpd']) + '; '
        else:
            for user in message.mentions:
                # print(user.display_name.split('*', 1)[0])
                name = user.display_name.split('*', 1)[0]
                # url = 'http://thunderskill.com/ru/stat/' + name + '\n'
                # text = text + url
                # name = message.author.display_name.split('*', 1)[0]
                base_url = "http://thunderskill.com/ru/stat/"
                url = "http://thunderskill.com/ru/stat/" + name + "/export/json"
                with urllib.request.urlopen(url) as url_link:
                    data = json.loads(url_link.read().decode())
                    text = user.mention + ' | ' + base_url + name \
                           + '\n' \
                           + '(**РБ**) ' + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                           + '(**СБ**) ' + str("%.2f" % data['stats']['s']['kpd']) + '; ' \
                           + '(**АБ**) ' + str("%.2f" % data['stats']['a']['kpd']) + '; ' \
                           + '\n' \
                           + '\n'
                    base_text = base_text + text
        msg = base_text.format(message)
        await client.send_message(message.channel, msg)
    elif message.content.startswith(u'!полк'):
        with urllib.request.urlopen("http://thunderskill.com/ru/squad/%E2%95%96AFI%E2%95%96/export/json") as url:
            data = json.loads(url.read().decode())
            text = u'__**КПД:**__ ' \
                   + '(**РБ**) ' + str("%.2f" % data['kpd_r']) + '; ' \
                   + '(**СБ**) ' + str("%.2f" % data['kpd_s']) + '; ' \
                   + '(**АБ**) ' + str("%.2f" % data['kpd_a']) + '; ' \
                   + '\n' \
                   + u'Подробнее - http://thunderskill.com/ru/squad/%E2%95%96AFI%E2%95%96'
        await client.send_message(message.channel, text)

client.run(settings.BOT_TOKEN)
