"""Write operation examples for aio123pan.

⚠️  WARNING: These examples will CREATE, MODIFY, or DELETE data in your 123Pan account!

These examples are commented out by default. Uncomment only the ones you want to run
and make sure you understand what they do before executing them.
"""

import secrets
from pathlib import Path

from aio123pan import Pan123Client

# Global variable to store the test folder ID
TEST_FOLDER_ID: int | None = None


async def example_create_folder():
    """Example: Create a new folder."""
    global TEST_FOLDER_ID
    async with Pan123Client() as client:
        random_name = f"aio123pan_test_{secrets.token_hex(4)}"
        TEST_FOLDER_ID = await client.folder.create_folder(parent_file_id=0, name=random_name)
        print(f"Created test folder '{random_name}' with ID: {TEST_FOLDER_ID}")


async def example_upload_file():
    """Example: Upload a file with progress tracking."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    def progress_callback(current: int, total: int):
        percentage = (current / total) * 100
        print(f"Upload progress: {percentage:.1f}% ({current}/{total} bytes)")

    # Create a test file if it doesn't exist
    test_file = Path("test_file.txt")
    if not test_file.exists():
        test_file.write_text("This is a test file created by aio123pan examples.\n")

    async with Pan123Client() as client:
        file_id = await client.upload.upload_file(
            file_path="test_file.txt",
            parent_file_id=TEST_FOLDER_ID,
            progress_callback=progress_callback,
        )
        print(f"File uploaded successfully! File ID: {file_id}")


async def example_upload_to_folder():
    """Example: Create subfolder and upload file to it."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        # Create subfolder inside test folder
        subfolder_id = await client.folder.create_folder(parent_file_id=TEST_FOLDER_ID, name="MyUploads")
        print(f"Created subfolder with ID: {subfolder_id}")

        # Create a test PDF-like file
        test_doc = Path("document.txt")
        if not test_doc.exists():
            test_doc.write_text("This is a test document.\n")

        # Upload file to subfolder
        file_id = await client.upload.upload_file(
            file_path="document.txt",
            parent_file_id=subfolder_id,
        )
        print(f"Uploaded file to subfolder! File ID: {file_id}")


async def example_rename_file():
    """Example: Rename a file."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=1)
        if files.file_list:
            file_info = files.file_list[0]
            original_name = file_info.filename

            await client.file.rename_file(file_info.file_id, f"renamed_{original_name}")
            print(f"Renamed: {original_name} -> renamed_{original_name}")
        else:
            print("No files found in test folder to rename")


async def example_move_file():
    """Example: Move a file to another folder."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        # Create target subfolder inside test folder
        target_folder = await client.folder.create_folder(parent_file_id=TEST_FOLDER_ID, name="Archive")

        # Move first file to target folder
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=1)
        if files.file_list and not files.file_list[0].is_folder:
            file_info = files.file_list[0]
            await client.file.move_file(file_info.file_id, target_folder)
            print(f"Moved {file_info.filename} to Archive folder")
        else:
            print("No files found in test folder to move")


async def example_copy_file():
    """Example: Copy a file to another location."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        # Create backup subfolder inside test folder
        backup_folder = await client.folder.create_folder(parent_file_id=TEST_FOLDER_ID, name="Backup")

        # Copy first file to backup folder
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=1)
        if files.file_list and not files.file_list[0].is_folder:
            file_info = files.file_list[0]
            new_file_id = await client.file.copy_file(file_info.file_id, backup_folder)
            print(f"Copied {file_info.filename} to Backup folder. New file ID: {new_file_id}")
        else:
            print("No files found in test folder to copy")


async def example_delete_file():
    """Example: Delete a file (moves to trash)."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=1)
        if files.file_list and not files.file_list[0].is_folder:
            file_info = files.file_list[0]
            await client.file.delete_file(file_info.file_id)
            print(f"Deleted: {file_info.filename} (moved to trash)")
        else:
            print("No files found in test folder to delete")


