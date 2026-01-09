from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Базовый класс для модели"""

    model_config = ConfigDict(from_attributes=True)
