# 独立拓展资产库

本仓库维护资产数据，NBTCreator 仓库维护生成引擎、应用和内置发行快照。新资产写入本仓库，不把配方硬编码回引擎。当前创作目标包含基于现实构造的华丽窗框和丰富纹样，实际查看预览后描述结果，不能由资产资料声称已验收。

- `assets/recipes/<kind>/<id>.json`：参数化配方，`kind` 为引擎构件类型。
- `assets/components/<category>/<id>.json`：已编译构件，使用 NBTCreator 构件格式，1～64 格/轴、最多65536个方块。
- `library.json`：唯一资产索引；`registry.json`：远端库目录，钉住 library.json 的 SHA256。
- `docs/PROTOCOL.md`：协议及错误处理约定。每项清单必须含 id、name、type、path、bytes、sha256，可含 category、tags、status、requires。
- 配方只允许 `{schema_version:1,kind:"nbtcreator.parametric-recipe",arguments:{...},controls?:{style:bool,spacing:bool}}`。参数须通过对应应用版本的 parametric_compile Schema。代码、压缩包、远端引用与运行脚本不能作为资产。
- 新文件先录入 library.json，再从本仓库执行 `mise run index`、`mise run check`。在相邻 NBTCreator 根目录运行 `mise run assets:sync -- --source ../NBTCreator-AssetLibrary` 和 `mise run assets:test`；同步只更新发行快照，不依赖相邻路径运行应用。
- 发布后同版本内容不可改变，变更须提高 library.json 的三段数字版本。发布的清单和资产须位于同源目录下，不能使用 ../、跨源资产或查询凭据。HTTPS 静态服务可直接托管整个仓库。
- 不修改 main/master/release/*；使用 feat/、fix/、docs/ 等任务分支。未经用户要求不提交或推送；此批资产远端发布由协调聊天统一处理，避免互相覆盖。
- 来源与许可保留于 README/NOTICE；无明确许可的第三方资产不冒充自有内容。保留真实图片预览与人工定稿导出流程。
