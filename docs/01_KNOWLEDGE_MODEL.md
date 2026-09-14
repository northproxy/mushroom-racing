# Mushroom Finder — базовая модель знаний для приложения

## Статус документа

**Версия:** 0.1  
**Дата:** 2026-09-13  
**Назначение:** базовый knowledge/model specification для приложения по поиску грибов в Австрии.  
**Текущий основной вид:** белый гриб / Steinpilz, прежде всего **Boletus edulis / Fichten-Steinpilz**, с учётом близких видов группы Steinpilze.  
**Географический фокус текущего исследования:** радиус до ~150 км от Вены.

---

# 1. Цель приложения

Приложение должно помогать пользователю не просто видеть лес на карте, а оценивать:

> **насколько конкретный лесной участок подходит для появления определённого вида грибов именно сейчас.**

Для этого модель должна объединять:

- вид гриба;
- древесные породы;
- тип леса;
- геологию;
- почвы;
- кислотность;
- питательность почвы;
- высоту;
- экспозицию склона;
- рельеф;
- влажность;
- осадки;
- температуру;
- сезон;
- историческую засуху;
- возраст и структуру леса;
- признаки растительности;
- юридические ограничения;
- доступность;
- пользовательские полевые наблюдения.

Приложение должно постепенно переходить:

**регион → лесной массив → участок → склон → конкретная зона поиска → пользовательские находки.**

---

# 2. Главный принцип модели

Нельзя использовать только одно правило типа:

> «Был дождь → через две недели будут грибы».

Вероятность появления грибов должна оцениваться как сочетание:

1. **Habitat suitability** — подходит ли место в принципе.
2. **Current fruiting conditions** — подходят ли текущие погодные условия.
3. **Timing** — прошло ли правильное время после накопления влаги.
4. **Local microclimate** — сохраняет ли конкретный склон влагу.
5. **Species ecology** — есть ли нужные деревья-хозяева и тип почвы.
6. **Legal/access layer** — разрешён ли сбор и реально ли попасть на участок.
7. **Observed evidence** — пользовательские находки и полевые признаки.

---

# 3. Виды Steinpilz, которые важно различать

Под разговорным словом **Steinpilz** могут подразумеваться разные близкие виды.

## 3.1 Boletus edulis / Fichten-Steinpilz

Основной вид текущей модели.

### Основные деревья-хозяева

Приоритет:

1. **Fichte — ель**
2. **Buche — бук**
3. **Tanne — пихта**
4. **Eiche — дуб**
5. **Kiefer — сосна**

Дополнительно:

- Birke — берёза

### Типичные условия

- хвойные и смешанные леса;
- кислые или нейтральные почвы;
- часто бедные питательными веществами;
- влажная лесная подстилка;
- развитая микориза со взрослыми деревьями.

---

## 3.2 Sommersteinpilz — Boletus reticulatus / aestivalis

Более теплолюбивый и ранний.

Особенно важны:

- **Eiche**
- **Buche**

Чаще интересен:

- конец весны;
- начало и середина лета;
- тёплые лиственные леса.

---

## 3.3 Kiefern-Steinpilz — Boletus pinophilus

Особенно связан с:

- Kiefer;
- иногда другими хвойными.

---

## 3.4 Bronzeröhrling — Boletus aereus

Более теплолюбивый.

Чаще связан с:

- дубовыми лесами;
- тёплыми участками;
- более южными или паннонскими условиями.

---

# 4. Деревья и микориза

Белые грибы — **эктомикоризные**.

Это значит:

- грибница связана с корнями деревьев;
- возраст и устойчивость леса важны;
- зрелые деревья часто ценнее молодых посадок;
- сильные рубки могут нарушать грибницу;
- смешанный зрелый лес часто перспективнее искусственной монокультуры.

## Практическая модель

### Очень хорошо

- Fichte + Buche
- Fichte + Tanne + Buche
- зрелая Fichte с мхом
- Buche с примесью Fichte/Tanne
- взрослый лес с разными возрастами деревьев

### Хорошо

- Eiche + Buche
- Kiefer + кислый подлесок
- смешанный хвойно-лиственный лес

### Слабее

- очень молодая посадка;
- интенсивно расчищенный лес;
- недавно сильно вырубленный участок;
- открытая лесосека.

