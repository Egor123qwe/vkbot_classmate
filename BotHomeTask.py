import requests
from bs4 import BeautifulSoup
import time
import math
import random
import datetime
import vk_api
import os
# -*- coding: utf8 -*




#Раз в час срабатывает. Заходит на сайт знай.бай и берёт Дз.
#Раз в неделю в ночь с Вс на Пн, переносит Дз с 2-ой недели 1-ую и чистит 2-ую.
def GetInfo(AllInfo,data,Gid_2):
    global WeekNow
    global First
    Reload = False

    if (First == True) and (WeekNow == 1):
        Reload = True
        First = False


    if Reload == False:
        def GetHT(session,week,URL_page):  #функция обрабатывает одну неделю
            Ht_page = session.get(URL_page, headers = header)
            if Ht_page.status_code == 200:
                Html_Ht = Ht_page.text
                soup = BeautifulSoup(Html_Ht, 'html.parser')
                items = soup.find_all('td', class_='diary-task')
                Num = 0
                for i in range(1,6):
                    for f in range(0,len((AllInfo[week])[str(i)])):
                        Temp = ((AllInfo[week])[str(i)])[f]
                        if len(Temp) >= 5:
                            if (Temp[len(Temp)-1]) != '#':
                                try:
                                    ((AllInfo[week])[str(i)])[f] = items[Num].find('span').text
                                except:
                                    pass
                        else:
                            try:
                                ((AllInfo[week])[str(i)])[f] = items[Num].find('span').text
                            except:
                                pass
                        Num+=1
            else:
                print('Error_1')

        URL = 'https://znaj.by/Account/LogOnInternalWithIpay'   #входные данные
        user = 'user'#fake_useragent.UserAgent().random
        header = {'User-Agent' : user}
        session = requests.Session()

        responce = session.post(URL, data=data, headers = header)  #авторизация
        if responce.status_code == 200: #если успешно обрабатывает 2 недели
            d = datetime.date.today()
            week = d.isocalendar()[1] + 1

            URL_2 = 'https://znaj.by/Client/PupilDiary?pupilId=1423890&yearStart=' + '2020'
            GetHT(session,0,URL_2)

            URL_2 = 'https://znaj.by/Client/GetPupilDiaryAjax?SchoolId=261cc9189b9&ClassId=0077f87a42e&YearStart=' + '2020' + '&PupilId=1423890&WeekNumber=' + str(week + 1) + '&QuarterTitle=3+%D1%87%D0%B5%D1%82%D0%B2%D0%B5%D1%80%D1%82%D1%8C&X-Requested-With=XMLHttpRequest'
            GetHT(session,1,URL_2)
        else:
            print('Error_login')

    else:
        for i in range(1,6):
            for f in range(0,len((AllInfo[0])[str(i)])):
                ((AllInfo[0])[str(i)])[f]= ((AllInfo[1])[str(i)])[f]
                ((AllInfo[1])[str(i)])[f]= ''


    Doc = open('D:/Bot/Newfolder/data.txt', 'w', encoding='UTF-8')
    for week in range(0,2):
        for i in range(1,6):
            for f in range(0,len((AllInfo[week])[str(i)])):
                temp = ((AllInfo[week])[str(i)])[f] + '\n'
                Doc.write(temp)
    Doc.close()

    return AllInfo



#Получает сообщения
def GetMessage(GId,vk):
    VkInfoMessage={'items': [{'text': '','from_id': ''}]}

    def GetMes(GId,vk):
        VkInfoMessage={'items': [{'text': '','from_id': ''}]}
        try:
            VkInfoMessage = vk.messages.getHistory(peer_id = GId, count=1)
        except:
            pass
        return VkInfoMessage

    time.sleep(0.3)
    VkInfoMessage = GetMes(GId,vk)
    Message = VkInfoMessage['items'][0]['text']
    Id = 'vk.com/id' + str(VkInfoMessage['items'][0]['from_id'])
    PersInfo = [Message, Id]
    return PersInfo



