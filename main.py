import asyncio
import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ===== НАСТРОЙКИ =====
TOKEN = "8692315145:AAFcBTfG8ehZzQeh7SFFv3M73wvk7jehxjw"
CHANNEL_LINK = "https://t.me/nushyatgk"
CHANNEL_USERNAME = "@nushyatgk"
BOT_USERNAME = "nushya001bot"
ADMIN_ID = 8251687795

NOTIFICATIONS_FILE = "notifications.json"
TICKETS_FILE = "tickets.json"
PROMO_FILE = "promo.json"
DATA_FILE = "users.json"
VIDEOS_FILE = "videos.json"
LIKES_FILE = "likes.json"
SUGGESTIONS_FILE = "suggestions.json"  # <--- ДОБАВЬ ЭТУ СТРОКУ

user_captcha = {}
user_last_bonus = {}  # {user_id: timestamp_last_bonus}
user_game_state = {}
tickets_data = {}
ticket_counter = 0
suggestions_data = {}
user_data = {}
user_counter = 0
videos_data = {}
video_counter = 0
likes_data = {}

admin_upload_state = {}
admin_coin_state = {}
admin_find_video_state = {}
admin_delete_video_state = {}
admin_ban_state = {}
admin_unban_state = {}
admin_find_user_state = {}
notifications_data = {}
notification_counter = 0


# =====================

