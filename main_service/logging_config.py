import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse


class Logger:
    def __init__(self, log_level: int = logging.DEBUG, log_file: Optional[str] = "logging_files/app.log"):
        # Уровень логирования
        self.log_level = log_level
        # Имя файла
        self.log_file = log_file

        # Созданние объекта логера
        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(self.log_level)

        # Формат для логов
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Обработчик, выводящий информацию в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(self.log_file, maxBytes=10**6, backupCount=3)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def log_request(self, request):
        self.logger.info(f"Request: {request.method} {request.url.path}")

    def log_exception(self, exception: Exception):
        self.logger.error(f"Exception: {str(exception)}")

    def register_global_exceprtion_handler(self, app: FastAPI):
        """
        Регистрирует глобальный обработчик исключений для FastAPI, который будет логировать все непойманные исключения.
        """
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc:Exception):
            self.log_exception(exc)
            return JSONResponse(
                status_code = 500,
                content={"detail": "Internal Server Error"}
            )
