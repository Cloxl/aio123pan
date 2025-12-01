# aio123pan

<div align="center">

[![PyPI version](https://badge.fury.io/py/aio123pan.svg)](https://badge.fury.io/py/aio123pan)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/aio123pan/)
[![License](https://img.shields.io/github/license/Cloxl/aio123pan.svg)](https://github.com/Cloxl/aio123pan/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/aio123pan)](https://pepy.tech/project/aio123pan)

123云盘异步API客户端，支持文件管理、上传下载、分享链接、离线下载等完整功能。

</div>

## 系统要求

- Python 3.10+

## 安装

```bash
pip install aio123pan
```

## 快速开始

```python
import asyncio
from aio123pan import Pan123Client

async def main():
    async with Pan123Client(
        client_id="your_client_id",
        client_secret="your_client_secret"
    ) as client:
        # 获取用户信息
        user_info = await client.user.get_user_info()
        print(f"用户: {user_info.nickname}")
        print(f"空间使用: {user_info.space_used / (1024**3):.2f}GB / {user_info.space_permanent / (1024**3):.2f}GB")

        # 列出根目录文件
        file_list = await client.file.list_files(parent_file_id=0)
        for file in file_list.file_list:
            print(f"{'[文件夹]' if file.is_folder else '[文件]'} {file.filename}")

asyncio.run(main())
```

## Token自动缓存

> **重要提示：** Token自动缓存功能默认**关闭**，需要主动启用。

启用Token持久化后，Token会自动缓存到`.env`文件：

```python
# 启用Token自动缓存
async with Pan123Client(
    client_id="xxx",
    client_secret="xxx",
    enable_token_storage=True  # 必须显式设置为True
) as client:
    # Token会自动存储到.env文件
    await client.user.get_user_info()

# 或通过环境变量启用
# PAN123_ENABLE_TOKEN_STORAGE=true
async with Pan123Client() as client:
    # 自动从.env读取token，过期时自动刷新
    await client.user.get_user_info()
```

**关于Token缓存字段：**
- Token保存到 `.env` 文件中的 `AIO123PAN_CACHED_ACCESS_TOKEN` 和 `AIO123PAN_CACHED_TOKEN_EXPIRY` 字段
- 这些字段由 aio123pan 自动管理，**请勿手动编辑**
- **请勿将这两个键名用于其他用途**，以避免冲突
- 如果不存在 `.env` 文件，首次认证成功后会自动创建

## 配置方式

支持三种配置方式，优先级：**显式参数 > 环境变量 > .env文件**

```python
# 方式1: 显式传参
client = Pan123Client(client_id="xxx", client_secret="xxx")

# 方式2: 环境变量
# export PAN123_CLIENT_ID=xxx
# export PAN123_CLIENT_SECRET=xxx
client = Pan123Client()

# 方式3: .env文件
# PAN123_CLIENT_ID=xxx
# PAN123_CLIENT_SECRET=xxx
client = Pan123Client()
```

## 完整功能列表

<details>
<summary><b>📁 文件管理</b></summary>

```python
# 列出文件/文件夹
file_list = await client.file.list_files(parent_file_id=0, limit=100)

# 获取文件信息
file_info = await client.file.get_file_info(file_id)

# 移动文件
await client.file.move_file(file_id, target_parent_id=folder_id)

# 重命名文件
await client.file.rename_file(file_id, "新文件名.txt")

# 复制文件
new_file_id = await client.file.copy_file(file_id, target_parent_id=folder_id)

# 删除文件（支持批量）
await client.file.delete_file(file_id)
await client.file.delete_file([file_id1, file_id2])

# 搜索文件
search_results = await client.file.search_files(keyword="关键词")
```
</details>

<details>
<summary><b>📂 文件夹操作</b></summary>

```python
# 创建文件夹
folder_id = await client.folder.create_folder(
    parent_file_id=0,
    name="新文件夹"
)
```
</details>

<details>
<summary><b>⬆️ 文件上传</b></summary>

```python
# 小文件直接上传
file_id = await client.upload.upload_file(
    file_path="local_file.txt",
    parent_file_id=0
)

# 大文件分片上传（自动处理）
file_id = await client.upload.upload_file(
    file_path="large_file.zip",
    parent_file_id=0,
    progress_callback=lambda current, total: print(f"{current}/{total}")
)

# 秒传支持（文件已存在时自动跳过上传）
```
</details>

<details>
<summary><b>🗑️ 回收站管理</b></summary>

```python
# 查看回收站
trash_list = await client.trash.list_trash(limit=100)

# 恢复文件
await client.trash.restore_file(file_id)

# 彻底删除
await client.trash.delete_permanently(file_id)

# 清空回收站
await client.trash.empty_trash()
```
</details>

<details>
<summary><b>🔗 分享链接</b></summary>

```python
# 创建分享链接
share_info = await client.share.create_share(
    file_ids=[file_id],
    share_name="分享名称",
    expire_days=7,  # 0=永久, 1/7/30天
    share_pwd="1234"  # 可选密码
)
print(f"分享链接: {share_info.share_url}")

# 列出所有分享
shares = await client.share.list_shares(limit=100)

# 更新分享（需特殊权限）
await client.share.update_share(
    share_id=share_info.share_id,
    share_name="新名称"
)

# 删除分享
await client.share.delete_share(share_id)
```
</details>

<details>
<summary><b>🔗 直链管理</b></summary>

```python
# 启用直链文件夹
await client.direct_link.enable_direct_link(folder_id)

# 获取直链URL
url = await client.direct_link.get_direct_link_url(file_id)

# 禁用直链
await client.direct_link.disable_direct_link(folder_id)

# 获取IP黑名单配置
blacklist = await client.direct_link.get_ip_blacklist()

# 设置IP黑名单
await client.direct_link.set_ip_blacklist(
    ip_list=["192.168.1.1", "10.0.0.1"],
    is_enabled=True
)
```
</details>

<details>
<summary><b>📥 离线下载</b></summary>

```python
# 创建离线下载任务
task_id = await client.offline.create_download_task(
    url="https://example.com/file.zip",
    file_name="file.zip",
    parent_file_id=0
)

# 查询下载进度
task_info = await client.offline.get_download_progress(task_id)
print(f"进度: {task_info.progress}%")
print(f"状态: {'下载中' if task_info.is_in_progress else '已完成'}")

# 获取离线任务日志（需特殊权限）
logs = await client.offline.get_offline_logs(limit=10)
```
</details>

<details>
<summary><b>🖼️ 图床功能</b></summary>

```python
# 上传图片到图床
direct_url = await client.image.upload_image(image_path="photo.jpg")
print(f"图片直链: {direct_url}")

# 从云盘文件复制到图床
direct_url = await client.image.copy_cloud_image(file_id)
```
</details>

<details>
<summary><b>🎬 视频转码</b></summary>

```python
# 创建转码任务
task_id = await client.video.create_transcode_task(video_file_id)

# 查询转码状态
task_info = await client.video.get_transcode_status(task_id)
print(f"进度: {task_info.progress}%")
```
</details>

<details>
<summary><b>👤 用户信息</b></summary>

```python
# 获取用户信息
user_info = await client.user.get_user_info()
print(f"用户: {user_info.nickname}")
print(f"UID: {user_info.user_id}")
print(f"已用空间: {user_info.space_used_gb:.2f}GB")
print(f"永久空间: {user_info.space_permanent_gb:.2f}GB")
```
</details>

## 参数说明

<details>
<summary><b>客户端初始化参数</b></summary>

- `client_id`: 123云盘应用ID
- `client_secret`: 123云盘应用密钥
- `access_token`: 访问令牌（可选，自动管理）
- `expired_at`: Token过期时间（可选，自动管理）
- `timeout`: 请求超时时间（秒，默认30.0）
- `base_url`: API基础URL（默认：https://open-api.123pan.com）
- `enable_token_storage`: 是否启用token持久化（默认：False）
- `env_file`: .env文件路径（默认：当前目录）
</details>

<details>
<summary><b>环境变量</b></summary>

所有配置项都支持通过环境变量设置：

- `PAN123_CLIENT_ID`: 应用ID
- `PAN123_CLIENT_SECRET`: 应用密钥
- `PAN123_TIMEOUT`: 请求超时时间（默认：30.0）
- `PAN123_BASE_URL`: API基础URL
- `PAN123_ENABLE_TOKEN_STORAGE`: 是否启用token持久化（默认：false）

**自动生成字段（请勿手动设置）：**
- `AIO123PAN_CACHED_ACCESS_TOKEN`: 缓存的访问令牌
- `AIO123PAN_CACHED_TOKEN_EXPIRY`: Token过期时间
</details>

<details>
<summary><b>文件限制</b></summary>

- 文件名最大长度：255字符
- 禁止字符：`"\\/:*?|><`
- 单文件最大：10GB
- 批量操作最大：100个项目
</details>

## 示例代码

完整的工作流程示例请查看：
- `examples/read_only_examples.py` - 只读操作示例（安全运行）
- `examples/complete_workflow_examples.py` - 完整工作流程示例（包含清理）


## 开发环境

### 环境准备

```bash
# 安装uv包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/Cloxl/aio123pan
cd aio123pan

# 安装依赖
uv sync --dev
```

### 开发流程

```bash
# 运行测试
uv run pytest tests/ -v

# 代码检查
uv run ruff check src/ tests/

# 代码格式化
uv run ruff format src/ tests/

# 查看测试覆盖率
uv run pytest tests/ --cov=aio123pan --cov-report=html

# 构建包
uv build
```

### Git工作流

```bash
# 创建功能分支
git checkout -b feat/your-feature

# 提交代码（遵循conventional commits规范）
git commit -m "feat(client): 添加新功能描述"

# 推送到远程
git push origin feat/your-feature
```

## 相关链接

- [123云盘开放平台](https://www.123pan.com/open/)
- [官方API文档](https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced)

## License

[MIT](LICENSE)