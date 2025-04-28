import hmac
import hashlib

api_key = input('Введите api_key: ').strip()
api_secret = input('Введите api_secret: ').strip()
data = 'all'
signature = hmac.new(api_secret.encode(), data.encode(), hashlib.sha256).hexdigest()

print(f'signature: {signature}')