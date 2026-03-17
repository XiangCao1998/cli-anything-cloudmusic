# 开发日志：cli-anything-cloudmusic

## 项目简介

这是一个 **CLI-anything** 网易云音乐控制插件，允许 AI Agents 通过命令行控制 Windows 上的网易云音乐播放器。

**项目地址**: https://github.com/XiangCao1998/cli-anything-cloudmusic

---

## 开发历程

### 第一阶段：修复基础bug
- **问题**: WSL 环境下，CMD 不支持 UNC 路径 `\\wsl.localhost\Ubuntu\...`，导致 `tasklist` 调用失败，进程检测误报"已经运行"
- **修复**: 执行子进程前先切换工作目录到 `C:\`，执行完再切回来
- **提交**: `fix: WSL UNC path detection bug`

### 第二阶段：增强自动发现
为了让 AI Agents 能够快速适配不同安装路径，添加了多级自动发现机制：

1. **自定义配置文件** - `~/.config/cli-anything-cloudmusic/path.txt` 持久保存
2. **Windows 注册表搜索** - 从卸载信息找安装路径
3. **where.exe 搜索** - 系统PATH搜索
4. **默认路径** - C:, D:, E:, F: 常见位置
5. **全盘搜索** - 遍历常见驱动器的 Program Files

新增命令：
- `detect` - 手动触发自动发现
- `config <path>` - 保存自定义路径

### 第三阶段：新增功能
在基础功能之外，新增实用功能：

1. **`volume set <0-100>`** - 设置音量到指定百分比
   - 实现方式：静音（归零）→ 步进 N 次到目标
   - 每个音量按键大约增加 4%，所以步进 = 百分比 // 4
   - 已知限制：无法读取当前音量，所以总是从头开始，会切换静音状态，文档已说明

2. **`like`** - 收藏当前歌曲
   - 实现方式：发送 `Ctrl+S` 快捷键，这是网易云音乐默认的收藏快捷键

### 第四阶段：代码审查修复
通过 code-review 发现并修复了以下问题：

| 问题 | 严重度 | 修复方案 |
|------|--------|----------|
| `find_window()` 返回假 handle `1` | HIGH | 改为真实枚举窗口，返回实际 HWND 或 `None` |
| `Volume.set()` 无法处理 1-3% | LOW | 保证最少 1 步，避免结果为 0 |
| `save_custom_path()` 不验证路径 | MEDIUM | 添加路径存在性验证才保存 |
| `import time` 在函数内部 | LOW | 移到文件顶部 |
| `play/pause` 实际都是 toggle | MEDIUM | 添加文档说明已知限制 |
| 残留搞笑注释 | LOW | 删除 |
| `_send_vk` 定义了 `KEYEVENTF_SCANCODE` 没使用 | MEDIUM | 不修改，因为发送 VK 码不需要这个，本来就是正确的 |

### 第五阶段：文档完善
- README 更新所有新命令
- SKILL.md 给 AI Agents 添加了快速开始步骤
- 更新表格包含所有命令

---

## 经验总结

### 1. WSL + Windows Python 开发要点
- 当前工作目录是 UNC 格式时，CMD 无法执行命令
- 解决方案：执行前 `os.chdir("C:")`，执行完切回去
- Windows Python 在 WSL 中可以正常调用 Windows API，一切工作正常

### 2. AI Agent 友好设计要点
- 所有命令支持 `--json` 输出，放在子命令前面
- JSON 输出统一格式：`{"success": bool, ...data...}`
- AI 第一步必须调用 `detect`，找不到提示用户配置
- 清晰错误信息告诉用户下一步怎么做

### 3. 自动发现设计
- 多级回退比单一方法可靠：自定义 > 注册表 > where > 默认 > 搜索
- 支持 Windows 路径 和 WSL 路径互相转换
- 自定义路径持久化保存，不用每次找

### 4. 局限性（无法解决，文档说明）
- 无法获取当前播放状态（播放/暂停），所以 `play/pause` 都是 toggle，文档说明
- 无法获取当前音量，所以 `volume set` 总是从头开始，文档说明
- 依靠窗口标题提取歌曲信息，某些版本 CloudMusic 不显示就无法获取，这是 limitation 不是 bug

### 5. GitHub 工作流程
- 新功能在 feature 分支开发
- 创建 PR → code-review → 修复 → 合并到 main
- 本次因为网络问题直接在 main 完成，但流程应该是：feature → PR → review → merge

---

## 项目结构

```
cli-anything-cloudmusic/
├── cli_anything/
│   └── cloudmusic/
│       ├── cloudmusic_cli.py          # CLI 入口
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   ├── playback.py          # 播放控制
│       │   ├── volume.py            # 音量控制
│       │   └── track.py             # 曲目信息获取
│       ├── utils/
│       │   ├── cloudmusic_backend.py # Windows 底层 API
│       │   ├── window_detector.py    # 窗口标题解析
│       │   └── __init__.py
│       └── skills/
│           └── SKILL.md              # AI Skill 文档
├── README.md                       # 主文档
├── setup.py                        # Python 打包
└── .gitignore
```

---

## 技术要点

### Windows API SendInput
```python
# 发送组合键（比如 Ctrl+S）
# 需要按顺序按下：按下 Ctrl → 按下 S → 松开 S → 松开 Ctrl
# 不能一次全发，要按顺序
```

### 注册表查询找安装路径
```
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall /s /f CloudMusic
```
从输出中解析 `DisplayIcon` 或 `InstallLocation`

### 音量百分比设置
- Windows 每个音量按键增减大约 4%
- 所以 `steps = percentage // 4`
- 1-3% 保证最少 1 步，不会变成 0

---

## 未来改进方向

1. **检测播放状态** - 可以通过像素识别播放按钮，但需要更多依赖，复杂度高
2. **读取当前音量** - 可以通过 Windows API 读取扬声器音量，需要更多 COM 接口编程
3 **支持播放列表/搜索** - 需要逆向网易云音乐 API，超出本项目范围
4. **单元测试** - 需要 Windows 环境运行，GitHub CI 不好做

本项目设计哲学：**简约可靠**，只做能通过 Windows API 简单实现的功能，不搞复杂逆向工程。

---

## 最终功能清单

| 命令 | 功能 |
|------|------|
| `detect` | 自动检测安装 |
| `config <path>` | 保存自定义路径 |
| `launch` | 启动应用 |
| `quit` | 退出应用 |
| `show` / `hide` | 显示/最小化 |
| `play` | 开始/继续播放（实际 toggle）|
| `pause` | 暂停播放（实际 toggle）|
| `toggle` | 切换播放暂停 |
| `next` | 下一曲 |
| `previous` | 上一曲 |
| `like` | 切换收藏状态 |
| `volume up [N]` | 增加音量 |
| `volume down [N]` | 减小音量 |
| `volume set <P>` | 设置音量百分比 |
| `mute` | 切换静音 |
| `current` | 当前曲目信息 |
| `status` | 播放状态 |

---

## 安装

```bash
git clone https://github.com/XiangCao1998/cli-anything-cloudmusic.git
cd cli-anything-cloudmusic
python -m pip install -e .
```

**对于 WSL:**
```bash
# 必须使用 Windows Python
export PATH="$PATH:/mnt/c/Users/YOUR_NAME/AppData/Local/Programs/Python/Python312/Scripts"
cli-anything-cloudmusic --json detect
```

---

*最后更新: 2026-03-18*
