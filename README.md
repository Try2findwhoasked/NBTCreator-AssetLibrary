# NBTCreator Asset Library

独立维护 Minecraft Java 1.20.1 的模块化建筑配方和构件数据。应用引擎与资产分开发布；安装或更新资产无需执行库中的程序。

在 NBTCreator 的“素材库 → 拓展资产库”填入本地目录、library.json 的 HTTPS 地址，或 registry.json 的 HTTPS 地址。先查看清单，再连接库。配方在“让 Agent 生成资产 → 参数化模块库”中使用；构件可导入当前工作区，再查看和放置。

公开库目录：[registry.json](https://raw.githubusercontent.com/Try2findwhoasked/NBTCreator-AssetLibrary/refs/heads/feat/initial-library/registry.json)。单库入口：[library.json](https://raw.githubusercontent.com/Try2findwhoasked/NBTCreator-AssetLibrary/refs/heads/feat/initial-library/library.json)。这两个地址跟随发布分支，更新需要在应用中显式刷新；固定复现时把 `refs/heads/feat/initial-library` 替换为已验证的提交 SHA。

首次公开候选为 **1.0.0，共121项（76配方、45构件）**，清单 SHA256 为 `b201eb04177c4d4f518090061aeaa288e3d30c012f2988b7c8534a1fc3e6f97e`。使用具备拓展库接入与花式窗框引擎的 NBTCreator 开发版本；旧版本可能尚未实现这些构件参数。

资产按 `assets/recipes/<kind>/` 和 `assets/components/<category>/` 组织。`library.json` 声明资产的稳定编号、分类、大小和 SHA256，`registry.json` 提供可连接的库目录。所有版本以清单哈希锁定，断网仍可使用已缓存内容。

本仓库使用 mise。维护者在本仓库根目录执行：

```powershell
mise run index
mise run check
mise run previews:check
```

资产须先登记 library.json。修改已发布数据时增加库版本；同步应用发行快照，在 NBTCreator 根目录执行：

```powershell
mise run assets:sync -- --source ../NBTCreator-AssetLibrary
mise run assets:test
```

协议、支持范围和异常处理见 [PROTOCOL.md](docs/PROTOCOL.md)，机器可读字段约束见 [schemas/](schemas/)。路径安全、依赖图、总字节数、哈希、引擎兼容性与配方参数仍由应用做语义校验，JSON Schema 不替代实际编译。当前内容从用户的 NBTCreator 项目迁入，许可标识为 `LicenseRef-NBTCreator-Project`；这不授予未声明的开源许可，见 [NOTICE](NOTICE)。模型仍需实际预览，安装后另验通路、承托及游戏内效果。

新一批[华丽建筑与陈设资产集](docs/ORNATE_COLLECTION.md)包含花式窗框、柱式、家具、花器、灯具和原创纹样，附实际预览与复现命令。当前共121项数据；预览不代替用户审批或游戏验收。

本次仓库整理、协议、维护工具与新增资产由 Agent 生成或辅助生成。发布前运行 `mise run previews:portable`，将预览记录的本机源码路径改为相对路径；渲染清单保留转换前的快照和清单哈希，模型、几何、相机与图片字节保持不变。此步骤不代表重新渲染或新增审批。
