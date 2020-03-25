import discord
from discord.ext import commands, tasks

import json
import bs4 as bs
from urllib.request import Request, urlopen

import os
from datetime import datetime

def get_realm(realm, filter=None):
    # Retrieves all the users on the requested realm
    urlbase = Request('https://medivia.online/community/online/' + realm, headers={'User-Agent': 'Mozilla/5.0'})
    source = urlopen(urlbase).read()
    parse = bs.BeautifulSoup(source, 'html.parser')
    html = list(parse.children)[2]
    body = list(html.children)[3]
    list1 = list(body.children)[3]
    list2 = list(list1.children)[5]
    list3 = list(list2.children)[1]
    finallist = list3.find_all('li')
    # removes the first line in the list as it is the header (Login, Name, Voc, Level)
    finallist.pop(0)
    if filter == 'name':
        return [z[1] for z in [[y.text for y in x.find_all('div')] for x in finallist]]
    else:
        return [[y.text for y in x.find_all('div')] for x in finallist]


# Compares the last online list with the current
def compare_current(online, listName, guild):
    checkfile = os.path.exists(f'config/saved_{guild}.json')
    if checkfile:
        data = json.load(open(f'config/saved_{guild}.json'))
        # If the list exists
        if listName in data[guild]['channels']:
            # Check online to past
            last = data[guild]['channels'][listName]['last']
            checkEqual = set(online) == set(last)
            # If changes are found
            if not checkEqual:
                data[guild]['channels'][listName]['last'] = list(online)
                print(f'{listName} updated:\n{data}')
                json.dump(data, open(f'config/saved_{guild}.json', 'w'))
                return online
        else:
            # Adds the list to the 'saved' json file
            data[guild]['channels'][listName] = {}
            data[guild]['channels'][listName]['last'] = []
            print(f'{listName} added:\n{data}')
            json.dump(data, open(f'config/saved_{guild}.json', 'w'))
            return online
    else:
        # Creating a new list for first time use
        data = {}
        data[guild] = {}
        data[guild]['channels'] = {}
        data[guild]['channels'][listName] = {}
        data[guild]['channels'][listName]['last'] = []
        print(data)
        json.dump(data, open(f'config/saved_{guild}.json', 'w'))
        print(f'new list added: {listName}. No past online to compare.')
        return online


