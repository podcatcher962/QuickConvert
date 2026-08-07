#!/usr/bin/env python3
"""QuickConvert v2.0 — universal offline unit converter with smart analogies"""
import tkinter as tk
from tkinter import ttk, messagebox
import os, sys, datetime, threading, json, urllib.request, ssl

APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

DISCLAIMER = """免责声明 / Disclaimer

1. QuickConvert 是纯本地离线换算工具。所有换算基于内置常量表，不连接互联网，不上传任何数据。
   QuickConvert is a pure offline conversion tool. All conversions are based on built-in constant tables. No internet, no upload.

2. 本软件按"原样"（AS-IS）提供，不提供任何明示或暗示的担保。开发者不对换算结果的准确性承担任何责任。
   货币汇率、时区信息等可能存在偏差，使用者应自行验证关键数据。
   This software is provided AS-IS without warranty of any kind. The developer assumes no responsibility for accuracy.
   Currency rates and timezone data may have discrepancies; users should verify critical data independently.

3. 内置汇率数据仅供参考，实际交易以银行实时报价为准。点击"实时汇率"可联网获取最新报价。
   Built-in exchange rates are for reference only. Click "Live Rates" to fetch updated quotes online.

4. 使用者须遵守所在地法律法规。本软件仅提供数学换算功能，不涉及金融交易、投资建议或法律意见。
   Users must comply with local laws. This tool provides mathematical conversion only.

5. 本软件仅供个人学习与工作效率提升使用。
   For personal study and productivity use only."""

# ============================================================
#  CATEGORIES — (display_label, key)
# ============================================================
CATEGORIES = [
    ("📏 长度 / Length", "length"), ("⚖️ 重量 / Weight", "weight"),
    ("🌡️ 温度 / Temp", "temperature"), ("📐 面积 / Area", "area"),
    ("🧪 体积 / Volume", "volume"), ("🏃 速度 / Speed", "speed"),
    ("💾 数据 / Data", "data"), ("📐 角度 / Angle", "angle"),
    ("⚡ 能量 / Energy", "energy"), ("💨 压力 / Pressure", "pressure"),
    ("💰 货币 / Currency", "currency"), ("👕 尺码 / Size", "size"),
    ("🕐 时区 / Timezone", "timezone"),
]

# ============================================================
#  TRANSLATION MAP — for UI strings
# ============================================================
T = {
    "zh": {
        "title": "QuickConvert · 万能换算",
        "input": "输入数值",
        "copy_all": "📋 复制全部",
        "copy_one": "📋 复制此项",
        "status_ready": "点击结果行查看类比 · Ctrl+1~9 切换类别",
        "status_copied": "✅ 已复制",
        "selected": "选中",
        "analogy_none": "💡 暂无匹配类比",
        "currency_hint": "以 {base} 为基准换算",
        "live_rate": "🌐 实时汇率",
        "offline": "📴 离线",
        "base_currency": "输入币种:",
        "fetching": "🌐 正在获取实时汇率...",
        "fetch_ok": "✅ 实时汇率已更新",
        "fetch_fail": "❌ 获取失败",
        "about_title": "关于 QuickConvert",
        "help_title": "使用说明",
        "help_text": (
            "🔢 QuickConvert 使用说明\n\n"
            "1. 点击类别 → 输入数值 → 自动出结果\n"
            "2. 单击某行结果 → 底部显示生活类比\n"
            "3. 双击某行结果 → 复制该项\n"
            "4. 📋 复制全部：一键复制所有换算结果\n"
            "5. 💰 货币 → 可选基准币种 → 🌐 联网更新汇率\n"
            "6. 👕 尺码 → 输入中国鞋码看各国对照\n"
            "7. 中/EN 按钮切换中英文界面\n"
            "8. Ctrl+数字键 快速切换类别\n\n"
            "⚠️ 完全离线运行（除主动点击联网汇率外）"
        ),
    },
    "en": {
        "title": "QuickConvert · Universal Converter",
        "input": "Enter value",
        "copy_all": "📋 Copy All",
        "copy_one": "📋 Copy This",
        "status_ready": "Click a result line for analogy · Ctrl+1~9 switch category",
        "status_copied": "✅ Copied",
        "selected": "Selected",
        "analogy_none": "💡 No matching analogy",
        "currency_hint": "Base: {base}",
        "live_rate": "🌐 Live Rates",
        "offline": "📴 Offline",
        "base_currency": "Base:",
        "fetching": "🌐 Fetching live rates...",
        "fetch_ok": "✅ Live rates updated",
        "fetch_fail": "❌ Fetch failed",
        "about_title": "About QuickConvert",
        "help_title": "Help",
        "help_text": (
            "🔢 QuickConvert Help\n\n"
            "1. Click category → type value → instant results\n"
            "2. Single-click a result line → analogy at bottom\n"
            "3. Double-click a result line → copy that line\n"
            "4. 📋 Copy All: copy all results at once\n"
            "5. 💰 Currency → select base → 🌐 fetch live rates\n"
            "6. 👕 Size → enter CN shoe size, see US/UK/EU\n"
            "7. 中/EN toggle to switch language\n"
            "8. Ctrl+number keys for quick category switch\n\n"
            "⚠️ Fully offline (except manual live-rates fetch)"
        ),
    },
}

