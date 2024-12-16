from passlib.hash import bcrypt
import os

password = 'random1234'
print(bcrypt.hash(password))

from jose import jwt
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"

service_token = jwt.encode({"sub": "celery_service", "role": "service"}, SECRET_KEY, algorithm=ALGORITHM)
print(service_token)
