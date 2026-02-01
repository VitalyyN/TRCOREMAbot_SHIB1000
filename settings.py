# Настройки для торговли
ONLY_LONG = True

EMA_FAST  = 50
EMA_SLOW  = 60
TAKE_PROFIT    = 0.007          # (0,015 это 1.5 %)
POSITION_SIZE = 0.1             # 10 % от equity (берём позже из биржи)
DCA_STEP = 0.00002              # $ шаг сетки усреднения
DCA_GRID = [1, 1, 2, 2]         # коэффициенты усреднения

SYMBOL = "SHIB1000USDT"
INTERVAL = '1'                  # минуты
COMMISSION_RATE = 0.001         # комиссия

DEMO=True                       # использовать ли демо торговлю
