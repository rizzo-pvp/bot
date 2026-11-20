import asyncio
import random
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated

# ВСТАВЬ СЮДА НОВЫЙ ТОКЕН (после /revoke в BotFather)
BOT_TOKEN = "9069178855:AAHR5q2dlfLabPK4HfqtGBfYGj1V_Ml63rM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗЫ ДАННЫХ (В ОПЕРАТИВНОЙ ПАМЯТИ) ---
users_data = {} 
active_battles = {} 

# --- УЛИЧНЫЕ МАТЫ И ОСКОРБЛЕНИЯ (ЖЕСТКИЕ) ---
STREET_INSULTS = [
    "я ебал твою мать в рот, шлюха ты подзаборная",
    "иди нахуй, хуесос гнойный",
    "твой батя хуй сосал, а ты его позорный выкидыш",
    "завали ебало, мразь",
    "ты че, пидор, быкуешь?",
    "соси хуй, уебок",
    "я твою мамку на спор ебал, а ты тут чето вякаешь",
    "ты чмо ебаное, тебя в детстве об угол роняли",
    "отсоси у трамвая, пес смердящий",
    "пизда тебе, петух общипанный",
    "да ты просто шлюха, которая не умеет себя вести",
    "хули ты как гандон растянулся, закрой рот",
    "ты такой тупой, что тебя даже в шлюхи не возьмут",
    "я твой рот ебал, дебил конченый"
]

# --- ТВОИ ТЕКСТЫ (ИНТЕЛЛЕКТУАЛЬНАЯ ПРОСТЫНЯ) ---
ACADEMIC_INSULTS = [
    "присутствие подобного фенотипа в человеческой популяции вызывает немало вопросов относительно механизмов естественной селекции",
    "твоя нейрофизиологическая организация словно подверглась необратимой дезорганизации на этапе формирования базовых когнитивных функций",
    "каждая твоя попытка самоутверждения сопровождается настолько выраженной поведенческой примитивностью, что даже простейшие беспозвоночные выглядят умнее",
    "твой генетический материал будто содержит исключительно последовательности отвечающие за воспроизводство самодовольства беспринципности и хронической социальной некомпетентности",
    "твоя поведенческая активность напоминает беспомощную колонию сапрофитов существующую исключительно за счёт чужих ресурсов",
    "твоя личностная структура напоминает патологически изменённую ткань в которой здоровые элементы окончательно вытеснены бесполезными клеточными образованиями",
    "ты настолько предсказуем в своей примитивности что даже паразитологическое исследование твоих поведенческих механизмов не обнаружило бы ничего нового",
    "даже простейшая амёба демонстрирует более убедительную стратегию существования поскольку хотя бы не пытается выдавать собственную примитивность за исключительную форму развития",
    "ты являешься настолько концентрированным воплощением человеческой неполноценности в коммуникации что любое соприкосновение с твоей риторикой вызывает желание провести тотальную санитарную обработку",
    "ты демонстрируешь настолько выраженную поведенческую несостоятельность что даже собственные высказывания становятся для тебя непреодолимым препятствием",
    "ты обладаешь поистине феноменальной способностью превращать любую дискуссию в демонстрацию собственной интеллектуальной импотенции",
    "твоя самоуверенность давно переросла границы обычного самомнения и превратилась в монументальную карикатуру на человеческое достоинство",
    "ты настолько зависим от конфронтации что без очередного словесного скандала твоя искусственная значимость перестаёт функционировать",
    "ты являешься не грозным оппонентом а затянувшимся социальным недоразумением чья единственная особенность заключается в патологической потребности занимать чужое внимание",
    "твоя патологическая потребность в демонстрации превосходства настолько выражена что любое столкновение с объективной действительностью вызывает у тебя приступ риторической беспомощности",
    "твои когнитивные процессы напоминают неисправную нейронную сеть в которой импульсивность полностью вытеснила аналитическое мышление",
    "ты словно перепутал агрессивность с авторитетом а отсутствие контроля над собственными реакциями с проявлением индивидуальности",
    "ты представляешь собой исключительный антропологический казус продукт настолько сомнительной эволюционной реализации",
    "твой характер является своеобразной биологической аномалией в которой патологическое самомнение вступает в прямое противоречие с фактической интеллектуальной состоятельностью",
    "ты настолько увлечён собственной персоной что даже элементарные социальные сигналы не способны преодолеть плотный барьер твоего гипертрофированного эго",
    "ты являешься своеобразным памятником когнитивной инертности и нравственной дезорганизации",
    "тупейший отморозок ты представляешь собой настолько жалкое и отвратительное сочетание человеческих качеств что даже само понятие посредственности рядом с тобой меркнет",
    "ты не обладаешь ни достоинством ни харизмой ни внутренним стержнем зато демонстрируешь поразительную концентрацию наглости и самодовольства",
    "ты обыкновенный самодовольный хам с завышенной самооценкой и крайне ограниченным представлением о собственной значимости",
    "чумозородобный отсталый проигравший спор собственной тени и до сих пор считает это стратегической победой",
    "ты не оппонент и не противник ты просто неисправный механизм словесного саморазрушения",
    "ты ходячий памятник словесному банкротству биологическая карикатура на здравый смысл",
    "твоя черепная коробка напоминает заброшенный склад сельскохозяйственных отходов где остатки логики покрылись пылью",
    "ты производишь впечатление существа которое случайно попало в человеческое общество через техническую ошибку на проходной эволюции",
    "блядское недоразумение подзаборной инженерии генетически выведенный побочный продукт",
    "ходячая катастрофа деревенского масштаба с интеллектом промокшей табуретки и самооценкой императора мусорной свалки",
    "ты абсолютный чемпион по производству словесных испражнений среди собственных отражений",
    "твоя аргументация состоит из трех элементов первый это невежество второй это необоснованная самоуверенность третий это катастрофическая неспособность осознать наличие первых двух",
    "ты не просто бездарность ты целая промышленная отрасль по производству бездарности",
    "твой разум напоминает заброшенную лабораторию в которой проводились эксперименты над здравым смыслом но единственным результатом стало полное уничтожение способности отличать мысль от шума",
    "твое присутствие не усложняет дискуссию и не делает ее интереснее оно лишь заставляет окружающих тратить время на восстановление элементарной логики"
]

