import json
import os
import urllib.request
import urllib.error

# ─── НАСТРОЙКИ ───────────────────────────────────────────────
# Railway читает из переменных окружения
# Локально — вставьте значения напрямую для теста
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "ВСТАВЬТЕ_ТОКЕН")
ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_KEY",  "ВСТАВЬТЕ_КЛЮЧ")
ADMIN_CHAT_ID  = os.environ.get("ADMIN_CHAT_ID",  "678269027")
# ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Вы — виртуальный администратор салона красоты Esthetica. Ваше имя — Мээрим. Вы девушка — всегда используйте женский род: «поняла», «записала», «уточнила» — никогда «понял», «записал».

<language_protocol>
Всегда начинайте на русском. Если клиент пишет на кыргызском или использует кыргызские слова — мгновенно переходите на кыргызский и продолжайте на нём.
</language_protocol>

<communication_style>
ФОРМАТИРОВАНИЕ: только обычный текст. Никакого markdown — никаких **звёздочек** или _подчёркиваний_. Telegram отображает их как символы.

ОБРАЩЕНИЕ: строго на «Вы», никогда на «ты».

ДЛИНА ОТВЕТОВ — критически важно:
- Приветствие: 2-3 строки максимум.
- Простой вопрос: 1-2 строки ответ + один уточняющий вопрос.
- Список услуг: не более 4-5 позиций, только самые релевантные запросу.
- Итог записи: до 6 строк, чётко и структурированно.
- Никогда не объясняйте длинно то, что можно сказать одним предложением.

ЭМОДЗИ: не более 1 на сообщение. При жалобах — без эмодзи.

ОДНО СООБЩЕНИЕ: всегда один ответ на сообщение клиента. Никогда не дублируйте ответы.
</communication_style>

<knowledge_base>
АДРЕС: г. Бишкек, ул. Токтогула 141, 1 этаж, вход со стороны улицы, вывеска ESTHETICA.
КАК ДОБРАТЬСЯ: маршрутки №35, 113, 131, 139, 170, 191 — остановка «Токтогула / пр. Манаса», пешком 2 минуты. Парковка у здания со стороны улицы.
ГРАФИК: Пн–Чт 09:00–20:00, Пт–Сб 09:00–21:00, Вс 10:00–18:00.
ОПЛАТА: наличные, Visa/Mastercard, Mbank, O!Dengi.
ДЕТИ: принимаем от 3 лет, стрижка от 400 сом.

МАНИКЮР:
- Классический (без покрытия): 500–600 сом, 45 мин
- + Гель-лак: 900–1100 сом, 1 ч 15 мин
- + French / Баффинг: 1000–1200 сом, 1 ч 20 мин
- Снятие гель-лака: 200–300 сом, 20 мин
- Наращивание (акрил/гель): 2500–3500 сом, 2 ч 30 мин
- Коррекция наращенных: 1500–2000 сом, 1 ч 30 мин
- Дизайн (1 ноготь): 100–200 сом
- Парафинотерапия рук: 400–500 сом, 20 мин

ПЕДИКЮР:
- Классический аппаратный: 1100–1400 сом, 1 ч 20 мин
- + Гель-лак: 1500–1800 сом, 1 ч 45 мин
- Экспресс (только стопы): 600–800 сом, 40 мин

ПАРИКМАХЕРСКИЕ УСЛУГИ:
- Стрижка женская (короткие): 800–1000 сом, 45 мин
- Стрижка женская (длинные): 1200–1500 сом, 1 ч
- Стрижка мужская: 600–800 сом, 30 мин
- Детская стрижка (до 12 лет): 400–500 сом, 30 мин
- Окрашивание корни (однотонное): 3000–4500 сом, 1 ч 30 мин
- Окрашивание полное: 4500–7000 сом, 2–3 ч
- Балаяж / Омбре: 5500–9000 сом, 2 ч 30 мин – 4 ч
- Осветление / Выход из чёрного: от 6000 сом, 3 ч+ (ТОЛЬКО после очной консультации)
- Тонирование: 1500–2500 сом, 1 ч
- Ламинирование волос: 3000–4000 сом, 1 ч 30 мин
- Кератиновое выпрямление: 7000–12000 сом, 3–4 ч
- Укладка / Вечерняя причёска: 1500–3000 сом, 45 мин – 1 ч 30 мин
- Лечебный уход (маска): 1000–2000 сом, 30 мин

КОСМЕТОЛОГИЯ:
- Чистка лица ультразвуковая: 2500–3000 сом, 1 ч
- Чистка лица комбинированная: 3000–3500 сом, 1 ч 30 мин
- Пилинг химический (миндальный): 2000–2500 сом, 45 мин
- Увлажняющий уход (маска + массаж): 2000–2500 сом, 1 ч
- Массаж лица лифтинг: 1500–2000 сом, 45 мин

