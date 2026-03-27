# Telegram Pet

A cross-platform desktop pet that connects to your Telegram bot. It relays messages, displays replies as speech bubbles, and lives on your desktop as a cute companion.

[中文说明](#中文说明)

## Features

- Transparent, always-on-top, draggable desktop pet with breathing animation
- Double-click to open chat input, send messages to your Telegram bot
- Bot replies appear as floating speech bubbles
- System tray integration (show/hide, quick send, quit)
- 4 pet states: idle, thinking, talking, happy
- Cross-platform: Windows & macOS

## Architecture

```
Local Machine                Telegram Cloud              Remote Server
┌──────────────┐            ┌──────────┐            ┌──────────────┐
│  Desktop Pet │ ─message─→ │ Telegram │ ─forward─→ │ Your Bot     │
│  (Telethon)  │ ←reply──── │  Server  │ ←reply──── │ (Claude etc) │
└──────────────┘            └──────────┘            └──────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- A Telegram account
- A Telegram bot (the one you want to talk to)
- API credentials from [my.telegram.org/apps](https://my.telegram.org/apps)

### 2. Install

```bash
git clone https://github.com/zzmzz/telegram-pet.git
cd telegram-pet
pip install -r requirements.txt
```

### 3. Configure

```bash
cp config.example.toml config.toml
```

Edit `config.toml`:

```toml
[telegram]
api_id = 12345                  # from my.telegram.org
api_hash = "your_api_hash"      # from my.telegram.org
phone = "+86xxxxxxxxxxx"        # your phone number
bot_username = "your_bot"       # bot username without @

[pet]
size = 120                      # pet window size
bubble_max_width = 300          # max bubble width
bubble_timeout = 15             # bubble auto-dismiss (seconds)
```

### 4. Run

```bash
python main.py
```

First run will ask for a Telegram verification code in the terminal.

### 5. Usage

| Action | Effect |
|--------|--------|
| Double-click pet | Open message input |
| Right-click pet | Context menu |
| Ctrl+Enter | Send message |
| Drag pet | Move it around |
| System tray | Show/hide, send, quit |

## Pre-built Binaries

Download from [Releases](https://github.com/zzmzz/telegram-pet/releases). Place `config.toml` in the same directory as the executable before running.

## Build from Source

```bash
pip install pyinstaller
python build.py
```

Output: `dist/TelegramPet.exe` (Windows) or `dist/TelegramPet` (macOS).

---

## 中文说明

一个跨平台桌面宠物，连接你的 Telegram Bot，帮你传话并以气泡形式显示回复。

### 功能

- 透明置顶、可拖拽的桌面宠物，带呼吸动画
- 双击宠物打开输入框，向你的 Telegram Bot 发消息
- Bot 回复以气泡形式弹出
- 系统托盘支持（显示/隐藏、发消息、退出）
- 4 种状态：待机、思考中、说话中、开心
- 支持 Windows 和 macOS

### 快速开始

#### 1. 环境要求

- Python 3.10+
- Telegram 账号
- 一个 Telegram Bot（你要对话的目标）
- 从 [my.telegram.org/apps](https://my.telegram.org/apps) 获取 API 凭据

#### 2. 安装

```bash
git clone https://github.com/zzmzz/telegram-pet.git
cd telegram-pet
pip install -r requirements.txt
```

#### 3. 配置

```bash
cp config.example.toml config.toml
```

编辑 `config.toml`：

```toml
[telegram]
api_id = 12345                  # 从 my.telegram.org 获取
api_hash = "your_api_hash"      # 从 my.telegram.org 获取
phone = "+86xxxxxxxxxxx"        # 你的手机号
bot_username = "your_bot"       # Bot 用户名（不带 @）

[pet]
size = 120                      # 宠物窗口大小
bubble_max_width = 300          # 气泡最大宽度
bubble_timeout = 15             # 气泡自动消失时间（秒）
```

#### 4. 运行

```bash
python main.py
```

首次运行会在终端要求输入 Telegram 验证码，之后会保存 session。

#### 5. 操作方式

| 操作 | 效果 |
|------|------|
| 双击宠物 | 打开输入框 |
| 右键宠物 | 弹出菜单 |
| Ctrl+Enter | 发送消息 |
| 拖拽宠物 | 移动位置 |
| 系统托盘 | 显示/隐藏、发消息、退出 |

#### 6. 下载可执行文件

从 [Releases](https://github.com/zzmzz/telegram-pet/releases) 下载。运行前在同目录下放一份 `config.toml`。

## License

MIT
