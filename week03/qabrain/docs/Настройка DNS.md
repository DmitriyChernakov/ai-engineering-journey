Общие настройки:
  1. Открыть Services → DNS.
  2. Включить Edit Mode → нажать Common Settings.
  3. Задать Minimum record TTL, sec → Save.
  Резолвер (Forwarder, настраивается для каждого VRF):
  4. На вкладке Resolvers нажать Add.
  5. Выбрать VRF, при необходимости Source Address (по умолчанию Default).
  6. В блоке DNS Servers (до 8 адресов) ввести IP в первую строку; дополнительные — кнопкой Add Server.
  7. Нажать Add. Включить/выключить резолвер можно тумблером On/Off в таблице.

  Статические записи (локальный резолвинг имён устройства):
  8. Перейти на вкладку Static Records → Add.
  9. Ввести Domain Name и IP Address → Add.
  10. Нажать Apply.