def load_data():
    global user_data, user_counter, videos_data, video_counter, likes_data, suggestions_data, promo_data, user_promos, tickets_data, ticket_counter, user_last_bonus, notifications_data, notification_counter

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_data = data.get("users", {})
                user_data = {int(k): v for k, v in user_data.items()}
                user_counter = data.get("user_counter", 0)

                for uid in user_data:
                    if "watched_videos" not in user_data[uid]:
                        user_data[uid]["watched_videos"] = []
                    if "referrals" not in user_data[uid]:
                        user_data[uid]["referrals"] = []
                    if "banned" not in user_data[uid]:
                        user_data[uid]["banned"] = False
                    if "sent_messages" not in user_data[uid]:
                        user_data[uid]["sent_messages"] = []
                    if "favorites" not in user_data[uid]:
                        user_data[uid]["favorites"] = []
        except Exception as e:
            print(f"❌ Ошибка загрузки пользователей: {e}")
            user_data = {}
            user_counter = 0
    else:
        user_data = {}
        user_counter = 0

    if os.path.exists(VIDEOS_FILE):
        try:
            with open(VIDEOS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                videos_data = data.get("videos", {})
                video_counter = data.get("video_counter", 0)
                print(f"📹 Загружено видео из БД: {len(videos_data)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки видео: {e}")
            videos_data = {}
            video_counter = 0
    else:
        videos_data = {}
        video_counter = 0

    if os.path.exists(LIKES_FILE):
        try:
            with open(LIKES_FILE, 'r', encoding='utf-8') as f:
                likes_data = json.load(f)
                print(f"👍 Загружено лайков: {len(likes_data)} видео")
        except Exception as e:
            print(f"❌ Ошибка загрузки лайков: {e}")
            likes_data = {}
    else:
        likes_data = {}

    if os.path.exists(SUGGESTIONS_FILE):
        try:
            with open(SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                suggestions_data = json.load(f)
                print(f"💬 Загружено предложений: {len(suggestions_data)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки предложений: {e}")
            suggestions_data = {}
    else:
        suggestions_data = {}

    if os.path.exists(PROMO_FILE):
        try:
            with open(PROMO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                promo_data = data.get("promos", {})
                user_promos = data.get("user_promos", {})
                print(f"🎫 Загружено промокодов: {len(promo_data)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки промокодов: {e}")
            promo_data = {}
            user_promos = {}
    else:
        promo_data = {}
        user_promos = {}

    try:
        promo_to_save = {
            "promos": promo_data,
            "user_promos": user_promos
        }
        with open(PROMO_FILE, 'w', encoding='utf-8') as f:
            json.dump(promo_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения промокодов: {e}")

    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tickets_data = data.get("tickets", {})
                ticket_counter = data.get("ticket_counter", 0)
                print(f"🎫 Загружено тикетов: {len(tickets_data)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки тикетов: {e}")
            tickets_data = {}
            ticket_counter = 0
    else:
        tickets_data = {}
        ticket_counter = 0

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_last_bonus = data.get("user_last_bonus", {})
                # Преобразуем ключи в int
                user_last_bonus = {int(k): v for k, v in user_last_bonus.items()}
        except Exception as e:
            print(f"❌ Ошибка загрузки бонусов: {e}")
            user_last_bonus = {}

    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                notifications_data = data.get("notifications", {})
                notification_counter = data.get("notification_counter", 0)
                print(f"📢 Загружено оповещений: {len(notifications_data)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки оповещений: {e}")
            notifications_data = {}
            notification_counter = 0
    else:
        notifications_data = {}
        notification_counter = 0


def save_data():
    try:
        data_to_save = {
            "users": user_data,
            "user_counter": user_counter
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения пользователей: {e}")

    try:
        video_to_save = {
            "videos": videos_data,
            "video_counter": video_counter
        }
        with open(VIDEOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(video_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения видео: {e}")

    try:
        with open(LIKES_FILE, 'w', encoding='utf-8') as f:
            json.dump(likes_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения лайков: {e}")

    try:
        with open(SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(suggestions_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения предложений: {e}")

    try:
        tickets_to_save = {
            "tickets": tickets_data,
            "ticket_counter": ticket_counter
        }
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tickets_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения тикетов: {e}")

    try:
        # Сохраняем время бонусов
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "users": user_data,
                "user_counter": user_counter,
                "user_last_bonus": user_last_bonus
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")

    try:
        notifications_to_save = {
            "notifications": notifications_data,
            "notification_counter": notification_counter
        }
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notifications_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения оповещений: {e}")

def init_video_likes(video_id):
    if video_id not in likes_data:
        likes_data[video_id] = {
            "likes": 0,
            "dislikes": 0,
            "users": {}
        }
        save_data()


def generate_captcha():
    """Генерирует простой пример и варианты ответов"""
    num1 = random.randint(2, 9)
    num2 = random.randint(2, 9)
    correct_answer = num1 + num2

    # Генерируем 4 неправильных варианта
    wrong_answers = []
    while len(wrong_answers) < 4:
        wrong = correct_answer + random.randint(-5, 5)
        if wrong != correct_answer and wrong > 0 and wrong not in wrong_answers:
            wrong_answers.append(wrong)

    # Все варианты
    all_answers = wrong_answers + [correct_answer]
    random.shuffle(all_answers)

    return {
        "question": f"{num1} + {num2}",
        "correct": correct_answer,
        "options": all_answers
    }

def is_captcha_banned(user_id: int) -> tuple:
    """Проверяет, не забанен ли пользователь каптчей"""
    current_time = asyncio.get_event_loop().time()
    if user_id in user_captcha:
        banned_until = user_captcha[user_id].get("banned_until", 0)
        if banned_until > current_time:
            remaining = int(banned_until - current_time)
            return True, remaining
    return False, 0


async def show_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает каптчу пользователю"""
    user_id = update.effective_user.id

    # Генерируем каптчу
    captcha_data = generate_captcha()
    user_captcha[user_id] = {
        "attempts": 0,
        "correct_answer": captcha_data["correct"],
        "banned_until": 0,
        "passed": False
    }

    # Создаём кнопки с вариантами ответов
    keyboard = []
    row = []
    for i, option in enumerate(captcha_data["options"]):
        row.append(InlineKeyboardButton(str(option), callback_data=f"captcha_{option}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🤖 Проверка безопасности**\n\n"
        "Вы новый пользователь! Решите пример, чтобы продолжить:\n\n"
        f"**📝 {captcha_data['question']} = ?**\n\n"
        "⚠️ У вас 5 попыток. После 5 ошибок - бан на 5 минут!"
    )

    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на каптчу"""
    query = update.callback_query
    user_id = query.from_user.id
    answer = int(query.data.split("_")[1])

    # Проверяем, есть ли пользователь в каптче
    if user_id not in user_captcha:
        await query.answer("❌", show_alert=False)
        await show_main_menu(update, context)
        return

    captcha = user_captcha[user_id]

    # Проверяем бан
    banned_until = captcha.get("banned_until", 0)
    current_time = asyncio.get_event_loop().time()
    if banned_until > current_time:
        remaining = int(banned_until - current_time)
        remaining_min = remaining // 60
        remaining_sec = remaining % 60
        await query.answer(f"❌ Вы в бане! Осталось: {remaining_min} мин {remaining_sec} сек", show_alert=True)
        return

    # Проверяем ответ
    if answer == captcha["correct_answer"]:
        # ✅ ПРАВИЛЬНО - каптча пройдена
        user_captcha[user_id]["passed"] = True

        # Регистрируем пользователя
        get_user_stats(user_id)

        await query.answer("✅ Каптча пройдена!", show_alert=False)

        # Удаляем сообщение с каптчей
        try:
            await query.message.delete()
        except:
            pass

        # ⭐ ПРОВЕРЯЕМ РЕФЕРАЛА (который мог быть сохранён до каптчи)
        pending_referrer = context.user_data.get('pending_referrer')
        if pending_referrer and pending_referrer != user_id:
            # Проверяем подписку
            is_subscribed = await check_subscription(user_id, context)
            if is_subscribed:
                if pending_referrer in user_data and user_id not in user_data[pending_referrer]["referrals"]:
                    user_data[pending_referrer]["referrals"].append(user_id)
                    user_data[pending_referrer]["coins"] += 5
                    save_data()

                    # Уведомляем реферала
                    try:
                        await context.bot.send_message(
                            pending_referrer,
                            f"✅ **Новый реферал!**\n\n"
                            f"👤 Пользователь ID #{user_data[user_id]['number']} перешёл по вашей ссылке и прошёл проверку!\n"
                            f"🪙 Вы получили +5 монет!\n"
                            f"💰 Ваш баланс: {user_data[pending_referrer]['coins']} монет",
                            parse_mode="Markdown"
                        )
                    except:
                        pass
            # Очищаем ожидающий реферал
            del context.user_data['pending_referrer']

        # Проверяем подписку и показываем главное меню
        is_subscribed = await check_subscription(user_id, context)
        if not is_subscribed:
            await show_subscription_required(update, context)
        else:
            await show_main_menu(update, context)
    else:
        # ❌ НЕПРАВИЛЬНО (остальной код без изменений)
        captcha["attempts"] += 1
        remaining_attempts = 5 - captcha["attempts"]

        if captcha["attempts"] >= 5:
            # БАН на 5 минут
            captcha["banned_until"] = current_time + 300
            save_data()

            await query.answer("❌ Вы использовали все попытки! Бан на 5 минут!", show_alert=True)

            keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text(
                "**🚫 Вы забанены на 5 минут!**\n\n"
                "Вы использовали все 5 попыток.\n"
                "Попробуйте снова через 5 минут.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # Даём новую попытку
            new_captcha = generate_captcha()
            captcha["correct_answer"] = new_captcha["correct"]
            captcha["options"] = new_captcha["options"]

            keyboard = []
            row = []
            for i, option in enumerate(new_captcha["options"]):
                row.append(InlineKeyboardButton(str(option), callback_data=f"captcha_{option}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.answer(f"❌ Неправильно! Осталось попыток: {remaining_attempts}", show_alert=True)

            await query.message.edit_text(
                f"**🤖 Проверка безопасности**\n\n"
                f"❌ **Неправильно!** Осталось попыток: {remaining_attempts}\n\n"
                f"**📝 {new_captcha['question']} = ?**\n\n"
                f"⚠️ После 5 ошибок - бан на 5 минут!",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )


def get_video_stats(video_id):
    if video_id not in likes_data:
        init_video_likes(video_id)
    return likes_data[video_id]


def get_next_user_number():
    global user_counter
    user_counter += 1
    save_data()
    return user_counter


def get_next_video_number():
    global video_counter
    video_counter += 1
    save_data()
    return str(video_counter).zfill(3)


def get_user_stats(user_id: int):
    if user_id not in user_data:
        user_number = get_next_user_number()
        user_data[user_id] = {
            "number": user_number,
            "user_id": user_id,
            "videos_watched": 0,
            "coins": 5,
            "subscription": "Нет",
            "referrals": [],
            "watched_videos": [],
            "banned": False,
            "sent_messages": [],
            "favorites": []
        }
        save_data()
    else:
        if "watched_videos" not in user_data[user_id]:
            user_data[user_id]["watched_videos"] = []
        if "referrals" not in user_data[user_id]:
            user_data[user_id]["referrals"] = []
        if "videos_watched" not in user_data[user_id]:
            user_data[user_id]["videos_watched"] = 0
        if "coins" not in user_data[user_id]:
            user_data[user_id]["coins"] = 5
        if "subscription" not in user_data[user_id]:
            user_data[user_id]["subscription"] = "Нет"
        if "banned" not in user_data[user_id]:
            user_data[user_id]["banned"] = False
        if "sent_messages" not in user_data[user_id]:
            user_data[user_id]["sent_messages"] = []
        if "favorites" not in user_data[user_id]:
            user_data[user_id]["favorites"] = []

    return user_data[user_id]


def get_random_video(user_id: int):
    if not videos_data:
        return None

    watched = user_data[user_id].get("watched_videos", [])
    all_videos = list(videos_data.keys())

    unwatched = [v for v in all_videos if v not in watched]

    if unwatched:
        return random.choice(unwatched)
    elif all_videos:
        user_data[user_id]["watched_videos"] = []
        save_data()
        return random.choice(all_videos)
    else:
        return None


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    clear_user_modes(context, user_id)

    if user_data.get(user_id, {}).get("banned", False):
        if update.callback_query:
            await update.callback_query.answer("❌ Вы забанены!", show_alert=True)
        else:
            await update.message.reply_text("❌ Вы забанены!")
        return

    keyboard = [
        [InlineKeyboardButton("📢 Наш канал", url=CHANNEL_LINK)],
        [
            InlineKeyboardButton("🎬 Видео (1 🪙)", callback_data="watch_video"),
            InlineKeyboardButton("⭐ Избранное", callback_data="favorites")
        ],
        [
            InlineKeyboardButton("🎫 Промо", callback_data="promo"),
            InlineKeyboardButton("💬 Предложение", callback_data="suggest")
        ],
        [
            InlineKeyboardButton("🎮 Игры", callback_data="games"),
            InlineKeyboardButton("🎁 Халява", callback_data="free_bonus")
        ],
        [
            InlineKeyboardButton("🆘 Поддержка", callback_data="support"),
            InlineKeyboardButton("👤 Профиль", callback_data="profile")
        ]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("👑 Админ панель", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🏠 Главное меню**\n\n"
        "💰 Вы можете зарабатывать/получать монеты различными способами\n\n"
        "⬇️ Выберите действие:"
    )

    try:
        if update.callback_query:
            # ⭐ ПРОВЕРКА: если сообщение уже такое же - не редактируем
            if update.callback_query.message.text == text and update.callback_query.message.reply_markup == reply_markup:
                await update.callback_query.answer("ℹ️ Вы уже в главном меню", show_alert=False)
                return
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        if "Message is not modified" not in str(e):
            print(f"Не удалось отредактировать: {e}")
            if update.callback_query:
                await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def free_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдаёт ежечасный бонус 1 монета"""
    query = update.callback_query
    user_id = query.from_user.id

    # Сразу отвечаем на callback, чтобы убрать "часики"
    await query.answer()

    current_time = asyncio.get_event_loop().time()

    # Проверяем, когда пользователь последний раз получал бонус
    last_bonus = user_last_bonus.get(user_id, 0)
    time_passed = current_time - last_bonus
    one_hour = 3600  # 1 час в секундах

    if time_passed < one_hour:
        # Осталось времени
        remaining = int(one_hour - time_passed)
        remaining_minutes = remaining // 60
        remaining_seconds = remaining % 60

        # Показываем сообщение с кнопкой OK
        keyboard = [[InlineKeyboardButton("✅ OK", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            f"❌ **Ошибка!**\n\n"
            f"Вы уже получали бонус!\n"
            f"⏳ Осталось: {remaining_minutes} мин {remaining_seconds} сек\n\n"
            f"Возвращайтесь позже!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # Выдаём бонус
    stats = get_user_stats(user_id)
    user_data[user_id]["coins"] += 1
    user_last_bonus[user_id] = current_time
    save_data()

    # Показываем сообщение с кнопкой OK
    keyboard = [[InlineKeyboardButton("✅ OK", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        f"✅ **Вы получили 1 монету!**\n\n"
        f"💰 Ваш баланс: {user_data[user_id]['coins']} монет\n\n"
        f"🎁 Следующий бонус через 1 час!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню игр"""
    query = update.callback_query
    user_id = query.from_user.id

    clear_user_modes(context, user_id)

    keyboard = [
        [InlineKeyboardButton("🎲 Кубик", callback_data="game_dice")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🎮 Игры**\n\n"
        "💰 Выберите игру и выигрывайте монеты!\n\n"
        "⬇️ **Доступные игры:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def game_dice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает игру в Кубик"""
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("🎲 Четное", callback_data="dice_even")],
        [InlineKeyboardButton("🎲 Нечетное", callback_data="dice_odd")],
        [InlineKeyboardButton("🔙 Назад", callback_data="games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🎲 Кубик**\n\n"
        "📌 **Правила игры:**\n"
        "• Выберите: Четное или Нечетное\n"
        "• Сделайте ставку\n"
        "• Коэффициент выигрыша: **1.5x**\n\n"
        "📌 **Пример:**\n"
        "Ставка 100 монет → Выигрыш 150 монет\n\n"
        "⬇️ **Выберите четное или нечетное:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def dice_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь выбрал четное/нечетное"""
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data.split("_")[1]  # "even" or "odd"

    context.user_data['dice_choice'] = choice
    context.user_data['awaiting_dice_bet'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="game_dice")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"**🎲 Кубик**\n\n"
        f"✅ Вы выбрали: **{'Четное' if choice == 'even' else 'Нечетное'}**\n\n"
        f"💰 **Напишите ставку (числом):**\n\n"
        f"💡 Минимальная ставка: **5 монет**\n"
        f"💡 Максимальная ставка: **{user_data[user_id]['coins']} монет** (ваш баланс)"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_dice_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ставку и бросает кубик"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('awaiting_dice_bet', False):
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте число!")
        return

    try:
        bet = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Введите число!")
        return

    # ⭐ Проверка ставки (минимальная 5)
    if bet < 5:
        await update.message.reply_text("❌ Минимальная ставка: 5 монет!")
        return

    stats = get_user_stats(user_id)
    if bet > stats["coins"]:
        await update.message.reply_text(f"❌ У вас только {stats['coins']} монет!", parse_mode="Markdown")
        return

    choice = context.user_data.get('dice_choice')
    if not choice:
        await update.message.reply_text("❌ Ошибка! Начните игру заново.")
        del context.user_data['awaiting_dice_bet']
        return

    # Списываем ставку
    user_data[user_id]["coins"] -= bet
    save_data()

    # Отправляем сообщение о броске
    msg = await update.message.reply_text(
        f"🎲 **Бросаем кубик...**\n\n"
        f"💰 Ставка: {bet} монет\n"
        f"🎯 Выбор: {'Четное' if choice == 'even' else 'Нечетное'}",
        parse_mode="Markdown"
    )

    # Ждём 1 секунду перед отправкой кубика
    await asyncio.sleep(1)

    # Отправляем кубик (Telegram встроенная анимация)
    dice_message = await context.bot.send_dice(chat_id=user_id, emoji="🎲")

    # Получаем значение кубика (1-6)
    dice_value = dice_message.dice.value

    # Определяем четное/нечетное
    is_even = dice_value % 2 == 0
    result = "even" if is_even else "odd"

    # Ждём 3 секунды перед результатом
    await asyncio.sleep(3)

    # Проверяем выигрыш
    if choice == result:
        # Выигрыш с коэффициентом 1.5
        win_amount = int(bet * 1.5)
        user_data[user_id]["coins"] += win_amount
        save_data()

        await update.message.reply_text(
            f"🎲 **Результат:** {dice_value} ({'Четное' if is_even else 'Нечетное'})\n\n"
            f"✅ **ВЫ ВЫИГРАЛИ!**\n\n"
            f"💰 Ставка: {bet} монет\n"
            f"🏆 Выигрыш: {win_amount} монет\n"
            f"📈 Коэффициент: 1.5x\n\n"
            f"💳 **Новый баланс:** {user_data[user_id]['coins']} монет",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"🎲 **Результат:** {dice_value} ({'Четное' if is_even else 'Нечетное'})\n\n"
            f"❌ **ВЫ ПРОИГРАЛИ!**\n\n"
            f"💰 Проиграно: {bet} монет\n\n"
            f"💳 **Новый баланс:** {user_data[user_id]['coins']} монет",
            parse_mode="Markdown"
        )

    # Кнопки для продолжения
    keyboard = [
        [InlineKeyboardButton("🎲 Играть ещё", callback_data="game_dice")],
        [InlineKeyboardButton("🔙 В меню игр", callback_data="games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("⬇️ **Выберите действие:**", reply_markup=reply_markup, parse_mode="Markdown")

    # Очищаем состояние
    del context.user_data['awaiting_dice_bet']
    del context.user_data['dice_choice']

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс создания тикета"""
    query = update.callback_query
    user_id = query.from_user.id

    clear_user_modes(context, user_id)
    context.user_data['creating_ticket'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🆘 **Поддержка**\n\n"
        "Вы попали в поддержку!\n"
        "Опишите вашу проблему и оно попадет модераторам\n\n"
        "📌 **Условия:**\n"
        "• Не короче 30 символов\n"
        "• Не больше 540 символов\n"
        "• Мы ответим вам в течение 24ч\n\n"
        "✏️ **Напишите ваше сообщение:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_create_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает создание тикета"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('creating_ticket', False):
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте текст!")
        return

    message_text = update.message.text.strip()

    # Проверка длины
    if len(message_text) < 30:
        await update.message.reply_text("❌ Сообщение должно быть не короче 30 символов!")
        return

    if len(message_text) > 540:
        await update.message.reply_text("❌ Сообщение должно быть не больше 540 символов!")
        return

    # Генерируем ID тикета
    global ticket_counter
    ticket_counter += 1
    ticket_id = str(ticket_counter).zfill(5)

    # Сохраняем тикет
    stats = get_user_stats(user_id)
    tickets_data[ticket_id] = {
        "id": ticket_id,
        "user_id": user_id,
        "user_number": stats["number"],
        "message": message_text,
        "status": "open",
        "created_at": asyncio.get_event_loop().time(),
        "admin_response": None
    }
    save_data()

    # Удаляем сообщение с инструкцией
    try:
        await update.message.delete()
    except:
        pass

    # Отправляем подтверждение
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ **Вы успешно подали тикет!**\n\n"
        f"🆔 **ID тикета:** `{ticket_id}`\n"
        f"📝 **Сообщение:** {message_text[:100]}...\n\n"
        f"⏳ Мы ответим вам в течение 24ч",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    # Отправляем уведомление админам
    keyboard_admin = [
        [InlineKeyboardButton("📋 Посмотреть", callback_data=f"view_ticket_{ticket_id}")],
        [InlineKeyboardButton("✅ Ответить", callback_data=f"answer_ticket_{ticket_id}")],
        [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_ticket_{ticket_id}")]
    ]
    reply_markup_admin = InlineKeyboardMarkup(keyboard_admin)

    admin_text = (
        f"🆘 **Новый тикет!**\n\n"
        f"🆔 **ID:** `{ticket_id}`\n"
        f"👤 **От пользователя:** ID #{stats['number']}\n"
        f"📝 **Сообщение:**\n{message_text}\n\n"
        f"⬇️ **Действия:**"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=reply_markup_admin,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"❌ Ошибка отправки админу: {e}")

    del context.user_data['creating_ticket']

async def admin_tickets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню тикетов"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("🔍 Найти тикет", callback_data="admin_find_ticket")],
        [InlineKeyboardButton("🗑️ Удалить тикет", callback_data="admin_delete_ticket")],
        [InlineKeyboardButton("💬 Ответить на тикет", callback_data="admin_answer_ticket")],
        [InlineKeyboardButton("📋 Список тикетов", callback_data="admin_list_tickets")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    open_tickets = sum(1 for t in tickets_data.values() if t["status"] == "open")
    closed_tickets = len(tickets_data) - open_tickets

    text = (
        "**🎫 Управление тикетами**\n\n"
        f"📊 **Статистика:**\n"
        f"• Открытых: {open_tickets}\n"
        f"• Закрытых: {closed_tickets}\n"
        f"• Всего: {len(tickets_data)}\n\n"
        f"⬇️ Выберите действие:"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def admin_find_ticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает поиск тикета"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['admin_finding_ticket'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🔍 **Найти тикет**\n\nВведите ID тикета (например: `00001`):"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_delete_ticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает удаление тикета"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['admin_deleting_ticket'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🗑️ **Удалить тикет**\n\nВведите ID тикета для удаления:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_answer_ticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает ответ на тикет"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['admin_answering_ticket'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "💬 **Ответить на тикет**\n\nВведите ID тикета (например: `00001`):"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список всех тикетов"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    if not tickets_data:
        text = "📋 **Список тикетов**\n\nНет тикетов"
    else:
        text = "📋 **Список тикетов**\n\n"
        for tid, ticket in list(tickets_data.items())[-10:]:  # последние 10
            status_emoji = "🟢" if ticket["status"] == "open" else "🔴"
            text += f"{status_emoji} `{tid}` | ID #{ticket['user_number']}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_admin_find_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает поиск тикета"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_finding_ticket', False):
        return

    if user_id != ADMIN_ID:
        return

    ticket_id = update.message.text.strip()

    if ticket_id not in tickets_data:
        await update.message.reply_text(f"❌ Тикет `{ticket_id}` не найден!", parse_mode="Markdown")
    else:
        ticket = tickets_data[ticket_id]
        status_emoji = "🟢 Открыт" if ticket["status"] == "open" else "🔴 Закрыт"
        text = (
            f"**🎫 Тикет #{ticket_id}**\n\n"
            f"👤 Пользователь: ID #{ticket['user_number']}\n"
            f"📊 Статус: {status_emoji}\n"
            f"📝 Сообщение:\n{ticket['message']}\n"
        )
        if ticket.get("admin_response"):
            text += f"\n💬 Ответ админа:\n{ticket['admin_response']}\n"
        await update.message.reply_text(text, parse_mode="Markdown")

    del context.user_data['admin_finding_ticket']
    keyboard = [[InlineKeyboardButton("🔙 В меню тикетов", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_admin_delete_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает удаление тикета"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_deleting_ticket', False):
        return

    if user_id != ADMIN_ID:
        return

    ticket_id = update.message.text.strip()

    if ticket_id not in tickets_data:
        await update.message.reply_text(f"❌ Тикет `{ticket_id}` не найден!", parse_mode="Markdown")
    else:
        del tickets_data[ticket_id]
        save_data()
        await update.message.reply_text(f"✅ Тикет `{ticket_id}` удалён!", parse_mode="Markdown")

    del context.user_data['admin_deleting_ticket']
    keyboard = [[InlineKeyboardButton("🔙 В меню тикетов", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_admin_answer_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод ID тикета для ответа"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_answering_ticket', False):
        return

    if user_id != ADMIN_ID:
        return

    ticket_id = update.message.text.strip()

    if ticket_id not in tickets_data:
        await update.message.reply_text(f"❌ Тикет `{ticket_id}` не найден!", parse_mode="Markdown")
        del context.user_data['admin_answering_ticket']
        return

    context.user_data['admin_answering_ticket_id'] = ticket_id
    context.user_data['admin_waiting_response'] = True

    await update.message.reply_text(f"💬 **Введите ответ для тикета {ticket_id}:**\n\nОтвет будет отправлен пользователю.", parse_mode="Markdown")


async def handle_admin_send_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отправку ответа пользователю"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_waiting_response', False):
        return

    if user_id != ADMIN_ID:
        return

    response = update.message.text.strip()
    ticket_id = context.user_data.get('admin_answering_ticket_id')

    if not ticket_id or ticket_id not in tickets_data:
        await update.message.reply_text("❌ Тикет не найден!")
        del context.user_data['admin_answering_ticket']
        del context.user_data['admin_waiting_response']
        del context.user_data['admin_answering_ticket_id']
        return

    ticket = tickets_data[ticket_id]
    ticket["status"] = "closed"
    ticket["admin_response"] = response
    save_data()

    # Отправляем ответ пользователю
    try:
        keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=ticket["user_id"],
            text=f"✅ **Ответ на ваш тикет #{ticket_id}**\n\n"
                 f"💬 **Ответ модератора:**\n{response}\n\n"
                 f"Спасибо за обращение!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except:
        pass

    await update.message.reply_text(f"✅ Ответ отправлен пользователю!\n\nТикет #{ticket_id} закрыт.", parse_mode="Markdown")

    del context.user_data['admin_answering_ticket']
    del context.user_data['admin_waiting_response']
    del context.user_data['admin_answering_ticket_id']

    keyboard = [[InlineKeyboardButton("🔙 В меню тикетов", callback_data="admin_tickets_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def view_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр тикета из уведомления"""
    query = update.callback_query
    user_id = query.from_user.id
    ticket_id = query.data.split("_")[2]

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    ticket = tickets_data.get(ticket_id)
    if not ticket:
        await query.answer("❌ Тикет не найден!", show_alert=True)
        return

    status_emoji = "🟢 Открыт" if ticket["status"] == "open" else "🔴 Закрыт"
    text = (
        f"**🎫 Тикет #{ticket_id}**\n\n"
        f"👤 Пользователь: ID #{ticket['user_number']}\n"
        f"📊 Статус: {status_emoji}\n"
        f"📝 Сообщение:\n{ticket['message']}\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Ответить", callback_data=f"answer_ticket_{ticket_id}")],
        [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_ticket_{ticket_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_tickets_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def promo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню промокодов"""
    query = update.callback_query
    user_id = query.from_user.id

    clear_user_modes(context, user_id)

    keyboard = [
        [InlineKeyboardButton("🎟️ Активировать промокод", callback_data="activate_promo")],
        [InlineKeyboardButton("✨ Создать промокод", callback_data="create_promo")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🎫 Промокоды**\n\n"
        "✨ **Создать промокод:**\n"
        "Вы можете создать свой промокод за монеты!\n"
        "Формат: `Название | кол-во использований | кол-во монет за использование`\n"
        "Пример: `Nushya | 10 | 100` - стоимость: 1000 монет\n\n"
        "🎟️ **Активировать промокод:**\n"
        "Введите код и получите награду!"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def create_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс создания промокода"""
    query = update.callback_query
    user_id = query.from_user.id

    context.user_data['creating_promo'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="promo")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**✨ Создание промокода**\n\n"
        "📌 **Формат:** `Название | кол-во использований | кол-во монет за использование`\n\n"
        "📌 **Пример:** `Nushya | 10 | 100`\n"
        "💰 **Стоимость:** кол-во использований × кол-во монет за использование\n"
        "В примере: 10 × 100 = 1000 монет\n\n"
        "✏️ **Введите данные:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_create_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает создание промокода"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('creating_promo', False):
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте текст!")
        return

    try:
        # Парсим ввод
        parts = update.message.text.split("|")
        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Неверный формат!\n\n"
                "Используйте: `Название | кол-во использований | кол-во монет`\n"
                "Пример: `Nushya | 10 | 100`",
                parse_mode="Markdown"
            )
            return

        code = parts[0].strip().upper()
        max_uses = int(parts[1].strip())
        reward = int(parts[2].strip())

        if max_uses <= 0 or reward <= 0:
            await update.message.reply_text("❌ Количество использований и награда должны быть больше 0!")
            return

        # Проверяем, не существует ли уже такой код
        if code in promo_data:
            await update.message.reply_text(f"❌ Промокод `{code}` уже существует!", parse_mode="Markdown")
            return

        # Рассчитываем стоимость
        cost = max_uses * reward

        # Проверяем баланс
        stats = get_user_stats(user_id)
        if stats["coins"] < cost:
            await update.message.reply_text(
                f"❌ Недостаточно монет!\n\n"
                f"💰 Стоимость: {cost} монет\n"
                f"💳 Ваш баланс: {stats['coins']} монет",
                parse_mode="Markdown"
            )
            return

        # Списываем монеты
        user_data[user_id]["coins"] -= cost
        save_data()

        # Сохраняем промокод
        promo_data[code] = {
            "creator_id": user_id,
            "creator_number": stats["number"],
            "uses": 0,
            "max_uses": max_uses,
            "reward": reward,
            "cost": cost,
            "used_by": []
        }

        # Сохраняем в историю созданных промокодов пользователя
        if str(user_id) not in user_promos:
            user_promos[str(user_id)] = []
        user_promos[str(user_id)].append({
            "code": code,
            "reward": reward,
            "max_uses": max_uses,
            "uses": 0
        })
        save_data()

        keyboard = [[InlineKeyboardButton("🔙 В меню промо", callback_data="promo")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ **Промокод создан!**\n\n"
            f"🎫 **Код:** `{code}`\n"
            f"📊 **Использований:** {max_uses}\n"
            f"🪙 **Награда:** {reward} монет\n"
            f"💰 **Потрачено:** {cost} монет\n\n"
            f"💳 **Новый баланс:** {user_data[user_id]['coins']} монет",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        del context.user_data['creating_promo']

    except ValueError:
        await update.message.reply_text("❌ Количество использований и награда должны быть числами!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def activate_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс активации промокода"""
    query = update.callback_query
    user_id = query.from_user.id

    context.user_data['activating_promo'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="promo")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**🎟️ Активация промокода**\n\n"
        "📌 **Инструкция:**\n"
        "Введите промокод, который хотите активировать.\n\n"
        "✏️ **Введите промокод:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_activate_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает активацию промокода"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('activating_promo', False):
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте промокод!")
        return

    code = update.message.text.strip().upper()

    # Проверяем существование промокода
    if code not in promo_data:
        await update.message.reply_text(f"❌ Промокод `{code}` не найден!", parse_mode="Markdown")
        return

    promo = promo_data[code]

    # Проверяем, не истек ли срок использований
    if promo["uses"] >= promo["max_uses"]:
        await update.message.reply_text(f"❌ Промокод `{code}` уже использован максимальное количество раз!",
                                        parse_mode="Markdown")
        return

    # Проверяем, не использовал ли пользователь уже этот промокод
    if str(user_id) in promo["used_by"]:
        await update.message.reply_text(f"❌ Вы уже использовали промокод `{code}`!", parse_mode="Markdown")
        return

    # ⭐ ВЫЧИСЛЯЕМ НАГРАДУ (поддержка разных типов)
    reward_type = promo.get("reward_type", "positive")

    if reward_type == "range":
        # Случайная награда в диапазоне
        reward_min = promo.get("reward_min", 1)
        reward_max = promo.get("reward_max", 10)
        reward = random.randint(reward_min, reward_max)
        reward_text = f"{reward} монет (случайная от {reward_min} до {reward_max})"
    elif reward_type == "negative":
        # Отрицательная награда (забирает монеты)
        reward = promo.get("reward_value", 0)
        reward_text = f"забрано {abs(reward)} монет"
    else:
        # Положительная награда
        reward = promo.get("reward_value", 0)
        reward_text = f"{reward} монет"

    # Проверяем, хватает ли монет если награда отрицательная
    stats = get_user_stats(user_id)
    if reward < 0 and stats["coins"] < abs(reward):
        await update.message.reply_text(
            f"❌ У вас недостаточно монет!\n\n"
            f"💰 Ваш баланс: {stats['coins']} монет\n"
            f"⚠️ Промокод забирает {abs(reward)} монет",
            parse_mode="Markdown"
        )
        return

    # Начисляем/забираем монеты
    user_data[user_id]["coins"] += reward
    save_data()

    # Обновляем данные промокода
    promo["uses"] += 1
    promo["used_by"].append(str(user_id))
    save_data()

    keyboard = [[InlineKeyboardButton("🔙 В меню промо", callback_data="promo")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reactions = ["🎉", "🔥", "⭐", "💎", "🎊", "✨", "🏆", "💰"]
    reaction = random.choice(reactions)

    if reward >= 0:
        await update.message.reply_text(
            f"{reaction} **Промокод активирован!** {reaction}\n\n"
            f"🎫 **Код:** `{code}`\n"
            f"🪙 **Вы получили:** +{reward_text}\n"
            f"💳 **Новый баланс:** {user_data[user_id]['coins']} монет\n\n"
            f"👤 **Создатель:** {promo['creator_number']}\n"
            f"📊 **Осталось использований:** {promo['max_uses'] - promo['uses']}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"⚠️ **Промокод активирован!** ⚠️\n\n"
            f"🎫 **Код:** `{code}`\n"
            f"🪙 **У вас забрали:** {reward_text}\n"
            f"💳 **Новый баланс:** {user_data[user_id]['coins']} монет\n\n"
            f"👤 **Создатель:** {promo['creator_number']}\n"
            f"📊 **Осталось использований:** {promo['max_uses'] - promo['uses']}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    # Уведомляем создателя промокода (если не админ)
    if promo['creator_number'] != "ADMIN":
        try:
            await context.bot.send_message(
                promo["creator_id"],
                f"🎫 **Ваш промокод `{code}` активировали!**\n\n"
                f"👤 Активировал: ID #{stats['number']}\n"
                f"📊 Осталось использований: {promo['max_uses'] - promo['uses']}",
                parse_mode="Markdown"
            )
        except:
            pass

    del context.user_data['activating_promo']


async def admin_promo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ меню для управления промокодами"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("➕ Создать промокод", callback_data="admin_create_promo")],
        [InlineKeyboardButton("🗑️ Удалить промокод", callback_data="admin_delete_promo")],
        [InlineKeyboardButton("📋 Список промокодов", callback_data="admin_list_promos")],
        [InlineKeyboardButton("👥 Промокоды юзеров", callback_data="admin_user_promos")],
        [InlineKeyboardButton("🏆 Топ промокодов", callback_data="admin_top_promos")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "**🎫 Управление промокодами**\n\nВыберите действие:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_create_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ создаёт промокод (бесплатно)"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['admin_creating_promo'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**➕ Создание промокода (Админ)**\n\n"
        "📌 **Формат:** `Название | кол-во использований | награда`\n\n"
        "📌 **Награда может быть:**\n"
        "• `10` - фиксированная награда (10 монет)\n"
        "• `-5` - забирает 5 монет\n"
        "• `1-20` - случайная награда от 1 до 20 монет\n\n"
        "📌 **Примеры:**\n"
        "`WELCOME | 100 | 50` - 50 монет, 100 использований\n"
        "`PENALTY | 10 | -5` - забирает 5 монет, 10 использований\n"
        "`LUCKY | 50 | 1-100` - случайно от 1 до 100 монет\n\n"
        "💰 **Стоимость для админа:** 0 монет (бесплатно)\n\n"
        "✏️ **Введите данные:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_admin_create_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает создание промокода админом (бесплатно)"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_creating_promo', False):
        return

    if user_id != ADMIN_ID:
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте текст!")
        return

    try:
        parts = update.message.text.split("|")
        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Неверный формат!\n\n"
                "Используйте: `Название | кол-во использований | награда`\n"
                "Примеры:\n"
                "`WELCOME | 100 | 50`\n"
                "`PENALTY | 10 | -5`\n"
                "`LUCKY | 50 | 1-100`\n"
                "`MIX | 10 | -100-100`",
                parse_mode="Markdown"
            )
            return

        code = parts[0].strip().upper()
        max_uses = int(parts[1].strip())
        reward_str = parts[2].strip()

        if max_uses <= 0:
            await update.message.reply_text("❌ Количество использований должно быть больше 0!")
            return

        # ⭐ ПАРСИМ НАГРАДУ (поддержка -100-100)
        reward_type = "positive"
        reward_value = 0
        reward_min = 0
        reward_max = 0

        if "-" in reward_str:
            # Проверяем, является ли это отрицательным числом или диапазоном
            if reward_str.startswith("-") and reward_str.count("-") == 1:
                # Отрицательное число (например: -5)
                try:
                    reward_value = int(reward_str)
                    reward_type = "negative"
                except:
                    await update.message.reply_text("❌ Неверный формат награды!")
                    return
            elif reward_str.count("-") == 1 and not reward_str.startswith("-"):
                # Положительный диапазон (например: 1-20)
                range_parts = reward_str.split("-")
                if len(range_parts) == 2:
                    try:
                        reward_min = int(range_parts[0])
                        reward_max = int(range_parts[1])
                        reward_type = "range"
                        reward_value = f"{reward_min}-{reward_max}"
                    except:
                        await update.message.reply_text("❌ Неверный формат диапазона! Пример: `1-20`")
                        return
                else:
                    await update.message.reply_text("❌ Неверный формат диапазона! Пример: `1-20`")
                    return
            elif reward_str.count("-") == 2:
                # Отрицательный диапазон (например: -100-100)
                range_parts = reward_str.split("-")
                if len(range_parts) == 3:
                    try:
                        reward_min = int(f"-{range_parts[1]}")
                        reward_max = int(range_parts[2])
                        reward_type = "range"
                        reward_value = f"{reward_min}-{reward_max}"
                    except:
                        await update.message.reply_text("❌ Неверный формат диапазона! Пример: `-100-100`")
                        return
                else:
                    await update.message.reply_text("❌ Неверный формат диапазона! Пример: `-100-100`")
                    return
            else:
                await update.message.reply_text("❌ Неверный формат награды!")
                return
        else:
            # Положительное число
            try:
                reward_value = int(reward_str)
                reward_type = "positive"
            except:
                await update.message.reply_text("❌ Неверный формат награды!")
                return

        # Проверяем, не существует ли уже такой код
        if code in promo_data:
            await update.message.reply_text(f"❌ Промокод `{code}` уже существует!", parse_mode="Markdown")
            return

        # Сохраняем промокод
        promo_data[code] = {
            "creator_id": user_id,
            "creator_number": "ADMIN",
            "uses": 0,
            "max_uses": max_uses,
            "reward_type": reward_type,
            "reward_value": reward_value,
            "reward_min": reward_min,
            "reward_max": reward_max,
            "cost": 0,
            "used_by": []
        }
        save_data()

        # Формируем текст награды для отображения
        if reward_type == "range":
            reward_text = f"случайная ({reward_min}-{reward_max}) монет"
        elif reward_type == "negative":
            reward_text = f"забирает {abs(reward_value)} монет"
        else:
            reward_text = f"{reward_value} монет"

        keyboard = [[InlineKeyboardButton("🔙 В меню промо", callback_data="admin_promo_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ **Промокод создан админом!**\n\n"
            f"🎫 **Код:** `{code}`\n"
            f"📊 **Использований:** {max_uses}\n"
            f"🪙 **Награда:** {reward_text}\n"
            f"💰 **Стоимость:** 0 монет (бесплатно для админа)",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        del context.user_data['admin_creating_promo']

    except ValueError:
        await update.message.reply_text("❌ Количество использований должно быть числом!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def admin_delete_promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс удаления промокода"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['admin_deleting_promo'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🗑️ **Удаление промокода**\n\nВведите название промокода для удаления:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")



async def admin_list_promos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список всех промокодов"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    if not promo_data:
        text = "📋 **Список промокодов**\n\nНет активных промокодов"
    else:
        text = "📋 **Список промокодов**\n\n"
        for code, promo in promo_data.items():
            reward_type = promo.get("reward_type", "positive")
            if reward_type == "range":
                reward_text = f"случайная ({promo['reward_min']}-{promo['reward_max']})"
            elif reward_type == "negative":
                reward_text = f"забирает {abs(promo['reward_value'])}"
            else:
                reward_text = f"{promo['reward_value']}"

            text += (
                f"🎫 `{code}`\n"
                f"   👤 Создатель: {promo['creator_number']}\n"
                f"   📊 {promo['uses']}/{promo['max_uses']} | 🪙 {reward_text}\n\n"
            )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_admin_delete_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет промокод"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('admin_deleting_promo', False):
        return

    if user_id != ADMIN_ID:
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте название промокода!")
        return

    code = update.message.text.strip().upper()

    if code not in promo_data:
        await update.message.reply_text(f"❌ Промокод `{code}` не найден!", parse_mode="Markdown")
        return

    del promo_data[code]
    save_data()

    keyboard = [[InlineKeyboardButton("🔙 В меню промо", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"✅ Промокод `{code}` удалён!", reply_markup=reply_markup, parse_mode="Markdown")

    del context.user_data['admin_deleting_promo']


async def admin_user_promos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает промокоды созданные пользователями"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    user_promos_list = []
    for uid, promos in user_promos.items():
        for promo in promos:
            user_promos_list.append((uid, promo))

    if not user_promos_list:
        text = "👥 **Промокоды юзеров**\n\nНет созданных пользователями промокодов"
    else:
        text = "👥 **Промокоды юзеров**\n\n"
        for uid, promo in user_promos_list:
            text += (
                f"👤 ID #{user_data[int(uid)]['number']}\n"
                f"   🎫 `{promo['code']}`\n"
                f"   📊 {promo['uses']}/{promo['max_uses']} | 🪙 {promo['reward']}\n\n"
            )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_top_promos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Топ 10 самых используемых промокодов"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    promo_list = [(code, promo["uses"]) for code, promo in promo_data.items()]
    promo_list.sort(key=lambda x: x[1], reverse=True)
    top = promo_list[:10]

    if not top:
        text = "🏆 **Топ промокодов**\n\nНет данных"
    else:
        text = "🏆 **Топ 10 самых используемых промокодов**\n\n"
        for i, (code, uses) in enumerate(top, 1):
            text += f"{i}. `{code}` — {uses} использований\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_promo_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def suggest_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню предложения видео"""
    query = update.callback_query
    user_id = query.from_user.id

    # ⭐ ОЧИЩАЕМ РЕЖИМЫ ПЕРЕД НОВЫМ
    clear_user_modes(context, user_id)

    context.user_data['suggesting_video'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "💬 **Предложить видео**\n\n"
        "Здесь вы можете предложить свое видео.\n"
        "Видео проходит проверку модераторами!\n\n"
        "📌 **Условия:**\n"
        "• Не короче 10 секунд\n"
        "• За каждое принятое видео вы получите +6 🪙\n\n"
        "📤 **Отправьте ваше видео в чат:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_suggest_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает предложенное видео от пользователя"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('suggesting_video', False):
        return

    # Проверяем, что прислали видео
    if not update.message.video and not update.message.video_note:
        await update.message.reply_text("❌ Отправьте видео или кружок!")
        return

    # Проверка длительности для обычного видео
    if update.message.video:
        duration = update.message.video.duration
        if duration < 10:
            await update.message.reply_text("❌ Видео должно быть не короче 10 секунд!")
            return
        file_id = update.message.video.file_id
        file_type = "video"
    else:
        # Для кружка
        duration = update.message.video_note.duration
        if duration < 10:
            await update.message.reply_text("❌ Кружок должен быть не короче 10 секунд!")
            return
        file_id = update.message.video_note.file_id
        file_type = "video_note"

    # Генерируем ID предложения
    suggestion_id = str(len(suggestions_data) + 1).zfill(4)

    # Сохраняем предложение
    suggestions_data[suggestion_id] = {
        "id": suggestion_id,
        "user_id": user_id,
        "user_number": user_data[user_id]["number"],
        "file_id": file_id,
        "type": file_type,
        "duration": duration,
        "status": "pending"  # pending, approved, rejected
    }
    save_data()

    # Отправляем подтверждение пользователю с кнопкой главного меню
    try:
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ **Успешно!**\n\n"
            "🔍 Видео отправлено на проверку модераторам.\n"
            "⌛️ Вам ответят в течение 24ч\n"
            "🕘 Если видео примут вы получите +6 🪙",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except:
        pass

    # Выходим из режима предложения
    if 'suggesting_video' in context.user_data:
        del context.user_data['suggesting_video']
    # Отправляем уведомление админам
    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"approve_suggest_{suggestion_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_suggest_{suggestion_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"📹 **Новое предложение видео!**\n\n"
        f"🆔 ID: `{suggestion_id}`\n"
        f"👤 От пользователя: ID #{user_data[user_id]['number']}\n"
        f"🎬 Тип: {'Видео' if file_type == 'video' else 'Кружок'}\n"
        f"⏱ Длительность: {duration} сек\n\n"
        f"⬇️ **Действия:**"
    )

    # Отправляем видео админу
    try:
        if file_type == "video":
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=file_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_video_note(chat_id=ADMIN_ID, video_note=file_id)
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"❌ Ошибка отправки админу: {e}")

    # Выходим из режима предложения
    del context.user_data['suggesting_video']


async def add_favorite_by_id_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс добавления видео в избранное по ID"""
    query = update.callback_query
    user_id = query.from_user.id

    context.user_data['adding_favorite_by_id'] = True

    keyboard = [[InlineKeyboardButton("🔙 Отмена", callback_data="favorites")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "➕ **Добавление видео в избранное по ID**\n\n"
        "📌 **Условие:**\n"
        "• Вы можете добавить только те видео, которые уже получили (просмотрели)\n\n"
        "📌 **Инструкция:**\n"
        "1. Введите ID видео (например: `001`, `042`, `128`)\n"
        "2. Если вы уже получали это видео - оно добавится в избранное\n\n"
        "✏️ **Введите ID видео:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_add_favorite_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод ID видео и добавляет в избранное (только если видео получено)"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('adding_favorite_by_id', False):
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте текст с ID видео!")
        return

    video_id = update.message.text.strip()

    # Проверяем существование видео в базе
    if video_id not in videos_data:
        await update.message.reply_text(
            f"❌ Видео с ID `{video_id}` не найдено в базе!\n\nПроверьте ID и попробуйте снова.", parse_mode="Markdown")
        # Выходим из режима добавления
        del context.user_data['adding_favorite_by_id']
        return

    # ⭐ ПРОВЕРЯЕМ: получал ли пользователь это видео
    stats = get_user_stats(user_id)
    watched_videos = stats.get("watched_videos", [])

    if video_id not in watched_videos:
        await update.message.reply_text(
            f"❌ Вы не можете добавить видео `{video_id}` в избранное!\n\n"
            f"📌 **Условие:** Добавлять можно только те видео, которые вы уже получили.\n\n"
            f"💡 Получите это видео через кнопку «🎬 Видео» в главном меню, а затем добавьте в избранное.",
            parse_mode="Markdown"
        )
        # Выходим из режима добавления
        del context.user_data['adding_favorite_by_id']
        return

    # Добавляем в избранное
    if "favorites" not in stats:
        stats["favorites"] = []

    if video_id in stats["favorites"]:
        await update.message.reply_text(f"❌ Видео `{video_id}` уже в избранном!", parse_mode="Markdown")
    else:
        stats["favorites"].append(video_id)
        save_data()
        await update.message.reply_text(
            f"✅ Видео `{video_id}` добавлено в избранное!\n\n"
            f"📹 Вы получили это видео ранее и теперь оно в вашей коллекции.",
            parse_mode="Markdown"
        )

    # Выходим из режима добавления
    del context.user_data['adding_favorite_by_id']

    # Показываем избранное
    favorites = stats.get("favorites", [])
    if favorites:
        keyboard = []
        for fav_id in favorites:
            if fav_id in videos_data:
                keyboard.append([InlineKeyboardButton(f"🎬 Видео {fav_id}", callback_data=f"watch_favorite_{fav_id}")])
        keyboard.append([InlineKeyboardButton("➕ Добавить по ID", callback_data="add_favorite_by_id")])
        keyboard.append([InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"⭐ **Избранное**\n\n📚 Всего видео: {len(favorites)}\n\n⬇️ Выберите видео для просмотра:"
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        keyboard = [
            [InlineKeyboardButton("➕ Добавить по ID", callback_data="add_favorite_by_id")],
            [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⭐ **Избранное**\n\nПока пусто", reply_markup=reply_markup,
                                        parse_mode="Markdown")


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает избранное пользователя"""
    query = update.callback_query
    user_id = query.from_user.id

    # ⭐ ОЧИЩАЕМ РЕЖИМЫ
    clear_user_modes(context, user_id)

    stats = get_user_stats(user_id)
    favorites = stats.get("favorites", [])

    if not favorites:
        text = "⭐ **Избранное**\n\n📭 У вас пока нет избранных видео\n\n💡 Добавить видео можно:\n• Через кнопку «➕ Добавить по ID» (только те видео, которые вы уже получили)\n• Или под видео при просмотре"
        keyboard = [
            [InlineKeyboardButton("➕ Добавить по ID", callback_data="add_favorite_by_id")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Добавить по ID", callback_data="add_favorite_by_id")]
    ]

    for video_id in favorites:
        if video_id in videos_data:
            keyboard.append([InlineKeyboardButton(f"🎬 Видео {video_id}", callback_data=f"watch_favorite_{video_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"⭐ **Избранное**\n\n📚 Всего видео: {len(favorites)}\n\n⬇️ Выберите видео для просмотра:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def add_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет видео в избранное"""
    query = update.callback_query
    user_id = query.from_user.id
    video_id = query.data.split("_")[2]

    stats = get_user_stats(user_id)
    if "favorites" not in stats:
        stats["favorites"] = []

    if video_id in stats["favorites"]:
        await query.answer("❌ Видео уже в избранном!", show_alert=True)
        return

    stats["favorites"].append(video_id)
    save_data()

    await query.answer("✅ Добавлено в избранное!", show_alert=False)

    video = videos_data[video_id]
    video_stats = get_video_stats(video_id)

    keyboard = [
        [
            InlineKeyboardButton(f"👍 {video_stats['likes']}", callback_data=f"like_{video_id}_like"),
            InlineKeyboardButton(f"👎 {video_stats['dislikes']}", callback_data=f"like_{video_id}_dislike")
        ],
        [
            InlineKeyboardButton("❌ Из избранного", callback_data=f"fav_remove_{video_id}"),
            InlineKeyboardButton("🎬 Ещё видео", callback_data="watch_video")
        ],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    except:
        pass


async def remove_from_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет видео из избранного"""
    query = update.callback_query
    user_id = query.from_user.id
    video_id = query.data.split("_")[2]

    stats = get_user_stats(user_id)
    if "favorites" not in stats:
        stats["favorites"] = []

    if video_id in stats["favorites"]:
        stats["favorites"].remove(video_id)
        save_data()
        await query.answer("❌ Удалено из избранного!", show_alert=False)
    else:
        await query.answer("❌ Видео не в избранном!", show_alert=True)
        return

    video = videos_data[video_id]
    video_stats = get_video_stats(video_id)

    keyboard = [
        [
            InlineKeyboardButton(f"👍 {video_stats['likes']}", callback_data=f"like_{video_id}_like"),
            InlineKeyboardButton(f"👎 {video_stats['dislikes']}", callback_data=f"like_{video_id}_dislike")
        ],
        [
            InlineKeyboardButton("⭐ В избранное", callback_data=f"fav_add_{video_id}"),
            InlineKeyboardButton("🎬 Ещё видео", callback_data="watch_video")
        ],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    except:
        pass


async def watch_favorite_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр видео из избранного (бесплатно)"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    video_id = query.data.split("_")[2]

    if user_data.get(user_id, {}).get("banned", False):
        await query.answer("❌ Вы забанены!", show_alert=True)
        return

    video = videos_data.get(video_id)
    if not video:
        await query.answer("❌ Видео не найдено!", show_alert=True)
        return

    video_stats = get_video_stats(video_id)
    stats = get_user_stats(user_id)

    is_fav = video_id in stats.get("favorites", [])
    fav_button = "⭐ В избранное" if not is_fav else "❌ Из избранного"
    fav_callback = f"fav_add_{video_id}" if not is_fav else f"fav_remove_{video_id}"

    keyboard = [
        [
            InlineKeyboardButton(f"👍 {video_stats['likes']}", callback_data=f"like_{video_id}_like"),
            InlineKeyboardButton(f"👎 {video_stats['dislikes']}", callback_data=f"like_{video_id}_dislike")
        ],
        [
            InlineKeyboardButton(fav_button, callback_data=fav_callback),
            InlineKeyboardButton("🎬 Ещё видео", callback_data="watch_video")
        ],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"🎬 **Видео #{video_id}**"

    try:
        await query.message.delete()
    except:
        pass

    try:
        if video["type"] == "video":
            await context.bot.send_video(
                chat_id=user_id,
                video=video["file_id"],
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_video_note(chat_id=user_id, video_note=video["file_id"])
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"❌ Ошибка отправки видео: {e}")


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("🪙 Монеты", callback_data="admin_coins")],
        [InlineKeyboardButton("🎬 Видео", callback_data="admin_videos")],
        [InlineKeyboardButton("👥 Юзеры", callback_data="admin_users")],
        [InlineKeyboardButton("🎫 Промокоды", callback_data="admin_promo_menu")],
        [InlineKeyboardButton("💬 Предложки", callback_data="admin_suggestions")],
        [InlineKeyboardButton("🎫 Тикеты", callback_data="admin_tickets_menu")],
        [InlineKeyboardButton("📢 Оповещения", callback_data="admin_notifications_menu")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "**👑 Админ панель**\n\nВыберите раздел:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def admin_notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню оповещений"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("📝 Создать оповещение", callback_data="admin_create_notification")],
        [InlineKeyboardButton("🗑️ Удалить оповещение", callback_data="admin_delete_notification")],
        [InlineKeyboardButton("📋 Список оповещений", callback_data="admin_list_notifications")],
        [InlineKeyboardButton("🔍 Найти оповещение", callback_data="admin_find_notification")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total = len(notifications_data)
    text = (
        "**📢 Управление оповещениями**\n\n"
        f"📊 **Всего оповещений:** {total}\n\n"
        f"⬇️ Выберите действие:"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_create_notification_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает создание оповещения"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['creating_notification'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**📝 Создание оповещения**\n\n"
        "📌 **Инструкция:**\n"
        "• Напишите текст оповещения\n"
        "• Текст может содержать эмодзи и Markdown\n"
        "• Оповещение получит уникальный ID\n\n"
        "✏️ **Введите текст оповещения:**"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_create_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает создание оповещения и рассылает всем"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('creating_notification', False):
        return

    if user_id != ADMIN_ID:
        return

    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Отправьте текст!")
        return

    notification_text = update.message.text.strip()

    # Генерируем ID оповещения
    global notification_counter
    notification_counter += 1
    notification_id = str(notification_counter).zfill(5)

    # Сохраняем оповещение
    notifications_data[notification_id] = {
        "id": notification_id,
        "text": notification_text,
        "created_at": asyncio.get_event_loop().time(),
        "created_by": user_id
    }
    save_data()

    # Отправляем подтверждение админу
    await update.message.reply_text(
        f"✅ **Оповещение создано!**\n\n"
        f"🆔 **ID:** `{notification_id}`\n"
        f"📝 **Текст:**\n{notification_text}\n\n"
        f"📤 Начинаю рассылку...",
        parse_mode="Markdown"
    )

    # Рассылаем всем пользователям (БЕЗ КНОПОК)
    sent_count = 0
    failed_count = 0

    for uid in user_data.keys():
        try:
            # ⭐ ОТПРАВЛЯЕМ ТОЛЬКО ТЕКСТ, БЕЗ КНОПОК
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 **Оповещение**\n\n{notification_text}",
                parse_mode="Markdown"
            )
            sent_count += 1
            await asyncio.sleep(0.05)  # Небольшая задержка, чтобы не забанили
        except Exception as e:
            failed_count += 1
            print(f"❌ Не удалось отправить пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"📤 Отправлено: {sent_count}\n"
        f"❌ Не доставлено: {failed_count}\n"
        f"👥 Всего пользователей: {len(user_data)}",
        parse_mode="Markdown"
    )

    keyboard = [[InlineKeyboardButton("🔙 В меню оповещений", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)

    del context.user_data['creating_notification']

async def admin_delete_notification_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает удаление оповещения"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['deleting_notification'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🗑️ **Удаление оповещения**\n\nВведите ID оповещения для удаления:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_delete_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет оповещение"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('deleting_notification', False):
        return

    if user_id != ADMIN_ID:
        return

    notification_id = update.message.text.strip()

    if notification_id not in notifications_data:
        await update.message.reply_text(f"❌ Оповещение `{notification_id}` не найдено!", parse_mode="Markdown")
    else:
        del notifications_data[notification_id]
        save_data()
        await update.message.reply_text(f"✅ Оповещение `{notification_id}` удалено!", parse_mode="Markdown")

    del context.user_data['deleting_notification']
    keyboard = [[InlineKeyboardButton("🔙 В меню оповещений", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def admin_list_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список всех оповещений (от новых к старым)"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    if not notifications_data:
        text = "📋 **Список оповещений**\n\nНет оповещений"
    else:
        # Сортируем по ID (от новых к старым)
        sorted_notifications = sorted(notifications_data.items(), key=lambda x: int(x[0]), reverse=True)

        text = "📋 **Список оповещений (от новых к старым)**\n\n"
        for nid, notif in sorted_notifications[:20]:  # Показываем последние 20
            preview = notif["text"][:35] + "..." if len(notif["text"]) > 35 else notif["text"]
            text += f"`{nid}` | {preview}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_find_notification_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает поиск оповещения"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['finding_notification'] = True

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🔍 **Найти оповещение**\n\nВведите ID оповещения:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_find_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Находит и показывает оповещение"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('finding_notification', False):
        return

    if user_id != ADMIN_ID:
        return

    notification_id = update.message.text.strip()

    if notification_id not in notifications_data:
        await update.message.reply_text(f"❌ Оповещение `{notification_id}` не найдено!", parse_mode="Markdown")
    else:
        notif = notifications_data[notification_id]

        text = (
            f"**📢 Найдено оповещение**\n\n"
            f"🆔 **ID:** `{notification_id}`\n"
            f"📝 **Текст:**\n{notif['text']}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    del context.user_data['finding_notification']
    keyboard = [[InlineKeyboardButton("🔙 В меню оповещений", callback_data="admin_notifications_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def admin_suggestions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню предложок"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    pending = {k: v for k, v in suggestions_data.items() if v["status"] == "pending"}

    if not pending:
        text = "💬 **Предложки**\n\n📭 Нет новых предложений"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    keyboard = []
    for sug_id, sug in pending.items():
        keyboard.append([InlineKeyboardButton(f"📹 Предложение #{sug_id} от ID #{sug['user_number']}",
                                              callback_data=f"view_suggest_{sug_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"💬 **Предложки**\n\n📚 Всего новых: {len(pending)}\n\n⬇️ Выберите предложение:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def view_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает конкретное предложение"""
    query = update.callback_query
    user_id = query.from_user.id
    suggestion_id = query.data.split("_")[2]

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    sug = suggestions_data.get(suggestion_id)
    if not sug:
        await query.answer("❌ Предложение не найдено!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"approve_suggest_{suggestion_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_suggest_{suggestion_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_suggestions")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"📹 **Предложение #{suggestion_id}**\n\n"
        f"👤 От пользователя: ID #{sug['user_number']}\n"
        f"🎬 Тип: {'Видео' if sug['type'] == 'video' else 'Кружок'}\n"
        f"⏱ Длительность: {sug['duration']} сек\n\n"
        f"⬇️ **Действия:**"
    )

    # ⭐ УДАЛЯЕМ СООБЩЕНИЕ СО СПИСКОМ ПРЕДЛОЖЕНИЙ
    try:
        await query.message.delete()
    except:
        pass

    # Отправляем видео с кнопками
    try:
        if sug["type"] == "video":
            await context.bot.send_video(
                chat_id=user_id,
                video=sug["file_id"],
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_video_note(chat_id=user_id, video_note=sug["file_id"])
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")


async def approve_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает предложение и добавляет видео в базу"""
    query = update.callback_query
    admin_id = query.from_user.id
    suggestion_id = query.data.split("_")[2]

    if admin_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    sug = suggestions_data.get(suggestion_id)
    if not sug:
        await query.answer("❌ Предложение не найдено!", show_alert=True)
        return

    # Генерируем ID для нового видео
    video_id = get_next_video_number()

    # Добавляем видео в базу
    videos_data[video_id] = {
        "id": video_id,
        "file_id": sug["file_id"],
        "type": sug["type"],
        "cost": 1
    }
    init_video_likes(video_id)

    # Обновляем статус предложения
    sug["status"] = "approved"
    sug["video_id"] = video_id
    save_data()

    # Начисляем монеты пользователю
    user_id = sug["user_id"]
    if user_id in user_data:
        user_data[user_id]["coins"] += 6
        save_data()

        # Уведомляем пользователя
        try:
            await context.bot.send_message(
                user_id,
                f"✅ **Ваше видео принято!**\n\n"
                f"📹 Видео #{video_id} добавлено в коллекцию\n"
                f"🪙 Вы получили +6 монет!\n"
                f"💰 Ваш баланс: {user_data[user_id]['coins']} монет",
                parse_mode="Markdown"
            )
        except:
            pass

    # ⭐ УДАЛЯЕМ ВСЁ СООБЩЕНИЕ С ВИДЕО И КНОПКАМИ
    try:
        await query.message.delete()
    except:
        pass

    await query.answer("✅ Видео принято!", show_alert=False)

    # Отправляем новое сообщение о результате
    await context.bot.send_message(
        chat_id=admin_id,
        text=f"✅ Видео #{suggestion_id} принято!\n\nДобавлено как #{video_id}",
        parse_mode="Markdown"
    )

    # Возвращаемся в меню предложок
    await admin_suggestions_menu(update, context)


async def reject_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклоняет предложение"""
    query = update.callback_query
    admin_id = query.from_user.id
    suggestion_id = query.data.split("_")[2]

    if admin_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    sug = suggestions_data.get(suggestion_id)
    if not sug:
        await query.answer("❌ Предложение не найдено!", show_alert=True)
        return

    # Обновляем статус предложения
    sug["status"] = "rejected"
    save_data()

    # Уведомляем пользователя
    user_id = sug["user_id"]
    try:
        await context.bot.send_message(
            user_id,
            f"❌ **Ваше видео отклонено**\n\n"
            f"К сожалению, ваше видео не прошло модерацию.\n"
            f"Вы можете предложить другое видео!",
            parse_mode="Markdown"
        )
    except:
        pass

    # ⭐ УДАЛЯЕМ ВСЁ СООБЩЕНИЕ С ВИДЕО И КНОПКАМИ
    try:
        await query.message.delete()
    except:
        pass

    await query.answer("❌ Видео отклонено!", show_alert=False)

    # Отправляем новое сообщение о результате
    await context.bot.send_message(
        chat_id=admin_id,
        text=f"❌ Предложение #{suggestion_id} отклонено",
        parse_mode="Markdown"
    )

    # Возвращаемся в меню предложок
    await admin_suggestions_menu(update, context)


async def reject_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклоняет предложение"""
    query = update.callback_query
    admin_id = query.from_user.id
    suggestion_id = query.data.split("_")[2]

    if admin_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    sug = suggestions_data.get(suggestion_id)
    if not sug:
        await query.answer("❌ Предложение не найдено!", show_alert=True)
        return

    # Обновляем статус предложения
    sug["status"] = "rejected"
    save_data()

    # Уведомляем пользователя
    user_id = sug["user_id"]
    try:
        await context.bot.send_message(
            user_id,
            f"❌ **Ваше видео отклонено**\n\n"
            f"К сожалению, ваше видео не прошло модерацию.\n"
            f"Вы можете предложить другое видео!",
            parse_mode="Markdown"
        )
    except:
        pass

    # ⭐ УДАЛЯЕМ ВСЁ СООБЩЕНИЕ С ВИДЕО И КНОПКАМИ
    try:
        await query.message.delete()
    except:
        pass

    await query.answer("❌ Видео отклонено!", show_alert=False)

    # Отправляем новое сообщение о результате
    await context.bot.send_message(
        chat_id=admin_id,
        text=f"❌ Предложение #{suggestion_id} отклонено",
        parse_mode="Markdown"
    )

    # Возвращаемся в меню предложок
    await admin_suggestions_menu(update, context)



async def admin_coins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("➕ Выдать монеты", callback_data="coins_give")],
        [InlineKeyboardButton("➖ Забрать монеты", callback_data="coins_take")],
        [InlineKeyboardButton("🔄 Ресетнуть монеты", callback_data="coins_reset")],
        [InlineKeyboardButton("⬆️ Выдать ДО", callback_data="coins_give_until")],
        [InlineKeyboardButton("⬇️ Забрать ДО", callback_data="coins_take_until")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "**🪙 Управление монетами**\n\nВыберите действие:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_videos_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("📤 Загрузить видео", callback_data="add_video_from_channel")],
        [InlineKeyboardButton("🗑️ Удалить видео", callback_data="video_delete")],
        [InlineKeyboardButton("🔍 Найти видео", callback_data="video_find")],
        [InlineKeyboardButton("🏆 Топ видео (по лайкам)", callback_data="video_top")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "**🎬 Управление видео**\n\nВыберите действие:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("🏆 Топ юзеров (по монетам)", callback_data="users_top_coins")],
        [InlineKeyboardButton("🏆 Топ юзеров (по просмотрам)", callback_data="users_top_views")],
        [InlineKeyboardButton("🚫 Забанить юзера", callback_data="user_ban")],
        [InlineKeyboardButton("✅ Разбанить юзера", callback_data="user_unban")],
        [InlineKeyboardButton("🔍 Найти юзера", callback_data="user_find")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "**👥 Управление юзерами**\n\nВыберите действие:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    total_videos = len(videos_data)
    total_users = len(user_data)
    total_views = sum(u.get("videos_watched", 0) for u in user_data.values())
    banned_users = sum(1 for u in user_data.values() if u.get("banned", False))
    unbanned_users = total_users - banned_users
    total_coins = sum(u.get("coins", 0) for u in user_data.values())

    text = (
        "**📊 Статистика**\n\n"
        f"🎬 **Всего видео:** {total_videos}\n"
        f"👥 **Всего юзеров:** {total_users}\n"
        f"📹 **Всего просмотров:** {total_views}\n"
        f"🚫 **Забаненых:** {banned_users}\n"
        f"✅ **Разбаненых:** {unbanned_users}\n"
        f"🪙 **Монет всего:** {total_coins}\n"
    )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def coins_give_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_coin_state[user_id] = {"action": "give"}
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_coins")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "💰 **Выдать монеты**\n\nОтправьте: `айди количество`\nПример: `8251687795 100` или `1 50`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def coins_take_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_coin_state[user_id] = {"action": "take"}
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_coins")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "💰 **Забрать монеты**\n\nОтправьте: `айди количество`\nПример: `8251687795 50`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def coins_reset_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_coin_state[user_id] = {"action": "reset"}
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_coins")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🔄 **Ресетнуть монеты**\n\nОтправьте `айди`\nПример: `8251687795` или `1`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def coins_give_until_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_coin_state[user_id] = {"action": "give_until"}
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_coins")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "⬆️ **Выдать ДО**\n\nОтправьте: `айди целевое_количество`\nПример: `1 100` (выдаст до 100 монет)"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def coins_take_until_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_coin_state[user_id] = {"action": "take_until"}
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_coins")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "⬇️ **Забрать ДО**\n\nОтправьте: `айди целевое_количество`\nПример: `1 50` (заберёт до 50 монет)"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def video_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_delete_video_state[user_id] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🗑️ **Удалить видео**\n\nОтправьте ID видео: `001`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def video_find_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_find_video_state[user_id] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🔍 **Найти видео**\n\nОтправьте ID видео: `001`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def video_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    video_list = []
    for vid in videos_data:
        stats = get_video_stats(vid)
        video_list.append((vid, stats["likes"]))

    video_list.sort(key=lambda x: x[1], reverse=True)
    top = video_list[:10]

    if not top:
        text = "🏆 **Топ видео**\n\nНет видео"
    else:
        text = "🏆 **Топ 10 видео по лайкам:**\n\n"
        for i, (vid, likes) in enumerate(top, 1):
            text += f"{i}. Видео `{vid}` — 👍 {likes}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def users_top_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    user_list = [(data["number"], data["coins"]) for data in user_data.values()]
    user_list.sort(key=lambda x: x[1], reverse=True)
    top = user_list[:10]

    text = "🏆 **Топ 10 юзеров по монетам:**\n\n"
    for i, (num, coins) in enumerate(top, 1):
        text += f"{i}. ID #{num} — 🪙 {coins}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def users_top_views(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    user_list = [(data["number"], data["videos_watched"]) for data in user_data.values()]
    user_list.sort(key=lambda x: x[1], reverse=True)
    top = user_list[:10]

    text = "🏆 **Топ 10 юзеров по просмотрам:**\n\n"
    for i, (num, views) in enumerate(top, 1):
        text += f"{i}. ID #{num} — 📹 {views}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def user_ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_ban_state[user_id] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🚫 **Забанить юзера**\n\nОтправьте ID юзера (номер регистрации): `1`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def user_unban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_unban_state[user_id] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "✅ **Разбанить юзера**\n\nОтправьте ID юзера (номер регистрации): `1`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def user_find_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    admin_find_user_state[user_id] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🔍 **Найти юзера**\n\nОтправьте ID юзера (номер регистрации): `1`"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def add_video_from_channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа!", show_alert=True)
        return

    context.user_data['adding_video'] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "📤 **Добавление видео**\n\nПерешлите видео сюда:"

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_video_from_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not context.user_data.get('adding_video', False):
        return

    try:
        video_id = get_next_video_number()

        if update.message.video:
            file_id = update.message.video.file_id
            file_type = "video"
        elif update.message.video_note:
            file_id = update.message.video_note.file_id
            file_type = "video_note"
        else:
            await update.message.reply_text("❌ Отправьте видео или кружок!")
            return

        videos_data[video_id] = {
            "id": video_id,
            "file_id": file_id,
            "type": file_type,
            "cost": 1
        }
        init_video_likes(video_id)
        save_data()

        keyboard = [
            [InlineKeyboardButton("✅ Добавить ещё", callback_data="add_video_from_channel")],
            [InlineKeyboardButton("🔙 В админ панель", callback_data="admin_videos")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ **Видео добавлено!**\n\n📹 ID: `{video_id}`\n📊 Всего: {len(videos_data)}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        context.user_data['adding_video'] = False


async def handle_coin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_coin_state.get(user_id):
        return

    action_data = admin_coin_state[user_id]
    action = action_data["action"]

    try:
        parts = update.message.text.strip().split()

        if action in ["give", "take"]:
            if len(parts) != 2:
                await update.message.reply_text("❌ Формат: `айди количество`", parse_mode="Markdown")
                return

            target = parts[0]
            amount = int(parts[1])

            if amount <= 0:
                await update.message.reply_text("❌ Количество > 0!")
                return

            target_user_id = None
            for uid, data in user_data.items():
                if str(data["number"]) == target:
                    target_user_id = uid
                    break

            if target_user_id is None:
                target_user_id = int(target)

            if target_user_id not in user_data:
                await update.message.reply_text(f"❌ Пользователь не найден!", parse_mode="Markdown")
                return

            if action == "give":
                user_data[target_user_id]["coins"] += amount
                await update.message.reply_text(
                    f"✅ **Выдано {amount} монет!**\n👤 ID #{user_data[target_user_id]['number']}", parse_mode="Markdown")
            else:
                if user_data[target_user_id]["coins"] < amount:
                    await update.message.reply_text(
                        f"❌ У пользователя только {user_data[target_user_id]['coins']} монет!", parse_mode="Markdown")
                    return
                user_data[target_user_id]["coins"] -= amount
                await update.message.reply_text(
                    f"✅ **Забрано {amount} монет!**\n👤 ID #{user_data[target_user_id]['number']}",
                    parse_mode="Markdown")

            save_data()

        elif action == "reset":
            if len(parts) != 1:
                await update.message.reply_text("❌ Формат: `айди`", parse_mode="Markdown")
                return

            target = parts[0]
            target_user_id = None
            for uid, data in user_data.items():
                if str(data["number"]) == target:
                    target_user_id = uid
                    break

            if target_user_id is None:
                target_user_id = int(target)

            if target_user_id not in user_data:
                await update.message.reply_text(f"❌ Пользователь не найден!", parse_mode="Markdown")
                return

            user_data[target_user_id]["coins"] = 0
            save_data()
            await update.message.reply_text(f"🔄 **Монеты обнулены!**\n👤 ID #{user_data[target_user_id]['number']}",
                                            parse_mode="Markdown")

        elif action in ["give_until", "take_until"]:
            if len(parts) != 2:
                await update.message.reply_text("❌ Формат: `айди целевое_количество`", parse_mode="Markdown")
                return

            target = parts[0]
            target_amount = int(parts[1])

            if target_amount < 0:
                await update.message.reply_text("❌ Целевое количество >= 0!")
                return

            target_user_id = None
            for uid, data in user_data.items():
                if str(data["number"]) == target:
                    target_user_id = uid
                    break

            if target_user_id is None:
                target_user_id = int(target)

            if target_user_id not in user_data:
                await update.message.reply_text(f"❌ Пользователь не найден!", parse_mode="Markdown")
                return

            current = user_data[target_user_id]["coins"]
            if action == "give_until":
                if current >= target_amount:
                    await update.message.reply_text(f"ℹ️ У пользователя уже {current} монет (нужно {target_amount})",
                                                    parse_mode="Markdown")
                    return
                diff = target_amount - current
                user_data[target_user_id]["coins"] = target_amount
                await update.message.reply_text(
                    f"✅ **Выдано {diff} монет!**\n👤 ID #{user_data[target_user_id]['number']}\n💰 Теперь: {target_amount}",
                    parse_mode="Markdown")
            else:
                if current <= target_amount:
                    await update.message.reply_text(f"ℹ️ У пользователя уже {current} монет (нужно {target_amount})",
                                                    parse_mode="Markdown")
                    return
                diff = current - target_amount
                user_data[target_user_id]["coins"] = target_amount
                await update.message.reply_text(
                    f"✅ **Забрано {diff} монет!**\n👤 ID #{user_data[target_user_id]['number']}\n💰 Теперь: {target_amount}",
                    parse_mode="Markdown")

            save_data()

        del admin_coin_state[user_id]

        keyboard = [[InlineKeyboardButton("🔙 В меню монет", callback_data="admin_coins")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)

    except ValueError:
        await update.message.reply_text("❌ Число!")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def handle_video_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_delete_video_state.get(user_id):
        return

    video_id = update.message.text.strip()

    if video_id not in videos_data:
        await update.message.reply_text(f"❌ Видео {video_id} не найдено!")
    else:
        del videos_data[video_id]
        if video_id in likes_data:
            del likes_data[video_id]
        save_data()
        await update.message.reply_text(f"✅ Видео {video_id} удалено!")

    del admin_delete_video_state[user_id]
    keyboard = [[InlineKeyboardButton("🔙 В меню видео", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_video_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_find_video_state.get(user_id):
        return

    video_id = update.message.text.strip()

    if video_id not in videos_data:
        await update.message.reply_text(f"❌ Видео {video_id} не найдено!")
    else:
        video = videos_data[video_id]
        stats = get_video_stats(video_id)

        text = f"🎬 **Видео {video_id}**\n👍 Лайков: {stats['likes']}\n👎 Дизлайков: {stats['dislikes']}"

        if video["type"] == "video":
            await context.bot.send_video(chat_id=user_id, video=video["file_id"], caption=text, parse_mode="Markdown")
        else:
            await context.bot.send_video_note(chat_id=user_id, video_note=video["file_id"])
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")

    del admin_find_video_state[user_id]
    keyboard = [[InlineKeyboardButton("🔙 В меню видео", callback_data="admin_videos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_user_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_ban_state.get(user_id):
        return

    target = update.message.text.strip()

    target_user_id = None
    for uid, data in user_data.items():
        if str(data["number"]) == target:
            target_user_id = uid
            break

    if target_user_id is None:
        target_user_id = int(target) if target.isdigit() else None

    if target_user_id not in user_data:
        await update.message.reply_text(f"❌ Пользователь не найден!")
    else:
        user_data[target_user_id]["banned"] = True
        save_data()
        await update.message.reply_text(f"🚫 Пользователь ID #{user_data[target_user_id]['number']} забанен!")

    del admin_ban_state[user_id]
    keyboard = [[InlineKeyboardButton("🔙 В меню юзеров", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_user_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_unban_state.get(user_id):
        return

    target = update.message.text.strip()

    target_user_id = None
    for uid, data in user_data.items():
        if str(data["number"]) == target:
            target_user_id = uid
            break

    if target_user_id is None:
        target_user_id = int(target) if target.isdigit() else None

    if target_user_id not in user_data:
        await update.message.reply_text(f"❌ Пользователь не найден!")
    else:
        user_data[target_user_id]["banned"] = False
        save_data()
        await update.message.reply_text(f"✅ Пользователь ID #{user_data[target_user_id]['number']} разбанен!")

    del admin_unban_state[user_id]
    keyboard = [[InlineKeyboardButton("🔙 В меню юзеров", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def handle_user_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_ID or not admin_find_user_state.get(user_id):
        return

    target = update.message.text.strip()

    target_user_id = None
    for uid, data in user_data.items():
        if str(data["number"]) == target:
            target_user_id = uid
            break

    if target_user_id is None:
        target_user_id = int(target) if target.isdigit() else None

    if target_user_id not in user_data:
        await update.message.reply_text(f"❌ Пользователь не найден!")
    else:
        data = user_data[target_user_id]
        text = (
            f"**👤 Найден пользователь**\n\n"
            f"🆔 ID: #{data['number']}\n"
            f"📹 Просмотрено: {data['videos_watched']}\n"
            f"🪙 Монет: {data['coins']}\n"
            f"🚫 Забанен: {'Да' if data['banned'] else 'Нет'}\n"
            f"👥 Рефералов: {len(data['referrals'])}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    del admin_find_user_state[user_id]
    keyboard = [[InlineKeyboardButton("🔙 В меню юзеров", callback_data="admin_users")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку для возврата:", reply_markup=reply_markup)


async def watch_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    await query.answer("✅", show_alert=False)

    if user_data.get(user_id, {}).get("banned", False):
        await query.answer("❌ Вы забанены!", show_alert=True)
        return

    if context.user_data.get('last_video_time', 0) > 0:
        time_diff = asyncio.get_event_loop().time() - context.user_data.get('last_video_time', 0)
        if time_diff < 2:
            await query.answer("⏳ Подождите немного!", show_alert=False)
            return

    context.user_data['last_video_time'] = asyncio.get_event_loop().time()

    stats = get_user_stats(user_id)
    if stats["coins"] < 1:
        await query.answer("❌ Недостаточно монет! Нужно 1 монета", show_alert=True)
        return

    if not videos_data:
        await query.answer("❌ Видео пока нет!", show_alert=True)
        return

    video_id = get_random_video(user_id)
    if video_id is None:
        await query.answer("❌ Нет доступных видео!", show_alert=True)
        return

    video = videos_data[video_id]
    video_stats = get_video_stats(video_id)

    user_data[user_id]["coins"] -= 1
    user_data[user_id]["videos_watched"] += 1

    if "watched_videos" not in user_data[user_id]:
        user_data[user_id]["watched_videos"] = []
    if video_id not in user_data[user_id]["watched_videos"]:
        user_data[user_id]["watched_videos"].append(video_id)

    if "sent_messages" not in user_data[user_id]:
        user_data[user_id]["sent_messages"] = []

    save_data()

    # ⭐ ОБНОВЛЯЕМ старые видео: оставляем ТОЛЬКО кнопку избранного (без главного меню)
    for msg_data in user_data[user_id]["sent_messages"]:
        try:
            if isinstance(msg_data, dict):
                msg_id = msg_data.get("message_id")
                old_video_id = msg_data.get("video_id", "???")
            else:
                msg_id = msg_data
                old_video_id = "???"

            if not msg_id or old_video_id == "???":
                continue

            # Проверяем, в избранном ли это видео
            is_fav = old_video_id in stats.get("favorites", [])

            # Текст без "просмотрено"
            new_text = f"🎬 **Видео #{old_video_id}**"

            # Обновляем caption у видео
            try:
                await context.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=msg_id,
                    caption=new_text,
                    parse_mode="Markdown"
                )
            except:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=new_text,
                        parse_mode="Markdown"
                    )
                except:
                    pass

            # ⭐ КЛАВИАТУРА ТОЛЬКО С КНОПКОЙ ИЗБРАННОГО (без главного меню)
            fav_button = "⭐ В избранное" if not is_fav else "❌ Из избранного"
            fav_callback = f"fav_add_{old_video_id}" if not is_fav else f"fav_remove_{old_video_id}"

            old_keyboard = [
                [InlineKeyboardButton(fav_button, callback_data=fav_callback)]
            ]
            old_reply_markup = InlineKeyboardMarkup(old_keyboard)

            # Обновляем кнопки
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=old_reply_markup
                )
                print(f"✅ У старого видео {old_video_id} оставлена только кнопка избранного")
            except Exception as e:
                print(f"⚠️ Не удалось обновить кнопки у видео {old_video_id}: {e}")

        except Exception as e:
            print(f"❌ Ошибка при обновлении: {e}")

    # Очищаем список и добавляем новое видео позже
    old_messages = user_data[user_id]["sent_messages"].copy()
    user_data[user_id]["sent_messages"] = []

    # Кнопки для НОВОГО видео (полные, с главным меню)
    is_fav = video_id in stats.get("favorites", [])
    fav_button = "⭐ В избранное" if not is_fav else "❌ Из избранного"
    fav_callback = f"fav_add_{video_id}" if not is_fav else f"fav_remove_{video_id}"

    keyboard = [
        [
            InlineKeyboardButton(f"👍 {video_stats['likes']}", callback_data=f"like_{video_id}_like"),
            InlineKeyboardButton(f"👎 {video_stats['dislikes']}", callback_data=f"like_{video_id}_dislike")
        ],
        [
            InlineKeyboardButton(fav_button, callback_data=fav_callback),
            InlineKeyboardButton("🎬 Ещё видео (1 🪙)", callback_data="watch_video")
        ],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"🎬 **Видео #{video_id}**\n💰 Стоимость: 1 🪙\n💳 Остаток: {user_data[user_id]['coins']} 🪙"

    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    try:
        if video["type"] == "video":
            sent = await context.bot.send_video(
                chat_id=user_id,
                video=video["file_id"],
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_video_note(chat_id=user_id, video_note=video["file_id"])
            sent = await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        # Сохраняем ID нового сообщения
        user_data[user_id]["sent_messages"].append({
            "message_id": sent.message_id,
            "video_id": video_id
        })

        # Возвращаем старые сообщения обратно в список
        for msg in old_messages:
            user_data[user_id]["sent_messages"].append(msg)

        save_data()

    except Exception as e:
        print(f"❌ Ошибка отправки видео: {e}")
        sent = await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Ошибка\n\n{text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        user_data[user_id]["sent_messages"].append({"message_id": sent.message_id, "video_id": video_id})
        for msg in old_messages:
            user_data[user_id]["sent_messages"].append(msg)
        save_data()


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    stats = get_user_stats(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    # Подсчитываем количество рефералов
    referrals_count = len(stats.get("referrals", []))

    # Получаем список рефералов (первые 5)
    referrals_list = ""
    if referrals_count > 0:
        referrals_list = "\n👥 **Приглашённые:**\n"
        for i, ref_id in enumerate(stats.get("referrals", [])[:5], 1):
            if ref_id in user_data:
                referrals_list += f"   {i}. ID #{user_data[ref_id]['number']}\n"
        if referrals_count > 5:
            referrals_list += f"   ... и ещё {referrals_count - 5}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "**👤 Профиль**\n\n"
        f"🆔 **ID:** `{stats['number']}`\n"
        f"📹 **Просмотрено:** {stats['videos_watched']}\n"
        f"🪙 **Монет:** {stats['coins']}\n"
        f"💎 **Подписка:** {stats['subscription']}\n"
        f"🚫 **Статус:** {'Забанен' if stats['banned'] else 'Активен'}\n"
        f"👥 **Рефералов:** {referrals_count}\n"
        f"{referrals_list}\n"
        f"🔗 **Реферальная ссылка:**\n`{referral_link}`\n\n"
        f"_(За каждого приглашённого +5 🪙)_\n\n"
        f"💡 **Совет:** Ищите рефералов на https://otvet.mail.ru/search/new/Боты%20по%20типу%20sunway/ и выкладывайте туда ссылку"
    )

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    # Очищаем режимы
    clear_user_modes(context, user_id)

    # Проверяем, проходил ли пользователь каптчу
    if user_id not in user_data:
        # Новый пользователь - показываем каптчу
        # Сохраняем реферальный код во временное хранилище
        if context.args and context.args[0].startswith("ref_"):
            context.user_data['pending_referrer'] = int(context.args[0].split("_")[1])
        await show_captcha(update, context)
        return

    # Проверяем бан
    banned, remaining = is_captcha_banned(user_id)
    if banned:
        remaining_min = remaining // 60
        remaining_sec = remaining % 60
        if update.callback_query:
            await update.callback_query.answer(f"❌ Вы в бане! Осталось: {remaining_min} мин {remaining_sec} сек",
                                               show_alert=True)
        else:
            await update.message.reply_text(
                f"🚫 **Вы в бане!**\n\nОсталось: {remaining_min} мин {remaining_sec} сек",
                parse_mode="Markdown"
            )
        return

    # Если пользователь не прошёл каптчу
    if user_id in user_captcha and not user_captcha[user_id].get("passed", False):
        await show_captcha(update, context)
        return

    # Регистрируем пользователя
    get_user_stats(user_id)

    # ⭐ ОБРАБОТКА РЕФЕРАЛА ТОЛЬКО ПОСЛЕ КАПТЧИ И ПОДПИСКИ
    # Проверяем, есть ли ожидающий реферал
    pending_referrer = context.user_data.get('pending_referrer')
    if pending_referrer and pending_referrer != user_id:
        # Проверяем подписку
        is_subscribed = await check_subscription(user_id, context)
        if is_subscribed:
            # Добавляем реферала
            if pending_referrer in user_data and user_id not in user_data[pending_referrer]["referrals"]:
                user_data[pending_referrer]["referrals"].append(user_id)
                user_data[pending_referrer]["coins"] += 5
                save_data()

                # Уведомляем реферала
                try:
                    await context.bot.send_message(
                        pending_referrer,
                        f"✅ **Новый реферал!**\n\n"
                        f"👤 Пользователь ID #{user_data[user_id]['number']} перешёл по вашей ссылке!\n"
                        f"🪙 Вы получили +5 монет!\n"
                        f"💰 Ваш баланс: {user_data[pending_referrer]['coins']} монет",
                        parse_mode="Markdown"
                    )
                except:
                    pass
        # Очищаем ожидающий реферал
        del context.user_data['pending_referrer']

    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await show_subscription_required(update, context)
        return

    await show_main_menu(update, context)


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        await query.answer("✅", show_alert=False)

        # ⭐ ПРОВЕРЯЕМ РЕФЕРАЛА ПОСЛЕ ПОДПИСКИ
        pending_referrer = context.user_data.get('pending_referrer')
        if pending_referrer and pending_referrer != user_id:
            if pending_referrer in user_data and user_id not in user_data[pending_referrer]["referrals"]:
                user_data[pending_referrer]["referrals"].append(user_id)
                user_data[pending_referrer]["coins"] += 5
                save_data()

                try:
                    await context.bot.send_message(
                        pending_referrer,
                        f"✅ **Новый реферал!**\n\n"
                        f"👤 Пользователь ID #{user_data[user_id]['number']} перешёл по вашей ссылке и подписался!\n"
                        f"🪙 Вы получили +5 монет!\n"
                        f"💰 Ваш баланс: {user_data[pending_referrer]['coins']} монет",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            del context.user_data['pending_referrer']

        await show_main_menu(update, context)
    else:
        await query.answer("❌", show_alert=False)


def clear_user_modes(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Очищает все режимы пользователя"""
    # Удаляем все состояния из context.user_data
    if 'suggesting_video' in context.user_data:
        del context.user_data['suggesting_video']
    if 'adding_favorite_by_id' in context.user_data:
        del context.user_data['adding_favorite_by_id']
    if 'adding_video' in context.user_data:
        del context.user_data['adding_video']

    # Очищаем состояния админа
    if user_id in admin_coin_state:
        del admin_coin_state[user_id]
    if user_id in admin_delete_video_state:
        del admin_delete_video_state[user_id]
    if user_id in admin_find_video_state:
        del admin_find_video_state[user_id]
    if user_id in admin_ban_state:
        del admin_ban_state[user_id]
    if user_id in admin_unban_state:
        del admin_unban_state[user_id]
    if user_id in admin_find_user_state:
        del admin_find_user_state[user_id]


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Очищаем режимы при нажатии кнопок (кроме специальных)
    if query.data not in ["suggest", "add_favorite_by_id", "watch_video", "favorites", "promo", "create_promo",
                          "activate_promo", "admin_promo_menu", "admin_create_promo", "admin_delete_promo",
                          "admin_list_promos", "admin_user_promos", "admin_top_promos", "games", "game_dice",
                          "dice_even", "dice_odd", "free_bonus"]:
        clear_user_modes(context, user_id)

    # Игры
    if query.data == "games":
        await games_menu(update, context)
    elif query.data == "game_dice":
        await game_dice_start(update, context)
    elif query.data == "dice_even":
        await dice_choice(update, context)
    elif query.data == "dice_odd":
        await dice_choice(update, context)

    # Халява
    elif query.data == "free_bonus":
        await free_bonus(update, context)

    # Игры
    if query.data == "games":
        await games_menu(update, context)
    elif query.data == "game_dice":
        await game_dice_start(update, context)
    elif query.data == "dice_even":
        await dice_choice(update, context)
    elif query.data == "dice_odd":
        await dice_choice(update, context)

    if query.data.startswith("like_"):
        await handle_like(update, context)
    elif query.data.startswith("fav_add_"):
        await add_to_favorites(update, context)
    elif query.data.startswith("fav_remove_"):
        await remove_from_favorites(update, context)
    elif query.data.startswith("watch_favorite_"):
        await watch_favorite_video(update, context)
    elif query.data.startswith("approve_suggest_"):
        await approve_suggestion(update, context)
    elif query.data.startswith("reject_suggest_"):
        await reject_suggestion(update, context)
    elif query.data.startswith("view_suggest_"):
        await view_suggestion(update, context)
    elif query.data == "favorites":
        await show_favorites(update, context)
    elif query.data == "add_favorite_by_id":
        await add_favorite_by_id_start(update, context)
    elif query.data == "suggest":
        await suggest_start(update, context)
    elif query.data == "promo":
        await promo_menu(update, context)
    elif query.data == "create_promo":
        await create_promo_start(update, context)
    elif query.data == "activate_promo":
        await activate_promo_start(update, context)
    elif query.data == "profile":
        await show_profile(update, context)
    elif query.data == "back_to_menu":
        await show_main_menu(update, context)
    elif query.data == "check_sub":
        await check_subscription_callback(update, context)
    elif query.data == "admin_panel":
        await show_admin_panel(update, context)
    elif query.data == "admin_promo_menu":
        await admin_promo_menu(update, context)
    elif query.data == "admin_create_promo":
        await admin_create_promo_start(update, context)
    elif query.data == "admin_delete_promo":
        await admin_delete_promo_start(update, context)
    elif query.data == "admin_list_promos":
        await admin_list_promos(update, context)
    elif query.data == "admin_user_promos":
        await admin_user_promos(update, context)
    elif query.data == "admin_top_promos":
        await admin_top_promos(update, context)
    elif query.data == "admin_suggestions":
        await admin_suggestions_menu(update, context)
    elif query.data == "admin_coins":
        await admin_coins_menu(update, context)
    elif query.data == "admin_videos":
        await admin_videos_menu(update, context)
    elif query.data == "admin_users":
        await admin_users_menu(update, context)
    elif query.data == "admin_stats":
        await admin_stats(update, context)
    elif query.data == "coins_give":
        await coins_give_start(update, context)
    elif query.data == "coins_take":
        await coins_take_start(update, context)
    elif query.data == "coins_reset":
        await coins_reset_start(update, context)
    elif query.data == "coins_give_until":
        await coins_give_until_start(update, context)
    elif query.data == "coins_take_until":
        await coins_take_until_start(update, context)
    elif query.data == "video_delete":
        await video_delete_start(update, context)
    elif query.data == "video_find":
        await video_find_start(update, context)
    elif query.data == "video_top":
        await video_top(update, context)
    elif query.data == "users_top_coins":
        await users_top_coins(update, context)
    elif query.data == "users_top_views":
        await users_top_views(update, context)
    elif query.data == "user_ban":
        await user_ban_start(update, context)
    elif query.data == "user_unban":
        await user_unban_start(update, context)
    elif query.data == "user_find":
        await user_find_start(update, context)
    elif query.data == "add_video_from_channel":
        await add_video_from_channel_start(update, context)
    elif query.data == "watch_video":
        await watch_video(update, context)
    elif query.data == "support":
        await support_start(update, context)
    elif query.data == "admin_tickets_menu":
        await admin_tickets_menu(update, context)
    elif query.data == "admin_find_ticket":
        await admin_find_ticket_start(update, context)
    elif query.data == "admin_delete_ticket":
        await admin_delete_ticket_start(update, context)
    elif query.data == "admin_answer_ticket":
        await admin_answer_ticket_start(update, context)
    elif query.data == "admin_list_tickets":
        await admin_list_tickets(update, context)
    elif query.data.startswith("view_ticket_"):
        await view_ticket(update, context)
    elif query.data.startswith("answer_ticket_"):
        ticket_id = query.data.split("_")[2]
        context.user_data['admin_answering_ticket_id'] = ticket_id
        context.user_data['admin_waiting_response'] = True
        await query.message.reply_text(
            f"💬 **Введите ответ для тикета {ticket_id}:**\n\nОтвет будет отправлен пользователю.",
            parse_mode="Markdown")
        await query.message.delete()
    elif query.data.startswith("delete_ticket_"):
        ticket_id = query.data.split("_")[2]
        if ticket_id in tickets_data:
            del tickets_data[ticket_id]
            save_data()
            await query.answer("✅ Тикет удалён!", show_alert=False)
            await query.message.delete()

    elif query.data == "admin_notifications_menu":
        await admin_notifications_menu(update, context)
    elif query.data == "admin_create_notification":
        await admin_create_notification_start(update, context)
    elif query.data == "admin_delete_notification":
        await admin_delete_notification_start(update, context)
    elif query.data == "admin_list_notifications":
        await admin_list_notifications(update, context)
    elif query.data == "admin_find_notification":
        await admin_find_notification_start(update, context)
    elif query.data.startswith("captcha_"):
        await handle_captcha(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    # Создание оповещения
    if context.user_data.get('creating_notification', False):
        await handle_create_notification(update, context)
        return

    # Удаление оповещения
    if context.user_data.get('deleting_notification', False):
        await handle_delete_notification(update, context)
        return

    # Поиск оповещения
    if context.user_data.get('finding_notification', False):
        await handle_find_notification(update, context)
        return

    # ... остальные режимы ...

    # Игра Кубик - ожидание ставки
    if context.user_data.get('awaiting_dice_bet', False):
        await handle_dice_bet(update, context)
        return

    # Создание тикета
    if context.user_data.get('creating_ticket', False):
        await handle_create_ticket(update, context)
        return

    # Создание тикета
    if context.user_data.get('creating_ticket', False):
        await handle_create_ticket(update, context)
        return

    # Админ отвечает на тикет
    if context.user_data.get('admin_waiting_response', False):
        await handle_admin_send_response(update, context)
        return

    # Админ ищет тикет
    if context.user_data.get('admin_finding_ticket', False):
        await handle_admin_find_ticket(update, context)
        return

    # Админ удаляет тикет
    if context.user_data.get('admin_deleting_ticket', False):
        await handle_admin_delete_ticket(update, context)
        return

    # Админ отвечает на тикет (ввод ID)
    if context.user_data.get('admin_answering_ticket', False):
        await handle_admin_answer_ticket(update, context)
        return

    # Создание промокода пользователем
    if context.user_data.get('creating_promo', False):
        await handle_create_promo(update, context)
        return

    # Активация промокода
    if context.user_data.get('activating_promo', False):
        await handle_activate_promo(update, context)
        return

    # Админ создаёт промокод
    if context.user_data.get('admin_creating_promo', False):
        await handle_admin_create_promo(update, context)
        return

    # Админ удаляет промокод
    if context.user_data.get('admin_deleting_promo', False):
        await handle_admin_delete_promo(update, context)
        return

    # Предложение видео
    if context.user_data.get('suggesting_video', False):
        await handle_suggest_video(update, context)
        return

    # Добавление в избранное по ID
    if context.user_data.get('adding_favorite_by_id', False):
        await handle_add_favorite_by_id(update, context)
        return

    # Админские режимы
    if user_id == ADMIN_ID:
        if admin_coin_state.get(user_id):
            await handle_coin_action(update, context)
        elif admin_delete_video_state.get(user_id):
            await handle_video_delete(update, context)
        elif admin_find_video_state.get(user_id):
            await handle_video_find(update, context)
        elif admin_ban_state.get(user_id):
            await handle_user_ban(update, context)
        elif admin_unban_state.get(user_id):
            await handle_user_unban(update, context)
        elif admin_find_user_state.get(user_id):
            await handle_user_find(update, context)
        elif context.user_data.get('adding_video', False):
            if update.message.video or update.message.video_note:
                await handle_video_from_channel(update, context)
        return


def main():
    load_data()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, handle_message))

    print("=" * 50)
    print("🤖 Бот запущен!")
    print(f"👥 Пользователей: {len(user_data)}")
    print(f"🎬 Видео: {len(videos_data)}")
    print(f"👍 Лайков в системе: {len(likes_data) - 248}")
    print("=" * 50)
    app.run_polling()


if __name__ == "__main__":
    main()
