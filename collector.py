import os

from telethon import TelegramClient


def collect_tg_messages(channel_name, msg_count=40):
    # клиент Телеграма делает за нас всю работу.
    client = TelegramClient(
        'collect_data',
        # мы считываем данные из переменных среды
        # т.к. "чувствительные" данные не должны находится в коде
        # и совершенно точно не в репозитории
        api_id=int(os.environ['TELEGRAM_API_ID']),
        api_hash=os.environ['TELEGRAM_API_HASH']
    )
    client.start()
    # по сути, мы просто задаём параметры и получаем сообщения
    # по одному из телеграм клиента
    for msg in client.iter_messages(
            entity=channel_name, limit=msg_count):
        # выдать "текущее" сообщение в виде словаря нужного нам формата
        # для каждого полученного сообщения из клиента
        yield {
            'id': msg.id,
            'date': msg.date,
            'out': msg.out,
            'mentioned': msg.mentioned,
            'media_unread': msg.media_unread,
            'silent': msg.silent,
            'post': msg.post,
            'reply_to_msg_id': msg.reply_to_msg_id,
            'message': msg.message,
            'via_bot_id': msg.via_bot_id,
            'author': msg.from_id and msg.from_id.user_id,
        }

