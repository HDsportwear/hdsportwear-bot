# HD Sportwear Telegram Bot

Версия 1.1 официального Telegram-бота HD Sportwear.

## Railway variables

Обязательные:

- `BOT_TOKEN` — новый токен BotFather.
- `ADMIN_CHAT_ID` — `8279849914`.
- `PAYMENT_GROUP_ID` — ID закрытой группы оплат. Пока можно поставить `8279849914`.

Дополнительные:

- `COMPANY_NAME` — `HD Sportwear`
- `SITE_URL` — `https://hdsportwear.shop`
- `MANAGER_URL` — `https://t.me/Danil_HDsportwear`
- `PAYMENT_RECIPIENT` — `ФОП Харланов Даніїл Едуардович`
- `PAYMENT_IBAN` — `UA373006140000026008500528004`
- `PAYMENT_BANK` — `АТ «КРЕДІ АГРІКОЛЬ БАНК»`
- `PAYMENT_TAX_ID` — `2988707315`
- `DISCOUNT_UAH` — `100`

## Как узнать ID группы

1. Сначала временно укажите `PAYMENT_GROUP_ID=8279849914`.
2. Запустите бота.
3. Добавьте бота в закрытую группу.
4. В группе отправьте `/chatid`.
5. Полученное отрицательное число вставьте в `PAYMENT_GROUP_ID`.

## Изменения 1.1

- вместо слова «Пропустити» используется «Далі»;
- старое слово «Пропустити» всё ещё принимается для совместимости.
