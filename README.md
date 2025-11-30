# aio123pan

<div align="center">

[![PyPI version](https://badge.fury.io/py/aio123pan.svg)](https://badge.fury.io/py/aio123pan)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/aio123pan/)
[![License](https://img.shields.io/github/license/Cloxl/aio123pan.svg)](https://github.com/Cloxl/aio123pan/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/aio123pan)](https://pepy.tech/project/aio123pan)

123云盘异步API客户端，支持文件管理、上传下载等完整功能。

</div>

## 系统要求

- Python 3.10+

## 安装

```bash
pip install aio123pan
```

## 快速开始

### 基本用法

```python
import asyncio
from aio123pan import Pan123Client

async def main():
    async with Pan123Client(
        client_id="your_client_id",
        client_secret="your_client_secret"
    ) as client:
        # 获取用户信息
        user_info = await client.user.get_info()
        print(f"用户: {user_info.nickname}")
        print(f"空间使用: {user_info.space_used / (1024**3):.2f}GB / {user_info.space_capacity / (1024**3):.2f}GB")

        # 列出根目录文件
        file_list = await client.file.list_files(parent_file_id=0)
        for file in file_list.file_list:
            print(f"{'[文件夹]' if file.is_folder else '[文件]'} {file.filename}")

asyncio.run(main())
```

### 配置方式

支持三种配置方式，优先级：显式参数 > 环境变量 > .env文件

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

### 文件操作

```python
# 上传文件
file_id = await client.upload.upload_file(
    file_path="local_file.txt",
    parent_file_id=0,
    progress_callback=lambda current, total: print(f"上传进度: {current}/{total}")
)

# 创建文件夹
folder_id = await client.folder.create_folder(name="新文件夹", parent_id=0)

# 移动文件
await client.file.move_file(file_id, target_parent_id=folder_id)

# 重命名文件
await client.file.rename_file(file_id, "新文件名.txt")

# 删除文件
await client.file.delete_file(file_id)

# 批量操作（最多100个）
await client.file.delete_file([file_id1, file_id2, file_id3])
```

### Token自动管理

Token会自动缓存到.env文件，无需手动管理：

```python
# 首次使用会获取token并缓存到.env
async with Pan123Client(client_id="xxx", client_secret="xxx") as client:
    # Token自动存储到.env
    # 如果.env文件不存在，会自动创建
    await client.user.get_info()

# 后续使用自动读取缓存的token
async with Pan123Client(client_id="xxx", client_secret="xxx") as client:
    # 自动从.env读取token，过期时自动刷新
    await client.user.get_info()
```

**重要提示：**
- Token会保存到 `.env` 文件中的 `AIO123PAN_CACHED_ACCESS_TOKEN` 和 `AIO123PAN_CACHED_TOKEN_EXPIRY` 字段
- 这些字段由 aio123pan 自动管理，**请勿手动编辑**
- **请勿将这两个键名用于其他用途**，以避免冲突
- 如果不存在 `.env` 文件，首次认证成功后会自动创建

禁用Token持久化：

```python
# 方式1: 通过参数
client = Pan123Client(enable_token_storage=False)

# 方式2: 通过环境变量
# PAN123_ENABLE_TOKEN_STORAGE=false
client = Pan123Client()
```

## 参数说明

### 客户端初始化

- `client_id`: 123云盘应用ID
- `client_secret`: 123云盘应用密钥
- `access_token`: 访问令牌（可选，自动管理）
- `expired_at`: Token过期时间（可选，自动管理）
- `timeout`: 请求超时时间（秒）
- `base_url`: API基础URL（默认：https://open-api.123pan.com）
- `enable_token_storage`: 是否启用token持久化（默认：True）
- `env_file`: .env文件路径（默认：当前目录）

### 环境变量

所有配置项都支持通过环境变量设置，优先级：**显式参数 > 环境变量 > .env文件**

- `PAN123_CLIENT_ID`: 应用ID
- `PAN123_CLIENT_SECRET`: 应用密钥
- `PAN123_TIMEOUT`: 请求超时时间（默认：30.0）
- `PAN123_BASE_URL`: API基础URL
- `PAN123_ENABLE_TOKEN_STORAGE`: 是否启用token持久化（默认：true）

**自动生成字段（请勿手动设置）：**
- `AIO123PAN_CACHED_ACCESS_TOKEN`: 缓存的访问令牌
- `AIO123PAN_CACHED_TOKEN_EXPIRY`: Token过期时间

### 文件限制

- 文件名最大长度：255字符
- 禁止字符：`"\/:*?|><`
- 单文件最大：10GB
- 批量操作最大：100个项目

## API功能

### 认证模块
- 获取访问令牌
- 自动刷新过期token

### 用户模块
- 获取用户信息
- 查看空间使用情况

### 文件模块
- 列出文件/文件夹
- 移动文件
- 重命名文件
- 删除文件（支持批量）
- 复制文件
- 搜索文件

### 文件夹模块
- 创建文件夹

### 上传模块
- 小文件直接上传
- 大文件分片上传
- 上传进度回调
- 秒传支持

### 回收站模块
- 查看回收站文件
- 恢复文件
- 彻底删除

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