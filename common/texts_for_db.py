from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Джинсы', 'Ремни']

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Магазин Джинса.\nРежим работы: Пн - Пт(9:00 - 18:00)",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        marker="✅ ",
    ).as_html(),
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}
