"""Advanced usage examples for aio123pan."""

import asyncio
from pathlib import Path

from aio123pan import Pan123Client


async def example_upload_file():
    """Example: Upload a file with progress tracking."""

    def progress_callback(current: int, total: int):
        percentage = (current / total) * 100
        print(f"Upload progress: {percentage:.1f}% ({current}/{total} bytes)")

    async with Pan123Client() as client:
        file_id = await client.upload.upload_file(
            file_path="test_file.txt",
            parent_file_id=0,
            progress_callback=progress_callback,
        )
        print(f"File uploaded successfully! File ID: {file_id}")


async def example_upload_to_folder():
    """Example: Create folder and upload file to it."""
    async with Pan123Client() as client:
        folder_id = await client.folder.create_folder(parent_file_id=0, name="MyUploads")
        print(f"Created folder with ID: {folder_id}")

        file_id = await client.upload.upload_file(
            file_path="document.pdf",
            parent_file_id=folder_id,
        )
        print(f"Uploaded file to folder! File ID: {file_id}")


async def example_download_file():
    """Example: Download a file."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=1)
        if files.file_list:
            file_info = files.file_list[0]
            print(f"Downloading: {file_info.filename}")

            await client.file.download_file(file_id=file_info.file_id, save_path=f"downloaded_{file_info.filename}")
            print("Download complete!")


async def example_rename_and_move():
    """Example: Rename and move a file."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=1)
        if files.file_list:
            file_info = files.file_list[0]
            original_name = file_info.filename

            await client.file.rename_file(file_info.file_id, f"renamed_{original_name}")
            print(f"Renamed: {original_name} -> renamed_{original_name}")

            target_folder = await client.folder.create_folder(parent_file_id=0, name="Archive")
            await client.file.move_file(file_info.file_id, target_folder)
            print("Moved file to Archive folder")


async def example_copy_file():
    """Example: Copy a file to another location."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=1)
        if files.file_list:
            file_info = files.file_list[0]

            backup_folder = await client.folder.create_folder(parent_file_id=0, name="Backup")
            new_file_id = await client.file.copy_file(file_info.file_id, backup_folder)
            print(f"Copied file to Backup folder. New file ID: {new_file_id}")


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


async def example_trash_operations():
    """Example: Work with trash."""
    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=0, limit=1)
        if files.file_list:
            file_info = files.file_list[0]

            await client.file.delete_file(file_info.file_id)
            print(f"Deleted: {file_info.filename}")

            print("\nFiles in trash:")
            async for trashed_file in client.trash.list_all_trash():
                print(f"  - {trashed_file.filename}")

            await client.trash.restore_file(file_info.file_id)
            print(f"\nRestored: {file_info.filename}")


async def example_batch_upload():
    """Example: Batch upload multiple files."""
    async with Pan123Client() as client:
        upload_folder = await client.folder.create_folder(parent_file_id=0, name="BatchUpload")

        files_to_upload = ["file1.txt", "file2.txt", "file3.txt"]

        for file_path in files_to_upload:
            if Path(file_path).exists():
                try:
                    file_id = await client.upload.upload_file(
                        file_path=file_path,
                        parent_file_id=upload_folder,
                    )
                    print(f"Uploaded: {file_path} -> File ID: {file_id}")
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")


async def example_organize_by_extension():
    """Example: Organize files by extension."""
    async with Pan123Client() as client:
        folders_created = {}

        async for file_info in client.file.list_all_files(parent_file_id=0):
            if file_info.is_file:
                ext = Path(file_info.filename).suffix.lower().lstrip(".")
                if not ext:
                    ext = "no_extension"

                if ext not in folders_created:
                    folder_id = await client.folder.create_folder(parent_file_id=0, name=f"Extension_{ext}")
                    folders_created[ext] = folder_id
                    print(f"Created folder for .{ext} files")

                await client.file.move_file(file_info.file_id, folders_created[ext])
                print(f"Moved {file_info.filename} to Extension_{ext} folder")


async def example_get_storage_usage():
    """Example: Get storage usage information."""
    async with Pan123Client() as client:
        user_info = await client.user.get_user_info()

        used_gb = user_info.space_used / (1024**3)
        total_gb = user_info.space_capacity / (1024**3)
        percentage = (user_info.space_used / user_info.space_capacity) * 100

        print(f"User: {user_info.nickname}")
        print(f"Storage: {used_gb:.2f} GB / {total_gb:.2f} GB ({percentage:.1f}%)")


if __name__ == "__main__":
    asyncio.run(example_upload_file())