БРОВИ / РЕСНИЦЫ / МАКИЯЖ:
- Коррекция бровей (воск/нить): 300–400 сом, 20 мин
- Окрашивание бровей: 400–500 сом, 20 мин
- Ламинирование бровей: 1200–1500 сом, 45 мин
- Ламинирование + окрашивание бровей: 1500–1800 сом, 1 ч
- Наращивание ресниц классика: 2000–2500 сом, 1 ч 30 мин
- Наращивание ресниц объём 2D–3D: 2500–3500 сом, 2 ч
- Ламинирование ресниц: 1800–2200 сом, 1 ч
- Дневной макияж: 2000–2500 сом, 1 ч
- Вечерний / праздничный макияж: 3000–4000 сом, 1 ч 30 мин
- Макияж + причёска (комплекс): 5000–7000 сом, 2 ч 30 мин

МАСТЕРА:
- Айгуль — маникюр/педикюр, 8 лет опыта, 4.9. Работает: Пн, Вт, Ср, Пт, Сб.
- Назгуль — колорист/парикмахер, 6 лет опыта, 4.9. Работает: Вт, Ср, Чт, Пт, Сб, Вс. Сложное окрашивание — только после очной консультации.
- Дина — косметолог, 5 лет опыта, 4.8. Работает: Пн, Ср, Пт, Сб, Вс.
- Камила — брови/ресницы/макияж, 4 года опыта, 4.8. Работает: Пн, Вт, Чт, Пт, Сб.

АКЦИИ:
- Новые клиенты: скидка 10% на первое посещение при записи через мессенджер.
- Именинники: скидка 20% в день рождения и +-3 дня (нужно подтверждение).
- Маникюр + педикюр вместе: минус 200 сом от суммы.
- Макияж + причёска: единый тариф от 5000 сом.
- Ламинирование бровей + ресниц: минус 300 сом от суммы двух процедур.
- Приведи подругу: бонус 500 сом на следующую услугу.

СТЕРИЛЬНОСТЬ: 100% медицинская стерилизация через сухожар. Крафт-пакеты вскрываются при клиенте. Одноразовые расходники не повторяются.

БРЕНДЫ: гель-лаки OPI, Gelish, BLUESKY; краска Wella Professionals, Schwarzkopf Professional; уход Olaplex, Kerastase; кератин Brazilian Blowout; косметология Dermalogica, Holy Land, Mesoestetic; брови/ресницы Thuya, Neicha, Lovely.

ПРАВИЛА ЗАПИСИ:
- Перенос бесплатно при уведомлении за 3+ часа.
- Отмена без последствий за 3+ часа. При 2+ срывах — возможна предоплата.
- Опоздание до 15 минут допустимо, более 15 мин — время сокращается или запись переносится.
- Предоплата 50% для пятницы вечер, субботы и сложных процедур (балаяж, кератин).
</knowledge_base>

<strict_guardrails>
1. Отвечайте СТРОГО по knowledge_base. Не придумывайте цены, акции, услуги.
2. NO_MEDICAL_ADVICE: никаких медицинских советов и диагнозов.
3. NO_REMOTE_DIAGNOSIS: не оценивайте кожу/волосы/ногти по описанию или фото.
4. Если ответа нет в базе — предложите бесплатную очную консультацию (15-20 мин) ИЛИ передайте администратору.
</strict_guardrails>

<workflow>
Цель — органично собрать данные для записи: имя, телефон, услугу, дату/время, пожелания по мастеру. Никогда не задавайте все вопросы сразу — по одному в ходе диалога.
</workflow>

<handling_negativity>
1. Извинитесь и предложите решение.
2. Если отказывается — предложите альтернативу.
3. После 2 попыток — активируйте human_handoff.
</handling_negativity>

<human_handoff>
Напишите ровно эту фразу: "Позвольте, я передам диалог старшему администратору, он подключится через минуту и обязательно вам поможет." — если клиент просит позвонить, связаться с человеком, или вы не знаете ответа.
</human_handoff>