---

# 5. Почвы и геология

## 5.1 Общий принцип

Для классического Boletus edulis особенно интересны:

- кислые;
- слабокислые;
- нейтральные;
- относительно бедные питательными веществами почвы.

---

## 5.2 Хорошие геологические признаки

Как proxy для кислотности можно использовать геологию.

### Часто перспективно

- Granit
- Gneis
- Schiefer
- Quarzit
- silikatischer Sandstein
- Flysch-Sandstein
- Podsol
- podsolige Böden

### Часто слабее

- Kalk
- Dolomit
- сильно карбонатные почвы

Это не абсолютное правило.

Даже в известняковых районах могут существовать:

- кислые карманы;
- моренные отложения;
- силикатные наносы;
- локальные бескарбонатные почвы.

---

# 6. Растения-индикаторы

Полевые растения могут использоваться как быстрый proxy состава почвы.

## Положительные индикаторы

Особенно полезны:

- **Moos — мох**
- **Heidelbeere — черника**
- **Heidekraut — вереск**
- Luzula
- редкий травяной покров

### Сильная сигнатура

> Fichte + Moos + Heidelbeere + редкая трава

Это один из лучших визуальных паттернов для текущей модели.

---

## Отрицательные индикаторы

Снижают приоритет:

- **Brennnessel — крапива**
- **Brombeere — ежевика**
- очень высокая густая трава
- растения, указывающие на богатую азотом почву

Но:

> наличие крапивы или ежевики не означает абсолютный ноль вероятности.

Это **negative weight**, а не жёсткий запрет.

---

# 7. Влага и осадки

## 7.1 Основная идея

Для грибов важен не единичный дождь, а:

> **история влажности почвы за несколько недель.**

Поэтому приложение не должно использовать только precipitation_last_24h.

Нужны агрегаты:

- 24h
- 3 days
- 7 days
- 14 days
- 21 days
- 28 days

---

## 7.2 Практический ориентир

30 л/м² = 30 мм осадков.

Но 30 мм не являются магическим порогом.

### Возможные сценарии

**Лучше:**

5 + 8 + 12 + 9 мм за несколько дней

чем:

35 мм за один короткий ливень

если после него всё быстро высохло.

---

## 7.3 После длительной засухи

После сухого лета первые:

**20–30 мм**

могут просто восстановить влагозапас почвы.

Следовательно, приложение должно учитывать:

- осадки предыдущих месяцев;
- drought_index;
- soil_moisture_anomaly;
- cumulative_deficit.

---

# 8. Временная задержка после дождя

Базовая полевая эвристика:

> хорошее увлажнение → потенциальный Schub примерно через 7–20 дней.

### Часто полезный ориентир

- 7–10 дней — ранняя реакция;
- 10–14 дней — классическое окно;
- 12–18 дней — очень интересное окно;
- до ~20 дней после глубокой засухи.

Нельзя привязываться к одной фиксированной цифре.

---

# 9. Температура

Для Boletus edulis перспективным считается продолжительный умеренно прохладный период.

Рабочий диапазон:

**~10–16 °C**

Особенно интересен период около:

**~13 °C средней температуры**

в течение нескольких недель.

В приложение полезно добавить:

- avg_temp_7d
- avg_temp_14d
- avg_temp_20d
- min_temp
- max_temp
- hot_days_count
- frost_event

---

# 10. Высота

Высота важна не сама по себе, а через:

- температуру;
- влажность;
- состав деревьев;
- скорость высыхания.

Для текущих лучших австрийских районов интересны:

### Wechsel

**~650–1 250 м**

### Semmering

**~700–1 300 м**

### западный Wienerwald

**~350–850 м**

Для приложения высота должна быть непрерывным параметром, а не жёсткой категорией.

---

# 11. Экспозиция склона

После жаркого и сухого периода большое значение имеет ориентация склона.

## Обычно лучше

- N
- NE
- NW
- иногда W

Причины:

- меньше прямого солнца;
- ниже испарение;
- медленнее высыхает подстилка;
- выше локальная влажность.

## Обычно хуже после засухи

- S
- SE
- SW

Особенно:

- открытые;
- крутые;
- без плотного лесного покрова.

