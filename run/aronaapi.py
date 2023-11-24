# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys
import socket
from asyncio import sleep

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice, Startup, MessageChain
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import ForwardMessageNode, Forward

from plugins.aronaBa import stageStrategy


def main(bot,logger):
    logger.info("arona loaded")
    @bot.on(GroupMessage)
    async def selectMission(event:GroupMessage):
        if str(event.message_chain).startswith("/攻略 "):
            url=str(event.message_chain).replace("/攻略 ","")
            logger.info("查询攻略："+url)
            try:
                p=await stageStrategy(url)
                await bot.send(event,Image(path=p))
            except:
                logger.error("无效的角色或网络连接错误")
                await bot.send(event,"无效的角色 或网络连接出错")
    @bot.on(Startup)
    async def pushAronaData(event: Startup):
        while True:
            logger.info("检查arona订阅更新")
            with open("data/aronaSub.yaml", 'r', encoding='utf-8') as f:
                result9 = yaml.load(f.read(), Loader=yaml.FullLoader)
                for i in result9:
                    for ia in result9.get(i).get("hash"):
                        logger.info("检查"+ia+"更新")
                        await sleep(5)
                        url1 = "https://arona.diyigemt.com/api/v2/image?name=" + ia
                        async with httpx.AsyncClient(timeout=100) as client:  # 100s超时
                            r = await client.get(url1)  # 发起请求
                            r = r.json()
                            newHash = r.get("data")[0].get("hash")
                        if str(newHash)!=result9.get(i).get("hash").get(ia):
                            p=await stageStrategy(ia)
                            for iss in result9.get(i).get("groups"):
                                try:
                                    await bot.send_group_message(int(iss),(ia+"数据更新",Image(path=p)))
                                except:
                                    logger.error("向"+str(iss)+"推送更新失败")
                            result9[i]["hash"][ia]=str(newHash)
                            with open('data/aronaSub.yaml', 'w', encoding="utf-8") as file:
                                yaml.dump(result9, file, allow_unicode=True)
            await sleep(600)#600秒更新一次
    @bot.on(GroupMessage)
    async def addSUBgroup(event: GroupMessage):
        if str(event.message_chain)=="/订阅日服":
            a="日服"
        elif str(event.message_chain)=="/订阅国际服":
            a="国际服"
        elif str(event.message_chain)=="/订阅国服":
            a="国服"
        else:
            if str(event.message_chain).startswith("/订阅"):
                await bot.send(event, "无效的服务器")
                return
            else:
                return
        with open("data/aronaSub.yaml", 'r', encoding='utf-8') as f:
            result9 = yaml.load(f.read(), Loader=yaml.FullLoader)
            bsg=result9.get(a).get("groups")
            bsg.append(event.group.id)
            result9[a]["groups"]=bsg
            with open('data/aronaSub.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(result9, file, allow_unicode=True)
            bss=result9.get(a).get("hash")
            for i in bss:
                p = await stageStrategy(i)
                await bot.send(event, ("获取到"+i+"数据",Image(path=p)))
            logger.info(str(event.group.id)+"新增订阅")
            await bot.send(event,"成功订阅")
