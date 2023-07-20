# -*- coding:utf-8 -*-
import asyncio
import datetime
import json

import os
import subprocess
from random import random

import httpx
import requests
import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter, Poke, GroupMessage, Image, Voice
from mirai.models import NudgeEvent, MemberHonorChangeEvent, MemberCardChangeEvent, MemberSpecialTitleChangeEvent

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger
from plugins.translater import translate
from run import poeAi, voiceReply, nudgeReply, blueArchiveHelper, imgSearch, extraParts, wReply, userSign, groupManager, \
    PicRandom

if __name__ == '__main__':
    with open('config.json','r',encoding='utf-8') as fp:
        data=fp.read()
    config=json.loads(data)
    qq=int(config.get('botQQ'))
    key=config.get("vertify_key")
    port= int(config.get("port"))
    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))
    botName = config.get('botName')
    master=int(config.get('master'))


    #芝士logger
    logger=newLogger()

    #读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    app_id = result.get("youdao").get("app_id")
    app_key=result.get("youdao").get("app_key")#有道翻译api
    sizhiKey=result.get("siZhiAi")
    proxy=result.get("proxy")
    moderate=result.get("moderate")
    logger.info("读取到apiKey列表")



    '''@bot.on(GroupMessage)
    async def imgGet(event:GroupMessage):
        if event.message_chain.count(Image):
            lst_img = event.message_chain.get(Image)
            for i in lst_img:
                img_url = i.url
                print(img_url)'''
    async def voiceGenerate(data):
        # 向本地 API 发送 POST 请求
        url = 'http://localhost:9080/synthesize'
        data=json.dumps(data)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            #print(response.text)






    subprocess.Popen(["venv/Scripts/python.exe", "flask_voice.py"],cwd="vits")
    #asyncio.run(os.system("cd vits && python flask_voice.py"))
    logger.info(" 语音合成sever启动....")

    def startVer():
        file_object = open("config/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)

    voiceReply.main(bot,app_id,app_key,logger)#语音生成
    if proxy!="":
        try:
            logger.info("开发过程中暂不启动poe-api")
            #poeAi.main(bot,master,result.get("poe-api"),result.get("proxy"),logger)#poe-api
        except:
            logger.error("poe-api启动失败")
        imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)
    else:
        logger.warning("未设置代理，禁用poe-api与搜图")
    nudgeReply.main(bot,app_id,app_key,logger)#戳一戳
    extraParts.main(bot,result.get("weatherXinZhi"),logger)#额外小功能
    wReply.main(bot,config,sizhiKey,app_id,app_key,logger)
    blueArchiveHelper.main(bot,app_id,app_key,logger)
    userSign.main(bot,result.get("weatherXinZhi"),logger)
    groupManager.main(bot,config,moderate,logger)
    PicRandom.main(bot,logger)
    startVer()

    bot.run()