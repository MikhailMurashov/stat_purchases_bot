## Statistic Of Purchases Bot

[@stat_purchases_bot](https://t.me/stat_purchases_bot)

Бот позволяет вести статистику покупок. Нужно просто отправить ему фотографию чека с QR-кодом.

**Список команд:**
* /sum или "Сумма" - показать общую сумму по всем покупкам
* /today или "Сегодня" - показать сумму за сегодня
* /month или "Месяц" - показать сумму за текущий месяц
* /clean - очистить всю статистику
* /help или "Список команд" - показать список команд

Чтобы показать сумму за конкретный день, нужно ввести дату в формате "ДД.ММ.ГГГГ".

### TODO

* приватное поле items в классе CashVoucher
* метод get для каждой покупки в классе user
* ~~сделать возможность присылать дату для суммы за день~~
* ~~сохранение всех покупок в файле (чтобы при перезапуске бота, они не терялись)~~
* обработка добавления чека, который уже есть в базе
* ~~возможность просмотра суммы за текущий месяц~~
* просмотр суммы за неделю **???**
* ~~вместо команд сделать запросы текстом~~
* удаление статистики за день (вчера, сегодня, по дате)
* удаление последнего чека
* подтверждение удаления статистики
