---
name: garlic
description: garlic（ARF 检出）—— 用 C 写成的 apk/java 反编译器与 aarch64 ELF 分析器，支持 class/jar/dex/apk/war 反编译与 ELF 控制流/IR/导入导出/字符串/调用图。触发：提到 garlic / garlic-mirror / garlic 反编译 / garlic MCP / MCP-SERVER.md / garlic 的 ELF 分析 或在本仓执行反编译前必加载。不触发：GDA（走 gda_mcp_server_guide.md 与 android-reverse-forge）；jadx/smali 路线（见 feedback_jadx_smali_fallback.md）。
status: draft
---

# garlic — C 实现的 apk/java 反编译器与 ELF 分析器

「The world's fastest apk (android)/java open source decompiler/elf analyzer」—— Android/Java decompiler written in C。

- 归属：`oneSeeker279/garlic`（上游 `neocanable/garlic`，另有 `oneSeeker279/garlic-mirror` 供应链镜像）；检出 `E:/cache/ext/review/garlic`。
- 查身份：`git -C <检出> remote -v` / `rev-parse HEAD`（**以实测为准**）。
- **ARF 中的角色**：Java/DEX 层静态分析工具链的**一级件**（见 Memory `feedback_ida_headless_only.md`：Java/DEX 层 **garlic > GDA > jadx**）。

## 项目定位

- **能力面**：
  - 反编译 `apk` / `dex` / `class` / `jar` / `war`；
  - 分析 `aarch64` ELF：control flow / IR / imports / exports / strings / **function call graph**；
  - 附带 **MCP server**（`MCP-SERVER.md` / `MCP-SERVER.CN.md`）。
- **上游 README 中文版**：`README.CN.md`。

## 架构与目录

| 路径 | 用途 |
|---|---|
| `src/` | C 主体（`.c` 151 件 + `.h` 122 件） |
| `libs/` | 依赖库（含预编译 `.a` / `.so` / `.dylib` / `.dll`） |
| `cmake/` · `toolchains/` | CMake 模块与交叉编译工具链 |
| `build.sh` · `build.zig` · `build.zig.zon` | 两套构建路径（CMake / Zig） |
| `shell/` · `docs/` | 脚本 / 文档 |
| `CMakeLists.txt` | 主构建入口 |

- `.gitignore`（实测）：`build/` `.idea/` `.vscode/` `.zig-cache/` `zig-out/` `zig-pkg/` `cmake-build-debug/` `doc/` `cmake-build-release/` `/*.java`。
  ⇒ **⚠️ `/*.java` 被忽略**：**⛔ 不要在仓根写 `.java` 文件**（静默不入跟踪）。**`doc/` 也被忽略**。

## 关键命令

```bash
# ── 工作目录: E:/cache/ext/review/garlic
# Linux/macOS 路径（需要 cmake >= 3.26）
cmake -B build && cmake --build build
./build/garlic

# Zig 路径
zig build
```

### 🔴 中文路径禁区（ARF 铁律）

> **garlic 的输入与输出路径均禁含中文**（miniz 实现限制）。⇒ **⛔ 不要把待分析 APK 放在含中文的目录下，也不要把 `-o` 指到含中文的目录。**

- **`-o` 是 jar/dex/war 的目录参数；默认写 stdout**。⇒ 直接 `./garlic x.apk` 会把反编译结果打到终端；要落盘必须显式给 `-o`。
- MCP server 用法见 `MCP-SERVER.md`（中文 `MCP-SERVER.CN.md`）。

## 核心约束 / 边界

- **🔴 中文路径双向禁区**：见上。这是本项目最高频的「莫名其妙失败」根因。
- **🔴 `/*.java` 与 `doc/` 被 `.gitignore` 排除**：仓根写 `.java` 会**静默消失**（`git status` 看不见）。
- **🔴 顺位不颠倒**：Java/DEX 层用 garlic 优先；**garlic 实测失败并留下证据后**才降级到 GDA / jadx（Memory 铁律）。
- **⛔ 上游同步纪律**：本仓跟踪上游（含 PR 合入）；改动前先确认是否要回馈上游，避免分叉。
- **⛔ `.gitignore` 不许为「方便」改**（如为了提交某个 `.java`）：属跨仓策略变更，须主线裁定。

## 踩坑

- **中文路径 ⇒ miniz 失败**：症状常是「打开文件失败」「输出为空」而不是清晰报错。**先检查路径**。
- **忘了 `-o`**：结果全进 stdout，落盘为空的假象。
- **`build/` 已 ignore**：找不到产物时确认是不是被忽略而非没编译。
- **`.so`/`.a`/`.dylib`/`.dll` 在 `libs/`**：换平台要确认对应件存在；本机是 Windows，**上游预编译件以 linux/mac 为主** ⇒ 本机可能要自行构建依赖（**未验证**）。
- **本文件由 2026-09-21 批量补建**：**未在本机实跑构建**（Win 平台的 cmake/zig 依赖未验）⇒ `status: draft`。

## 进度指针 / 怎么查

- 能力与构建：`README.md` / `README.CN.md`（§Features / §Build）
- MCP 用法：`MCP-SERVER.md` / `MCP-SERVER.CN.md`
- 实际状态：`git -C <检出> log --oneline -20`
- 顺位与踩坑：Memory `feedback_ida_headless_only.md` · `ida_gda_automation_lessons.md`

## 相关

- Memory：`gda_mcp_server_guide.md` · `ida_gda_automation_lessons.md` · `feedback_ida_headless_only.md`（garlic > GDA > jadx 顺位 + 中文路径禁区 + `-o` 语义）
- 供应链镜像：`oneSeeker279/garlic-mirror`（ARF 静态分析供应链备份，见 `repo-index`）
- 判词/工作台：`android-reverse-forge`
