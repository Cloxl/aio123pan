"""Complete workflow examples for aio123pan.

⚠️  WARNING: These examples will CREATE, MODIFY, or DELETE data in your 123Pan account!

This file demonstrates complete end-to-end workflows that combine write and read operations.
All examples are commented out by default for safety.

Usage:
1. Uncomment the workflow you want to test
2. Run: python examples/complete_workflow_examples.py
3. Check the output and your 123Pan account
"""

import asyncio
import secrets
from datetime import datetime
from pathlib import Path

from aio123pan import Pan123Client

# Global variables to track created resources for cleanup
CREATED_FILE_IDS: list[int] = []
CREATED_FOLDER_IDS: list[int] = []
CREATED_SHARE_IDS: list[int] = []


async def workflow_direct_link():
    """Complete direct link workflow: create folder → upload file → enable → get URL → disable."""
    print("\n" + "=" * 70)
    print("Direct Link Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        # Step 1: Create a test folder
        print("\n[1/6] Creating test folder...")
        folder_name = f"DirectLinkTest_{secrets.token_hex(4)}"
        folder_id = await client.folder.create_folder(parent_file_id=0, name=folder_name)
        CREATED_FOLDER_IDS.append(folder_id)
        print(f"✅ Created folder: {folder_name} (ID: {folder_id})")

        # Step 2: Create and upload a test file
        print("\n[2/6] Creating and uploading test file...")
        test_file = Path("direct_link_test.txt")
        test_file.write_text(f"Direct link test file created at {datetime.now()}\n")
        file_id = await client.upload.upload_file(file_path="direct_link_test.txt", parent_file_id=folder_id)
        CREATED_FILE_IDS.append(file_id)
        print(f"✅ Uploaded file to folder (File ID: {file_id})")
        test_file.unlink()  # Clean up local file

        # Step 3: Enable direct link for the folder
        print("\n[3/6] Enabling direct link space for folder...")
        filename = await client.direct_link.enable_direct_link(folder_id)
        print(f"✅ Enabled direct link for: {filename}")

        # Step 4: Get direct link URL for the file
        print("\n[4/6] Getting direct link URL...")
        direct_url = await client.direct_link.get_direct_link_url(file_id)
        print(f"✅ Direct link URL: {direct_url}")

        # Step 5: Refresh direct link cache
        print("\n[5/6] Refreshing direct link cache...")
        await client.direct_link.refresh_direct_link_cache()
        print("✅ Cache refreshed")

        # Step 6: Disable direct link
        print("\n[6/6] Disabling direct link space...")
        filename = await client.direct_link.disable_direct_link(folder_id)
        print(f"✅ Disabled direct link for: {filename}")

        print("\n" + "=" * 70)
        print("Direct Link Workflow Completed Successfully!")
        print("=" * 70)


async def workflow_share():
    """Complete share workflow: upload file → create share → update share → list shares."""
    print("\n" + "=" * 70)
    print("Share Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        file_id = None
        try:
            # Step 1: Create and upload a test file
            print("\n[1/4] Creating and uploading test file...")
            test_file = Path("share_test.txt")
            test_file.write_text(f"Share test file created at {datetime.now()}\n")
            file_id = await client.upload.upload_file(file_path="share_test.txt", parent_file_id=0)
            print(f"✅ Uploaded file (File ID: {file_id})")
            test_file.unlink()

            # Step 2: Create a share link with password
            print("\n[2/4] Creating share link with password...")
            share = await client.share.create_share(
                file_ids=[file_id],
                share_name=f"Test Share {secrets.token_hex(4)}",
                expire_days=7,
                share_pwd="1234",
            )
            CREATED_SHARE_IDS.append(share.share_id)
            print("✅ Created share:")
            print(f"   ID: {share.share_id}")
            print(f"   URL: {share.share_url}")
            print("   Password: 1234")
            print("   Expires: 7 days")

            # Step 3: Update the share (change password and expiration)
            print("\n[3/4] Updating share link...")
            try:
                await client.share.update_share(
                    share_id=share.share_id,
                    share_name="Updated Share Name",
                    expire_days=1,
                    share_pwd="5678",
                )
                print("✅ Updated share:")
                print("   New password: 5678")
                print("   New expiration: 1 day")
            except Exception as e:
                print(f"⚠️  Update share API not available: {e}")
                print("   (This API may require special permissions)")

            # Step 4: List all shares to verify
            print("\n[4/4] Listing all shares...")
            shares = await client.share.list_shares(limit=5)
            print(f"✅ Found {len(shares.share_list)} shares (showing first 5):")
            for s in shares.share_list[:5]:
                status = "Expired" if s.is_expired else "Active"
                print(f"   - {s.share_name} [{status}]")
                print(f"     URL: {s.share_url}")
                if s.has_password:
                    print(f"     Password: {s.share_pwd}")
                print(f"     Downloads: {s.download_count}, Saves: {s.save_count}")

        finally:
            # Cleanup: Delete the test file
            if file_id:
                print("\n[Cleanup] Deleting test file...")
                try:
                    await client.file.delete_file(file_id)
                    print(f"✅ Deleted test file (ID: {file_id})")
                except Exception as e:
                    print(f"⚠️  Failed to delete file: {e}")
                    CREATED_FILE_IDS.append(file_id)  # Add to global list for later cleanup

        print("\n" + "=" * 70)
        print("Share Workflow Completed Successfully!")
        print("=" * 70)


async def workflow_folder_and_files():
    """Complete file management workflow in a single test folder."""
    print("\n" + "=" * 70)
    print("File Management Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        # Step 1: Create a test folder
        print("\n[1/8] Creating test folder...")
        test_folder_name = f"WorkflowTest_{secrets.token_hex(4)}"
        test_folder_id = await client.folder.create_folder(parent_file_id=0, name=test_folder_name)
        CREATED_FOLDER_IDS.append(test_folder_id)
        print(f"✅ Created test folder: {test_folder_name} (ID: {test_folder_id})")

        # Step 2: Create a subfolder inside test folder
        print("\n[2/8] Creating subfolder inside test folder...")
        subfolder_name = "Subfolder"
        subfolder_id = await client.folder.create_folder(parent_file_id=test_folder_id, name=subfolder_name)
        CREATED_FOLDER_IDS.append(subfolder_id)
        print(f"✅ Created subfolder: {subfolder_name} (ID: {subfolder_id})")

        # Step 3: Upload files to test folder
        print("\n[3/8] Uploading test files to test folder...")
        uploaded_file_ids = []
        for i in range(3):
            test_file = Path(f"test_file_{i}.txt")
            test_file.write_text(f"Test file {i} content\n")
            file_id = await client.upload.upload_file(file_path=f"test_file_{i}.txt", parent_file_id=test_folder_id)
            CREATED_FILE_IDS.append(file_id)
            uploaded_file_ids.append(file_id)
            print(f"✅ Uploaded: test_file_{i}.txt (ID: {file_id})")
            test_file.unlink()

        # Step 4: List files in test folder
        print("\n[4/8] Listing files in test folder...")
        files = await client.file.list_files(parent_file_id=test_folder_id)
        print(f"✅ Found {len(files.file_list)} items in test folder:")
        for f in files.file_list:
            type_str = "Folder" if f.is_folder else "File"
            size_str = f"({f.size / (1024 * 1024):.2f} MB)" if f.is_file else ""
            print(f"   - [{type_str}] {f.filename} {size_str}")

        # Step 5: Move first file to subfolder
        print("\n[5/8] Moving first file to subfolder...")
        first_file_id = uploaded_file_ids[0]
        await client.file.move_file(first_file_id, subfolder_id)
        print("✅ Moved test_file_0.txt to subfolder")

        # Step 6: Verify move
        print("\n[6/8] Verifying move operation...")
        subfolder_files = await client.file.list_files(parent_file_id=subfolder_id)
        print(f"✅ Subfolder now has {len(subfolder_files.file_list)} file(s):")
        for f in subfolder_files.file_list:
            print(f"   - {f.filename}")

        # Step 7: Rename second file
        print("\n[7/8] Renaming second file...")
        second_file_id = uploaded_file_ids[1]
        new_name = "renamed_file.txt"
        await client.file.rename_file(second_file_id, new_name)
        print(f"✅ Renamed test_file_1.txt to {new_name}")

        # Step 8: Copy third file to subfolder (optional - API may not be available)
        print("\n[8/8] Copying third file to subfolder...")
        third_file_id = uploaded_file_ids[2]
        try:
            copied_file_id = await client.file.copy_file(third_file_id, subfolder_id)
            CREATED_FILE_IDS.append(copied_file_id)
            print(f"✅ Copied test_file_2.txt to subfolder (new file ID: {copied_file_id})")
        except Exception as e:
            print(f"⚠️  Copy file API not available: {e}")
            print("   (This API may require special permissions)")

        # Final verification
        print("\n[Final] Verifying final state...")
        final_test_folder = await client.file.list_files(parent_file_id=test_folder_id)
        final_subfolder = await client.file.list_files(parent_file_id=subfolder_id)
        print(f"✅ Test folder has {len(final_test_folder.file_list)} items:")
        for f in final_test_folder.file_list:
            type_str = "Folder" if f.is_folder else "File"
            print(f"   - [{type_str}] {f.filename}")
        print(f"✅ Subfolder has {len(final_subfolder.file_list)} items:")
        for f in final_subfolder.file_list:
            print(f"   - {f.filename}")

        print("\n" + "=" * 70)
        print("File Management Workflow Completed Successfully!")
        print("=" * 70)


async def workflow_offline_download():
    """Complete offline download workflow: create task → monitor progress."""
    print("\n" + "=" * 70)
    print("Offline Download Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        # Step 1: Create offline download task
        print("\n[1/2] Creating offline download task...")
        print("⚠️  Note: You need to provide a valid download URL")
        print("Example: magnet link, HTTP/HTTPS URL, etc.")

        # Example URL - replace with actual URL
        download_url = "https://example.com/sample.zip"
        print(f"URL: {download_url}")

        try:
            task_id = await client.offline.create_download_task(
                url=download_url,
                file_name="sample_download.zip",
            )
            print(f"✅ Created task (ID: {task_id})")

            # Step 2: Monitor progress
            print("\n[2/2] Monitoring download progress...")
            for _ in range(5):
                await asyncio.sleep(2)
                task_info = await client.offline.get_download_progress(task_id)

                if task_info.is_success:
                    print("✅ Download completed!")
                    if task_info.file_id:
                        print(f"   File ID: {task_info.file_id}")
                        CREATED_FILE_IDS.append(task_info.file_id)
                    break
                elif task_info.is_in_progress:
                    print(f"⏳ Progress: {task_info.progress}%")
                elif task_info.is_failed:
                    print(f"❌ Download failed: {task_info.fail_reason}")
                    break
                else:
                    print(f"⏳ Status: {task_info.status}")
        except Exception as e:
            print(f"❌ Failed to create task: {e}")
            print("This is expected if the URL is invalid")

        print("\n" + "=" * 70)
        print("Offline Download Workflow Completed!")
        print("=" * 70)


async def workflow_image_hosting():
    """Complete image hosting workflow: upload image → get URL → copy cloud image."""
    print("\n" + "=" * 70)
    print("Image Hosting Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        # Step 1: Create a test image
        print("\n[1/3] Creating test image...")
        test_image = Path("test_image.png")
        # Create a minimal valid PNG file (1x1 transparent pixel)
        test_image.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        print("✅ Created test image")

        # Step 2: Upload to image hosting
        print("\n[2/3] Uploading to image hosting...")
        try:
            image_info = await client.image.upload_image(file_path="test_image.png")
            CREATED_FILE_IDS.append(image_info.file_id)
            print("✅ Uploaded image:")
            print(f"   File ID: {image_info.file_id}")
            print(f"   Direct URL: {image_info.direct_url}")
            print(f"   Size: {image_info.size_mb:.4f} MB")
        except Exception as e:
            print(f"⚠️  Image hosting API not available: {e}")
            print("   (This feature may require special account permissions)")
        finally:
            test_image.unlink()

        # Step 3: Try to copy an existing cloud image (if any)
        print("\n[3/3] Listing cloud files to copy to image hosting...")
        files = await client.file.list_files(parent_file_id=0, limit=10)

        image_found = False
        for file_info in files.file_list:
            image_extensions = [".png", ".jpg", ".jpeg", ".gif"]
            is_image = not file_info.is_folder and any(
                file_info.filename.lower().endswith(ext) for ext in image_extensions
            )
            if is_image:
                print(f"Found image: {file_info.filename}")
                try:
                    direct_url = await client.image.copy_cloud_image(file_info.file_id)
                    print("✅ Copied to image hosting:")
                    print(f"   Direct URL: {direct_url}")
                    image_found = True
                    break
                except Exception as e:
                    print(f"⚠️  Failed to copy image: {e}")

        if not image_found:
            print("ℹ️  No suitable image files found in cloud storage")

        print("\n" + "=" * 70)
        print("Image Hosting Workflow Completed!")
        print("=" * 70)


async def workflow_trash():
    """Complete trash workflow: delete file → list trash → restore → permanent delete."""
    print("\n" + "=" * 70)
    print("Trash Workflow Test")
    print("=" * 70)

    async with Pan123Client() as client:
        # Step 1: Create and upload a test file
        print("\n[1/6] Creating test file for trash workflow...")
        test_file = Path("trash_test.txt")
        test_file.write_text(f"Trash test file created at {datetime.now()}\n")
        file_id = await client.upload.upload_file(file_path="trash_test.txt", parent_file_id=0)
        print(f"✅ Uploaded file (ID: {file_id})")
        test_file.unlink()

        # Step 2: Delete file (move to trash)
        print("\n[2/6] Deleting file (moving to trash)...")
        await client.file.delete_file(file_id)
        print("✅ Moved file to trash")

        # Step 3: List trash
        print("\n[3/6] Listing trash contents...")
        trash_items = await client.trash.list_trash(limit=10)
        print(f"✅ Found {len(trash_items.file_list)} items in trash:")
        for item in trash_items.file_list[:5]:
            print(f"   - {item.filename}")

        # Step 4: Restore file (optional - API may not be available)
        print("\n[4/6] Restoring file from trash...")
        try:
            await client.trash.restore_file(file_id)
            print("✅ Restored file from trash")

            # Step 5: Delete again
            print("\n[5/6] Deleting file again...")
            await client.file.delete_file(file_id)
            print("✅ Moved file to trash again")
        except Exception as e:
            print(f"⚠️  Restore file API not available: {e}")
            print("   (This API may require special permissions)")
            print("   Skipping re-delete step")

        # Step 6: Permanently delete (optional - API may not be available)
        print("\n[6/6] Permanently deleting file...")
        try:
            await client.trash.delete_permanently(file_id)
            print("✅ Permanently deleted file")
        except Exception as e:
            print(f"⚠️  Permanent delete API not available: {e}")
            print("   (This API may require special permissions)")
            print("   File remains in trash")

        print("\n" + "=" * 70)
        print("Trash Workflow Completed Successfully!")
        print("=" * 70)


async def cleanup_all():
    """Cleanup all created resources."""
    print("\n" + "=" * 70)
    print("Cleanup - Deleting All Test Data")
    print("=" * 70)

    async with Pan123Client() as client:
        # Delete files
        if CREATED_FILE_IDS:
            print(f"\nDeleting {len(CREATED_FILE_IDS)} files...")
            for file_id in CREATED_FILE_IDS:
                try:
                    await client.file.delete_file(file_id)
                    print(f"✅ Deleted file (ID: {file_id})")
                except Exception as e:
                    print(f"❌ Failed to delete file {file_id}: {e}")

        # Delete folders
        if CREATED_FOLDER_IDS:
            print(f"\nDeleting {len(CREATED_FOLDER_IDS)} folders...")
            for folder_id in CREATED_FOLDER_IDS:
                try:
                    await client.file.delete_file(folder_id)
                    print(f"✅ Deleted folder (ID: {folder_id})")
                except Exception as e:
                    print(f"❌ Failed to delete folder {folder_id}: {e}")

        print("\nℹ️  Note:")
        print("   - Deleted items are in trash")
        print("   - trash.delete_permanently() API may not be available (requires special permissions)")
        print("   - You can manually empty trash from 123Pan web interface")
        print("   - Share links will expire automatically based on their settings")
        print("   - Offline tasks complete automatically")

        print("\n" + "=" * 70)
        print("Cleanup Completed!")
        print("=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("⚠️  WARNING: COMPLETE WORKFLOW TESTS - WILL MODIFY YOUR 123PAN DATA!")
    print("=" * 70)
    print()
    print("All workflows are commented out by default for safety.")
    print("Uncomment only the ones you want to test.")
    print()
    print("-" * 70)
    print()

    # ⚠️  UNCOMMENT ONLY THE WORKFLOWS YOU WANT TO TEST ⚠️

    # Direct link workflow (recommended to test first)
    # asyncio.run(workflow_direct_link())

    # Share workflow
    # asyncio.run(workflow_share())

    # File and folder management
    # asyncio.run(workflow_folder_and_files())

    # Offline download (requires valid URL)
    # asyncio.run(workflow_offline_download())

    # Image hosting
    # asyncio.run(workflow_image_hosting())

    # Trash operations
    # asyncio.run(workflow_trash())

    # Cleanup (run this after testing)
    # asyncio.run(cleanup_all())

    print("No workflows executed. Uncomment the workflows you want to test.")
