Создание VLAN:
  1. Открыть Switching → VLAN.
  2. Включить Edit Mode.
  3. Нажать кнопку Add (плюс над таблицей).
  4. В окне «Creating VLAN» ввести ID (один номер, список через запятую или диапазон), при желании Name, выбрать Work Mode: Force Up или Follow the Interface Status.
  5. Нажать Create.
  6. Нажать Apply внизу.

  Изменение/удаление: выделить чекбокс строки → Edit (имя и Work Mode; ID неизменяем) или Remove (с подтверждением; default удалить нельзя). Фильтры — кнопка фильтра (по
  ID/Name/Work Mode).

  Назначение порта в VLAN (L2):
  1. Interfaces → Physical → карточка порта → Mode = Switchport → Save (у порта исчезают L3-поля).

  Интерфейс с тегом VLAN (L3, dot1q-сабинтерфейс):
  2. Interfaces → Physical → кнопка ⋮ в строке порта → Add sub-interface.
  3. Ввести VLAN tag → Create (тег после создания не меняется).
  4. В открывшейся карточке сабинтерфейса задать IP-адрес и прочие L3-настройки (как у обычного интерфейса) → Save.
  5. Нажать Apply.