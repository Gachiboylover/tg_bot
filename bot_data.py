import aiosqlite as sq
from datetime import datetime

async def db_connect():
    global db
    global cursor
    db = await sq.connect('tg_training_bot.db')
    cursor = await db.cursor()
    await cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY);
    ''')
    await cursor.execute('''CREATE TABLE IF NOT EXISTS trainings(
                    user_id INTEGER,
                    training TEXT);
    ''')
    
async def db_write_training(u_id, training):
    await cursor.execute(f'INSERT INTO trainings (user_id, training) SELECT ?, ? WHERE NOT EXISTS(SELECT * FROM trainings WHERE user_id = ? AND training = ?)', (u_id, training, u_id, training))
    await db.commit()
    
async def db_del_training(u_id, training):
    await cursor.execute(f'DELETE FROM trainings WHERE user_id = ? AND training = ?', (u_id, training))
    await db.commit()

async def db_write_user(u_id):
    await cursor.execute(f'INSERT INTO users VALUES (?) ON CONFLICT DO NOTHING', (u_id,))
    await db.commit()
    
async def db_show_all(u_id):
    await cursor.execute('SELECT training FROM trainings WHERE user_id = ?', (u_id,))
    trainings = await cursor.fetchall()
    await db.commit()
    return trainings

async def db_get_all_id():
    await cursor.execute('SELECT * FROM users')
    all_id = await cursor.fetchall()
    await db.commit()
    return all_id

async def db_del_old(trainings, u_id):
    for t in trainings:
        await cursor.execute('DELETE FROM trainings WHERE training = ? AND user_id = ?', (t, u_id))
        await db.commit()
    
