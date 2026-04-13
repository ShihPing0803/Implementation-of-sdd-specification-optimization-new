class AppError(Exception):
    pass


class ValidationError(AppError):
    pass


class BusinessError(AppError):
    pass


class StorageError(AppError):
    pass