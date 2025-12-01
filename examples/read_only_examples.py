"""Read-only usage examples for aio123pan.

These examples are SAFE to run as they only read data without modifying anything.
"""

import asyncio

from aio123pan import Pan123Client


async def example_get_user_info():
    """Example: Get user information."""
    async with Pan123Client() as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname}")
        print(f"VIP: {user.vip}")
        print(f"Space: {user.space_used}/{user.space_permanent} bytes")


async def example_list_files():
    """Example: List files in a directory."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=10)
        print(f"Found {len(files.file_list)} files")

        for file_info in files.file_list:
            file_type = "Folder" if file_info.is_folder else "File"
            print(f"  - {file_type}: {file_info.filename} ({file_info.size} bytes)")


async def example_auto_pagination():
    """Example: Automatic pagination with async iterator."""
    async with Pan123Client() as client:
        print("Listing all files (auto-pagination):")
        count = 0
        async for file_info in client.file.list_all_files(parent_file_id=0):
            print(f"  {count + 1}. {file_info.filename}")
            count += 1
            if count >= 20:  # Limit output for demo
                print("  ... (showing first 20 files)")
                break


async def example_search_files():
    """Example: Search for files."""
    async with Pan123Client() as client:
        search_keyword = "test"
        print(f"Searching for files containing '{search_keyword}'...")

        files = await client.file.list_files(parent_file_id=0, search_data=search_keyword, search_mode=0)

        print(f"Found {len(files.file_list)} files:")
        for file_info in files.file_list:
            file_type = "Folder" if file_info.is_folder else "File"
            print(f"  - {file_type}: {file_info.filename}")


async def example_list_trash():
    """Example: List files in trash."""
    async with Pan123Client() as client:
        print("Files in trash:")
        async for trashed_file in client.trash.list_all_trash():
            file_type = "Folder" if trashed_file.is_folder else "File"
            print(f"  - {file_type}: {trashed_file.filename}")


async def example_get_storage_usage():
    """Example: Get storage usage information."""
    async with Pan123Client() as client:
        user_info = await client.user.get_user_info()

        used_gb = user_info.space_used / (1024**3)
        total_gb = user_info.space_permanent / (1024**3)
        percentage = (user_info.space_used / user_info.space_permanent) * 100

        print(f"User: {user_info.nickname}")
        print(f"Storage: {used_gb:.2f} GB / {total_gb:.2f} GB ({percentage:.1f}%)")


async def example_with_explicit_credentials():
    """Example: Provide credentials explicitly (overrides environment variables).

    Note: Replace 'your_client_id' and 'your_client_secret' with actual values,
    or comment out this example if you're using environment variables.
    """
    # Uncomment and replace with your actual credentials:
    # async with Pan123Client(
    #     client_id="your_client_id",
    #     client_secret="your_client_secret",
    # ) as client:
    #     user = await client.user.get_user_info()
    #     print(f"User: {user.nickname}")
    print("(Skipped: requires explicit credentials)")


async def example_disable_token_storage():
    """Example: Disable token storage (no persistent cache).

    Note: This will authenticate every time without caching the token.
    """
    # This example uses env credentials but disables token caching
    async with Pan123Client(enable_token_storage=False) as client:
        user = await client.user.get_user_info()
        print(f"User: {user.nickname} (token not cached)")


if __name__ == "__main__":
    print("=" * 60)
    print("Running SAFE read-only examples")
    print("=" * 60)
    print()

    # Uncomment the examples you want to run:
    asyncio.run(example_get_user_info())
    asyncio.run(example_list_files())
    asyncio.run(example_auto_pagination())
    asyncio.run(example_search_files())
    asyncio.run(example_list_trash())
    asyncio.run(example_get_storage_usage())
    # asyncio.run(example_with_explicit_credentials())  # Requires manual credentials
    # asyncio.run(example_disable_token_storage())  # Demonstrates token not being cached