#Обрабатывает Message и находит Case(случай). С этими случаями работает функция Completed
def CheckMessage(Message, AllInfo):
    Case = ''
    FailMassege=''

    if Message[0:4].lower() == 'bot.':

        if Message[4:7].lower() == 'all':
            Case = 'All'
        elif Message[4:7].lower() == 'dev':
            Case = 'Dev'
        elif Message[4:8].lower() == 'help':
            Case = 'Help'
        elif Message[4:8].lower() == 'sosi':
            Case = 'Sosi'
        elif Message[4:10].lower() == 'format':
            Case = 'Form_1'
        elif Message[4:8].lower() == 'form':
            Case = 'Form'
        elif Message[4:8].lower() == 'list':
            Case = 'List'
        elif Message[4:8].lower() == 'code':
            Case = 'Code'
        elif Message[4:10].lower() == 'random':
            Case = 'Random'

        elif Message[4:7].lower() == 'day':
            Case = 'Day'
            WeekTo = False
            Auto_day = False
            global WeekNow

            if (len(Message) >= 9):
                DayNomber = Message[8]
                if (DayNomber.isdigit() == True):
                    if (int(DayNomber) < 6) and (int(DayNomber) != 0):
                        Case = Case + DayNomber
                    else:
                        FailMassege = 'Ошибка: Вы Лунтик...Учебных дней может быть максимум 5...'
                        Case = 'Error'
                else:
                    Auto_day = True
            else:
                Auto_day = True

            if Auto_day == True:
                DayNomber = WeekNow + 1
                if (DayNomber >= 6):  
                    DayNomber = 1
                    WeekTo = True
                Case = Case + str(DayNomber)

            if Case != 'Error':
                Auto_week = False
                if (len(Message) >= 11):
                    WeekNomber = Message[10]
                    if (WeekNomber.isdigit() == True):
                        if (int(WeekNomber) == 0) or (int(WeekNomber) == 1):
                            Case = Case + WeekNomber
                        else:
                            FailMassege = 'Ошибка: Вы телепузик... Часть команды с неделей заполнена неправильно...'
                            Case = 'Error'
                    else:
                        Auto_week = True
                else:
                    Auto_week = True
                    
                if Case != 'Error':
                    if Auto_week == True:
                        if WeekTo == False: 
                            Case = Case + '0'
                        else: 
                            Case = Case + '1'

            if Case != 'Error':
                if (Message[8:13] == 'clean') or (Message[12:17] == 'clean') or (Message[10:15] == 'clean'):
                    Case = Case + '0'
                else:
                    Case = Case + '1'


        elif Message[4:8].lower() == 'week':
            Case = 'Week'
            if (len(Message) >= 10):
                WeekNomber = Message[9]
                if (WeekNomber.isdigit() == True):
                    if int(WeekNomber) == 1:
                        Case = Case + '1'
                    elif int(WeekNomber) == 0:
                        Case = Case + '0'
                    else:
                        Case = 'Error'
                        FailMassege = 'Ошибка: Вы черепашка ниндзя... Часть команды с днём заполнена неправильно... '
                else:
                    Case = Case + '0'
            else:
                Case = Case + '0'

        elif Message[4:8].lower() == 'edit':
            Case = 'Edit'

        elif len(Message) >= 9:
            Truth = True
            CheckWord= Message[4]+Message[6]+Message[8]
            if(CheckWord.isdigit() == True):
                DayNomber = Message[4]
                if ((int(DayNomber) > 5) or (int(DayNomber) == 0)):
                    FailMassege = 'Ошибка: Вы Лунтик...Учебных дней может быть максимум 5... '
                    Truth = False

                if Truth == True:
                    LessonNomber = Message[6]
                    if ((int(LessonNomber) > 6) or (int(LessonNomber) == 0)):
                        if (int(LessonNomber) == 7):
                            if (DayNomber != '3') and (DayNomber != '4'):
                                FailMassege = 'Ошибка: Вы черепашка ниндзя... В этом дне уроков может быть максимум 6... '
                                Truth = False
                        else:
                            FailMassege = 'Ошибка: Вы черепашка ниндзя... Часть команды с днём заполнена неправильно... '
                            Truth = False

                if Truth == True:
                    WeekNomber = Message[8]
                    if int(WeekNomber) > 1:
                        FailMassege = 'Ошибка: Вы телепузик... Часть команды с неделей заполнена неправильно... '
                        Truth = False

                if Truth == True:
                    Case = 'HomeWork'

                    if (len(Message) >= 13) and (Message[10:13].lower() == 'new'):
                        FailMassege = 'Вы успешно добавили Дз... Спасибо)'
                        Case = Case + '1'

                    elif (len(Message) >= 15) and (Message[10:15].lower() == 'clean'):
                        FailMassege = 'Вы успешно отчистили ДЗ с этого урока...'
                        Case = Case + '2'

                if Truth == False:
                    Case = 'Error'
            else:
                FailMassege = 'Ошибка: Вы отсталый... Команда введена не верно...'
                Case = 'Error'

        else:
            FailMassege = 'Ошибка: Вы отсталый... Команда введена не верно...'
            Case = 'Error'

    CheckInfo = [FailMassege,Case]
    return CheckInfo



