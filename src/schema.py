from typing import Optional, Union

from pydantic import BaseModel, Field

from src.enums import EmployeePermissionType


class UserLoginRequest(BaseModel):
    email: str
    password: str
    refresh_token_info: Optional[dict] = None


class AddUpdateUserRequest(BaseModel):
    email: str
    name: str
    phone_number: int


class GetAccessTokenRequest(BaseModel):
    email: str
    refresh_token: str


# Employee Master
class EmployeePermissions(BaseModel):
    gallery_management: EmployeePermissionType = EmployeePermissionType.NOT_ALLOWED
    blog_management: EmployeePermissionType = EmployeePermissionType.NOT_ALLOWED
    employee_master: EmployeePermissionType = EmployeePermissionType.NOT_ALLOWED


class EmployeeDetails(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=300)
    phone_number: str = Field(..., max_length=20)
    permissions: EmployeePermissions