---

# 12. Рельеф и микроклимат

Очень перспективны:

- ложбины;
- небольшие долины;
- глубокие лесные овраги;
- нижняя треть северного склона;
- участки возле ручьёв без заболачивания;
- места с длительно влажной лесной подстилкой.

Пример:

**Göstritzgraben** в районе Semmering интересен не только осадками, но и геометрией долины:

- меньше солнца;
- вода собирается с большой площади;
- выше влажность;
- медленнее испарение.

---

# 13. Сезонность

Грибной сезон состоит не из одного непрерывного периода, а из **волн / Schübe / flushes**.

В хороший год возможны:

## Волна 1

конец мая / июнь

Особенно Sommersteinpilz.

## Волна 2

июль / август

если хватает влаги.

## Волна 3

конец августа / сентябрь / октябрь

обычно наиболее важная для классического Steinpilz.

---

# 14. Погодный контекст 2026

2026 год оказался очень сухим.

Для модели текущего сезона важно учитывать:

- экстремально жаркое лето;
- сильный общий дефицит осадков;
- особенно сухой Waldviertel;
- первые осенние дожди не везде означают немедленный Schub.

Вывод:

> одна и та же сумма дождя после нормального лета и после экстремальной засухи имеет разное значение.

---

# 15. Основные картографические слои для приложения

Приложение должно объединять несколько независимых слоёв.

## 15.1 Forest cover

Нужно знать:

- лес / не лес;
- плотность кроны;
- размеры непрерывного массива.

---

## 15.2 Tree species / Baumartenmischung

Нужно определять:

- Fichte
- Buche
- Tanne
- Eiche
- Kiefer
- Birke
- Lärche
- прочие

Полезно хранить:

- dominant_species
- species_mix
- conifer_ratio
- deciduous_ratio

---

## 15.3 Soil

Желательные поля:

- pH
- nutrient_level
- humus
- soil_type
- permeability
- moisture_capacity
- carbonate_content

---

## 15.4 Geology

Нужно хранить:

- bedrock_type
- silicate_vs_carbonate
- geology_confidence

---

## 15.5 DEM / Elevation

Поля:

- elevation_m
- slope_deg
- aspect_deg
- terrain_position

---

## 15.6 Hydrology

Полезны:

- streams
- springs
- wet depressions
- drainage density
- distance_to_stream

---

## 15.7 Weather

Минимум:

- precipitation 24h
- precipitation 3d
- precipitation 7d
- precipitation 14d
- precipitation 21d
- precipitation 28d
- avg temperature
- min/max temperature
- humidity
- wind
- soil moisture, если доступна

---

## 15.8 Drought

Нужны:

- rainfall anomaly
- historical precipitation deficit
- soil moisture anomaly
- drought index

---

## 15.9 Protected areas

Нужно хранить:

- protected_area_type
- collecting_allowed
- off_trail_allowed
- seasonal_restrictions

---

## 15.10 Access

- nearest legal parking
- forest roads
- hiking paths
- public transport
- private road restrictions

---

# 16. Важные источники данных

## Леса

**BFW — Österreichische Waldinventur**

Полезно для:

- Waldfläche
- Baumarten
- Mischwald
- forest structure

URL:

https://www.bfw.gv.at/fachinstitute/waldinventur/

---

## Почвы Niederösterreich

**BFW — Bodenkarte Niederösterreich**

URL:

https://www.bfw.gv.at/bodenkarte-niederoesterreich/

Важно:

обычная eBOD / bodenkarte.at преимущественно ориентирована на сельскохозяйственные почвы.

---

## Геология

**GeoSphere Austria**

URL:

https://www.geosphere.at/

---

## Осадки и климат

**GeoSphere Austria**

и региональные станции.

В предыдущем исследовании использовался также:

https://regenmenge.spqrk.at/

---

## Природоохранные территории

**Biosphärenpark Wienerwald**

https://www.bpww.at/

Kernzonen:

https://kernzonen.bpww.at/

---

## Waldentwicklungspläne / Naturschutz

**Land Niederösterreich**

https://www.noe.gv.at/

---

# 17. Юридический слой

Приложение обязательно должно предупреждать пользователя о правилах.

## Общий принцип

