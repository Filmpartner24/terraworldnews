#!/usr/bin/env python3
"""Erzeugt fnlib/geo.js: Ländercode -> [Hauptstadt EN, DE, BG, Zeitzone der Hauptstadt].
Zeitzone: aus /usr/share/zoneinfo/zone.tab (bei mehreren Zonen manuell festgelegt)."""
import json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# code: (EN, DE, BG)  – BG/DE leer = wie EN
CAP = {
'AD': ('Andorra la Vella', '', 'Андора ла Веля'), 'AE': ('Abu Dhabi', 'Abu Dhabi', 'Абу Даби'), 'AF': ('Kabul', '', 'Кабул'),
'AG': ("St. John's", '', 'Сейнт Джонс'), 'AL': ('Tirana', '', 'Тирана'), 'AM': ('Yerevan', 'Jerewan', 'Ереван'), 'AO': ('Luanda', '', 'Луанда'),
'AR': ('Buenos Aires', '', 'Буенос Айрес'), 'AT': ('Vienna', 'Wien', 'Виена'), 'AU': ('Canberra', '', 'Канбера'), 'AZ': ('Baku', '', 'Баку'),
'BA': ('Sarajevo', '', 'Сараево'), 'BB': ('Bridgetown', '', 'Бриджтаун'), 'BD': ('Dhaka', 'Dhaka', 'Дака'), 'BE': ('Brussels', 'Brüssel', 'Брюксел'),
'BF': ('Ouagadougou', '', 'Уагадугу'), 'BG': ('Sofia', 'Sofia', 'София'), 'BH': ('Manama', '', 'Манама'), 'BI': ('Gitega', '', 'Гитега'),
'BJ': ('Porto-Novo', '', 'Порто Ново'), 'BN': ('Bandar Seri Begawan', '', 'Бандар Сери Бегаван'), 'BO': ('Sucre', '', 'Сукре'),
'BR': ('Brasília', '', 'Бразилия'), 'BS': ('Nassau', '', 'Насау'), 'BT': ('Thimphu', '', 'Тхимпху'), 'BW': ('Gaborone', '', 'Габороне'),
'BY': ('Minsk', '', 'Минск'), 'BZ': ('Belmopan', '', 'Белмопан'), 'CA': ('Ottawa', '', 'Отава'), 'CD': ('Kinshasa', '', 'Киншаса'),
'CF': ('Bangui', '', 'Банги'), 'CG': ('Brazzaville', '', 'Бразавил'), 'CH': ('Bern', '', 'Берн'), 'CI': ('Yamoussoukro', '', 'Ямусукро'),
'CL': ('Santiago', 'Santiago de Chile', 'Сантяго'), 'CM': ('Yaoundé', 'Yaoundé', 'Яунде'), 'CN': ('Beijing', 'Peking', 'Пекин'),
'CO': ('Bogotá', '', 'Богота'), 'CR': ('San José', '', 'Сан Хосе'), 'CU': ('Havana', 'Havanna', 'Хавана'), 'CV': ('Praia', '', 'Прая'),
'CY': ('Nicosia', 'Nikosia', 'Никозия'), 'CZ': ('Prague', 'Prag', 'Прага'), 'DE': ('Berlin', 'Berlin', 'Берлин'), 'DJ': ('Djibouti', 'Dschibuti', 'Джибути'),
'DK': ('Copenhagen', 'Kopenhagen', 'Копенхаген'), 'DM': ('Roseau', '', 'Розо'), 'DO': ('Santo Domingo', '', 'Санто Доминго'), 'DZ': ('Algiers', 'Algier', 'Алжир'),
'EC': ('Quito', '', 'Кито'), 'EE': ('Tallinn', '', 'Талин'), 'EG': ('Cairo', 'Kairo', 'Кайро'), 'ER': ('Asmara', '', 'Асмара'),
'ES': ('Madrid', '', 'Мадрид'), 'ET': ('Addis Ababa', 'Addis Abeba', 'Адис Абеба'), 'FI': ('Helsinki', '', 'Хелзинки'), 'FJ': ('Suva', '', 'Сува'),
'FM': ('Palikir', '', 'Паликир'), 'FR': ('Paris', '', 'Париж'), 'GA': ('Libreville', '', 'Либревил'), 'GB': ('London', '', 'Лондон'),
'GD': ("St. George's", '', 'Сейнт Джорджис'), 'GE': ('Tbilisi', 'Tiflis', 'Тбилиси'), 'GH': ('Accra', '', 'Акра'), 'GM': ('Banjul', '', 'Банджул'),
'GN': ('Conakry', '', 'Конакри'), 'GQ': ('Malabo', '', 'Малабо'), 'GR': ('Athens', 'Athen', 'Атина'), 'GT': ('Guatemala City', 'Guatemala-Stadt', 'Гватемала'),
'GW': ('Bissau', '', 'Бисау'), 'GY': ('Georgetown', '', 'Джорджтаун'), 'HN': ('Tegucigalpa', '', 'Тегусигалпа'), 'HR': ('Zagreb', '', 'Загреб'),
'HT': ('Port-au-Prince', '', 'Порт о Пренс'), 'HU': ('Budapest', '', 'Будапеща'), 'ID': ('Jakarta', '', 'Джакарта'), 'IE': ('Dublin', '', 'Дъблин'),
'IL': ('Jerusalem', '', 'Йерусалим'), 'IN': ('New Delhi', 'Neu-Delhi', 'Ню Делхи'), 'IQ': ('Baghdad', 'Bagdad', 'Багдад'), 'IR': ('Tehran', 'Teheran', 'Техеран'),
'IS': ('Reykjavík', '', 'Рейкявик'), 'IT': ('Rome', 'Rom', 'Рим'), 'JM': ('Kingston', '', 'Кингстън'), 'JO': ('Amman', '', 'Аман'),
'JP': ('Tokyo', 'Tokio', 'Токио'), 'KE': ('Nairobi', '', 'Найроби'), 'KG': ('Bishkek', 'Bischkek', 'Бишкек'), 'KH': ('Phnom Penh', '', 'Пном Пен'),
'KI': ('Tarawa', '', 'Тарава'), 'KM': ('Moroni', '', 'Морони'), 'KN': ('Basseterre', '', 'Бастер'), 'KP': ('Pyongyang', 'Pjöngjang', 'Пхенян'),
'KR': ('Seoul', '', 'Сеул'), 'KW': ('Kuwait City', 'Kuwait-Stadt', 'Кувейт'), 'KZ': ('Astana', '', 'Астана'), 'LA': ('Vientiane', '', 'Виентян'),
'LB': ('Beirut', '', 'Бейрут'), 'LC': ('Castries', '', 'Кастрийс'), 'LI': ('Vaduz', '', 'Вадуц'), 'LK': ('Colombo', '', 'Коломбо'),
'LR': ('Monrovia', '', 'Монровия'), 'LS': ('Maseru', '', 'Масеру'), 'LT': ('Vilnius', '', 'Вилнюс'), 'LU': ('Luxembourg', 'Luxemburg', 'Люксембург'),
'LV': ('Riga', '', 'Рига'), 'LY': ('Tripoli', 'Tripolis', 'Триполи'), 'MA': ('Rabat', '', 'Рабат'), 'MC': ('Monaco', '', 'Монако'),
'MD': ('Chișinău', 'Chișinău', 'Кишинев'), 'ME': ('Podgorica', '', 'Подгорица'), 'MG': ('Antananarivo', '', 'Антананариво'), 'MH': ('Majuro', '', 'Маджуро'),
'MK': ('Skopje', '', 'Скопие'), 'ML': ('Bamako', '', 'Бамако'), 'MM': ('Naypyidaw', '', 'Нейпидо'), 'MN': ('Ulaanbaatar', 'Ulaanbaatar', 'Улан Батор'),
'MR': ('Nouakchott', '', 'Нуакшот'), 'MT': ('Valletta', '', 'Валета'), 'MU': ('Port Louis', '', 'Порт Луи'), 'MV': ('Malé', '', 'Мале'),
'MW': ('Lilongwe', '', 'Лилонгве'), 'MX': ('Mexico City', 'Mexiko-Stadt', 'Мексико'), 'MY': ('Kuala Lumpur', '', 'Куала Лумпур'), 'MZ': ('Maputo', '', 'Мапуто'),
'NA': ('Windhoek', '', 'Виндхук'), 'NE': ('Niamey', '', 'Ниамей'), 'NG': ('Abuja', '', 'Абуджа'), 'NI': ('Managua', '', 'Манагуа'),
'NL': ('Amsterdam', '', 'Амстердам'), 'NO': ('Oslo', '', 'Осло'), 'NP': ('Kathmandu', '', 'Катманду'), 'NR': ('Yaren', '', 'Ярен'),
'NZ': ('Wellington', '', 'Уелингтън'), 'OM': ('Muscat', 'Maskat', 'Мускат'), 'PA': ('Panama City', 'Panama-Stadt', 'Панама'), 'PE': ('Lima', '', 'Лима'),
'PG': ('Port Moresby', '', 'Порт Морсби'), 'PH': ('Manila', '', 'Манила'), 'PK': ('Islamabad', '', 'Исламабад'), 'PL': ('Warsaw', 'Warschau', 'Варшава'),
'PS': ('Ramallah', '', 'Рамала'), 'PT': ('Lisbon', 'Lissabon', 'Лисабон'), 'PW': ('Ngerulmud', '', 'Нгерулмуд'), 'PY': ('Asunción', '', 'Асунсион'),
'QA': ('Doha', '', 'Доха'), 'RO': ('Bucharest', 'Bukarest', 'Букурещ'), 'RS': ('Belgrade', 'Belgrad', 'Белград'), 'RU': ('Moscow', 'Moskau', 'Москва'),
'RW': ('Kigali', '', 'Кигали'), 'SA': ('Riyadh', 'Riad', 'Рияд'), 'SB': ('Honiara', '', 'Хониара'), 'SC': ('Victoria', '', 'Виктория'),
'SD': ('Khartoum', 'Khartum', 'Хартум'), 'SE': ('Stockholm', '', 'Стокхолм'), 'SG': ('Singapore', 'Singapur', 'Сингапур'), 'SI': ('Ljubljana', '', 'Любляна'),
'SK': ('Bratislava', '', 'Братислава'), 'SL': ('Freetown', '', 'Фрийтаун'), 'SM': ('San Marino', '', 'Сан Марино'), 'SN': ('Dakar', '', 'Дакар'),
'SO': ('Mogadishu', 'Mogadischu', 'Могадишу'), 'SR': ('Paramaribo', '', 'Парамарибо'), 'SS': ('Juba', '', 'Джуба'), 'ST': ('São Tomé', '', 'Сао Томе'),
'SV': ('San Salvador', '', 'Сан Салвадор'), 'SY': ('Damascus', 'Damaskus', 'Дамаск'), 'SZ': ('Mbabane', '', 'Мбабане'), 'TD': ("N'Djamena", "N'Djamena", 'Нджамена'),
'TG': ('Lomé', '', 'Ломе'), 'TH': ('Bangkok', '', 'Банкок'), 'TJ': ('Dushanbe', 'Duschanbe', 'Душанбе'), 'TL': ('Dili', '', 'Дили'),
'TM': ('Ashgabat', 'Aschgabat', 'Ашхабад'), 'TN': ('Tunis', '', 'Тунис'), 'TO': ("Nuku'alofa", '', 'Нукуалофа'), 'TR': ('Ankara', '', 'Анкара'),
'TT': ('Port of Spain', '', 'Порт ъф Спейн'), 'TV': ('Funafuti', '', 'Фунафути'), 'TW': ('Taipei', '', 'Тайпе'), 'TZ': ('Dodoma', '', 'Додома'),
'UA': ('Kyiv', 'Kyjiw', 'Киев'), 'UG': ('Kampala', '', 'Кампала'), 'US': ('Washington, D.C.', 'Washington, D.C.', 'Вашингтон'), 'UY': ('Montevideo', '', 'Монтевидео'),
'UZ': ('Tashkent', 'Taschkent', 'Ташкент'), 'VA': ('Vatican City', 'Vatikanstadt', 'Ватикан'), 'VC': ('Kingstown', '', 'Кингстаун'), 'VE': ('Caracas', '', 'Каракас'),
'VN': ('Hanoi', '', 'Ханой'), 'VU': ('Port Vila', '', 'Порт Вила'), 'WS': ('Apia', '', 'Апия'), 'XK': ('Pristina', 'Pristina', 'Прищина'),
'YE': ("Sana'a", "Sanaa", 'Сана'), 'ZA': ('Pretoria', '', 'Претория'), 'ZM': ('Lusaka', '', 'Лусака'), 'ZW': ('Harare', '', 'Хараре'),
'HK': ('Hong Kong', 'Hongkong', 'Хонконг'), 'MO': ('Macau', 'Macau', 'Макао'), 'PR': ('San Juan', '', 'Сан Хуан'), 'GL': ('Nuuk', '', 'Нуук'),
'FO': ('Tórshavn', '', 'Торсхавн'), 'GI': ('Gibraltar', '', 'Гибралтар'), 'IM': ('Douglas', '', 'Дъглас'), 'JE': ('Saint Helier', '', 'Сейнт Хелиър'),
'GG': ('Saint Peter Port', '', 'Сейнт Питър Порт'), 'RE': ('Saint-Denis', '', 'Сен Дени'), 'NC': ('Nouméa', '', 'Нумеа'), 'PF': ('Papeete', '', 'Папеете'),
}
TZ_OVERRIDE = {'AR': 'America/Argentina/Buenos_Aires', 'AU': 'Australia/Sydney', 'BR': 'America/Sao_Paulo', 'CA': 'America/Toronto', 'CD': 'Africa/Kinshasa',
               'CL': 'America/Santiago', 'CN': 'Asia/Shanghai', 'CY': 'Asia/Nicosia', 'DE': 'Europe/Berlin', 'EC': 'America/Guayaquil', 'ES': 'Europe/Madrid',
               'FM': 'Pacific/Pohnpei', 'GL': 'America/Nuuk', 'ID': 'Asia/Jakarta', 'KI': 'Pacific/Tarawa', 'KZ': 'Asia/Almaty', 'MH': 'Pacific/Majuro',
               'MN': 'Asia/Ulaanbaatar', 'MX': 'America/Mexico_City', 'MY': 'Asia/Kuala_Lumpur', 'NZ': 'Pacific/Auckland', 'PF': 'Pacific/Tahiti',
               'PG': 'Pacific/Port_Moresby', 'PS': 'Asia/Hebron', 'PT': 'Europe/Lisbon', 'RU': 'Europe/Moscow', 'UA': 'Europe/Kiev', 'US': 'America/New_York',
               'UZ': 'Asia/Tashkent', 'XK': 'Europe/Belgrade'}
zones = {}
for line in open('/usr/share/zoneinfo/zone.tab'):
    if line.startswith('#'): continue
    p = line.split('\t')
    zones.setdefault(p[0], p[2].strip())
out = {}
for cc, (en, de, bg) in CAP.items():
    tz = TZ_OVERRIDE.get(cc) or zones.get(cc)
    if not tz: print('no tz', cc); continue
    out[cc] = [en, de or en, bg or en, tz]
js = ('// Erzeugt von tools/make_geo.py: Ländercode -> [Hauptstadt EN, DE, BG, Zeitzone]\n'
      'export const CAP = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
open(os.path.join(HERE, 'fnlib', 'geo.js'), 'w', encoding='utf-8').write(js)
print(len(out), 'Länder')
