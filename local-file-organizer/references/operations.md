# 操作说明

依赖：本机 Windows、Python 3.11 或更新版本；执行脚本只使用标准库。命令示例均为 PowerShell。脚本自身输出 UTF-8，建议调用时也使用 `python -X utf8`。

## 运行位置与配置

默认读取同目录的 `locations.json`。`source_roots` 是允许整理的精确入口；每个批次选择其中一个。`destination_roots` 限定目标范围；目标父目录必须已经存在。`state_root` 保存清单和日志，应与源和归档目录分离。

当用户明确指定其他源目录时，可在 state_root 为该次任务生成独立配置，并在源目录检查后使用 `--config`；不要静默扩大默认配置到整个 D 盘。配置中的源、目标根不能重叠。`--config` 必须放在子命令之前。

```powershell
$organizer = 'C:\Users\yongs\.codex\skills\local-file-organizer\scripts\organize.py'
$batch = Join-Path 'C:\Users\yongs\.codex\file-organizer\runs' ((Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $batch -ErrorAction Stop | Out-Null
python -X utf8 $organizer scan --source 'D:\01 Downloads' --out (Join-Path $batch 'inventory.json')
```

所有输入清单、计划、日志和输出必须位于 state_root，且父目录已存在。输出文件使用独占创建，已存在时拒绝覆盖。任务状态文件可以由代理生成，但不能替换或修改用户待整理文件。

## 清单与预览

`scan` 只检查顶层元数据；`eligible_for_review` 仅表示未被基础检查排除，不代表分类确定、没有引用或可以直接移动。它不是完整盘点子目录内容，也不自动选择归档位置。

代理按实际证据写 `routes.json`，完整目标包含最终文件名。结构如下（示例路径需要替换为真实已核对路径）：

```json
{
  "source_root": "D:\\01 Downloads",
  "moves": [
    {
      "source": "D:\\01 Downloads\\示例文件.pdf",
      "target": "D:\\03_Resources\\已核实的现有目录\\示例文件.pdf",
      "reason": "具体内容、项目归属或既有同类存放惯例"
    }
  ],
  "deferred": [
    {
      "source": "D:\\01 Downloads\\待判断文件.zip",
      "reason": "缺少项目归属证据，暂留原位"
    }
  ]
}
```

```powershell
python -X utf8 $organizer prepare --routes (Join-Path $batch 'routes.json') --out (Join-Path $batch 'plan.json')
```

`prepare` 不移动文件。它检查范围、同盘、目标无冲突、路径不重叠、无链接或重解析点，以及文件是否稳定；为明确选中的文件计算完整 SHA-256、文件身份和修改时间。目录会递归检查全部子项并作为整体生成指纹；内部有临时、隐藏/系统或近期变化文件时整项拒绝。

大型视频或大目录的完整校验可能较慢；先用少量候选校准，不必为尚未决定归属的条目提前读取全量内容。不能以降低校验或随意关闭排除项来消除报错。

`plan.json` 的 `status: ready` 表示技术检查通过，不表示用户已经确认归属或所有下载文件均已分类。展示完整源→目标与理由，明确区分已准备、候选和未逐项研究的条目。只展示文件大小或数量时注明顶层计数范围。

## 执行与核验

用户授权覆盖清单后执行：

```powershell
python -X utf8 $organizer apply --plan (Join-Path $batch 'plan.json') --journal (Join-Path $batch 'journal.jsonl')
```

全批先检查，再在每次移动前检查。移动采用 Windows 同卷、不覆盖的重命名操作，不做跨盘复制、不合并目录。先持久化 `intent`，移动并核验后写 `done`；完整完成有 `complete`。命令返回成功和核验数量；异常保留实际结果并返回非零状态。

不要手改生成的计划。若源发生变化、目标冲突或范围配置变化，回到原清单重新核对，生成新计划。已存在日志会阻止重跑同一日志文件，但脚本没有跨批次业务去重数据库；不要用换日志文件名的方法绕过失败。先查实际路径和日志，必要时撤回已执行部分。

文件指纹能发现内容、身份和时间变化，不能证明外部快捷方式或工程引用仍有效，也不保证文件在其他程序中未打开；这类关系需要分类时核对。文件名修改也可能影响外部引用，因此默认不改名。

## 撤销与中断

默认仅预览撤回动作：

```powershell
python -X utf8 $organizer undo --journal (Join-Path $batch 'journal.jsonl')
```

用户要求撤销且预检通过后：

```powershell
python -X utf8 $organizer undo --journal (Join-Path $batch 'journal.jsonl') --execute
```

逆序检查归档位置的内容、身份、时间是否仍与计划相符，原路径是否可用；有任何冲突时整批预检停止。执行中的新错误仍可能造成部分撤回，应据日志继续判断。已经撤回的操作不重复移动。

日志保留完整计划，使用逐行校验链与持久化写入。它可识别写入 intent 后、尚未写 done 的中断，并依据两端存在状态与指纹判断是否已移动；撤回过程也有对应恢复记录。日志损坏、缺少结尾或原路径/内容变化时拒绝自动恢复，保留现场，不强行重建日志或覆盖文件。

每个 state_root 使用操作系统文件锁，进程结束会释放锁；`.organizer.lock` 文件本身可以长期存在，不需要删除。不要并行运行多个修改同一批文件的工具。