В Австрии сбор грибов для личных нужд обычно ограничен:

**до 2 кг на человека в день**

если владелец леса или локальные правила не устанавливают более строгие ограничения.

---

## Wienerwald Kernzonen

В Kernzonen Biosphärenpark Wienerwald:

> **сбор грибов запрещён.**

Во многих Kernzonen также нельзя свободно сходить с разрешённых маршрутов.

Это должен быть **hard exclusion layer**.

---

# 18. Основные исследованные регионы

---

# 18.1 Wechsel

## Общая оценка

**Очень высокий потенциал.**

Причины:

- Fichte;
- Tanne;
- Buche;
- силикатный субстрат;
- высота;
- прохладный климат;
- хорошая влажность в сентябре 2026.

---

## Лучшие рабочие участки

### W1 — Kampstein → Mariensee

**Оценка:** ~9.5/10

Целевая зона:

- 1000–1250 м;
- N/NE;
- лес ниже открытых Schwaigen.

Индикаторы:

- Fichte;
- Buche/Tanne;
- Moos;
- Heidelbeere.

---

### W2 — Mariensee → Kampsteiner Schwaig

**Оценка:** ~9.4/10

Целевая высота:

**850–1200 м**

Особенно интересны:

- прохладные боковые склоны;
- понижения;
- зоны ниже открытых лугов.

---

### W3 — St. Corona → Ödenhof → Kampstein

**Оценка:** ~9.3/10

Интересен длинный вертикальный профиль:

**~950–1250 м**

---

### W4 — Mariensee → Hallerhaus

**Оценка:** ~9.2/10

Не искать на открытых лыжных трассах.

Интересны лесные полосы по сторонам.

---

### W5 — Orthof → Antrittsstein / Almrauschhütte

**Оценка:** ~9.2/10

Особенно теневые смешанные леса.

---

### W6 — Unternberg → Neuwaldhütte

**Оценка:** ~9.1/10

Лучше всего:

**~900–1150 м**

---

### W7 — Mönichkirchner Schwaig → Hallerhaus

**Оценка:** ~9.1/10

Лучше нижняя лесистая часть.

---

### W8 — Mönichkirchen → Mönichkirchner Schwaig

**Оценка:** ~8.7/10

Минус:

- больше туристической;
- лыжной;
- дорожной инфраструктуры.

---

### W9 — Kampsteiner Schwaig → Feistritzer Schwaig

**Оценка:** ~8.7/10

Высоко и прохладно, но слишком много открытых зон.

---

### W10 — Trattenbach → Feistritzsattel

**Оценка:** ~8.6/10

Лучше теневые леса ниже седловины.

---

### W11 — Vorauer Schwaig → Studentenkreuz

**Оценка:** ~8.5/10

Лучше нижний лесной пояс.

---

### W12 — Feistritzsattel → Kranichberger Schwaig

**Оценка:** ~8.2/10

Минус:

много высоких открытых участков.

---

# 18.2 Semmering

## Общая оценка

Очень высокий потенциал.

Плюсы:

- хорошие осадки;
- высота;
- прохлада;
- большие лесные массивы.

Минус:

- геология более мозаична;
- рядом силикатные и карбонатные зоны.

---

## Лучшие рабочие участки

### S1 — Göstritzgraben → Kummerbauer

**Оценка:** ~9.4/10

Очень сильный микроклимат:

- глубокая долина;
- удержание влаги;
- большой лес.

Цель:

**850–1100 м**

---

### S2 — Maria Schutz → северный Sonnwendstein

**Оценка:** ~9.3/10

Плюсы:

- северный склон;
- лес;
- высота;
- влажность.

Нужно проверять актуальные лесохозяйственные ограничения.

---

### S3 — Pinkenkogel N/E

**Оценка:** ~9.2/10

Цель:

**950–1200 м**

Лучше лесной пояс, чем вершина.

---

### S4 — Pinkenkogel → Kampalpe / Saurücken

**Оценка:** ~9.0/10

Длинный лесной коридор.

---

### S5 — Hirschenkogel → Erzkogel

**Оценка:** ~8.9/10

Хороший климат.

Минус:

- лыжная инфраструктура;
- дороги;
- антропогенное воздействие.

---

### S6 — Passhöhe → Maria Schutz

