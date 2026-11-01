1. Открыть Routing → VRF.
2. Включить Edit Mode → нажать Add.
3. В окне «Creating VRF» ввести Name (по умолчанию генерируется vrf_xxxxxxxx; после создания имя не меняется) → Create — откроется карточка VRF.
4. В карточке настроить:
    - Interfaces — выбрать интерфейсы, которые войдут в VRF;
    - Description;
    - Лимиты Max Route для BGP/OSPF/IS-IS отдельно для IPv4 и IPv6 (0 = без лимита);
    - RD (route distinguisher, формат N:nn или A.B.C.D:nn);
    - Route-target: добавить Export и Import RT (кнопка «+», формат N:nn или A.B.C.D:nn).
5. (Альтернатива привязки порта) В карточке интерфейса (Interfaces → Physical) выбрать нужный VRF в поле VRF → Save.
6. Нажать Apply.