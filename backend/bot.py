import asyncio
from aiogram import Bot, Dispatcher, types
# from aiogram.types import ParseMode, InputFile
from aiogram.utils import executor
import aiohttp
import re

API_TOKEN = '7257443971:AAGKnyYb49fA-limjqJJqGldqzZMLX-aNC8'
BASE_URL = 'http://web:80'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def parse_student_ids(text: str):
    student_ids = re.split(r'[;, \n]+', text)
    student_ids = [id for id in student_ids if id]
    return student_ids

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Добро пожаловать! Вы можете ввести несколько ID студентов или загрузить текстовый файл с ID студентов.")

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Используйте команду /ids для ввода ID студентов.\nИспользуйте команду /file для загрузки текстового файла с ID студентов.")

@dp.message_handler(commands=['ids'])
async def handle_ids(message: types.Message):
    await message.reply("Пожалуйста, введите ID студентов, разделяя их запятыми, точками с запятой, пробелами или новыми строками:")

@dp.message_handler(commands=['file'])
async def handle_file(message: types.Message):
    await message.reply("Пожалуйста, загрузите текстовый файл с ID студентов:")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_ids(message: types.Message):
    student_ids = parse_student_ids(message.text)
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{BASE_URL}/bot_submit_student_id', data={'student_id': ','.join(student_ids)}) as response:
            if response.status == 200:
                data = await response.json()
                await message.reply(f"Полученные ID студентов: {data['student_ids']}")
                await display_results(session, message, data['student_ids'][:3])
            else:
                await message.reply("Ошибка при обработке ID студентов.")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def process_file(message: types.Message):
    document_id = message.document.file_id
    file = await bot.get_file(document_id)
    file_path = file.file_path
    file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as file_response:
            content = await file_response.text()
            student_ids = parse_student_ids(content)
            async with session.post(f'{BASE_URL}/bot_submit_file', data={'file': content}) as response:
                if response.status == 200:
                    data = await response.json()
                    await message.reply(f"Полученные ID студентов: {data['student_ids']}")
                    await display_results(session, message, data['student_ids'][:3])
                else:
                    await message.reply("Ошибка при обработке файла.")

async def display_results(session, message, student_ids):
    results = []
    for student_id in student_ids:
        async with session.post(f'{BASE_URL}/bot_get_student_performance', data={'student_id': student_id}) as response:
            # print(response)
            if response.status == 200:
                # print(response.status)
                # print(dir(response))
                # print(type(student_id))
                data = await response.json()
                # print(data)
                result = f"ID: {student_id}\n"
                for performance in data[student_id]:
                    result += f"Курс: {performance[0]}, Предсказанная оценка: {performance[1]}, Настоящаяя оценка: {performance[2]}\n"
                result += (f'accuracy: {data["acc"]} \n Пересдач в действительности: {data["c_in_true"]} \n Пересдач предсказано: {data["c_in_predict"]}\n')
                results.append(result)

            else:
                results.append(f"Ошибка при получении данных для студента ID {student_id}")
    await message.reply("\n\n".join(results))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
