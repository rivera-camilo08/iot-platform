from fastapi import HTTPException, status


class EntityNotFound(HTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedAction(HTTPException):
    def __init__(self, detail: str = "No tiene permiso para realizar esta acción"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