#Эта функция получает Case(из массива CheckInfo) в котором хранится случай(комманда) и функция умеет работать с этими коммандами.
def Completed(Message,Id,AllInfo,CheckInfo,GId,vk,Subj,About,Pass,Gid_2): 

    def AllHt(AllInfo,Sub):
        def AllWeekHt(AllInfo,Subj,week,Result):
            for i in range(1,6):
                Result = Result + '\n' + str(i) + '-й день недели: ' + '\n'
                for f in range(0,len((AllInfo[week])[str(i)])):
                    Temp = str(((AllInfo[week])[str(i)])[f])
                    if Temp != '':
                        Result = Result + str((Subj[str(i)])[f]) + ': ' + Temp + ', ' + '\n'
            return Result

        Result = '- Эта неделя - '
        Result = AllWeekHt(AllInfo,Subj,0,Result)
        Result =  Result + '\n' + '- Следующая неделя - '
        Result = AllWeekHt(AllInfo,Subj,1,Result)
        return Result

    def AllDay(AllInfo,Subj,Day,Week):
        if Week == 0:
            Result = '- Эта неделя - ' + '\n'
        else:
            Result = '- Следующая неделя - ' + '\n'
        Result = Result + str(Day) + '-й день недели: ' + '\n'
        for f in range(0,len((AllInfo[Week])[str(Day)])):
            Temp = str(((AllInfo[Week])[str(Day)])[f])
            if Temp != '':
                Result = Result + str((Subj[str(Day)])[f]) + ': ' + Temp + ', ' + '\n'
        return Result

    def AllWeek(AllInfo,Subj,Week):
        if Week == 0:
            Result = '- Эта неделя - ' + '\n'
        else:
            Result = '- Следующая неделя - ' + '\n'

        for i in range(1,6):
            Result = Result + '\n' + str(i) + '-й день недели: ' + '\n'
            for f in range(0,len((AllInfo[Week])[str(i)])):
                Temp = str(((AllInfo[Week])[str(i)])[f])
                if Temp != '':
                    Result = Result + str((Subj[str(i)])[f]) + ': ' + Temp + ', ' + '\n'
        return Result

    def FormEditor(Subj):
        def AllWeekHt(Subj,week,Result):
            for i in range(1,6):
                Result = Result + '\n' + str(i) + '-й день недели: ' + '\n'
                for f in range(0,len((AllInfo[week])[str(i)])):
                    Result = Result + str((Subj[str(i)])[f]) + ': ' + '\n'
            return Result

        Result = 'bot.edit\n'
        Result = Result + '- Эта неделя - '
        Result = AllWeekHt(Subj,0,Result)
        Result =  Result + '\n' + '- Следующая неделя - '
        Result = AllWeekHt(Subj,1,Result)
        return Result

    def List(Subj):
        Result = 'Расписание:\n'
        for i in range(1,6):
            Result = Result + '\n' + str(i) + '-й день: ' + '\n'
            for f in range(0,7):
                if str((Subj[str(i)])[f]) != '':
                    Result = Result + str((Subj[str(i)])[f]) + '\n'
        return Result

    def Refresh(AllInfo):
        Doc = open('D:/Bot/Newfolder/data.txt', 'w', encoding='UTF-8')
        for week in range(0,2):
            for i in range(1,6):
                for f in range(0,len((AllInfo[week])[str(i)])):
                    temp = ((AllInfo[week])[str(i)])[f] + '\n'
                    Doc.write(temp)
        Doc.close()

    def Cleanner(AllInfo,Day,Week):
        for f in range(0,len((AllInfo[Week])[str(Day)])):
            ((AllInfo[Week])[str(Day)])[f] = ''


    if CheckInfo[1] == 'All':
        Result = AllHt(AllInfo,Subj)
    
    elif CheckInfo[1] == 'Help':
        Result = About

    elif CheckInfo[1] == 'List':
        Result = List(Subj)
        
    elif CheckInfo[1] == 'Code':
        trueCode = '0115863'
        Code = Message[9:16]
        if (Code == trueCode):
            Result = 'Местоположение: Родный кут в твоём дворе. Справой стороны есть дверь. Перед этой дверью деревянная платформа. Под ней белый бумажный пакет.'
        else:
            Result = 'Неверный код...'

    elif CheckInfo[1] == 'Random':
        People = random.randint(1,23)
        Result = 'Номер: ' + str(People)

    elif CheckInfo[1] == 'Sosi':
        Result = 'Было бы что)&#128526;'

    elif CheckInfo[1] == 'Dev':
        Result = 'Информация для разработчика: \n' + str(AllInfo) + '\n' + Pass + ' seconds' 

    elif CheckInfo[1][0:4] == 'Week':
        Week = int(CheckInfo[1][4])
        Result = AllWeek(AllInfo,Subj,Week)

    elif CheckInfo[1] == 'Form':
        Result = 'bot.format\nОтправьте, боту сообщение снизу, добавив после ":" Дз. \nПри заполнении не используйте переносы на новую строку (Переносы, которые делает VK не считаются).'

    elif CheckInfo[1] == 'Form_1':
        Result = FormEditor(Subj)

    elif CheckInfo[1] == 'Error':
        Result = CheckInfo[0] + '\n' + Id + ', введите команду bot.help для изучения команд.'


    elif CheckInfo[1][0:3] == 'Day':
        DayNomber = CheckInfo[1][3]
        WeekNomber = CheckInfo[1][4]
        Job = CheckInfo[1][5]
        Day = int(DayNomber)
        Week = int(WeekNomber)
        if Job == '1':
            Result = AllDay(AllInfo,Subj,Day,Week)
        else:
            Cleanner(AllInfo,Day,Week)
            Refresh(AllInfo)
            Result = 'Вы успешно отчистили ДЗ с этого дня...'

    elif CheckInfo[1][0:8] == 'HomeWork':
        if len(CheckInfo[1]) == 9:
            if CheckInfo[1][8] == '1':
                Message = Message + ' (Добавлено пользователями)#'
                Mes = Message[14:len(Message)].splitlines()
                MesReck = ''
                for i in Mes:
                    MesReck = MesReck + ' ' + i
                ((AllInfo[int(Message[8])])[str(Message[4])])[int(Message[6])-1] = MesReck
            else:
                ((AllInfo[int(Message[8])])[str(Message[4])])[int(Message[6])-1] = ''
    
            Refresh(AllInfo)
            Result = CheckInfo[0]
        else:
            Info = ((AllInfo[int(Message[8])])[str(Message[4])])[int(Message[6])-1]
            if Info == '':
                Info = 'На сайте Знай Бай, не найдено ДЗ для этого предмета попробуйте позже...'
            Result = Info
    
    elif CheckInfo[1] == 'Edit':
        Stop = False
        Err = True
        NewHT = Message.splitlines()
        if (len(NewHT) == 86):
            line=0
            for week in range(0,2):
                line+=1
                for i in range(1,6):
                    line+=2
                    for f in range(0,len((AllInfo[week])[str(i)])):
                        Object = NewHT[line]
                        Sub = (Subj[str(i)])[f]
                        for g in range(0,len(Object)):
                            if (Object[g] == ":"):
                                Parts=g
                                break
                        CheckItem = Object[0:Parts]
                        if CheckItem != Sub:
                            Err = False
                        if Err == True:
                            CheckHT = Object[Parts+1:len(Object)]
                            CheckHt_ed = ''
                            for h in CheckHT:
                                if h != ' ':
                                    CheckHt_ed += h
                            if CheckHt_ed != '':
                                ((AllInfo[week])[str(i)])[f] = CheckHT + ' (Добавлено пользователями)#'
                        line+=1
        else:
            Result = 'Дз не добавленно, бот не смог обработать сообщение, возможно вы использовали перенос на новую строку...'
            Stop = True

        if Stop == False:
            if Err == False:
                Result = 'Дз не добавленно, бот не смог обработать сообщение, возможно вы сделали изменения в шаблоне. Возможно бот добавил некоторое Дз до ошибки...' 
            else:
                Result = 'Вы успешно добавили Дз... Спасибо)'
            Refresh(AllInfo)


    else:
        Result = ''

    return Result