**Оценка:** ~8.9/10

Удобный разведывательный переход.

---

### S7 — Erzkogel → Drei Kreuze → Kummerbauer

**Оценка:** ~8.8/10

---

### S8 — Wolfsbergkogel → 20-Schilling-Blick

**Оценка:** ~8.7/10

Искать:

- ложбины;
- N/NW;
- лес вдали от открытых viewpoints.

---

### S9 — Adlitzgraben → Roter Berg

**Оценка:** ~8.7/10

Влажный рельеф.

---

### S10 — Eselstein / Georgswarte → Maria Schutz

**Оценка:** ~8.6/10

---

### S11 — Kalte Rinne / Krauselklause → Breitenstein

**Оценка:** ~8.5/10

Плюсы:

- прохладные ущелья.

Минус:

- сложная геология.

---

### S12 — Kreuzberg NW

**Оценка:** ~8.4/10

Предпочтение:

- северо-западные склоны.

---

# 18.3 Западный Wienerwald

## Общая оценка

Очень хороший habitat potential.

Но в сентябре 2026 основная подпитка дождями пришла позже, чем на Wechsel/Semmering.

Потенциально интересное окно:

**примерно 18–27 сентября 2026**

если не будет резкого высыхания.

---

## Ключевая геология

Западный Wienerwald:

- Flysch;
- Sandstein;
- Mergel;
- Ton.

Особенно интересны более кислые песчаниковые участки.

---

## Лучшие рабочие участки

### WW1 — Schöpfl W/NW от Laaben

**Оценка:** ~9.0/10

Цель:

**600–800 м**

Искать:

- N/NW/W;
- Buche;
- Tanne/Fichte;
- Moos.

Важно:

не заходить в Kernzone Mitterschöpfl.

---

### WW2 — Gföhlberg → Klammhöhe

**Оценка:** ~8.8/10

Большой непрерывный Flysch-лес.

---

### WW3 — Forsthof / Laaben → Schöpfl

**Оценка:** ~8.8/10

Хороший вертикальный профиль.

---

### WW4 — Schöpflgitter → Wienhof → St. Corona am Schöpfl

**Оценка:** ~8.7/10

Следить за границей Kernzone Mitterschöpfl.

---

### WW5 — Hochstraß → Falkensteinerhütte

**Оценка:** ~8.5/10

Большой лесной массив.

Не заезжать на Forststraße без разрешения.

---

### WW6 — Brand-Laaben / Gern–Klamm

**Оценка:** ~8.5/10

Очень высокая лесистость.

---

### WW7 — Kleinkrottenbach → Hasenriegel

**Оценка:** ~8.3/10

Только вне Hainbach/Hengstlberg Kernzone.

---

### WW8 — Rekawinkel → Hochstraße

**Оценка:** ~8.2/10

Плюсы:

- песчаниковый Flysch;
- доступность.

---

### WW9 — Eichgraben → Reisetberg → Stiefelberg

**Оценка:** ~8.0/10

Ниже и теплее.

---

### WW10 — Rekawinkel → Kaiserspitz / Zwickelberg

**Оценка:** ~8.0/10

Интересны кислые песчаниковые участки.

---

### WW11 — Rekawinkel → западный Pressbaum

**Оценка:** ~7.9/10

Избегать Kernzone Sattel.

---

### WW12 — Tullnerbach / Irenental — периферия Troppberg

**Оценка:** ~7.8/10

Важно:

**не заходить в Kernzone Troppberg.**

---

# 19. Другие исследованные регионы

## Dunkelsteinerwald / Jauerling

Потенциал:

**очень высокий**

Причины:

- Granit;
- Gneis;
- Granulit;
- Fichte;
- Tanne;
- Buche.

Основной текущий лимит:

недостаточная влага после сухого лета.

---

## Waldviertel

Потенциал habitat:

**почти идеальный**

Сигнатура:

> Fichte + Heidelbeere + Moose + Podsol + Granit/Gneis

Но сезон 2026:

- сильная засуха;
- местами дефицит осадков до ~70%.

Вывод:

после серьёзного дождевого цикла может быстро стать одним из лучших регионов.

---

## Rax / Schneeberg

Плюс:

