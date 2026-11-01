1. Shared Objects → Access Lists → включить Edit Mode → Add.
2. Ввести Name ACL (после создания не меняется) → Create.
3. В карточке ACL заполнить Description → нажать Create Rule → ввести индекс правила (1–4094) → Create.
4. В правиле: включить Enable, выбрать Permit/Deny.
5. Нажать Add Match, в списке Match выбрать тип и заполнить Parameter: Source address, Destination address, Protocol, Source port/Destination port (доступны после выбора   протокола), VLAN, Source MAC, Destination MAC, DSCP, CoS, IP precedence. Повторить для добавления нескольких условий.
6. Нажать Save, затем Apply.

  Группы объектов для условий создаются в Shared Objects → Object Groups (Addresses and Ports, Applications, MAC, Networks, Domain Names, Services, URL, Content Filter).