async def example_batch_delete():
    """Example: Batch delete multiple files."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=5)
        if files.file_list:
            # Only delete files, not folders
            file_ids = [f.file_id for f in files.file_list if not f.is_folder]
            if file_ids:
                await client.file.delete_file(file_ids)
                print(f"Deleted {len(file_ids)} files")
            else:
                print("No files found to delete (only folders)")
        else:
            print("No items found in test folder")


async def example_trash_operations():
    """Example: Work with trash (restore and permanent delete).

    FINAL STEP: Clean up test folder and all its contents.
    """
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        # Delete the entire test folder (moves to trash)
        await client.file.delete_file(TEST_FOLDER_ID)
        print(f"Deleted test folder (ID: {TEST_FOLDER_ID}) - moved to trash")

        # List trash to verify
        print("\nVerifying test folder is in trash:")
        trash_files = await client.trash.list_trash(limit=10)
        test_folder_in_trash = None
        for file_info in trash_files.file_list:
            if file_info.file_id == TEST_FOLDER_ID:
                test_folder_in_trash = file_info
                print(f"  ✓ Found in trash: {file_info.filename}")
                break

        # Permanently delete the test folder from trash
        if test_folder_in_trash:
            await client.trash.delete_permanently(TEST_FOLDER_ID)
            print(f"  ✓ Permanently deleted test folder: {test_folder_in_trash.filename}")

        print("\nCleanup complete! All test data has been removed.")


async def example_batch_upload():
    """Example: Batch upload multiple files."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        # Create upload subfolder inside test folder
        upload_folder = await client.folder.create_folder(parent_file_id=TEST_FOLDER_ID, name="BatchUpload")

        # Create and upload multiple test files
        files_to_upload = ["file1.txt", "file2.txt", "file3.txt"]

        for file_path in files_to_upload:
            test_file = Path(file_path)
            if not test_file.exists():
                test_file.write_text(f"Test content for {file_path}\n")

            try:
                file_id = await client.upload.upload_file(
                    file_path=file_path,
                    parent_file_id=upload_folder,
                )
                print(f"Uploaded: {file_path} -> File ID: {file_id}")
            except Exception as e:
                print(f"Failed to upload {file_path}: {e}")


async def example_organize_by_extension():
    """Example: Organize files by extension into folders."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        folders_created = {}

        # Iterate through all files in test folder
        async for file_info in client.file.list_all_files(parent_file_id=TEST_FOLDER_ID):
            if file_info.is_file:
                # Get file extension
                ext = Path(file_info.filename).suffix.lower().lstrip(".")
                if not ext:
                    ext = "no_extension"

                # Create folder for this extension if not exists
                if ext not in folders_created:
                    folder_id = await client.folder.create_folder(
                        parent_file_id=TEST_FOLDER_ID, name=f"Extension_{ext}"
                    )
                    folders_created[ext] = folder_id
                    print(f"Created folder for .{ext} files")

                # Move file to extension folder
                await client.file.move_file(file_info.file_id, folders_created[ext])
                print(f"Moved {file_info.filename} to Extension_{ext} folder")


async def example_download_file():
    """Example: Download a file."""
    if TEST_FOLDER_ID is None:
        print("Skipped: TEST_FOLDER_ID not set")
        return

    async with Pan123Client() as client:
        files = await client.file.list_files(parent_file_id=TEST_FOLDER_ID, limit=1)
        if files.file_list and not files.file_list[0].is_folder:
            file_info = files.file_list[0]
            print(f"Downloading: {file_info.filename}")

            await client.file.download_file(file_id=file_info.file_id, save_path=f"downloaded_{file_info.filename}")
            print("Download complete!")
        else:
            print("No files found in test folder to download")


if __name__ == "__main__":
    print("=" * 70)
    print("⚠️  WARNING: WRITE OPERATIONS - WILL MODIFY YOUR 123PAN DATA!")
    print("=" * 70)
    print()
    print("All examples are commented out by default for safety.")
    print("Uncomment only the ones you want to run.")
    print()
    print("-" * 70)
    print()

    # ⚠️  UNCOMMENT ONLY THE EXAMPLES YOU WANT TO RUN ⚠️
    #
    # Safe write operations (create new data):
    # asyncio.run(example_create_folder())
    # asyncio.run(example_upload_file())
    # asyncio.run(example_upload_to_folder())
    # asyncio.run(example_batch_upload())
    # asyncio.run(example_download_file())
    #
    # Modify operations (change existing data):
    # asyncio.run(example_rename_file())
    # asyncio.run(example_move_file())
    # asyncio.run(example_copy_file())
    # asyncio.run(example_organize_by_extension())
    #
    # Destructive operations (delete data):
    # asyncio.run(example_delete_file())
    # asyncio.run(example_batch_delete())
    # asyncio.run(example_trash_operations())

    print("No examples executed. Uncomment the examples you want to run.")
