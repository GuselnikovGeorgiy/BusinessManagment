from pydantic import BaseModel, ConfigDict
from typing import Optional


class DepartmentBase(BaseModel):
    name: str
    company_id: int
    parent_path: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_path: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    company_id: int
    path: str

    model_config = ConfigDict(from_attributes=True)