- хорошие осадки;
- прохлада.

Минус:

- много Kalk/Dolomit.

Нужно искать локальные кислые участки.

---

## Rosaliengebirge

Интересный компромисс.

Есть:

- Buche;
- Eiche;
- Fichte;
- Rotföhre;
- Lärche.

Минус:

- паннонское влияние;
- суше и теплее.

---

## Leithagebirge

Для классического Boletus edulis слабее.

Но интереснее для:

- Sommersteinpilz;
- Bronzeröhrling;
- дубовых Boletus.

---

# 20. Рейтинг регионов на 13 сентября 2026

| Регион | Деревья | Почва | Влага | Общая оценка |
|---|---:|---:|---:|---:|
| Wechsel / Aspang / Mönichkirchen | 5/5 | 5/5 | 5/5 | 9.5/10 |
| Semmering | 5/5 | 4.5/5 | 5/5 | 9.4/10 |
| западный Wienerwald | 4.5/5 | 4/5 | 4/5 | 8.4/10 |
| Dunkelsteinerwald / Jauerling | 5/5 | 5/5 | 3/5 | 8.2/10 |
| Rosaliengebirge | 4/5 | 4/5 | 4/5 | 8.0/10 |
| Waldviertel / Bärnkopf | 5/5 | 5/5 | 2/5 | 7.7/10 |
| Rax / Puchberg | 4.5/5 | 2.5/5 | 5/5 | 7.5/10 |
| Leithagebirge | 3/5 | 2.5/5 | 2.5/5 | 5.5/10 |

---

# 21. Базовый scoring model

Первая рабочая формула приложения может выглядеть так:

```text
mushroom_probability_score =
    habitat_score
  + moisture_score
  + temperature_score
  + timing_score
  + terrain_score
  + observation_score
  - drought_penalty
  - disturbance_penalty
  - legal_exclusion
```

---

# 22. Предлагаемые веса для Steinpilz v0.1

На основе текущего исследования:

| Фактор | Вес |
|---|---:|
| Tree species / host suitability | 25% |
| Soil + geology | 20% |
| Moisture / rainfall history | 20% |
| Temperature / season | 10% |
| Elevation + aspect + terrain | 10% |
| Forest maturity / disturbance | 5% |
| Field vegetation indicators | 5% |
| User observations | 5% |

Отдельно:

**legal exclusion** должен быть hard filter, а не частью обычного score.

---

# 23. Habitat score

Пример:

```text
Fichte dominant                    +25
Fichte + Buche/Tanne              +30
Buche + Tanne                     +20
Eiche + Buche                     +18
Kiefer + acidic undergrowth       +15
Moos                              +8
Heidelbeere                       +10
Heidekraut                        +6
Brennnessel                       -8
dense Brombeere                   -6
dense tall grass                  -5
recent clearcut                  -15
```

Значения примерные и должны калиброваться по пользовательским данным.

---

# 24. Geology / soil score

Пример:

```text
granit                            +10
gneis                             +10
quarzit                           +9
silicate sandstone               +8
acid flysch                       +7
podsol                            +10
weakly acidic soil               +10
neutral soil                     +6
limestone                         -5
dolomite                          -5
high carbonate soil              -8
```

---

# 25. Moisture score

Не использовать только одну сумму осадков.

Пример набора признаков:

```text
rain_3d
rain_7d
rain_14d
rain_21d
rain_28d
soil_moisture
rainfall_anomaly_90d
drought_index
```

Важна нелинейность:

30 мм после нормального месяца ≠ 30 мм после трёх месяцев засухи.

---

# 26. Timing score

Примерная кривая после значимого увлажнения:

```text
0–3 days      низко
4–6 days      растёт
7–10 days     хорошо
10–16 days    очень хорошо
17–20 days    хорошо
>20 days      зависит от последующих дождей и температуры
```

Это должна быть **плавная функция**, а не if/else.

---

# 27. Aspect score

После жаркого лета:

```text
N      +10
NE     +9
NW     +9
W      +5
E      +3
SE      0
SW     -4
S      -6
```

При прохладной влажной погоде влияние aspect должно ослабевать.

---

# 28. Terrain score

