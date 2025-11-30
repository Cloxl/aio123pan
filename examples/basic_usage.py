"""Usage examples for aio123pan."""

import asyncio

from aio123pan import Pan123Client


async def example_1_auto_load():
    """Example 1: Auto-load credentials from environment variables.

    Set environment variables:
    export PAN123_CLIENT_ID=your_client_id
    export PAN123_CLIENT_SECRET=your_client_secret

    Or create .env file:
    PAN123_CLIENT_ID=your_client_id
    PAN123_CLIENT_SECRET=your_client_secret
    """
    async with Pan123Client() as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname}")
        print(f"Space: {user.space_used}/{user.space_capacity} bytes")


async def example_2_explicit_credentials():
    """Example 2: Provide credentials explicitly (overrides environment variables)."""
    async with Pan123Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
    ) as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname}")


async def example_3_file_operations():
    """Example 3: File operations."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=10)
        print(f"Found {len(files.file_list)} files")

        for file_info in files.file_list:
            file_type = "Folder" if file_info.is_folder else "File"
            print(f"{file_type}: {file_info.filename} ({file_info.size} bytes)")


async def example_4_auto_pagination():
    """Example 4: Automatic pagination with async iterator."""
    async with Pan123Client() as client:
        async for file_info in client.file.list_all_files(parent_file_id=0):
            print(f"{file_info.filename}")


async def example_5_create_folder():
    """Example 5: Create folder."""
    async with Pan123Client() as client:
        folder_id = await client.folder.create_folder(parent_file_id=0, name="MyNewFolder")
        print(f"Created folder with ID: {folder_id}")


async def example_6_disable_token_storage():
    """Example 6: Disable token storage (no persistent cache)."""
    async with Pan123Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        enable_token_storage=False,
    ) as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname}")


async def example_7_custom_env_file():
    """Example 7: Custom .env file path."""
    async with Pan123Client(
        env_file="/custom/path/.env",
    ) as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname}")


if __name__ == "__main__":
    asyncio.run(example_1_auto_load())