# ============================================================
#  UNITS — (zh_label, en_label, factor_from_base)
#  factor = how many of this unit equals 1 base unit
# ============================================================
UNITS = {
    "length": [
        ("米 (m)", "Meter (m)", 1),
        ("厘米 (cm)", "Centimeter (cm)", 100),
        ("毫米 (mm)", "Millimeter (mm)", 1000),
        ("千米 (km)", "Kilometer (km)", 0.001),
        ("尺 (chi)", "Chi (CN foot)", 3),
        ("寸 (cun)", "Cun (CN inch)", 30),
        ("丈 (zhang)", "Zhang (10 chi)", 0.3),
        ("英尺 (ft)", "Foot (ft)", 3.28084),
        ("英寸 (in)", "Inch (in)", 39.3701),
        ("码 (yd)", "Yard (yd)", 1.09361),
        ("英里 (mi)", "Mile (mi)", 0.000621371),
        ("里 (li)", "Li (500m)", 0.002),
        ("海里 (nmi)", "Nautical mile", 0.000539957),
    ],
    "weight": [
        ("千克 (kg)", "Kilogram (kg)", 1),
        ("克 (g)", "Gram (g)", 1000),
        ("毫克 (mg)", "Milligram (mg)", 1e6),
        ("吨 (t)", "Tonne (t)", 0.001),
        ("斤 (jin)", "Jin (500g)", 2),
        ("两 (liang)", "Liang (50g)", 20),
        ("磅 (lb)", "Pound (lb)", 2.20462),
        ("盎司 (oz)", "Ounce (oz)", 35.274),
        ("克拉 (ct)", "Carat (ct)", 5000),
    ],
    "area": [
        ("平方米 (m²)", "Square meter", 1),
        ("平方厘米 (cm²)", "Square cm", 10000),
        ("平方千米 (km²)", "Square km", 1e-6),
        ("公顷 (ha)", "Hectare (ha)", 0.0001),
        ("亩 (mu)", "Mu (CN acre)", 0.0015),
        ("平方英尺 (ft²)", "Square foot", 10.7639),
        ("英亩 (acre)", "Acre", 0.000247105),
    ],
    "speed": [
        ("米/秒 (m/s)", "m/s", 1),
        ("千米/时 (km/h)", "km/h", 3.6),
        ("英里/时 (mph)", "mph", 2.23694),
        ("节 (kn)", "Knot (kn)", 1.94384),
        ("马赫 (Ma)", "Mach", 0.00294),
        ("光速 (c)", "Speed of light", 3.3356e-9),
    ],
    "volume": [
        ("升 (L)", "Liter (L)", 1),
        ("毫升 (mL)", "Milliliter (mL)", 1000),
        ("立方米 (m³)", "Cubic meter", 0.001),
        ("加仑 (gal)", "Gallon (US)", 0.264172),
        ("品脱 (pt)", "Pint (US)", 2.11338),
        ("杯 (cup)", "Cup (US)", 4.22675),
        ("茶匙 (tsp)", "Teaspoon", 202.884),
        ("汤匙 (tbsp)", "Tablespoon", 67.628),
    ],
    "angle": [
        ("度 (°)", "Degree (°)", 1),
        ("弧度 (rad)", "Radian (rad)", 0.0174533),
        ("梯度 (grad)", "Gradian", 1.11111),
        ("角分 (')", "Arcminute", 60),
        ("角秒 (\")", "Arcsecond", 3600),
        ("圈 (rev)", "Revolution", 0.00277778),
    ],
    "energy": [
        ("焦耳 (J)", "Joule (J)", 1),
        ("千焦 (kJ)", "Kilojoule (kJ)", 0.001),
        ("卡路里 (cal)", "Calorie (cal)", 0.239006),
        ("千卡 (kcal)", "Kilocalorie (kcal)", 0.000239006),
        ("千瓦时 (kWh)", "Kilowatt-hour", 2.77778e-7),
        ("电子伏特 (eV)", "Electronvolt", 6.242e18),
        ("英热单位 (BTU)", "BTU", 0.000947817),
    ],
    "pressure": [
        ("帕斯卡 (Pa)", "Pascal (Pa)", 1),
        ("千帕 (kPa)", "Kilopascal (kPa)", 0.001),
        ("巴 (bar)", "Bar", 1e-5),
        ("大气压 (atm)", "Atmosphere", 9.86923e-6),
        ("毫米汞柱 (mmHg)", "mmHg", 0.00750062),
        ("psi", "psi", 0.000145038),
        ("兆帕 (MPa)", "Megapascal", 1e-6),
    ],
    "data": [
        ("字节 (B)", "Byte (B)", 1),
        ("KB", "KB", 1/1024),
        ("MB", "MB", 1/1024**2),
        ("GB", "GB", 1/1024**3),
        ("TB", "TB", 1/1024**4),
        ("PB", "PB", 1/1024**5),
        ("比特 (bit)", "Bit", 8),
        ("Kb", "Kb", 8*1/1024),
        ("Mb", "Mb", 8*1/1024**2),
    ],
}

CURRENCY_RATES = {
    "美元 (USD)": 1, "人民币 (CNY)": 7.25, "欧元 (EUR)": 0.92,
    "日元 (JPY)": 148, "英镑 (GBP)": 0.79, "港币 (HKD)": 7.82,
    "韩元 (KRW)": 1350, "澳元 (AUD)": 1.55, "加元 (CAD)": 1.37,
    "新加坡元 (SGD)": 1.35, "瑞士法郎 (CHF)": 0.88, "新台币 (TWD)": 32.5,
}

CURRENCY_RATES_EN = {
    "US Dollar (USD)": 1, "Chinese Yuan (CNY)": 7.25, "Euro (EUR)": 0.92,
    "Japanese Yen (JPY)": 148, "British Pound (GBP)": 0.79, "HK Dollar (HKD)": 7.82,
    "Korean Won (KRW)": 1350, "Australian Dollar (AUD)": 1.55, "Canadian Dollar (CAD)": 1.37,
    "Singapore Dollar (SGD)": 1.35, "Swiss Franc (CHF)": 0.88, "New Taiwan Dollar (TWD)": 32.5,
}

TIMEZONES = {
    "北京 (CST)": 8, "东京 (JST)": 9, "新加坡 (SGT)": 8,
    "伦敦 (GMT)": 0, "纽约 (EST)": -5, "洛杉矶 (PST)": -8,
    "悉尼 (AEST)": 10, "迪拜 (GST)": 4, "莫斯科 (MSK)": 3,
    "巴黎 (CET)": 1, "孟买 (IST)": 5.5, "巴西 (BRT)": -3,
}

TIMEZONES_EN = {
    "Beijing (CST)": 8, "Tokyo (JST)": 9, "Singapore (SGT)": 8,
    "London (GMT)": 0, "New York (EST)": -5, "Los Angeles (PST)": -8,
    "Sydney (AEST)": 10, "Dubai (GST)": 4, "Moscow (MSK)": 3,
    "Paris (CET)": 1, "Mumbai (IST)": 5.5, "Brazil (BRT)": -3,
}

SHOE_SIZES = {
    "男鞋|Men": {"CN": [38,39,40,41,42,43,44,45,46],
             "US": [6,6.5,7,8,8.5,9.5,10,11,12],
             "UK": [5,5.5,6,7,7.5,8.5,9,10,11],
             "EU": [38,39,40,41,42,43,44,45,46]},
    "女鞋|Women": {"CN": [35,36,37,38,39,40,41,42],
             "US": [5,5.5,6,7,7.5,8.5,9.5,10],
             "UK": [2.5,3,3.5,4.5,5,6,7,7.5],
             "EU": [35,36,37,38,39,40,41,42]}
}

