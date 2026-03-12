from dataclasses import dataclass


REFERRAL_BONUS = 25


@dataclass(frozen=True, slots=True)
class Task:
    task_id: int
    title: str
    description: str
    reward: int


TASKS: dict[int, Task] = {
    1: Task(1, "Задание 1", "Подпишитесь на канал проекта.", 20),
    2: Task(2, "Задание 2", "Пригласите хотя бы 1 друга по реферальной ссылке.", 30),
    3: Task(3, "Задание 3", "Откройте раздел магазина и выберите любой товар.", 15),
}


@dataclass(frozen=True, slots=True)
class Product:
    product_id: str
    title: str
    description: str
    price: int


PRODUCTS: dict[str, Product] = {
    "vip": Product("vip", "Купить VIP", "VIP-статус на 30 дней.", 100),
    "bonus": Product("bonus", "Купить бонус", "Разовый бонус +50 к очкам активности.", 50),
    "withdraw": Product("withdraw", "Вывести средства", "Заявка на вывод средств (демо).", 200),
}
