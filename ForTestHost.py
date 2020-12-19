import vk_api
import time


my_token = '8850f4386b2db7b79e7fdc99f71e4cd59e4e445996592d8bad877d1eaed48a9251010a6a6a14c726281cd'
GId = 2000000058
session= vk_api.VkApi(token = my_token)
vk = session.get_api()

mes = 'bot.'
while True:
    try:
        vk.messages.send(peer_id = GId, message = mes, random_id = 0)
    except:
        pass
    time.sleep(120)