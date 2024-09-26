import grpc
from pb import users_pb2, users_pb2_grpc
from grpc import StatusCode


def handle_grpc_error(error):
    """Handles gRPC errors and prints user-friendly messages."""
    if error.code() == StatusCode.NOT_FOUND:
        print("Error: Resource not found.")
    elif error.code() == StatusCode.ALREADY_EXISTS:
        print("Error: Resource already exists.")
    elif error.code() == StatusCode.INVALID_ARGUMENT:
        print("Error: Invalid argument provided.")
    elif error.code() == StatusCode.UNAUTHENTICATED:
        print("Error: Authentication failed.")
    elif error.code() == StatusCode.PERMISSION_DENIED:
        print("Error: Permission denied.")
    else:
        print(f"An unexpected error occurred: {error.details()}")


def create_user(stub, name, email, password):
    """Create a new user."""
    try:
        user = users_pb2.User(name=name, email=email, password=password)
        response = stub.CreateUser(users_pb2.CreateUserRequest(user=user))
        print(f"CreateUser Response: {response.user}, Message: {response.message}")
    except grpc.RpcError as e:
        handle_grpc_error(e)


def get_users(stub, page, page_size):
    """Retrieve multiple users."""
    try:
        response = stub.GetUsers(
            users_pb2.GetUsersRequest(page=page, page_size=page_size)
        )
        print(f"Total users: {response.total_count}")
        for user in response.users:
            print(f"User: {user.id}, Name: {user.name}, Email: {user.email}")
    except grpc.RpcError as e:
        handle_grpc_error(e)


def get_user_by_id(stub, user_id):
    """Retrieve a single user by ID."""
    try:
        response = stub.GetUserByID(users_pb2.GetUserByIDRequest(id=user_id))
        if response.user:
            print(f"User Found: {response.user}")
        else:
            print("User not found")
    except grpc.RpcError as e:
        handle_grpc_error(e)


def update_user(stub, user_id, name, email, password):
    """Update an existing user."""
    try:
        user = users_pb2.User(id=user_id, name=name, email=email, password=password)
        response = stub.UpdateUser(users_pb2.UpdateUserRequest(user=user))
        print(f"UpdateUser Response: {response.user}, Message: {response.message}")
    except grpc.RpcError as e:
        handle_grpc_error(e)


def delete_user(stub, user_id):
    """Delete a user by ID."""
    try:
        response = stub.DeleteUser(users_pb2.DeleteUserRequest(id=user_id))
        print(f"DeleteUser Response: ID {response.id}, Message: {response.message}")
    except grpc.RpcError as e:
        handle_grpc_error(e)


def run():
    """Client entry point."""
    # Connect to the gRPC server
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = users_pb2_grpc.UsersStub(channel)

        # 1. Create new users
        print("Creating users...")
        create_user(stub, "John Doe", "john@example.com", "password123")
        create_user(stub, "Jane Doe", "jane@example.com", "password456")

        # 2. Get all users
        print("\nFetching all users...")
        get_users(stub, page=1, page_size=10)

        # 3. Get a specific user by ID
        print("\nFetching a specific user by ID...")
        user_id = "1"  # Replace with actual ID returned from server
        get_user_by_id(stub, user_id)

        # 4. Update a user
        print("\nUpdating a user...")
        update_user(
            stub,
            user_id="1",
            name="John Updated",
            email="john_updated@example.com",
            password="newpassword123",
        )

        # 5. Delete a user
        print("\nDeleting a user...")
        delete_user(stub, user_id="1")

        # 6. Fetch all users again to confirm deletion
        print("\nFetching all users after deletion...")
        get_users(stub, page=1, page_size=10)


if __name__ == "__main__":
    run()