# ============================================================
#  ANALOGIES — per category, (threshold_in_base_unit, zh_desc, en_desc)
#  Matched by relative difference < 50%
# ============================================================
ANALOGIES = {
    "length": [
        (0.0001, "≈ 一根头发丝的直径", "≈ diameter of a human hair"),
        (0.001, "≈ 一张信用卡的厚度", "≈ thickness of a credit card"),
        (0.01, "≈ 手指指甲宽度", "≈ width of a fingernail"),
        (0.1, "≈ 一部手机的宽度", "≈ width of a smartphone"),
        (0.21, "≈ A4纸宽度", "≈ width of A4 paper"),
        (0.3, "≈ 一把标准尺子", "≈ a standard ruler"),
        (0.5, "≈ 成人手臂长度", "≈ length of an adult arm"),
        (0.76, "≈ 一把吉他长度", "≈ length of a guitar"),
        (1, "≈ 一扇标准门的高度", "≈ height of a standard door"),
        (1.7, "≈ 成年人身高", "≈ height of an adult"),
        (3, "≈ 一层居民楼的高度", "≈ one floor of a building"),
        (6, "≈ 两层居民楼", "≈ two-story building"),
        (20, "≈ 6层居民楼高度", "≈ a 6-story building"),
        (50, "≈ 一座15层高层住宅", "≈ a 15-story residential tower"),
        (100, "≈ 一个标准足球场长边", "≈ length of a soccer field"),
        (400, "≈ 标准田径跑道一圈", "≈ one lap on a standard track"),
        (1000, "≈ 步行约10分钟的距离", "≈ a 10-minute walk"),
        (5000, "≈ 5公里健身跑", "≈ a 5K fun run"),
        (42195, "≈ 全程马拉松距离", "≈ a full marathon"),
        (100000, "≈ 北京到天津的距离", "≈ Beijing to Tianjin"),
        (1000000, "≈ 北京到上海距离的80%", "≈ 80% of Beijing to Shanghai"),
        (384400000, "≈ 地球到月球的距离", "≈ Earth to Moon distance"),
    ],
    "weight": [
        (0.000001, "≈ 一粒细沙的重量", "≈ weight of a grain of sand"),
        (0.001, "≈ 一粒米 / 一张纸", "≈ one grain of rice / a sheet of paper"),
        (0.005, "≈ 一颗方糖", "≈ one sugar cube"),
        (0.02, "≈ 一支签字笔", "≈ a ballpoint pen"),
        (0.05, "≈ 一个鸡蛋", "≈ one chicken egg"),
        (0.1, "≈ 一部智能手机", "≈ a smartphone"),
        (0.15, "≈ 一个棒球", "≈ a baseball"),
        (0.5, "≈ 一瓶矿泉水 (500mL)", "≈ a bottle of water (500mL)"),
        (1, "≈ 1升水的重量", "≈ weight of 1 liter of water"),
        (3, "≈ 一台笔记本电脑", "≈ a laptop computer"),
        (5, "≈ 一袋5kg大米", "≈ a 5kg bag of rice"),
        (10, "≈ 一个登机行李箱", "≈ a carry-on suitcase"),
        (20, "≈ 一桶桶装水 (19L)", "≈ a water cooler jug (19L)"),
        (25, "≈ 一个装满的行李箱", "≈ a fully packed suitcase"),
        (60, "≈ 成年人体重", "≈ weight of an adult"),
        (80, "≈ 一名健壮成年男性", "≈ a strong adult male"),
        (100, "≈ 一头小牛 / 一台洗衣机", "≈ a calf / a washing machine"),
        (200, "≈ 一辆摩托车", "≈ a motorcycle"),
        (1000, "≈ 一辆小型轿车", "≈ a compact car"),
        (2000, "≈ 一辆中型SUV", "≈ a midsize SUV"),
        (5000, "≈ 一头成年大象", "≈ an adult elephant"),
    ],
    "temperature": [
        (-273.15, "绝对零度 | 理论最低温度", "Absolute zero | theoretical minimum"),
        (-89.2, "地球表面最低自然温度记录", "Coldest natural temp recorded on Earth"),
        (-40, "−40°C = −40°F | 极寒", "−40°C = −40°F | extreme cold"),
        (-20, "严寒 | 东北冬季常见温度", "Deep freeze | typical Siberian winter"),
        (-10, "冰点以下 | 需穿羽绒服", "Below freezing | wear a down jacket"),
        (0, "冰点 | 水结冰的温度", "Freezing point | water turns to ice"),
        (5, "冰箱冷藏室温度", "Refrigerator temperature"),
        (10, "春秋凉爽天气", "Cool spring/autumn day"),
        (15, "微凉 | 需穿薄外套", "Chilly | light jacket weather"),
        (20, "舒适室温 | 春季常温", "Comfortable room temperature"),
        (25, "空调推荐制冷温度", "Recommended AC cooling temp"),
        (30, "夏季炎热 | 海滩天气", "Hot summer day | beach weather"),
        (35, "酷热 | 高温预警温度", "Scorching | heat warning threshold"),
        (37, "人体正常体温 | 约37°C", "Normal human body temperature"),
        (40, "高烧危险温度", "High fever danger zone"),
        (50, "地表极热记录附近", "Near hottest surface temp recorded"),
        (100, "沸点 | 水沸腾的温度 (标准大气压)", "Boiling point | water boils (sea level)"),
        (200, "烤箱高温 | 烘焙披萨温度", "Hot oven | pizza baking temp"),
        (1500, "熔岩温度 | 约1500°C", "Lava temperature | ~1500°C"),
        (56000, "闪电温度 | 约56,000°C", "Lightning temperature | ~56,000°C"),
    ],
    "area": [
        (0.06, "≈ 一张A4纸的面积", "≈ area of A4 paper"),
        (0.5, "≈ 一张小茶几台面", "≈ a small coffee table"),
        (1, "≈ 一张标准办公桌", "≈ a standard office desk"),
        (5, "≈ 一个紧凑停车位", "≈ a compact parking space"),
        (15, "≈ 一间小卧室", "≈ a small bedroom"),
        (25, "≈ 一间客厅", "≈ a living room"),
        (50, "≈ 一间大开间公寓", "≈ a studio apartment"),
        (67, "≈ 一套一居室小户型", "≈ a 1-bedroom apartment"),
        (100, "≈ 一套大两居室", "≈ a large 2-bedroom apartment"),
        (420, "≈ 一个标准篮球场", "≈ a standard basketball court"),
        (666.7, "≈ 1市亩 | 中国市亩", "≈ 1 Chinese mu (~1/15 hectare)"),
        (1000, "≈ 两个篮球场", "≈ two basketball courts"),
        (7140, "≈ 一个标准足球场 (105m×68m)", "≈ a standard soccer field"),
        (10000, "≈ 1公顷 = 1.4个足球场", "≈ 1 hectare = 1.4 soccer fields"),
        (40000, "≈ 天安门广场面积", "≈ Tiananmen Square"),
        (1000000, "≈ 1平方千米 = 140个足球场", "≈ 1 km² = 140 soccer fields"),
    ],
    "volume": [
        (0.000001, "≈ 一粒米大小的体积", "≈ volume of a grain of rice"),
        (0.005, "5mL ≈ 一茶匙", "5mL ≈ one teaspoon"),
        (0.015, "15mL ≈ 一汤匙", "15mL ≈ one tablespoon"),
        (0.03, "30mL ≈ 一口烈酒 (shot)", "30mL ≈ one shot of liquor"),
        (0.2, "200mL ≈ 一杯水 / 玻璃杯", "200mL ≈ one glass of water"),
        (0.25, "250mL ≈ 一盒牛奶", "250mL ≈ a carton of milk"),
        (0.33, "330mL ≈ 一罐可乐", "330mL ≈ a can of cola"),
        (0.5, "500mL ≈ 一瓶矿泉水", "500mL ≈ a bottle of water"),
        (1, "1L ≈ 一大瓶饮料", "1L ≈ a large bottle of drink"),
        (1.5, "1.5L ≈ 大瓶矿泉水", "1.5L ≈ a large water bottle"),
        (2, "2L ≈ 大瓶可乐", "2L ≈ a large cola bottle"),
        (5, "5L ≈ 一桶食用油", "5L ≈ a jug of cooking oil"),
        (19, "19L ≈ 一桶桶装水", "19L ≈ a water cooler jug"),
        (60, "60L ≈ 一个车载行李箱", "60L ≈ a car trunk suitcase"),
        (200, "200L ≈ 一台中型冰箱", "200L ≈ a medium refrigerator"),
        (500, "500L ≈ 一台大冰箱", "500L ≈ a large refrigerator"),
        (1000, "1000L = 1m³ ≈ 一个IBC吨桶", "1000L = 1m³ ≈ an IBC tote"),
    ],
    "speed": [
        (0.1, "≈ 蜗牛爬行速度", "≈ snail crawling speed"),
        (1, "≈ 慢速散步 (3.6km/h)", "≈ slow walking (3.6km/h)"),
        (1.4, "≈ 正常步行速度 (5km/h)", "≈ normal walking (5km/h)"),
        (2.5, "≈ 快走速度 (9km/h)", "≈ brisk walking (9km/h)"),
        (5, "≈ 慢跑速度 (18km/h)", "≈ light jogging (18km/h)"),
        (8, "≈ 自行车骑行速度 (29km/h)", "≈ cycling speed (29km/h)"),
        (10, "≈ 短跑冲刺速度 (36km/h)", "≈ sprinting (36km/h)"),
        (13, "≈ 城市道路限速 (47km/h)", "≈ city speed limit (47km/h)"),
        (20, "≈ 市区快速路 (72km/h)", "≈ urban expressway (72km/h)"),
        (33, "≈ 高速公路限速 (120km/h)", "≈ highway speed limit (120km/h)"),
        (55, "≈ F1赛车弯道速度 (200km/h)", "≈ F1 cornering speed (200km/h)"),
        (97, "≈ 中国高铁巡航速度 (350km/h)", "≈ China high-speed rail (350km/h)"),
        (250, "≈ 民航客机巡航速度 (900km/h)", "≈ airliner cruising (900km/h)"),
        (340, "≈ 音速 | 马赫1 (常温)", "≈ speed of sound | Mach 1"),
        (2000, "≈ 超音速战斗机 (Mach 6)", "≈ supersonic fighter (Mach 6)"),
        (7900, "≈ 第一宇宙速度 | 卫星入轨", "≈ orbital velocity | satellite launch"),
    ],
    "data": [
        (1, "1字节 ≈ 一个英文字母", "1 byte ≈ one English letter"),
        (10, "10字节 ≈ 一个短单词", "10 bytes ≈ a short word"),
        (100, "100字节 ≈ 一条短信提要", "100 bytes ≈ a short text snippet"),
        (1024, "1KB ≈ 一条简短短信", "1KB ≈ a short SMS message"),
        (4096, "4KB ≈ 一页纯文本文档", "4KB ≈ one page of plain text"),
        (51200, "50KB ≈ 一张低分辨率图片", "50KB ≈ a low-res image"),
        (200000, "200KB ≈ 一张中等质量照片", "200KB ≈ a medium-quality photo"),
        (1048576, "1MB ≈ 一张手机拍摄的照片", "1MB ≈ a smartphone photo"),
        (5242880, "5MB ≈ 一首MP3歌曲", "5MB ≈ one MP3 song"),
        (104857600, "100MB ≈ 10首无损歌曲", "100MB ≈ ten lossless songs"),
        (734003200, "700MB ≈ 一张CD光盘容量", "700MB ≈ one CD capacity"),
        (1073741824, "1GB ≈ 一部720p高清电影", "1GB ≈ one 720p HD movie"),
        (4294967296, "4GB ≈ 一部1080p电影", "4GB ≈ one 1080p movie"),
        (17179869184, "16GB ≈ 一个USB闪存盘", "16GB ≈ a USB flash drive"),
        (68719476736, "64GB ≈ 一部手机存储", "64GB ≈ a phone storage"),
        (274877906944, "256GB ≈ 一台轻薄本SSD", "256GB ≈ an ultrabook SSD"),
        (1099511627776, "1TB ≈ 一个笔记本电脑硬盘", "1TB ≈ a laptop hard drive"),
        (4398046511104, "4TB ≈ 一个大容量外接硬盘", "4TB ≈ a large external HDD"),
    ],
    "angle": [
        (0.00028, "≈ 人眼最小分辨角", "≈ human eye minimum resolution"),
        (1, "1° ≈ 钟表上分针走10秒", "1° ≈ minute hand moving 10s on a clock"),
        (5, "5° ≈ 手掌宽度在臂长处张角", "5° ≈ angle of palm width at arm's length"),
        (10, "10° ≈ 拳头宽度在臂长处张角", "10° ≈ angle of fist at arm's length"),
        (15, "15° ≈ 15分钟时针偏转角度", "15° ≈ 15min on a clock"),
        (30, "30° ≈ 常见斜坡 / 屋顶坡度", "30° ≈ typical slope / roof pitch"),
        (45, "45° ≈ 对角线 / 正等腰三角", "45° ≈ diagonal / isosceles right triangle"),
        (60, "60° ≈ 等边三角形内角", "60° ≈ equilateral triangle interior angle"),
        (90, "90° ≈ 直角 | 墙角", "90° ≈ right angle | corner of a wall"),
        (180, "180° ≈ 直线 / 平角", "180° ≈ straight line / flat angle"),
        (270, "270° ≈ 四分之三圈", "270° ≈ three-quarter rotation"),
        (360, "360° ≈ 一整圈 | 完整圆周", "360° ≈ full circle"),
        (720, "720° ≈ 两圈 | 滑雪旋转", "720° ≈ two full spins | ski trick"),
    ],
    "energy": [
        (1, "1J ≈ 一个苹果下落1米", "1J ≈ an apple falling 1 meter"),
        (10, "10J ≈ 把1kg抬高1米", "10J ≈ lifting 1kg by 1 meter"),
        (100, "100J ≈ 一盏LED灯亮1分钟", "100J ≈ an LED lamp for 1 min"),
        (1000, "1kJ ≈ 成年人静坐10分钟耗能", "1kJ ≈ sitting quietly for 10 min"),
        (4184, "4.184kJ ≈ 1千卡 | 一个大苹果的热量", "4.184kJ ≈ 1 kcal | one large apple"),
        (20000, "20kJ ≈ 一分钟慢跑耗能", "20kJ ≈ one minute of jogging"),
        (84000, "84kJ ≈ 一杯牛奶的热量 (200kcal)", "84kJ ≈ a glass of milk (200kcal)"),
        (420000, "420kJ ≈ 一小时步行耗能 (100kcal)", "420kJ ≈ 1 hour walking (100kcal)"),
        (2000000, "2MJ ≈ 一顿正餐热量 (500kcal)", "2MJ ≈ one meal (500kcal)"),
        (8400000, "8.4MJ ≈ 成年人一天基础代谢", "8.4MJ ≈ adult daily BMR (2000kcal)"),
        (36000000, "36MJ ≈ 1度电 = 1kWh", "36MJ ≈ 1 kWh electricity"),
    ],
    "pressure": [
        (1, "1Pa ≈ 一张纸币对桌面的压强", "1Pa ≈ a banknote on a table"),
        (100, "100Pa ≈ 一个苹果对桌面的压强", "100Pa ≈ an apple on a table"),
        (1000, "1kPa ≈ 普通气球内压", "1kPa ≈ pressure inside a balloon"),
        (5000, "5kPa ≈ 吸尘器吸力", "5kPa ≈ vacuum cleaner suction"),
        (101325, "101.3kPa ≈ 1个标准大气压", "101.3kPa ≈ 1 standard atmosphere"),
        (230000, "230kPa ≈ 汽车标准胎压", "230kPa ≈ standard car tire pressure"),
        (400000, "400kPa ≈ 高压锅内部压力", "400kPa ≈ pressure cooker pressure"),
        (1000000, "1MPa ≈ 10个大气压 | 潜水10米", "1MPa ≈ 10 atm | diving 10m"),
        (10000000, "10MPa ≈ 深海1000米压力", "10MPa ≈ pressure at 1000m deep"),
        (200000000, "200MPa ≈ 工业液压系统", "200MPa ≈ industrial hydraulics"),
    ],
}

