import asyncio
import os

from config import API_HASH, API_ID, INVITE_LINK, PHONE_NUMBER, logger
from db import create_tables_if_exists, ensure_user_exists
from telethon.sync import TelegramClient

client = TelegramClient('session_name', API_ID, API_HASH)

async def get_chat_users(chat_id):
    try:
        participants = await client.get_participants(chat_id, limit=100)
        for participant in participants:
            user_id = participant.id
            username = participant.username
            first_name = participant.first_name
            last_name = participant.last_name
            await ensure_user_exists(user_id, username, first_name, last_name)
        logger.info(f"Successfully retrieved users from chat {chat_id}")
    except Exception as e:
        logger.error(f"Error retrieving users from chat {chat_id}: {str(e)}")
        raise e

async def log_dir():
    try:
        dir_path = "/app/log"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")
        else:
            logger.info(f"Directory already exists: {dir_path}")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        raise e

async def main():
    await log_dir()
    await create_tables_if_exists()
    await client.start(PHONE_NUMBER)
    chat_entity = await client.get_entity(INVITE_LINK)
    chat_id = chat_entity.id
    users = await get_chat_users(chat_id)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