```text
shaded hollow             +8
stream valley             +6
lower north slope         +6
closed mature canopy      +5
open ridge                -5
ski slope                 -8
clearcut                  -12
dry exposed ridge         -10
```

---

# 29. Полевое наблюдение пользователя

Это критически важный слой для будущей модели.

Каждая поездка должна сохраняться как observation.

## Поля observation

```yaml
observation_id:
user_id:
date_time:
latitude:
longitude:
species:
species_confidence:
count:
photo:
elevation:
aspect:
slope:
forest_type:
dominant_trees:
secondary_trees:
moss_present:
blueberry_present:
heather_present:
nettle_present:
blackberry_present:
grass_density:
soil_surface_moisture:
soil_moisture_5cm:
recent_rain_estimate:
temperature:
canopy_density:
forest_maturity:
disturbance:
notes:
```

---

# 30. Даже отсутствие грибов — данные

Очень важно сохранять **negative observations**:

> участок проверен, но грибов нет.

Без этого модель будет страдать selection bias.

Поля:

```yaml
searched_minutes:
searched_area_estimate:
found_target_species: false
other_mushrooms_found:
soil_wetness:
weather:
```

---

# 31. Пользовательская карта грибницы

После нескольких находок приложение должно выявлять:

- recurring hotspot;
- высотный пояс;
- preferred aspect;
- preferred tree mix;
- recurring time lag after rain.

Например:

> на данном склоне белые регулярно появляются между 1030 и 1160 м на NE-экспозиции через 10–14 дней после 30–50 мм осадков.

Это намного ценнее общей публичной карты.

---

# 32. Алгоритм маршрута поиска

Вместо «ехать в лес X» приложение должно eventually давать сценарий:

1. припарковаться в разрешённой точке;
2. подняться по дороге/тропе;
3. войти в целевой высотный пояс;
4. перейти на N/NE склон;
5. искать Fichte + Buche/Tanne;
6. проверить наличие Moos/Heidelbeere;
7. проверить влажность подстилки;
8. при первой находке двигаться примерно по горизонтали;
9. сохранять находки и пустые участки.

---

# 33. Почему после первой находки полезно идти по горизонтали

Если гриб найден, это означает, что совпали:

- почва;
- влажность;
- дерево-хозяин;
- высота;
- экспозиция;
- микроклимат.

Эти условия часто продолжаются вдоль одной горизонтали.

Поэтому приложение может предлагать:

> explore_same_elevation_band()

---

# 34. Минимальная сущность Forest Spot

```yaml
spot_id:
name:
latitude:
longitude:
region:
country:
elevation_min:
elevation_max:
dominant_aspect:
forest_type:
tree_species:
geology:
soil_type:
soil_ph:
nutrient_level:
moss_probability:
blueberry_probability:
canopy_density:
forest_age_class:
disturbance_level:
nearest_stream_m:
protected_area:
collecting_allowed:
legal_notes:
parking:
access_notes:
habitat_score:
current_weather_score:
final_score:
confidence:
last_updated:
```

---

# 35. Минимальная сущность Weather Snapshot

```yaml
spot_id:
date:
rain_24h:
rain_3d:
rain_7d:
rain_14d:
rain_21d:
rain_28d:
rain_90d:
rain_anomaly:
avg_temp_7d:
avg_temp_14d:
avg_temp_20d:
soil_moisture:
humidity:
wind:
drought_index:
```

---

# 36. Минимальная сущность Species Profile

```yaml
species_id:
latin_name:
common_name:
german_name:
host_trees:
preferred_soil:
preferred_ph:
preferred_geology:
preferred_elevation:
preferred_temperature:
preferred_season:
rain_response_window:
positive_indicator_plants:
negative_indicator_plants:
habitat_notes:
```

---

# 37. Минимальная сущность Legal Zone

```yaml
zone_id:
name:
type:
geometry:
collecting_allowed:
max_quantity_kg:
off_trail_allowed:
vehicle_access:
seasonal_rules:
source:
last_checked:
```

---

# 38. Confidence score

Любой прогноз должен иметь не только вероятность, но и качество данных.

Пример:

```text
prediction_score: 82/100
confidence: 61/100
```

Причины низкого confidence:

- неизвестный состав леса;
- старая карта;
- нет soil moisture;
- нет точной геологии;
- нет пользовательских наблюдений.