def SendMessage(GId,vk,Result):
    if Result != '':
        try:
            print('Отправка сообщения...')
            vk.messages.send(peer_id = GId, message = Result, random_id = 0)
            print('Успешно!')
        except:
            pass





#Первое заполнение всех элементов
Week_1 = {'1' : ['','','','','','',''], '2' : ['','','','','',''], '3' : ['','','','','',''], '4' : ['','','','','',''], '5' : ['','','','','','','']}
Week_2 = {'1' : ['','','','','','',''], '2' : ['','','','','',''], '3' : ['','','','','',''], '4' : ['','','','','',''], '5' : ['','','','','','','']}
AllInfo = [Week_1, Week_2]
     
my_token = os.environ.get('tok')  #токен VK
passw = os.environ.get('passw')
name = os.environ.get('name')

data = {'UserName': name, 'Password': passw}     
GId = 2000000058   #Peer_id беседы VK | для основы 2000000047 | для тестов 2000000058
Gid_2 = 2000000059   #Для облачной БД
StartTime = time.time()     #Начальное время
Num = -1      #Колличество раз, обновления базы данных -1 для первого обновления
Time = 1800        #Промежуток между обновлениями бызы данных ДЗ
First = False

#Уроки в моём классе.
Subj = {
    '1' : ['Химия','Всемирная история','Англ. яз','Математика','Математика','География','Физра'],
    '2' : ['Черчение','Биология','Физра','Математика','Математика','Англ. яз',''], 
    '3' : ['Обществовединие','Англ. яз','Бел. яз.','Белорусская лит.','Физика','Математика',''], 
    '4' : ['Русск. яз.','Русск. лит.','Химия','Информатика','Англ. яз.','Физра',''], 
    '5' : ['Англ. яз.', 'Биология', 'ДМП','Физика','Математика','Русск. лит.','История Беларуси']
    }

