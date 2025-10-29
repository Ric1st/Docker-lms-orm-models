# gunicorn_config.py

# Socket untuk komunikasi dengan Nginx. 
# Jika Gunicorn dan Nginx di server yang sama, gunakan alamat local (127.0.0.1:8000)
bind = "127.0.0.1:8000"

# Jumlah worker yang ideal biasanya (2 * $num_cores) + 1
workers = 3 

# Kelas worker yang digunakan (async adalah yang paling umum)
worker_class = "sync" # Bisa diubah ke 'gevent' atau 'eventlet' untuk performa lebih baik (membutuhkan instalasi tambahan)

# Lokasi log (ganti dengan path log server Anda)
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Waktu timeout (jika permintaan lebih dari 30 detik)
timeout = 30 