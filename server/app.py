from concurrent import futures
import logging
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from pb import users_pb2, users_pb2_grpc
import hashlib
from datetime import datetime
import uuid
import re
from pydantic import BaseModel, EmailStr, constr

# Configure logger to show debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory database for users
users_db = {}


# Pydantic model for user data validation
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=6)  # Password must be at least 6 characters long


class UserUpdate(BaseModel):
    id: str
    name: str
    email: EmailStr
    password: str = None  # Optional


# New utility function to count total users
def total_users_count():
    """Returns the total number of users."""
    return len(users_db)


# Utility function to generate unique ID
def generate_id():
    """Generates a unique ID for a user."""
    return str(total_users_count() + 1)


# Utility function to hash passwords
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# Utility function to convert datetime to Timestamp
def convert_datetime_to_timestamp(datetime_obj: datetime) -> Timestamp:
    """Converts a datetime object to a gRPC Timestamp."""
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime_obj)
    return timestamp


# Error handling utility
def handle_grpc_error(context, code, message):
    """Sets the gRPC context error code and message."""
    context.set_code(code)
    context.set_details(message)
    logger.error(f"Error {code.name}: {message}")


class UsersServicer(users_pb2_grpc.UsersServicer):
    def GetUsers(self, request, context):
        logger.debug("GetUsers Request: %s", request)
        try:
            users_list = []
            for user_id, user_data in users_db.items():
                users_list.append(
                    users_pb2.User(
                        id=user_data["id"],
                        name=user_data["name"],
                        email=user_data["email"],
                        password=user_data[
                            "password"
                        ],  # Ideally, this should not be exposed
                        created_at=user_data["created_at"],
                        updated_at=user_data["updated_at"],
                    )
                )
            return users_pb2.GetUsersResponse(
                users=users_list, total_count=len(users_list)
            )

        except Exception as e:
            handle_grpc_error(
                context, grpc.StatusCode.INTERNAL, "Failed to fetch users."
            )
            return users_pb2.GetUsersResponse()

    def GetUserByID(self, request, context):
        logger.debug("GetUserByID Request: %s", request)
        try:
            user_data = users_db.get(request.id)
            if not user_data:
                handle_grpc_error(context, grpc.StatusCode.NOT_FOUND, "User not found.")
                return users_pb2.GetUserByIDResponse()

            return users_pb2.GetUserByIDResponse(
                user=users_pb2.User(
                    id=user_data["id"],
                    name=user_data["name"],
                    email=user_data["email"],
                    password=user_data[
                        "password"
                    ],  # Ideally, this should not be exposed
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"],
                )
            )

        except Exception as e:
            handle_grpc_error(
                context, grpc.StatusCode.INTERNAL, "Failed to retrieve user."
            )
            return users_pb2.GetUserByIDResponse()

    def CreateUser(self, request, context):
        logger.debug("CreateUser Request: %s", request)
        try:
            # Validate request data using Pydantic
            user_data = UserCreate(
                name=request.user.name,
                email=request.user.email,
                password=request.user.password,
            )

            # Check for existing user with the same email
            if user_data.email in [user["email"] for user in users_db.values()]:
                handle_grpc_error(
                    context,
                    grpc.StatusCode.ALREADY_EXISTS,
                    "User with this email already exists.",
                )
                return users_pb2.CreateUserResponse()

            user_id = generate_id()
            created_at = convert_datetime_to_timestamp(datetime.now())
            updated_at = created_at
            hashed_password = hash_password(user_data.password)

            users_db[user_id] = {
                "id": user_id,
                "name": user_data.name,
                "email": user_data.email,
                "password": hashed_password,
                "created_at": created_at,
                "updated_at": updated_at,
            }

            user = users_pb2.User(
                id=user_id,
                name=user_data.name,
                email=user_data.email,
                password=hashed_password,
                created_at=created_at,
                updated_at=updated_at,
            )

            return users_pb2.CreateUserResponse(
                user=user, message="User created successfully"
            )

        except Exception as e:
            handle_grpc_error(
                context, grpc.StatusCode.INTERNAL, "Failed to create user."
            )
            return users_pb2.CreateUserResponse()

    def UpdateUser(self, request, context):
        logger.debug("UpdateUser Request: %s", request)
        try:
            user_data = users_db.get(request.user.id)
            if not user_data:
                handle_grpc_error(context, grpc.StatusCode.NOT_FOUND, "User not found.")
                return users_pb2.UpdateUserResponse()

            # Validate update request data using Pydantic
            update_data = UserUpdate(
                id=request.user.id,
                name=request.user.name,
                email=request.user.email,
                password=request.user.password,
            )

            # Update user details (except the password, unless explicitly provided)
            user_data["name"] = update_data.name
            user_data["email"] = update_data.email
            if update_data.password:
                user_data["password"] = hash_password(update_data.password)
            user_data["updated_at"] = convert_datetime_to_timestamp(datetime.now())

            user = users_pb2.User(
                id=update_data.id,
                name=update_data.name,
                email=update_data.email,
                password=user_data["password"],
                created_at=user_data["created_at"],
                updated_at=user_data["updated_at"],
            )

            return users_pb2.UpdateUserResponse(
                user=user, message="User updated successfully"
            )

        except Exception as e:
            handle_grpc_error(
                context, grpc.StatusCode.INTERNAL, "Failed to update user."
            )
            return users_pb2.UpdateUserResponse()

    def DeleteUser(self, request, context):
        logger.debug("DeleteUser Request: %s", request)
        try:
            if request.id not in users_db:
                handle_grpc_error(context, grpc.StatusCode.NOT_FOUND, "User not found.")
                return users_pb2.DeleteUserResponse()

            del users_db[request.id]
            return users_pb2.DeleteUserResponse(
                id=request.id, message="User deleted successfully"
            )

        except Exception as e:
            handle_grpc_error(
                context, grpc.StatusCode.INTERNAL, "Failed to delete user."
            )
            return users_pb2.DeleteUserResponse()


def serve():
    # Create a gRPC server with 10 workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add UsersServicer to the server
    users_pb2_grpc.add_UsersServicer_to_server(UsersServicer(), server)

    # Bind the server to port 50051
    server.add_insecure_port("[::]:50051")

    # Start the server
    server.start()
    logger.info("Server started on port 50051")

    # Keep the server running
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