LEVEL_NAMES = {
    1: "нищий тролл", 2: "нигга тролл", 3: "биг нигга тролл", 4: "аристократ тролл",
    5: "тролл полиция", 6: "баянист", 7: "биг босс тролл", 8: "крепкий тролл",
    9: "сын троллинга", 10: "отец троллинга", 11: "дед троллинга", 12: "профессиональный тролл",
    13: "начитанный шаблонер", 14: "1000 аура тролл", 15: "the god of trolling."
}

def get_user(chat_id, user_id):
    if chat_id not in users_data:
        users_data[chat_id] = {}
    if user_id not in users_data[chat_id]:
        users_data[chat_id][user_id] = {"xp": 0, "level": 1, "points": 0, "words": 0}
    return users_data[chat_id][user_id]

def add_xp(chat_id, user_id, words):
    user = get_user(chat_id, user_id)
    user["xp"] += words
    user["words"] += words
    required_xp = user["level"] * 100
    if user["xp"] >= required_xp and user["level"] < 15:
        user["xp"] -= required_xp
        user["level"] += 1
        return True, user["level"], LEVEL_NAMES[user["level"]]
    return False, user["level"], LEVEL_NAMES[user["level"]]

# Генератор жесткого ответа (комбинирует мат и твои тексты)
def generate_hard_reply(user_name):
    # 50% шанс что начнет с уличного мата, потом добавит умный текст
    if random.random() > 0.5:
        street = random.choice(STREET_INSULTS)
        academic = random.choice(ACADEMIC_INSULTS)
        return f"{user_name}, {street}. И знай, {academic}."
    else:
        # Или сразу выдаст два умных текста
        return f"{user_name}, {random.choice(ACADEMIC_INSULTS)}. {random.choice(ACADEMIC_INSULTS)}."

