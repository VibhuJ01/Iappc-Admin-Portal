from datetime import datetime, timezone
from http import HTTPStatus

from pydantic import ValidationError
from pymongo import ReturnDocument

from src.enums import MongoCollectionsNames, UserRoles
from src.mongodb.base import BaseDatabase
from src.schema import EmployeeDetails
from src.utils import create_user_and_send_email


class EmployeeMaster:

    collection = BaseDatabase.get_collection(collection_name=MongoCollectionsNames.USER_MASTER)

    def is_user_exists(self, email: str) -> bool:
        user_exists = self.collection.find_one({"email": email.lower()})
        return user_exists is not None

    def add_employee(self, request_data: dict, current_user_email: str) -> tuple[dict, int]:
        try:
            validated_request_data = EmployeeDetails.model_validate(request_data)
        except ValidationError:
            return {"is_successful": False, "message": "Invalid or incomplete request data."}, HTTPStatus.BAD_REQUEST

        if self.is_user_exists(validated_request_data.email):
            return {
                "is_successful": False,
                "message": f"User with email '{validated_request_data.email}' already exists",
            }, HTTPStatus.BAD_REQUEST

        employee_data = validated_request_data.model_dump()

        extra_data = {
            "permissions": employee_data["permissions"],
            "created_at": datetime.now(timezone.utc),
            "created_by": current_user_email,
        }

        user_creation = create_user_and_send_email(
            email=validated_request_data.email,
            name=validated_request_data.name,
            role=UserRoles.EMPLOYEE,
            created_by=current_user_email,
            phone_number=validated_request_data.phone_number,
            extra_data=extra_data,
        )

        if not user_creation["is_successful"]:
            self.collection.delete_one({"email": validated_request_data.email})  # Rollback if needed
            return user_creation, HTTPStatus.INTERNAL_SERVER_ERROR

        return {"is_successful": True, "message": "Employee added successfully"}, HTTPStatus.OK

    def update_employee(self, request_data: dict, current_user_email: str) -> tuple[dict, int]:

        try:
            validated_request_data = EmployeeDetails.model_validate(request_data)
        except ValidationError:
            return {"is_successful": False, "message": "Invalid or incomplete request data."}, HTTPStatus.BAD_REQUEST

        update_data = validated_request_data.model_dump()
        employee_email = update_data.pop("email")

        update_data["updated_by"] = current_user_email
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = self.collection.find_one_and_update(
            {"email": employee_email.lower()},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        if not result:
            return {"is_successful": False, "message": "Employee not found"}, HTTPStatus.NOT_FOUND

        return {"is_successful": True, "message": "Employee updated successfully"}, HTTPStatus.OK

    def fetch_all_employees(self) -> tuple[dict, int]:

        employees = self.collection.find(
            {},
            {
                "_id": 0,
                "name": 1,
                "email": 1,
                "phone_number": 1,
                "permissions": 1,
                "is_disabled": 1,
            },
        )

        return {
            "is_successful": True,
            "employees": list(employees),
            "message": "Employees fetched successfully.",
        }, HTTPStatus.OK

    def disable_employee(self, disable_user_email: str, current_user_email: str) -> tuple[dict, int]:
        if disable_user_email.lower() == current_user_email.lower():
            return {
                "is_successful": False,
                "message": "You can't disable yourself.",
            }, HTTPStatus.FORBIDDEN

        user_to_disable = self.collection.find_one({"email": disable_user_email.lower(), "is_disabled": False})

        if not user_to_disable:
            return {
                "is_successful": False,
                "message": f"Employee with email '{disable_user_email}' not found or is already disabled.",
            }, HTTPStatus.NOT_FOUND

        result = self.collection.update_one(
            {
                "email": disable_user_email.lower(),
                "role": UserRoles.EMPLOYEE.value,
            },
            {"$set": {"is_disabled": True}},
        )

        if result.matched_count == 0:
            return {
                "is_successful": False,
                "message": "Failed to disable the employee. Invalid email.",
            }, HTTPStatus.BAD_REQUEST

        return {
            "is_successful": True,
            "message": f"Employee with '{disable_user_email}' has been disabled.",
        }, HTTPStatus.OK

    def enable_employee(self, enable_user_email: str) -> tuple[dict, int]:
        user_to_enable = self.collection.find_one({"email": enable_user_email.lower(), "is_disabled": True})

        if not user_to_enable:
            return {
                "is_successful": False,
                "message": f"Either Employee with email '{enable_user_email}' not found or is already enabled/active.",
            }, HTTPStatus.NOT_FOUND

        result = self.collection.update_one(
            {
                "email": enable_user_email.lower(),
                "role": UserRoles.EMPLOYEE.value,
            },
            {"$set": {"is_disabled": False}},
        )

        if result.matched_count == 0:
            return {
                "is_successful": False,
                "message": "Failed to enable the employee.",
            }, HTTPStatus.BAD_REQUEST

        return {
            "is_successful": True,
            "message": f"Employee with email '{enable_user_email}' has been enabled.",
        }, HTTPStatus.OK
