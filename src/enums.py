from enum import Enum


class ApiReponseStatus(str, Enum):
    FAILED = "failed"
    PROCESSING = "processing"
    SUCCESS = "success"


class AuthTokenType(str, Enum):
    JWT_TOKEN = "jwt"
    REFRESH_TOKEN = "refresh"


class MongoCollectionsNames(str, Enum):
    USER_MASTER = "user_master"

    # Only for permission management in the app, not an actual collection
    EMPLOYEE_MASTER = "employee_master"


class UserRoles(str, Enum):
    SUPER_ADMIN = "super_admin"
    EMPLOYEE = "employee"


class Environments(str, Enum):
    LOCAL = "LOCAL"
    UAT = "UAT"
    PRODUCTION = "PRODUCTION"


class EmployeePermissionType(str, Enum):
    VIEW = "view"
    EDIT = "edit"
    NOT_ALLOWED = "not_allowed"
