from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from io import BytesIO
import random
import smtplib
import string
from typing import Annotated, Any
from uuid import uuid4

from PIL import Image
from PIL.Image import Image as PILImage
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import EmailStr

from app.utils.config import get_env_settings
from app.utils.logger_config import user_lobby_logger

oauth2_scheme = HTTPBearer()
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


class EmailService:
    @staticmethod
    def send_registration_confirm_link(
        email: EmailStr,
        link: str,
    ) -> None:
        """Функция отправки ссылки на почту"""

        subject = 'Подтверждение почты в TowerEmpire.'
        body = f"""
        <h2>Спасибо за регистрацию!</h2>
        <p>Для подтверждения почты перейдите по ссылке:</p>
        <a href="{link}" target="_blank">Перейти по ссылке</a>
        """
        EmailService._send_email(email, subject, body, subtype='html')

    @staticmethod
    def send_password_reset_code(
        email: EmailStr,
        code: str,
    ) -> None:
        """Функция для отправки кода для сбора пароля"""

        subject = 'Сброс пароля'
        body = f'Ваш код для сброса пароля: {code}'
        EmailService._send_email(email, subject, body)

    @staticmethod
    def _send_email(
        email: list[EmailStr] | EmailStr,
        subject: str,
        body: str,
        subtype: str = 'plain',  # Также есть возможность отправить 'html' --> MessageType.html.
    ) -> None:
        """Функция для отправки email"""
        smtp_server = get_env_settings().smtp_server.get_secret_value()
        smtp_username = get_env_settings().smtp_username.get_secret_value()
        smtp_port = 465
        smtp_password = get_env_settings().smtp_password.get_secret_value()

        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = smtp_username
        message['To'] = email
        message.set_content(body, subtype=subtype)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
                server.send_message(message)
            else:
                server.send_message(message)


def generate_verification_code(
    length: int = 6,
) -> str:
    """Функция генерации 6 значного кода"""
    return ''.join(random.choices(string.digits, k=length))


def generate_token(
    data: dict[str, Any],
    token_type: str,
) -> str:
    """Функция генерации токенов"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(timezone.utc)
    to_encode.update(
        {
            'token_type': token_type,
            'exp': expire,
            'iat': iat,
            'jti': str(uuid4()),
        },
    )
    return jwt.encode(
        to_encode,
        get_env_settings().secret_key.get_secret_value(),
        algorithm=get_env_settings().algorithm.get_secret_value(),
    )


def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
) -> int:
    """Функция получения id пользователя"""
    try:
        jwt_token = token.credentials
        payload = jwt.decode(
            jwt_token,
            get_env_settings().secret_key.get_secret_value(),
            algorithms=[get_env_settings().algorithm.get_secret_value()],
        )
        _id: int | None = payload.get('user_id')
        if _id is None:
            raise HTTPException(status_code=401, detail='Неверный токен')
        return _id
    except JWTError:
        raise HTTPException(status_code=401, detail='Неверный или истёкший токен')


def get_current_ws_user(
    token: str,
) -> int:
    try:
        payload = jwt.decode(
            token,
            get_env_settings().secret_key.get_secret_value(),
            algorithms=[get_env_settings().algorithm.get_secret_value()],
        )
        _id: int | None = payload.get('user_id')
        if _id is None:
            raise HTTPException(status_code=401, detail='Неверный токен')
        return _id
    except JWTError:
        raise HTTPException(status_code=401, detail='Неверный или истёкший токен')


def create_access_token(
    data: dict[str, int],
) -> str:
    """Функция создания access токена"""
    return generate_token(data, 'access')


def create_refresh_token(
    data: dict[str, int],
) -> str:
    """Функция создания refresh токена"""
    return generate_token(data, 'refresh')


def create_token_for_confirm_email(
    data: dict[str, EmailStr],
) -> str:
    """Функция создания токена для подтверждения регистрации пользователя по почте."""
    return generate_token(data, 'confirm')


def generate_link_for_confirm_email(url: str, token: str) -> str:
    """Функция генерирует ссылку для подтверждения регистрации."""
    return f'{url}access_email/{token}/'


def resize_user_avatar(max_size: int, contents: bytes) -> PILImage:
    """Функция обрезки аватара по максимальному размеру"""
    image: PILImage = Image.open(BytesIO(contents))
    if max(image.width, image.height) > max_size:
        user_lobby_logger.warning('Изображение слишком большое, будет уменьшено!')
        ratio = max_size / max(image.width, image.height)
        new_size = (round(image.width * ratio), round(image.height * ratio))
        user_lobby_logger.info('Изменяем размер рисунка на {}', new_size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image