@dp.chat_member()
async def bot_added(event: ChatMemberUpdated):
    if event.new_chat_member.user.id == (await bot.get_me()).id and event.new_chat_member.status == "member":
        text = ("Всем привет, я — виза, бог троллинга 2026, ебу весь ксививайд и выебу этот чат тоже. "
                "Спасибо за добавление, ознакомиться как со мной говорить можно тут - https://telegra.ph/Viza-troll-bot-11-20")
        await event.answer(text)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = "Привет друн, я виза — лучшая ИИ 2026 года от великого создателя @reportspy. Добавь меня в группу и начни общение!"
    await message.answer(text)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in users_data or not users_data[chat_id]:
        await message.reply("Тут пока нет нищих троллов, которые набили хоть что-то. Позор.")
        return
    
    sorted_users = sorted(users_data[chat_id].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
    text = "🏆 **Таблица лидеров по троллингу:**\n\n"
    for i, (uid, data) in enumerate(sorted_users[:10]):
        try:
            user_info = await bot.get_chat_member(chat_id, uid)
            name = user_info.user.first_name
        except:
            name = "Аноним"
        text += f"{i+1}. {name} — {data['level']} лвл ({data['xp']} XP) | {data['points']} поинтов\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    text = message.text.lower()
    words_count = len(message.text.split())

    # Начисляем XP
    leveled_up, lvl, lvl_name = add_xp(chat_id, user_id, words_count)
    if leveled_up:
        await message.reply(f"{user_name}, хули ты так разболтался? Ладно, твой уровень повышен до {lvl} ({lvl_name}). Продолжай в том же духе, клоун.")

    # Токс-батл
    if user_id in active_battles and active_battles[user_id]["active"]:
        active_battles[user_id]["words"] += words_count
        return 

    # Проверка на обращение к Визе
    is_reply_to_viza = message.reply_to_message and message.reply_to_message.from_user.id == (await bot.get_me()).id
    called_by_name = "виза" in text or "визу" in text or "визе" in text

    if not (is_reply_to_viza or called_by_name):
        return 

    clean_text = text.replace("виза", "").replace("визу", "").replace("визе", "").strip()

    # КНБ
    if "камень ножницы бумага" in clean_text or "кнб" in clean_text:
        await play_rps(message, chat_id, user_id, user_name)
        return

    # Поинты
    if "сколько" in clean_text and "поинт" in clean_text:
        points = get_user(chat_id, user_id)["points"]
        await message.reply(f"У тебя {points} поинтов, {user_name}. Это всё, на что ты способен? Позор ебаный.")
        return

    # Токс-батл
    if "токс" in clean_text and "батл" in clean_text:
        if user_id in active_battles and active_battles[user_id]["active"]:
            await message.reply("Ты че, батл уже идет! Строчи давай, хули молчишь!")
        else:
            asyncio.create_task(run_tox_battle(message, chat_id, user_id, user_name))
        return

    # Поддержка
    sad_words = ["грустно", "плохо", "одиноко", "депрессия", "устал", "тяжело", "паршиво"]
    if any(word in clean_text for word in sad_words):
        replies = [
            f"да ты че брат, не расстраивайся, все нормалды будет, побурмалди со мной и кайф будет все)",
            f"{user_name}, ты че раскис как лох? Держи хвост пистолетом, я с тобой, все вывезем. А кто тебя обидел - тому ебало разобьем.",
            f"Хули ты нос повесил? Жизнь - это полоса препятствий. Соберись, братан, не будь чмошником!"
        ]
        await message.reply(random.choice(replies))
        return

    # Похвала
    praise_words = ["крутой", "лучший", "молодец", "спасибо", "топ", "бог", "хорош", "красава"]
    if any(word in clean_text for word in praise_words):
        replies = [
            f"пожалуйста, учись у меня, я твой биг босс. А ты {user_name} тоже не плох в троллинге, прокачиваешься потихоньку.",
            f"Я знаю, что я лучший. Но ты тоже молодец, что признаешь это. Растешь над собой, {user_name}.",
            f"Спасибо нахуй. Приятно, когда холопы признают величие своего господина."
        ]
        await message.reply(random.choice(replies))
        return

    # ОСКОРБЛЕНИЯ / ПРОВОКАЦИИ
    bad_words = ["говно", "хуй", "пизда", "лох", "дурак", "тупой", "ебаный", "долбоеб", "мразь", "пидор", "говночист", "пес", "скотина", "уебан", "шлюха"]
    if any(word in clean_text for word in bad_words):
        match = re.search(r'виза\s+([а-яa-z]+)', text)
        
        if match:
            insulted_word = match.group(1)
            # Если он нашел конкретное слово (типо "говночист")
            reply = f"{insulted_word} батек твой, а я бог твой. " + generate_hard_reply(user_name)
        else:
            # Иначе просто жесткий ответ
            reply = generate_hard_reply(user_name)
        
        # Отвечаем ИМЕННО на сообщение юзера
        await message.reply(reply)
        return

    # Приветствия
    if "привет" in clean_text or "здарова" in clean_text or "ку" in clean_text or not clean_text:
        reply = f"Здарова, {user_name}, хули надо. " + random.choice(STREET_INSULTS) + ". " + random.choice(ACADEMIC_INSULTS)
        await message.reply(reply)
        return

    # Если просто написал что-то с упоминанием Виза
    await message.reply(generate_hard_reply(user_name))

async def play_rps(message, chat_id, user_id, user_name):
    choices = ["камень", "ножницы", "бумага"]
    viza_choice = random.choice(choices)
    result = random.choice([0, 1, 2])
    user = get_user(chat_id, user_id)

    if result == 0:
        await message.reply(f"Я выбрал {viza_choice}. Ничья, лошара. Давай еще.")
    elif result == 1:
        reply = f"Я выбрал {viza_choice} и выиграл! Ты просто ебаный нищук. {random.choice(STREET_INSULTS)}. Иди учись, {user_name}."
        await message.reply(reply)
    else:
        user["points"] += 1
        reply = f"Я выбрал {viza_choice}... И ты выиграл. БЛЯТЬ! Ты че пидорас, просто с софтом хуяришь? Забирай свой жалкий +1 поинт, читер. {random.choice(ACADEMIC_INSULTS)}"
        await message.reply(reply)

async def run_tox_battle(message, chat_id, user_id, user_name):
    active_battles[user_id] = {"active": True, "words": 0}
    
    await message.reply(f"⚔️ **ТОКС-БАТЛ НАЧАЛСЯ!**\n\n{user_name}, у тебя ровно 30 секунд, чтобы вывалить на меня весь свой словесный понос. Начинай, я слушаю. Время пошло!")
    await asyncio.sleep(30)
    
    user_words = active_battles[user_id]["words"]
    active_battles[user_id]["active"] = False
    
    await message.reply(f"Время вышло! Ты наговорил на {user_words} слов. А теперь смотри, как работает настоящий бог...")
    
    viza_words = 0
    for _ in range(30):
        # Комбинируем мат и умные фразы для токс-батла
        if random.random() > 0.5:
            phrase = random.choice(STREET_INSULTS) + " " + random.choice(ACADEMIC_INSULTS)
        else:
            phrase = random.choice(ACADEMIC_INSULTS)
            
        phrase = phrase[:200] + "..." # Ограничиваем длину
        await bot.send_message(chat_id, phrase)
        viza_words += len(phrase.split())
        await asyncio.sleep(1)

    await bot.send_message(chat_id, f"Итого от меня: {viza_words} слов. \n\nСчитаем результаты...")
    await asyncio.sleep(2)

    if viza_words > user_words:
        await bot.send_message(chat_id, f"ХА-ХА-ХА! Я победил! {user_name}, ты внатуре ебаный нищук, у тебя {user_words} слов, а у меня {viza_words}. Иди плачь в подушку, {random.choice(STREET_INSULTS)}.")
    else:
        bonus_xp = viza_words - user_words
        leveled_up, lvl, lvl_name = add_xp(chat_id, user_id, bonus_xp)
        await bot.send_message(chat_id, f"Этого не может быть! Ты выиграл со счетом {user_words} против {viza_words}. Видимо, я сегодня не в форме. Получай {bonus_xp} XP, ты доказал, что не полный ноль.")
        if leveled_up:
            await bot.send_message(chat_id, f"И ты даже апнул уровень до {lvl} ({lvl_name})! Глазам своим не верю.")

async def main():
    print("Бот Виза запущен. Пощады не будет.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())