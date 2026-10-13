import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Замените на ваш токен от @BotFather
BOT_TOKEN = "8693301880:AAHy4tzecwSMEFoQe-XaJI78REXf-I368NY"

dp = Dispatcher()

# --- Клавиатура для оплаты ---
def get_stars_keyboard():
    builder = InlineKeyboardBuilder()
    # Кнопка с pay=True автоматически создает кнопку оплаты в инвойсе
    builder.button(text="Оплатить 1 ⭐", pay=True)
    return builder.as_markup()

# --- Команда /start ---
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы получить звезды Telegram:"
    )

# --- Кнопка "Получить звезды" ---
@dp.message(F.text == "Получить звезды")
async def send_invoice_handler(message: Message) -> None:
    # В Telegram Stars 1 звезда = 100 единиц (центов)
    prices = [LabeledPrice(label="1 Звезда", amount=100)]

    await message.answer_invoice(
        title="Покупка звезд",
        description="Оплатите 1 звезду Telegram",
        provider_token="",  # Для Stars оставляем пустым [citation:4]
        currency="XTR",     # Код валюты для Telegram Stars [citation:4][citation:8]
        prices=prices,
        payload="stars_payment_1",  # Уникальный ID для отслеживания
        reply_markup=get_stars_keyboard()
    )

# --- Обработчик pre_checkout_query (обязательный шаг) ---
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    # Подтверждаем возможность оплаты
    await pre_checkout_query.answer(ok=True)

# --- Обработчик успешной оплаты ---
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: Message) -> None:
    payment = message.successful_payment

    if payment.currency == "XTR":
        # В XTR amount = 100 равняется 1 звезде [citation:16]
        stars_count = payment.total_amount // 100
        await message.answer(
            f"✅ Спасибо! Вы успешно получили {stars_count} ⭐!\n"
            f"ID транзакции: {payment.telegram_payment_charge_id}"
        )
    else:
        await message.answer(f"Платеж получен: {payment.total_amount} {payment.currency}")

# --- Запуск бота ---
async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
