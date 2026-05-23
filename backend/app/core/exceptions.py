"""Пользовательские исключения приложения."""


class AppException(Exception):
    """
    Базовое исключение приложения.
    
    Все пользовательские исключения должны наследовать от этого класса.
    Содержит message и status_code для HTTP ответа.
    """
    
    def __init__(self, message: str, status_code: int = 400):
        """
        Инициализация исключения.
        
        Args:
            message: Описание ошибки
            status_code: HTTP статус код (по умолчанию 400)
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Ошибка аутентификации - неверный пароль, токен, и т.д."""
    
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message, 401)


class AuthorizationError(AppException):
    """Ошибка авторизации - пользователь не имеет прав доступа."""
    
    def __init__(self, message: str = "Недостаточно прав доступа"):
        super().__init__(message, 403)


class NotFoundError(AppException):
    """Ошибка - ресурс не найден."""
    
    def __init__(self, resource: str = "Ресурс"):
        super().__init__(f"{resource} не найден", 404)


class ValidationError(AppException):
    """Ошибка валидации данных."""
    
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message, 422)


class ConflictError(AppException):
    """Ошибка конфликта ресурса - например, email уже существует."""
    
    def __init__(self, message: str = "Конфликт ресурса"):
        super().__init__(message, 409)


class InternalServerError(AppException):
    """Ошибка внутреннего сервера."""
    
    def __init__(self, message: str = "Ошибка внутреннего сервера"):
        super().__init__(message, 500)
