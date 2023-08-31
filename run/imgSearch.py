# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys
import socket

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice, MessageChain
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import ForwardMessageNode, Forward

from plugins.RandomStr import random_str
from plugins.imgSearch import test2, superSearch, test1, test

from plugins.modelsLoader import modelLoader
from plugins.translater import translate


def main(bot,api_key,proxy,logger):
    logger.info("搜图功能启动完毕")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    cookies=result.get("e-hentai")
    @bot.on(GroupMessage)
    async def imgSearcher(event:GroupMessage):
        if "搜图" in str(event.message_chain) and event.message_chain.count(Image):
            logger.info("接收来自群："+str(event.group.id)+" 用户："+str(event.sender.id)+" 的搜图指令")
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            proxies = {
                "http://": proxy,
                "https://": proxy
            }

            # Replace the key with your own
            dataa = {"url": img_url, "db": "999", "api_key": api_key, "output_type": "2", "numres": "3"}
            logger.info("发起搜图请求")
            #sauceno搜图
            lisas=[]
            try:
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.post(url="https://saucenao.com/search.php", data=dataa)
                #response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                logger.info("获取到结果"+str(response.json().get("results")[0]))
                #logger.info("下载缩略图")
                #filename=dict_download_img(img_url,dirc="data/pictures/imgSearchCache")
                result=' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]","")
                urlss=str(response.json().get("results")[0].get('header').get('thumbnail'))
                b1=ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result,Image(url=urlss)]))
                #b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
                lisas.append(b1)

                #await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
            except:
                logger.warning("sauceno搜图失败，无结果或访问次数过多，请稍后再试")
                await bot.send(event,"sauceno搜图失败，无结果或访问次数过多，请稍后再试")
            #使用TraceMoe搜图
            try:
                result,piccc=await test(url=img_url,proxies=proxy)
                logger.info("TraceMoe获取到结果：" +result)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([result, Image(url=piccc)]))
                lisas.append(b1)
                try:
                    pass
                    #await bot.send(event,(result,Image(url=piccc)))
                except:
                    await bot.send(event, result)
            except:
                logger.info("TraceMoe未获取到结果" )
                await bot.send(event, "TraceMoe搜图失败，无结果或访问次数过多，请稍后再试")
            #使用Ascii2D
            try:
                result,piccc=await test1(url=img_url,proxies=proxy)
                logger.info("Ascii2D获取到结果：" +result)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([result, Image(url=piccc)]))
                lisas.append(b1)
                try:
                    pass
                    #await bot.send(event,(result,Image(url=piccc)))
                except:
                    await bot.send(event, result)
            except:
                logger.info("Ascii2D未获取到结果" )
                await bot.send(event, "Ascii2D搜图失败，无结果或访问次数过多，请稍后再试")
            # 使用IQDB
            try:
                result, piccc = await superSearch(url=img_url, proxies=proxy)
                logger.info("iqdb获取到结果：" + result)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([result, Image(url=piccc)]))
                lisas.append(b1)
                try:
                    pass
                    #await bot.send(event, (result, Image(url=piccc)))
                except:
                    await bot.send(event, result)
            except:
                logger.info("iqdb未获取到结果")
                await bot.send(event, "iqdb搜图失败，无结果或访问次数过多，请稍后再试")
            # 使用E-hentai
            try:
                result, piccc = await test2(url=img_url, proxies=proxy,cookies=cookies)
                logger.info("E-hentai获取到结果：" + result)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([result, Image(url=piccc)]))
                lisas.append(b1)
                try:
                    pass
                    #await bot.send(event, (result, Image(url=piccc)))
                except:
                    await bot.send(event, result)
            except:
                logger.info("E-hentai未获取到结果")
                await bot.send(event, "E-hentai搜图失败，无结果或访问次数过多，请稍后再试")
            await bot.send(event,Forward(node_list=lisas))