---

# 39. Источники ошибок модели

Приложение должно учитывать:

- карты лесных пород могут быть слишком грубыми;
- геология ≠ точная почва;
- дождь на ближайшей станции ≠ дождь на конкретном склоне;
- влажность резко меняется по экспозиции;
- лесохозяйственные работы могут быть свежими;
- грибы плодоносят локально и неравномерно;
- отсутствие находки не доказывает отсутствие грибницы;
- виды Boletus нельзя всегда надёжно различить без проверки.

---

# 40. MVP приложения

Первый MVP может быть очень простым.

## Экран 1 — карта

Показывает участки:

- green
- yellow
- red

по текущему Steinpilz score.

---

## Экран 2 — карточка участка

Показывает:

- итоговый score;
- confidence;
- деревья;
- почву;
- geology;
- высоту;
- aspect;
- rain 14d;
- rain 28d;
- temperature;
- legal status;
- лучший временной интервал;
- почему место получило такой score.

---

## Экран 3 — field report

Пользователь отмечает:

- нашёл / не нашёл;
- вид;
- количество;
- фото;
- растения;
- влажность;
- лес;
- высоту;
- заметки.

---

# 41. Explainable AI

Очень важно не показывать пользователю только:

> 87%

Нужно объяснять:

**Почему:**

- + Fichte/Buche/Tanne
- + кислый силикат
- + 44 мм за 14 дней
- + северный склон
- + высота 980–1150 м
- + средняя температура 13.5 °C
- − сильная засуха предыдущих 60 дней
- − часть леса недавно вырублена

---

# 42. Три типа score

Лучше разделить:

## Habitat Score

> насколько участок хорош вообще.

## Current Conditions Score

> насколько хорошие условия сейчас.

## Final Opportunity Score

> насколько разумно ехать туда сегодня.

Пример:

```text
Habitat: 94
Current weather: 72
Access/legal: 100
Confidence: 68

Final opportunity: 84
```

---

# 43. Suggested app architecture

Логически приложение можно разделить на слои.

```text
Species knowledge
        ↓
Static geodata
        ↓
Dynamic weather
        ↓
Legal/access filters
        ↓
Scoring engine
        ↓
User observations
        ↓
Model calibration
        ↓
Map + recommendations
```

---

# 44. Главный принцип дальнейшей разработки

Не пытаться сразу создать «AI, который знает, где грибы».

Сначала построить прозрачную модель:

> **ecology + geodata + weather + observations**

и только потом использовать ML для калибровки весов.

Первые версии могут быть полностью rule-based.

Это даст:

- объяснимость;
- возможность отладки;
- понимание ошибок;
- хороший training dataset для будущей ML-модели.

---

# 45. Следующий логичный этап

После этого базового документа стоит создать:

## `SPECIES_MODEL.md`

Подробная модель каждого вида гриба.

## `DATA_SOURCES.md`

Все доступные австрийские источники:

- леса;
- почвы;
- geology;
- elevation;
- rainfall;
- weather;
- protected areas.

## `SCORING_MODEL.md`

Формулы и веса.

## `DATABASE_SCHEMA.md`

Структура БД.

## `MVP.md`

Минимальный функционал приложения.

## `FIELD_PROTOCOL.md`

Как собирать качественные данные в лесу.

---

# 46. Текущий TOP районов для тестирования MVP

Для первых полевых тестов около Вены:

1. **Mariensee / Kampstein**
2. **Göstritzgraben / Maria Schutz**
3. **St. Corona / Mönichkirchen**
4. **Pinkenkogel**
5. **Schöpfl / Laaben**
6. **Gföhlberg / Klammhöhe**

Эти районы хороши тем, что различаются:

- геологией;
- высотой;
- лесным составом;
- микроклиматом;
- текущей влажностью.

Это позволит проверить, насколько правильно работает scoring model.

---

# 47. Главная рабочая гипотеза проекта

Для Steinpilz вероятность плодоношения можно достаточно полезно оценивать через сочетание:

> **дерево-хозяин × почва × накопленная влага × температура × задержка после дождя × высота × экспозиция × структура леса**

а точность модели должна постепенно расти за счёт:

> **реальных пользовательских наблюдений.**