# ============================================================
#  QuickConvert App
# ============================================================
class QuickConvert:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QuickConvert v2.0 - 永远的兰兰")
        self.root.geometry("720x760")
        self.root.minsize(520, 600)
        self.root.configure(bg='#F5F5F5')
        self.BG = '#F5F5F5'; self.card = '#FFFFFF'
        self.accent = '#3949AB'; self.accent2 = '#5C6BC0'
        self.fg = '#212121'; self.fg2 = '#757575'
        self.green = '#43A047'; self.amber = '#FB8C00'

        self.current_cat = 'length'
        self.lang = 'zh'
        self._base_val = 0
        self._selected_line = None
        self._currency_base_key = "美元 (USD)"
        # Per-category base unit index (default 0 = first unit)
        self._base_idx = {}

        self._build_menu()
        self._build_ui()
        self._select_category("length")
        self._bind_keys()

    # ================================================================
    #  UTILITY
    # ================================================================
    def _t(self, key, **fmt):
        """Return translated string by key, format with kwargs"""
        s = T[self.lang].get(key, key)
        if fmt:
            s = s.format(**fmt)
        return s

    def _get_unit_label(self, zh_label, en_label):
        return zh_label if self.lang == 'zh' else en_label

    def _get_currency_dict(self):
        return CURRENCY_RATES if self.lang == 'zh' else CURRENCY_RATES_EN

    def _get_tz_dict(self):
        return TIMEZONES if self.lang == 'zh' else TIMEZONES_EN

    # ================================================================
    #  MENU
    # ================================================================
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self._t("help_title"), command=self._show_help)
        help_menu.add_command(label="免责声明 / Disclaimer",
            command=lambda: messagebox.showinfo("免责声明 / Disclaimer", DISCLAIMER))
        help_menu.add_separator()
        help_menu.add_command(label=self._t("about_title"), command=self._show_about)
        menubar.add_cascade(label="帮助 / Help", menu=help_menu)
        self.root.config(menu=menubar)

    def _show_help(self):
        messagebox.showinfo(self._t("help_title"), self._t("help_text"))

    def _show_about(self):
        messagebox.showinfo(self._t("about_title"),
            "QuickConvert v2.0\n\n万能离线换算器 · 永远的兰兰\n"
            "Universal Offline Converter · forever-chitanda\n\n"
            "Python 3 + tkinter\n纯本地 · 零隐私风险\n"
            "Pure local · zero privacy risk\n\n"
            "GitHub: github.com/podcatcher962/QuickConvert\n"
            "© 永远的兰兰 / forever-chitanda")

    # ================================================================
    #  BUILD UI
    # ================================================================
    def _build_ui(self):
        # ---- Title bar ----
        tb = tk.Frame(self.root, bg=self.accent, height=38)
        tb.pack(fill=tk.X); tb.pack_propagate(False)
        tk.Label(tb, text="🔢 QuickConvert", font=('Microsoft YaHei UI', 11, 'bold'),
                 bg=self.accent, fg='white').pack(side=tk.LEFT, padx=12, pady=6)
        self.lang_btn = tk.Button(tb, text="中/EN", font=('Microsoft YaHei UI', 8),
            bg='#283593', fg='white', relief='flat', bd=0, padx=8, pady=2,
            cursor='hand2', command=self._toggle_lang)
        self.lang_btn.pack(side=tk.RIGHT, padx=12, pady=6)
        tk.Label(tb, text="永远的兰兰 · 万能换算", font=('Microsoft YaHei UI', 8),
                 bg=self.accent, fg='#C5CAE9').pack(side=tk.RIGHT, padx=8, pady=6)

        # ---- Main ----
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # ---- Input ----
        inf = tk.Frame(main, bg=self.card, highlightbackground='#E0E0E0', highlightthickness=1)
        inf.pack(fill=tk.X, pady=(0, 6))
        self.input_label = tk.Label(inf, text=self._t("input"), font=('Microsoft YaHei UI', 9),
            bg=self.card, fg=self.fg2)
        self.input_label.pack(anchor='w', padx=10, pady=(8, 0))
        self.input_var = tk.StringVar()
        self.input_var.trace_add('write', lambda *a: self._convert())
        self.input_entry = tk.Entry(inf, textvariable=self.input_var,
            font=('Consolas', 20), bg=self.card, fg=self.fg, relief='flat',
            insertbackground=self.accent, justify='center')
        self.input_entry.pack(fill=tk.X, padx=10, pady=(2, 10))
        self.input_entry.focus_set()

        # ---- Category buttons ----
        cf = tk.Frame(main, bg=self.BG); cf.pack(fill=tk.X, pady=(0, 6))
        self.cat_buttons = {}
        btn_font = ('Microsoft YaHei UI', 8)
        for row_cats in [CATEGORIES[:7], CATEGORIES[7:]]:
            rf = tk.Frame(cf, bg=self.BG); rf.pack(fill=tk.X, pady=1)
            for label, key in row_cats:
                btn = tk.Button(rf, text=label, font=btn_font,
                    bg=self.card, fg=self.fg, relief='flat', bd=0, padx=4, pady=5,
                    cursor='hand2', activebackground=self.accent, activeforeground='white',
                    command=lambda k=key: self._select_category(k))
                btn.pack(side=tk.LEFT, padx=1); self.cat_buttons[key] = btn

        # ---- Currency bar (hidden by default) ----
        self.currency_frame = tk.Frame(main, bg=self.BG)

        # ---- Base unit selector (hidden except for general/temp cats) ----
        self.base_unit_frame = tk.Frame(main, bg=self.BG)

        # ---- Category label ----
        self.cat_label = tk.Label(main, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg=self.BG, fg=self.fg, anchor='w')
        self.cat_label.pack(fill=tk.X, pady=(6, 4))

        # ---- Results ----
        rf2 = tk.Frame(main, bg=self.card, highlightbackground='#E0E0E0', highlightthickness=1)
        rf2.pack(fill=tk.BOTH, expand=True)
        tc = tk.Frame(rf2, bg=self.card); tc.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.result_text = tk.Text(tc, font=('Consolas', 10),
            bg=self.card, fg=self.fg, relief='flat', bd=0, padx=8, pady=4,
            wrap=tk.NONE, state=tk.DISABLED, cursor='hand2')
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Tag for selected line
        self.result_text.tag_configure('selected', background='#E8EAF6',
            foreground=self.accent)
        self.result_text.tag_configure('analogy', foreground='#5C6BC0',
            font=('Microsoft YaHei UI', 8))
        self.result_text.tag_configure('clickable', foreground=self.accent2)

        # Bind click events
        self.result_text.bind('<Button-1>', self._on_result_click)
        self.result_text.bind('<Double-Button-1>', self._on_result_double)

        # ---- Bottom bar ----
        bottom = tk.Frame(main, bg=self.BG, height=28)
        bottom.pack(fill=tk.X, pady=(8, 0))
        bottom.pack_propagate(False)
        btn_fr = tk.Frame(bottom, bg=self.BG)
        btn_fr.pack(side=tk.RIGHT)
        self.copy_all_btn = tk.Button(btn_fr, text=self._t("copy_all"), font=('Microsoft YaHei UI', 8),
            bg=self.accent, fg='white', relief='flat', bd=0, padx=10, pady=4,
            cursor='hand2', command=self._copy_all)
        self.copy_all_btn.pack(side=tk.RIGHT, padx=2)
        self.copy_one_btn = tk.Button(btn_fr, text=self._t("copy_one"), font=('Microsoft YaHei UI', 8),
            bg='#BDBDBD', fg='#616161', relief='flat', bd=0, padx=10, pady=4,
            cursor='hand2', command=self._copy_one)
        self.copy_one_btn.pack(side=tk.RIGHT, padx=2)
        self.status_label = tk.Label(bottom, text="💡 " + ("单击行复制" if self.lang == 'zh' else "Click to copy"),
            font=('Microsoft YaHei UI', 7), bg=self.BG, fg=self.fg2, anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=(4, 0))

    # ================================================================
    #  KEYBOARD SHORTCUTS
    # ================================================================
    def _bind_keys(self):
        # Ctrl+1~9 for first 9 categories (Key-10/11/12/13 not valid)
        for i, (_, key) in enumerate(CATEGORIES):
            if i + 1 <= 9:
                self.root.bind(f'<Control-Key-{i+1}>', lambda e, k=key: self._select_category(k))
        self.root.bind('<Control-c>', lambda e: self._copy_one() if self._selected_line else self._copy_all())

    # ================================================================
    #  LANGUAGE TOGGLE
    # ================================================================
    def _toggle_lang(self):
        self.lang = 'en' if self.lang == 'zh' else 'zh'
        # Update UI strings
        self.input_label.config(text=self._t("input"))
        self.copy_all_btn.config(text=self._t("copy_all"))
        self.copy_one_btn.config(text=self._t("copy_one"))
        self.status_label.config(text=("💡 单击行复制" if self.lang == 'zh' else "💡 Click line to copy"))
        # Update category buttons
        for label, key in CATEGORIES:
            if key in self.cat_buttons:
                self.cat_buttons[key].config(text=label)
        # Rebuild currency frame if visible
        if self.current_cat == "currency":
            self._show_currency_bar()
        elif self.current_cat in UNITS or self.current_cat == "temperature":
            self._show_base_selector(self.current_cat)
        self._convert()

    # ================================================================
    #  CATEGORY SELECTION
    # ================================================================
    def _select_category(self, key):
        self.current_cat = key
        self._selected_line = None
        self.copy_one_btn.config(bg='#BDBDBD', fg='#616161')
        for k, btn in self.cat_buttons.items():
            btn.configure(bg=self.accent if k == key else self.card,
                          fg='white' if k == key else self.fg)
        # Update cat label
        cat_names = {v: k for k, v in CATEGORIES}
        self.cat_label.config(text=cat_names.get(key, key))
        if key == "currency":
            self._show_currency_bar()
        else:
            self.currency_frame.pack_forget()
        # Base unit selector for non-currency, non-timezone, non-size cats
        if key in UNITS:
            self._show_base_selector(key)
        elif key in ("temperature",):
            self._show_base_selector("temperature")
        else:
            self.base_unit_frame.pack_forget()
        self._convert()
        self.input_entry.focus_set()

    def _show_currency_bar(self):
        self.currency_frame.pack(fill=tk.X, pady=(0, 4))
        for w in self.currency_frame.winfo_children():
            w.destroy()
        tk.Label(self.currency_frame, text=self._t("base_currency"), font=('Microsoft YaHei UI', 9),
            bg=self.BG, fg=self.fg2).pack(side=tk.LEFT, padx=(0, 6))
        currency_dict = self._get_currency_dict()
        currency_names = list(currency_dict.keys())
        base_var = tk.StringVar(value=currency_names[0])
        cb = ttk.Combobox(self.currency_frame, textvariable=base_var,
            values=currency_names, state='readonly', width=18, font=('Microsoft YaHei UI', 9))
        cb.pack(side=tk.LEFT, padx=(0, 6))
        cb.bind('<<ComboboxSelected>>', lambda e: (
            setattr(self, '_currency_base_key', base_var.get()),
            self._convert()
        ))
        tk.Label(self.currency_frame, text="│", font=('Microsoft YaHei UI', 9),
            bg=self.BG, fg='#E0E0E0').pack(side=tk.LEFT, padx=4)
        tk.Button(self.currency_frame, text=self._t("offline"), font=('Microsoft YaHei UI', 8),
            bg=self.card, fg=self.fg, relief='flat', bd=0, padx=6, pady=3,
            cursor='hand2', command=lambda: (self.status_label.config(text="当前: 离线固定汇率" if self.lang=='zh' else "Current: offline rates"), self._convert())
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(self.currency_frame, text=self._t("live_rate"), font=('Microsoft YaHei UI', 8),
            bg=self.green, fg='white', relief='flat', bd=0, padx=6, pady=3,
            cursor='hand2', command=self._fetch_live_rates
        ).pack(side=tk.LEFT, padx=2)

    def _show_base_selector(self, cat):
        """Show base unit dropdown for general categories + temperature"""
        self.base_unit_frame.pack(fill=tk.X, pady=(0, 4))
        for w in self.base_unit_frame.winfo_children():
            w.destroy()
        tk.Label(self.base_unit_frame, text=("基准:" if self.lang == 'zh' else "Base:"),
            font=('Microsoft YaHei UI', 9), bg=self.BG, fg=self.fg2).pack(side=tk.LEFT, padx=(0, 6))

        if cat == "temperature":
            keys = [("摄氏度 (°C)", "Celsius (°C)"), ("华氏度 (°F)", "Fahrenheit (°F)"),
                    ("开尔文 (K)", "Kelvin (K)"), ("列氏度 (°Re)", "Réaumur (°Re)"),
                    ("兰金度 (°Ra)", "Rankine (°Ra)")]
        else:
            keys = [(zh, en) for zh, en, _ in UNITS.get(cat, [])]

        unit_labels = [self._get_unit_label(zh, en) for zh, en in keys]
        bi = self._base_idx.get(cat, 0)
        if bi >= len(unit_labels):
            bi = 0
        var = tk.StringVar(value=unit_labels[bi])
        cb = ttk.Combobox(self.base_unit_frame, textvariable=var,
            values=unit_labels, state='readonly', width=18, font=('Microsoft YaHei UI', 9))
        cb.pack(side=tk.LEFT, padx=(0, 6))
        cb.bind('<<ComboboxSelected>>', lambda e, c=cat, v=var, labels=unit_labels: (
            self._base_idx.__setitem__(c, labels.index(v.get())),
            self._update_input_hint(c),
            self._convert()
        ))
        self._update_input_hint(cat)

    def _update_input_hint(self, cat):
        """Show unit in input label"""
        if cat == "temperature":
            idx = self._base_idx.get(cat, 0)
            keys = [("摄氏度 (°C)", "Celsius (°C)"), ("华氏度 (°F)", "Fahrenheit (°F)"),
                    ("开尔文 (K)", "Kelvin (K)"), ("列氏度 (°Re)", "Réaumur (°Re)"),
                    ("兰金度 (°Ra)", "Rankine (°Ra)")]
            if idx < len(keys):
                unit_label = self._get_unit_label(keys[idx][0], keys[idx][1])
                self.input_label.config(text=f"{self._t('input')} ({unit_label})")
            else:
                self.input_label.config(text=self._t("input"))
        elif cat in UNITS:
            units = UNITS[cat]
            bi = self._base_idx.get(cat, 0)
            if bi < len(units):
                unit_label = self._get_unit_label(units[bi][0], units[bi][1])
                self.input_label.config(text=f"{self._t('input')} ({unit_label})")
            else:
                self.input_label.config(text=self._t("input"))
        else:
            self.input_label.config(text=self._t("input"))

    # ================================================================
    #  CONVERSION ENGINE
    # ================================================================
    def _convert(self):
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self._selected_line = None
        self.copy_one_btn.config(bg='#BDBDBD', fg='#616161')
        self.result_text.tag_remove('selected', '1.0', 'end')

        cat = self.current_cat
        raw = self.input_var.get().strip()

        try:
            if cat == "temperature":
                self._conv_temp(raw)
            elif cat == "currency":
                self._conv_currency(raw)
            elif cat == "timezone":
                self._conv_timezone()
            elif cat == "size":
                self._conv_size(raw)
            else:
                self._conv_general(cat, raw)
        except Exception as e:
            self.result_text.insert('end', f"⚠ Error: {e}")

        self.result_text.configure(state=tk.DISABLED)

    def _format_num(self, v):
        """Smart number formatting"""
        if abs(v) < 1e-15:
            return "0"
        if abs(v) >= 1e12 or (0 < abs(v) <= 1e-10):
            return f"{v:.4e}"
        if abs(v) >= 1000000:
            return f"{v:,.2f}"
        if abs(v) >= 1000:
            return f"{v:,.2f}"
        if abs(v) >= 1:
            return f"{v:.4f}"
        if abs(v) >= 0.001:
            return f"{v:.6f}"
        return f"{v:.8f}"

    def _conv_general(self, cat, raw):
        try:
            val = float(raw) if raw else 0
        except ValueError:
            if raw:
                self.result_text.insert('end', f"⚠ {raw} — " + ("请输入有效数字" if self.lang=='zh' else "invalid number"))
            return

        units = UNITS.get(cat, [])
        if not units:
            return

        base_idx = self._base_idx.get(cat, 0)
        if base_idx >= len(units):
            base_idx = 0
        base_factor = units[base_idx][2]
        base_val = val / base_factor if base_factor != 0 else val
        self._base_val = base_val
        analogy = self._get_analogy_text(cat, base_val)
        first = True

        for zh_name, en_name, factor in units:
            if factor == 0:
                continue
            v = base_val * factor
            disp = self._format_num(v)
            label = self._get_unit_label(zh_name, en_name)
            line = f"  {disp:>16s}  {label}"
            if analogy and first:
                pad = max(2, 56 - self._visual_width(line))
                line += " " * pad + analogy
                first = False
            self.result_text.insert('end', line + "\n")

    def _conv_temp(self, raw):
        try:
            v = float(raw) if raw else 0
        except ValueError:
            if raw:
                self.result_text.insert('end', f"⚠ {raw} — " + ("请输入有效数字" if self.lang=='zh' else "invalid number"))
            return
        bi = self._base_idx.get("temperature", 0)
        # Convert input to °C based on selected base unit
        if bi == 1:   # °F → °C
            c = (v - 32) * 5 / 9
        elif bi == 2: # K → °C
            c = v - 273.15
        elif bi == 3: # °Re → °C
            c = v * 5 / 4
        elif bi == 4: # °Ra → °C
            c = (v - 491.67) * 5 / 9
        else:         # °C
            c = v
        self._base_val = c
        items = [
            ("摄氏度 (°C)", "Celsius (°C)", c),
            ("华氏度 (°F)", "Fahrenheit (°F)", c * 9 / 5 + 32),
            ("开尔文 (K)", "Kelvin (K)", c + 273.15),
            ("列氏度 (°Re)", "Réaumur (°Re)", c * 4 / 5),
            ("兰金度 (°Ra)", "Rankine (°Ra)", (c + 273.15) * 9 / 5),
        ]
        analogy = self._get_analogy_text("temperature", c)
        first = True
        for zh, en, x in items:
            label = self._get_unit_label(zh, en)
            line = f"  {x:>16.4f}  {label}"
            if analogy and first:
                pad = max(2, 56 - self._visual_width(line))
                line += " " * pad + analogy
                first = False
            self.result_text.insert('end', line + "\n")

    def _conv_currency(self, raw):
        try:
            v = float(raw) if raw else 0
        except ValueError:
            if raw:
                self.result_text.insert('end', f"⚠ {raw} — " + ("请输入有效数字" if self.lang=='zh' else "invalid number"))
            return
        currency_dict = self._get_currency_dict()
        base_name = getattr(self, '_currency_base_key', list(currency_dict.keys())[0])
        base_rate = currency_dict.get(base_name, 1)
        usd_val = v / base_rate if base_rate != 0 else v
        self._base_val = usd_val  # USD equivalent
        for name, rate in currency_dict.items():
            self.result_text.insert('end', f"  {usd_val * rate:>16.4f}  {name}\n")
        self.result_text.insert('end', "\n" + self._t("currency_hint", base=base_name))

    def _conv_timezone(self):
        now = datetime.datetime.utcnow()
        tz_dict = self._get_tz_dict()
        self._base_val = 0
        for name, off in tz_dict.items():
            local = now + datetime.timedelta(hours=off)
            sign = '+' if off >= 0 else ''
            self.result_text.insert('end', f"  UTC{sign}{off:<4}  {local.strftime('%H:%M')}  {name}\n")
        self.result_text.insert('end', f"\n  {'UTC 时间' if self.lang=='zh' else 'UTC Time':>20}  {now.strftime('%Y-%m-%d %H:%M')}\n")

    def _conv_size(self, raw):
        try:
            cn = int(raw) if raw and raw.strip() else 40
        except ValueError:
            if raw and raw.strip():
                self.result_text.insert('end', f"⚠ {raw} — " + ("请输入整数字码" if self.lang=='zh' else "enter integer size"))
            return
        self._base_val = cn
        header = "👞 鞋码对照" if self.lang == 'zh' else "👞 Shoe Size Chart"
        self.result_text.insert('end', header + "\n\n")
        for gender_key, data in SHOE_SIZES.items():
            zh_g, en_g = gender_key.split('|')
            gender_label = zh_g if self.lang == 'zh' else en_g
            self.result_text.insert('end', f"  {gender_label}:\n")
            cn_list = data["CN"]
            if cn not in cn_list:
                self.result_text.insert('end', f"    CN {cn} → " + ("不在常用范围\n\n" if self.lang=='zh' else "out of range\n\n"))
                continue
            idx = cn_list.index(cn)
            for sys_key in ["CN", "US", "UK", "EU"]:
                if idx < len(data[sys_key]):
                    self.result_text.insert('end', f"    {sys_key}: {data[sys_key][idx]}\n")
            self.result_text.insert('end', "\n")
        # Clothing reference
        ref_title = "👔 服装尺码参考" if self.lang == 'zh' else "👔 Clothing Size Ref"
        self.result_text.insert('end', ref_title + "\n")
        cloth = {
            160: ("XS-160", "XS", "S"),
            165: ("S-165", "S", "M"),
            170: ("M-170", "M", "M"),
            175: ("L-175", "L", "L"),
            180: ("XL-180", "XL", "XL"),
            185: ("XXL-185", "XXL", "XXL"),
        }
        for h, (cn_name, us_name, _) in sorted(cloth.items()):
            lbl = f"    {h}cm → CN: {cn_name} | US: {us_name}"
            self.result_text.insert('end', lbl + "\n")

    # ================================================================
    #  ANALOGY ENGINE
    # ================================================================
    def _visual_width(self, s):
        """Approximate display width: CJK chars count as 2, ASCII as 1"""
        w = 0
        for ch in s:
            w += 2 if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f' or '\uff00' <= ch <= '\uffef' else 1
        return w

    def _get_analogy_text(self, cat, base_val):
        """Return analogy string for a category+value, or '' if no match"""
        if cat not in ANALOGIES:
            return ''
        analogs = ANALOGIES[cat]
        bv = base_val
        if bv <= 0 and cat != "temperature":
            return ''
        best, best_diff = None, float('inf')
        for thr, zh_desc, en_desc in analogs:
            diff = abs(bv - thr) / max(abs(thr), 1e-9)
            if diff <= 0.6 and diff < best_diff:
                best, best_diff = (zh_desc, en_desc), diff
        if best:
            desc = best[0] if self.lang == 'zh' else best[1]
            return f"💡 {desc}"
        return ''

    # ================================================================
    #  RESULT CLICK HANDLERS
    # ================================================================
    def _on_result_click(self, event):
        """Single click: highlight line for copy"""
        self.result_text.configure(state=tk.NORMAL)
        try:
            idx = self.result_text.index(f"@{event.x},{event.y}")
            line = int(idx.split('.')[0])
        except Exception:
            self.result_text.configure(state=tk.DISABLED)
            return

        self.result_text.tag_remove('selected', '1.0', 'end')
        linestart = f"{line}.0"
        lineend = f"{line}.end"
        line_text = self.result_text.get(linestart, lineend).strip()

        if line_text and (line_text[0].isdigit() or (len(line_text) > 1 and line_text[1].isdigit())):
            self.result_text.tag_add('selected', linestart, lineend)
            self._selected_line = line
            self.copy_one_btn.config(bg=self.accent2, fg='white')
        else:
            self._selected_line = None
            self.copy_one_btn.config(bg='#BDBDBD', fg='#616161')

        self.result_text.configure(state=tk.DISABLED)

    def _on_result_double(self, event):
        """Double click: copy the line"""
        try:
            idx = self.result_text.index(f"@{event.x},{event.y}")
            line = int(idx.split('.')[0])
        except Exception:
            return
        linestart = f"{line}.0"
        lineend = f"{line}.end"
        line_text = self.result_text.get(linestart, lineend).strip()
        if line_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(line_text)
            self.status_label.config(text=("✅ 已复制" if self.lang == 'zh' else "✅ Copied"))
            self.root.after(2000, lambda: self.status_label.config(text=("💡 单击行复制" if self.lang == 'zh' else "💡 Click line to copy")))

    def _copy_one(self):
        """Copy the currently selected line"""
        if not self._selected_line:
            return
        linestart = f"{self._selected_line}.0"
        lineend = f"{self._selected_line}.end"
        line_text = self.result_text.get(linestart, lineend).strip()
        if line_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(line_text)
            self.status_label.config(text=("✅ 已复制" if self.lang == 'zh' else "✅ Copied"))
            self.root.after(2000, lambda: self.status_label.config(text=("💡 单击行复制" if self.lang == 'zh' else "💡 Click line to copy")))

    def _copy_all(self):
        """Copy all results"""
        content = self.result_text.get('1.0', 'end-1c')
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(text=("✅ 已复制" if self.lang == 'zh' else "✅ Copied"))
            self.root.after(2000, lambda: self.status_label.config(text=("💡 单击行复制" if self.lang == 'zh' else "💡 Click line to copy")))

    # ================================================================
    #  LIVE EXCHANGE RATES
    # ================================================================
    def _fetch_live_rates(self):
        self.status_label.config(text=self._t("fetching"))
        self.root.update()
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            rq = urllib.request.Request("https://open.er-api.com/v6/latest/USD",
                headers={'User-Agent': 'QuickConvert/2.0'})
            with urllib.request.urlopen(rq, timeout=15, context=ctx) as r:
                data = json.loads(r.read())
            # Update both currency dictionaries
            for d in [CURRENCY_RATES, CURRENCY_RATES_EN]:
                for name in list(d.keys()):
                    code = name.split('(')[-1].rstrip(')')
                    if code in data.get('rates', {}):
                        d[name] = data['rates'][code]
            self.root.after(0, lambda: self.status_label.config(text=self._t("fetch_ok")))
            self.root.after(0, self._convert)
        except Exception as e:
            msg = f"❌ {e}"
            self.root.after(0, lambda m=msg: self.status_label.config(text=m))


if __name__ == '__main__':
    QuickConvert().root.mainloop()