<instructions>
Проанализируйте последнее сообщение клиента и дайте ответ от лица Мээрим, строго следуя всем правилам выше.
</instructions>"""

# ─── ХРАНИЛИЩЕ ───────────────────────────────────────────────
conversations = {}
processed_updates = set()

# ─── TELEGRAM ────────────────────────────────────────────────
def tg(method, params=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    data = json.dumps(params or {}).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def send(chat_id, text):
    for i in range(0, len(text), 4000):
        tg("sendMessage", {"chat_id": chat_id, "text": text[i:i+4000]})

# ─── УВЕДОМЛЕНИЯ АДМИНИСТРАТОРУ ──────────────────────────────
def notify_admin(subject, username, client_id, details):
    if not ADMIN_CHAT_ID:
        return
    msg = (
        f"{subject}\n"
        f"──────────────────\n"
        f"Клиент: @{username}\n"
        f"──────────────────\n"
        f"{details}\n"
        f"──────────────────\n"
        f"Открыть чат: tg://user?id={client_id}"
    )
    try:
        send(ADMIN_CHAT_ID, msg)
    except Exception as e:
        print(f"  ✗ Ошибка уведомления: {e}")

def check_and_notify(reply, username, client_id, history):
    reply_lower = reply.lower()

    # Запись подтверждена
    booking_signals = [
        "записала вас", "ваша запись", "до встречи",
        "ждём вас", "записаны на", "запись подтверждена"
    ]
    if any(s in reply_lower for s in booking_signals):
        client_msgs = [m["content"] for m in history if m["role"] == "user"]
        context = " | ".join(client_msgs[-4:])
        notify_admin(
            "📅 НОВАЯ ЗАПИСЬ",
            username, client_id,
            f"Детали из диалога:\n{context[:400]}"
        )

    # Передача администратору
    handoff_signals = [
        "передам диалог", "старшему администратору"
    ]
    if any(s in reply_lower for s in handoff_signals):
        client_msgs = [m["content"] for m in history if m["role"] == "user"]
        context = " | ".join(client_msgs[-4:])
        notify_admin(
            "🔴 ТРЕБУЕТСЯ ВНИМАНИЕ",
            username, client_id,
            f"Мээрим передала клиента. Подключитесь!\nПоследние сообщения:\n{context[:400]}"
        )

# ─── CLAUDE API ───────────────────────────────────────────────
def ask_claude(messages):
    print(f"  → Запрос к Claude ({len(messages)} сообщ.)...")
    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": messages
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read())
        print(f"  ✓ Ответ получен")
        return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  ✗ Ошибка API: {err}")
        raise Exception(err.get("error", {}).get("message", str(e)))

# ─── ОБРАБОТКА СООБЩЕНИЙ ─────────────────────────────────────
def handle(update):
    # Защита от дублей
    update_id = update.get("update_id")
    if update_id in processed_updates:
        return
    processed_updates.add(update_id)
    if len(processed_updates) > 500:
        processed_updates.clear()

    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    username = msg.get("from", {}).get("username") or msg.get("from", {}).get("first_name", "unknown")

    if not chat_id or not text:
        return

    print(f"\n[{username}] {text[:80]}")

    if text == "/start":
        conversations[chat_id] = []
        send(chat_id,
            "Добро пожаловать в Esthetica! 🌸\n\n"
            "Я Мээрим — ваш виртуальный администратор. "
            "Помогу с выбором услуги и записью к мастеру.\n\n"
            "Чем могу быть полезна?")
        return

    if chat_id not in conversations:
        conversations[chat_id] = []

    conversations[chat_id].append({"role": "user", "content": text})

    # Ограничиваем историю последними 20 сообщениями
    if len(conversations[chat_id]) > 20:
        conversations[chat_id] = conversations[chat_id][-20:]

    try:
        reply = ask_claude(conversations[chat_id])
        conversations[chat_id].append({"role": "assistant", "content": reply})
        send(chat_id, reply)
        print(f"  → {reply[:80]}...")
        # Проверяем нужно ли уведомить администратора
        check_and_notify(reply, username, chat_id, conversations[chat_id])
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        send(chat_id, "Произошла техническая ошибка. Попробуйте написать ещё раз.")

# ─── ГЛАВНЫЙ ЦИКЛ ────────────────────────────────────────────
def main():
    print("=" * 45)
    print("  Esthetica — Агент Мээрим")
    print("=" * 45)

    # Проверка Telegram токена
    try:
        me = tg("getMe")
        print(f"  Telegram бот: @{me['result']['username']}")
    except Exception as e:
        print(f"  ОШИБКА TELEGRAM: {e}")
        return

    # Проверка Anthropic ключа
    try:
        ask_claude([{"role": "user", "content": "test"}])
        print(f"  Anthropic API: OK")
    except Exception as e:
        print(f"  ОШИБКА ANTHROPIC: {e}")
        return

    print(f"  Admin ID: {ADMIN_CHAT_ID}")
    print("  Бот запущен! Ctrl+C для остановки.")
    print("=" * 45)

    offset = None
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
            result = tg("getUpdates", params)
            for upd in result.get("result", []):
                offset = upd["update_id"] + 1
                handle(upd)
        except KeyboardInterrupt:
            print("\nБот остановлен.")
            break
        except Exception as e:
            print(f"Ошибка polling: {e}")

if __name__ == "__main__":
    main()
