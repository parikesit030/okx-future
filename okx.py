import ccxt
import time

# Masukkan API key dan secret Anda
api_key = ''
api_secret = ''
passphrase = '!'  # Jika dibutuhkan oleh OKX

# Inisialisasi exchange
exchange = ccxt.okx({
    'apiKey': api_key,
    'secret': api_secret,
    'password': passphrase,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'swap',  # Penting: Pilih 'swap' untuk futures perpetual
    },
})

# Pilih pasangan trading futures
symbol = 'BTC-USDT-SWAP'

# Konfigurasi strategi
leverage = 100  # Leverage yang digunakan
trade_amount = 1  # Misal 100 USDT
stop_loss_pct = 0.01  # Stop-loss 1% di bawah harga masuk
take_profit_pct = 0.1  # Take-profit 2% di atas harga masuk

# Fungsi untuk mendapatkan harga terakhir
def get_last_price(symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

# Fungsi untuk membuka posisi long
def open_long(symbol, amount):
    order = exchange.create_market_buy_order(symbol, amount)
    return order

# Fungsi untuk membuka posisi short
def open_short(symbol, amount):
    order = exchange.create_market_sell_order(symbol, amount)
    return order

# Fungsi untuk menghitung take-profit dan stop-loss
def calculate_tp_sl(entry_price, stop_loss_pct, take_profit_pct, is_long=True):
    if is_long:
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct)
    else:
        stop_loss = entry_price * (1 + stop_loss_pct)
        take_profit = entry_price * (1 - take_profit_pct)
    return stop_loss, take_profit

# Fungsi utama untuk trading futures dengan stop-loss dan take-profit
def main():
    global leverage
    exchange.set_leverage(leverage, symbol)  # Mengatur leverage untuk pasangan trading

    while True:
        try:
            # Mengambil harga terbaru
            last_price = get_last_price(symbol)
            print(f"Current Price: {last_price}")

            # Masuk posisi long dengan stop-loss dan take-profit
            long_order = open_long(symbol, trade_amount / last_price)
            entry_price = last_price
            stop_loss, take_profit = calculate_tp_sl(entry_price, stop_loss_pct, take_profit_pct, is_long=True)
            print(f"Opened Long Position at {entry_price}. Stop-Loss: {stop_loss}, Take-Profit: {take_profit}")

            # Monitoring posisi long
            while True:
                current_price = get_last_price(symbol)
                if current_price <= stop_loss:
                    print(f"Hit Stop-Loss at {current_price}, exiting position.")
                    open_short(symbol, trade_amount / current_price)  # Exit by opening a short position
                    break
                elif current_price >= take_profit:
                    print(f"Hit Take-Profit at {current_price}, exiting position.")
                    open_short(symbol, trade_amount / current_price)  # Exit by opening a short position
                    break
                time.sleep(10)  # Monitoring setiap 10 detik

            time.sleep(60)  # Tunggu 1 menit sebelum melakukan trading berikutnya

        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