#На команду bot.help, бот это отправляет
Commands = [
    '1. Дз на один урок - bot.x.y.z, x - день[1;5], y - урок[1;7], z - неделя[0 - эта неделя; 1 - следующая неделя].' + '\n',
    '2. Добавления Дз пользователями. Начало команды такое же, только добавляете - ".new.ваше дз" Пример: bot.1.1.0.new.параграф 20.' + '\n',
    '3. Команда bot.all, бот скинет всё Дз, которое у него есть.' + '\n',
    '4. Команда bot.day, бот скинет Дз на следующий день. Добавление: 1) .x - день[1;5] 2) .z - неделя [0 - эта неделя; 1 - следующая неделя], меняет неделю.' + '\n',
    '5. Команда bot.week, бот скинет Дз на эту неделю. Добавление: 1) .z - неделя [0 - эта неделя; 1 - следующая неделя], меняет неделю.' + '\n',
    '6. Команда bot.x.y.z.clean - отчищает Дз на выбранный урок. Также можно написать после команды bot.day. Делайте, это если заполнили урок, не правильно.' + '\n',
    '7. Команда bot.form - отправляет шаблон и объясняет, как работать с командой bot.edit' + '\n',
    '8. Команда bot.edit - сначала читайте пункт 7. Отправьте полученный шаблон и после ":" вписывайте Дз. Не используйте переносы на новую строку.' + '\n',
    '9. Команда bot.list - отправляет расписание на неделю.' + '\n',
    'Создатель: Егор Трухан. 10 "A" класс 2020 год. Версия: Beta 2.3. Приятного использования)'
]
About = ''
for i in range(0,len(Commands)):
    About = About + Commands[i] + '\n'

session= vk_api.VkApi(token = my_token)
vk = session.get_api()







SaveData = True

if SaveData == True:  #Берёт Дз с файла SaveData.txt, чтобы не потерять Дз, записанное пользователями после отключения программы.
    Doc = open('D:/Bot/Newfolder/data.txt', 'r', encoding='UTF-8')
    for week in range(0,2):
        for i in range(1,6):
            for f in range(0,len((AllInfo[week])[str(i)])):
                Temp = Doc.readline()
                ((AllInfo[week])[str(i)])[f] = Temp

    Doc.close()
    print(AllInfo)


print('Бот приступил к работе. Для выключения программы зажмите "-"...')
time.sleep(1)

while True:
    time.sleep(0.5) 
    Pass = str(math.floor(time.time()-StartTime))
    print('...Works...' + Pass + 'sec')
    WeekNow = datetime.datetime.now().weekday() + 1    #День недели
    PassTime = time.time()-StartTime-(Time*Num)    #Прошло времени между обновленими базы данныйх ДЗ


    if PassTime > Time:      #Если прошёл час(переменная Time). Для того, что бы каждый час обновлялась база данных.
        if WeekNow != 1:
            First = True
        Num = Num + 1        #Количество обновлений базы данных
        AllInfo = GetInfo(AllInfo,data,Gid_2)     #Обновление базы данных
        print('Завершение ' + str(Num + 1) + '-ого обновления базы данных... ' + str(Time * Num))

    else:
        PersInfo = GetMessage(GId,vk)       #Получение сообщения с беседы VK
        CheckInfo = CheckMessage(PersInfo[0],AllInfo)          #Проверка сообщения на принадлежность к команде бота(отправляет Case(случай), если да) и поиск ошибки
        Result = Completed(PersInfo[0],PersInfo[1],AllInfo,CheckInfo,GId,vk,Subj,About,Pass,Gid_2)         #Обработка сообщения с ДЗ или ошибкой
        SendMessage(GId,vk,Result)            #Отправка сообщения с ДЗ или ошибкой



print('программа завершена успешно...')
