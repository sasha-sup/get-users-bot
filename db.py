from datetime import datetime

import asyncpg
import config
from config import logger


async def create_db_connection():
    db_config = {
        "host": config.DB_HOST,
        "port": config.DB_PORT,
        "database": config.DB_NAME,
        "user": config.DB_USER,
        "password": config.DB_PASS,
    }
    try:
        # Connect db
        connection = await asyncpg.connect(**db_config)
        return connection
    except asyncpg.PostgresError as e:
        logger.error(f"Error connecting to DB: {e}")
        raise e

async def close_db_connection(connection):
    await connection.close()

async def create_tables_if_exists():
    connection = await create_db_connection()
    try:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS telegram_users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255));
            """)
    except asyncpg.PostgresError as e:
        logger.error(f"Error creating table: {e}")
    finally:
        await connection.close()

async def ensure_user_exists(user_id, username, first_name, last_name):
    connection = await create_db_connection()
    try:
        select_query = "SELECT user_id FROM telegram_users WHERE user_id = $1"
        user = await connection.fetchrow(select_query, user_id)
        if user is None:
            insert_query = "INSERT INTO telegram_users (user_id, username,  first_name, last_name) VALUES ($1, $2, $3, $4)"
            await connection.execute(insert_query, user_id, username, first_name, last_name)
            logger.info(f"Added new user with user_id {user_id}, username {username}")
    except asyncpg.UniqueViolationError:
        logger.warning(f"User with user_id {user_id}, username {username} already exists.")
    except asyncpg.PostgresError as e:
        logger.error(f"Error adding user_id {user_id}, username {username}: {e}")
    finally:
        await connection.close()