class Medivia(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.friendlist = []
        self.enemylist = []
        self.medivia_online.start()

    # Events: On ready
    @commands.Cog.listener()
    async def on_ready(self):
        print('medivia cog ready.')


    # Cancels tasks if the bog unloads
    def cog_unload(self):
        self.medivia_online.cancel()

    # Commands: medivia
    @commands.command()
    async def medivia(self, ctx):
        players = get_realm('pendulum', 'name')
        await ctx.send(players[0:3])

    ###########
    ## LISTS ##
    ###########
    # Commands: Get lists
    @commands.command()
    async def get_lists(self, ctx):
        guild = ctx.guild.name
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            listText = '\n'.join([listName for listName in data[guild]['channels']])
            await ctx.send(f'Medivia lists:\n{listText}')
        else:
            await ctx.send('Medivia list: No lists currently exist.')


    # Commands: New list
    @commands.command()
    async def new_list(self, ctx, listName, channelId):
        guild = ctx.guild.name
        guildId = ctx.guild.id
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            print(f'Before:\n{data}')
            # Checking to see if the list exists
            if listName in data[guild]['channels']:
                await ctx.send(f'Medivia lists: {listName} already exists.')
            else:
                data[guild]['channels'][listName] = {}
                data[guild]['channels'][listName]['id'] = channelId
                data[guild]['channels'][listName]['members'] = []
                print(f'After:\n{data}')
                json.dump(data, open(f'config/{guild}.json', 'w'))
                await ctx.send(f'Medivia lists: {listName} added.')
        else:
            # Creating a new list
            data = {}
            data[guild] = {}
            data[guild]['id'] = guildId
            data[guild]['channels'] = {}
            data[guild]['channels'][listName] = {}
            data[guild]['channels'][listName]['id'] = channelId
            data[guild]['channels'][listName]['members'] = []
            print(data)
            json.dump(data, open(f'config/{guild}.json', 'w'))
            await ctx.send(f'Medivia lists: {listName} added.')


    # Commands: Remove list
    @commands.command()
    async def remove_list(self, ctx, listName):
        guild = ctx.guild.name
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            print(f'Before:\n{data}')
            # If the list exists
            if listName in data[guild]['channels']:
                data[guild]['channels'].pop(listName)
                print(f'After:\n{data}')
                json.dump(data, open(f'config/{guild}.json', 'w'))
                await ctx.send(f'Medivia lists: {listName} removed.')
            else:
                await ctx.send(f'Medivia lists: {listName} does not exist.')
        else:
            await ctx.send(f'Medivia lists: No lists exist yet.')


    #############
    ## MEMBERS ##
    #############
    # Commands: Add member
    @commands.command()
    async def add_member(self, ctx, listName, *members):
        guild = ctx.guild.name
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            print(f'Before:\n{data}')
            # If the list exists
            if listName in data[guild]['channels']:
                for member in members:
                    data[guild]['channels'][listName]['members'].append(member)
                print(f'After:\n{data}')
                json.dump(data, open(f'config/{guild}.json', 'w'))
                memberstext = "\n".join(sorted(members))
                await ctx.send(f'Medivia lists: Members added to the {listName} list:\n{memberstext}')
            else:
                await ctx.send(f'Medivia lists: {listName} does not exist. Please create the list before adding members.')
        else:
            await ctx.send(f'Medivia lists: {listName} does not exist. Please create the list before adding members.')


    # Commands: Remove member
    @commands.command()
    async def remove_member(self, ctx, listName, *members):
        guild = ctx.guild.name
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            print(f'Before:\n{data}')
            # If the list exists
            if listName in data[guild]['channels']:
                for member in members:
                    data[guild]['channels'][listName]['members'].remove(member)
                print(f'After:\n{data}')
                json.dump(data, open(f'config/{guild}.json', 'w'))
                memberstext = "\n".join(sorted(members))
                await ctx.send(f'Medivia lists: Members removed from the {listName} list:\n{memberstext}')
            else:
                await ctx.send(f'Medivia lists: {listName} does not exist.')
        else:
            await ctx.send(f'Medivia lists: {listName} does not exist.')


    # Commands: list members
    @commands.command()
    async def get_members(self, ctx, listName):
        guild = ctx.guild.name
        print(f'Guild: {guild}')
        checkfile = os.path.exists(f'config/{guild}.json')
        if checkfile:
            data = json.load(open(f'config/{guild}.json'))
            # If the list exists
            if listName in data[guild]['channels']:
                # If members exist
                if data[guild]['channels'][listName]['members']:
                    memberstext = "\n".join(sorted(data[guild]['channels'][listName]['members']))
                    await ctx.send(f'{memberstext}')
                else:
                    await ctx.send(f'Medivia lists: {listName} does not have any members yet.')
            else:
                await ctx.send(f'Medivia lists: {listName} does not exist.')
        else:
            await ctx.send(f'Medivia lists: {listName} does not exist.')


    # Commands: medivia - check character online status
    @tasks.loop(seconds=60.0)
    async def medivia_online(self):
        print("\n  -- online sync -- ")
        print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        # Gets all the guild json files
        guildFiles = [file for file in os.listdir("config/") if 'saved' not in file and file.endswith(".json")]
        print(f'guild files: {guildFiles}')
        # If any guild files are found
        if guildFiles:
            # Gets the currently only player list
            current = get_realm('pendulum', 'name')
            # Loops through each guild file
            for guildFile in guildFiles:
                print(f"  guild: {guildFile}")
                guild = guildFile.split('.')[0]
                data = json.load(open(f'config/{guildFile}'))
                # Loops through each list in the guild
                for mediviaList in data[guild]['channels']:
                    print(f"  list: {mediviaList}")
                    # If the list exists
                    if mediviaList in data[guild]['channels']:
                        # Gets the online characters from the list
                        online = set(current) & set(data[guild]['channels'][mediviaList]['members'])
                        checkPast = compare_current(online, mediviaList, guild)
                        # Only updates the channel if changes are found
                        if checkPast:
                            onlinetext = "\n".join(sorted(online))
                            # Gets the channel to send the updates to
                            channelId = int(data[guild]['channels'][mediviaList]['id'])
                            channel = self.client.get_channel(channelId)
                            # Sends the latest online list if the channel exists
                            if channel:
                                await channel.purge(limit=4)
                                # Post text if people are online
                                if online:
                                    await channel.send(f"```text\n{onlinetext}```")
                            else:
                                print(f'FAILED: {guildFiles} || {guildFile} || {guild} || {mediviaList}')
                                raise ValueError(f"{channelId} does not exist.")


    # Waits for the cog to be ready
    @medivia_online.before_loop
    async def before_medivia(self):
        print('Waiting...')
        await self.client.wait_until_ready()


    # # Commands: medivia - check character online status
    # @tasks.loop(seconds=30000.0)
    # async def medivia_online(self):
    #     current = get_realm('pendulum', 'name')
    #     mediviaLists = 
    #     onlinefriends = set(current) & set(self.friendlist)
    #     onlinefriendtext = "\n".join(sorted(onlinefriends))
    #     onlineenemies = set(current) & set(self.enemylist)
    #     onlineenemytext = "\n".join(sorted(onlineenemies))
    #     channel = self.client.get_channel(338411352081170433)
    #     print(channel)
    #     await channel.send(f"```diff\n-@@ ENEMIES\n{onlineenemytext}```")
    #     await channel.send(f"```yaml\n-@@ FRIENDS\n{onlinefriendtext}```")


    # #############
    # ## ENEMIES ##
    # #############
    # # Commands: medivia - add enemies
    # @commands.command()
    # async def add_enemy(self, ctx, *enemies):
    #     for enemy in enemies:
    #         self.enemylist.append(enemy)
    #         await ctx.send(f'{enemy} has been added to the enemy list.')


    # # Commands: medivia - remove enemies
    # @commands.command()
    # async def remove_enemy(self, ctx, *enemies):
    #     for enemy in enemies:
    #         self.enemylist.remove(enemy)
    #         await ctx.send(f'{enemy} has been removed to the enemy list.')


    # # Commands: medivia - list enemies
    # @commands.command()
    # async def list_enemy(self, ctx):
    #     text = "\n".join(sorted(self.enemylist))
    #     await ctx.send(f"```yaml\n-@@ ALL ENEMIES\n{text}```")


    # #############
    # ## FRIENDS ##
    # #############
    # # Commands: medivia - add friends
    # @commands.command()
    # async def add_friend(self, ctx, *friends):
    #     for friend in friends:
    #         self.friendlist.append(friend)
    #         await ctx.send(f'{friend} has been added to the friend list.')


    # # Commands: medivia - remove friends
    # @commands.command()
    # async def remove_friend(self, ctx, *friends):
    #     for friend in friends:
    #         self.friendlist.remove(friend)
    #         await ctx.send(f'{friend} has been removed to the friend list.')


    # # Commands: medivia - list friends
    # @commands.command()
    # async def list_friend(self, ctx):
    #     text = "\n".join(sorted(self.friendlist))
    #     await ctx.send(f"```yaml\n-@@ ALL FRIENDS\n{text}```")


def setup(client):
    client.add_cog(Medivia(client))