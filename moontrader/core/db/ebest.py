from pony.orm import *

def create_FutureCode(db):
    class FutureCode(db.Entity):
        _table_ = 'future_codes'
        cd = PrimaryKey(str)
        nm = Required(str)
    return FutureCode

def create_StockCode(db):
    class StockCode(db.Entity):
        _table_ = 'stock_codes'
        cd = PrimaryKey(str)
        nm = Required(str)
        exp_cd = Required(str)
        market = Required(str)
        etf = Required(str)
    return StockCode

def create_StockTheme(db):
    class StockTheme(db.Entity):
        _table_ = 'stock_themes'
        cd = PrimaryKey(str)
        nm = Required(str)
    return StockTheme    


future_month_map = {1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M', 
             7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'}

future_code_map = {   
    'AD': {'months': [3, 6, 9, 12], 'name': 'Australian Dollar'},
    'BP': {'months': [3, 6, 9, 12], 'name': 'British Pound'},
    'BR': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'Brazilian Real'},
    'CC': {'months': [3, 5, 7, 9, 12], 'name': 'ICE Cocoa'},
    'CD': {'months': [3, 6, 9, 12], 'name': 'Canadian Dollar'},
    'CL': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'Crude Oil (WTI)'},
    'CT': {'months': [3, 5, 7, 10, 12], 'name': 'ICE Cotton'},
    'CUS': {'months': [2, 3, 4, 6, 9, 12], 'name': 'Renminbi_USD/CNH'},
    'DX': {'months': [3, 6, 9, 12], 'name': 'US Dollar Index'},
    'E7': {'months': [3, 6], 'name': 'E-mini Euro FX'},
    'ED': {'months': [3, 6, 9, 12], 'name': 'Eurodollar'},
    'EMD': {'months': [3, 6, 9, 12], 'name': 'E-mini S&P MidCap 400'},
    'ES': {'months': [3, 6, 9, 12], 'name': 'E-mini S&P 500'},
    'FBTP': {'months': [3, 6, 9], 'name': 'Long-term Euro-BTP'},
    'FC': {'months': [1, 3, 4, 5, 8, 9, 10, 11], 'name': 'Feeder Cattle'},
    'FDAX': {'months': [3, 6, 9], 'name': 'DAX'},
    'FDXM': {'months': [3, 6, 9], 'name': 'Mini-DAX'},
    'FESX': {'months': [3, 6, 9, 12], 'name': 'DJ Euro Stoxx 50'},
    'FGBL': {'months': [3, 6, 9], 'name': 'Euro Bund'},
    'FGBM': {'months': [3, 6, 9], 'name': 'Euro Bobl'},
    'FGBS': {'months': [3, 6, 9], 'name': 'Euro Schatz'},
    'FOAM': {'months': [3, 6, 9], 'name': 'Mid-Term Euro-OAT'},
    'FOAT': {'months': [3, 6, 9], 'name': 'Euro-OAT'},
    'FVS': {'months': [2, 3, 4, 5, 6, 7, 8], 'name': 'VSTOXX'},
    'GC': {'months': [2, 4, 6, 8, 10, 12], 'name': 'Gold'},
    'HCEI': {'months': [1, 2, 3, 6, 12], 'name': 'H-Share'},
    'HCHH': {'months': [1, 2, 3, 6], 'name': 'CES China 120'},
    'HG': {'months': [3, 5, 7, 9, 12], 'name': 'Copper'},
    'HMCE': {'months': [1, 2, 3, 6], 'name': 'Mini H-Shares'},
    'HMH': {'months': [1, 2, 3, 6], 'name': 'Mini Hang Seng'},
    'HO': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'Heating Oil'},
    'HSI': {'months': [1, 2, 3, 6, 12], 'name': 'Hang Seng'},
    'J7': {'months': [3, 6], 'name': 'E-mini Japanese Yen'},
    'JY': {'months': [3, 6, 9, 12], 'name': 'Japanese Yen'},
    'KC': {'months': [3, 5, 7, 9, 12], 'name': 'ICE Coffee'},
    'LC': {'months': [2, 4, 6, 8, 10, 12], 'name': 'Live Cattle'},
    'LH': {'months': [2, 4, 5, 6, 7, 8, 10, 12], 'name': 'Lean Hogs'},
    'M6A': {'months': [3, 6], 'name': 'E-micro AUD/USD'},
    'M6B': {'months': [3, 6], 'name': 'E-micro GBP/USD'},
    'M6E': {'months': [3, 6], 'name': 'E-micro EUR/USD'},
    'MCD': {'months': [3, 6], 'name': 'E-micro CAD/USD'},
    'MGC': {'months': [2, 4, 6, 8, 10, 12], 'name': 'E-micro Gold'},
    'MJY': {'months': [3, 6], 'name': 'E-micro JPY/USD'},
    'MP': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'Mexican Peso'},
    'NE': {'months': [3, 6, 9, 12], 'name': 'New Zealand Dollar'},
    'NG': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'Natural Gas'},
    'NIY': {'months': [3, 6, 9, 12], 'name': 'Nikkei 225 Yen-based'},
    'NKD': {'months': [3, 6, 9, 12], 'name': 'Nikkei 225 Dollar-based'},
    'NQ': {'months': [3, 6, 9, 12], 'name': 'E-mini NASDAQ 100'},
    'OJ': {'months': [1, 3, 5, 7, 9, 11], 'name': 'ICE ORANGE JUICE'},
    'PA': {'months': [3, 6, 9, 12], 'name': 'Palladium'},
    'PL': {'months': [4, 7, 10], 'name': 'Platinum'},
    'QC': {'months': [3, 5, 7, 9, 12], 'name': 'E-mini Copper'},
    'QG': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'miNY Natural Gas'},
    'QM': {'months': [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'miNY Crude Oil'},
    'RB': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'RBOB Gasoline'},
    'RTY': {'months': [3, 6, 9, 12], 'name': 'E-mini Russell 2000'},
    'RY': {'months': [3, 6, 9, 12], 'name': 'Euro/Yen Cross'},
    'SB': {'months': [3, 5, 7, 10], 'name': 'ICE Sugar'},
    'SCH': {'months': [1, 2, 3, 6, 9, 12], 'name': 'SGX MSCI China'},
    'SCN': {'months': [1, 2, 3, 6, 9, 12], 'name': 'SGX FTSE China A50'},
    'SF': {'months': [3, 6, 9, 12], 'name': 'Swiss Franc'},
    'SI': {'months': [1, 3, 5, 7, 9, 12], 'name': 'Silver'},
    'SIN': {'months': [1, 2, 6, 9, 12], 'name': 'SGX Nifty'},
    'SIU': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'SGX INR/USD FX'},
    'SKU': {'months': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'SGX KRW/USD FX'},
    'SNS': {'months': [3, 6, 9, 12], 'name': 'SGX Mini Nikkei 225'},
    'SNU': {'months': [3, 6, 9, 12], 'name': 'SGX USD Nikkei 225'},
    'SSG': {'months': [1, 2, 3, 6, 9, 12], 'name': 'SIMSCI'},
    'SSI': {'months': [3, 6, 9, 12], 'name': 'SGX Nikkei 225'},
    'STW': {'months': [1, 2, 3, 6, 9, 12], 'name': 'MSCI Taiwan'},
    'SUC': {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'name': 'SGX USD/CNH FX'},
    'URO': {'months': [3, 6, 9, 12], 'name': 'Euro FX'},
    'VX': {'months': [2, 3, 4, 5, 6, 7, 8, 9], 'name': 'VIX'},
    'XC': {'months': [3, 5, 7, 9, 12], 'name': 'Mini Corn'},
    'XK': {'months': [1, 3, 5, 7, 8, 9, 11], 'name': 'Mini Soybean'},
    'XW': {'months': [3, 5, 7, 9, 12], 'name': 'Mini Wheat'},
    'YG': {'months': [2, 4, 6, 8, 12], 'name': 'Mini Gold'},
    'YI': {'months': [3, 5, 7, 9, 12], 'name': 'Mini Silver'},
    'YM': {'months': [3, 6, 9, 12], 'name': 'Mini Dow'},
    'ZB': {'months': [3, 6, 9], 'name': '30Year U.S. T-Bond'},
    'ZC': {'months': [3, 5, 7, 9, 12], 'name': 'Corn'},
    'ZF': {'months': [3, 6, 9], 'name': '5Year U.S. T-Note'},
    'ZL': {'months': [1, 3, 5, 7, 8, 9, 10, 12], 'name': 'Soybean Oil'},
    'ZM': {'months': [1, 3, 5, 7, 8, 9, 10, 12], 'name': 'Soybean Meal'},
    'ZN': {'months': [3, 6, 9], 'name': '10Year U.S. T-Note'},
    'ZO': {'months': [3, 5, 7, 9, 12], 'name': 'Oats'},
    'ZR': {'months': [1, 3, 5, 7, 9, 11], 'name': 'Rough Rice'},
    'ZS': {'months': [1, 3, 5, 7, 8, 9, 11], 'name': 'Soybeans'},
    'ZT': {'months': [3, 6, 9], 'name': '2Year U.S.T-Note'},
    'ZW': {'months': [3, 5, 7, 9, 12], 'name': 'Wheat'}
}