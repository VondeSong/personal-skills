# 输入契约与原图读取

发现实际可用 CAD/连接工具，核对目标文档完整路径后只读提取。不保存、不炸开原图；展开/转换用副本。记录工具、版本、导出方法及外参覆盖。CAD 可导出原生表格，或通过 API/AutoLISP 导出文字、插入点、句柄、空间/块名和网格。MTEXT 同时保留原串与解码文本。旋转、嵌套块、属性、TABLE、外参须另处理，不能只读文字后宣称全覆盖。无法获取原生数据时继续处理可读部分并明确缺口。

原图与实体文件的哈希应在导出时一起记录。extract CLI 会记录本次实体文件哈希并随来源合并保留，但不能证明旧缓存一定由当前原图生成；缺少当时来源记录时标“既有缓存，来源关联待复核”，不可事后计算哈希冒充已证明版本一致。

## 文字实体

兼容已有提取格式：
```json
[{"block":"*Model_Space","0":"TEXT","5":"A12","10":[10,25,0],"1":"Wire ID","text":"Wire ID"}]
```
标准格式：
```json
[{"space":"Model","type":"TEXT","handle":"A12","x":10,"y":25,"raw_text":"Wire ID","text":"Wire ID"}]
```
`text` 必须可靠解码，`handle` 在空间内唯一，展开实例须包含实例路径。坐标统一到表所在空间。无文字的复杂对象不默认为已解析。

## 提取计划

坐标放在每次任务计划，不写进脚本。行和列允许不等间距。bounds 只框数据区，不含表头；预期记录数来自独立数表，不能取脚本输出。最少五列如下，可扩展字段。
```json
{
  "source":{"id":"drawing-A-rev1","path":"D:/project/a.dwg","sha256":"真实SHA256","harness":"FLH","drawing_number":"图号","revision":"版本","project":"项目","length_unit":"mm","size_unit":"mm2","method":"CAD原生文字导出","uncovered":[]},
  "tables":[{
    "id":"wire-01","space":"*Model_Space","bounds":[0,0,100,30],
    "rows_y":[20,13,5],"tolerance":0.5,"expected_records":3,
    "columns":[
      {"field":"wire_id","left":0,"right":20},
      {"field":"from_id","left":20,"right":40},
      {"field":"from_pin","left":40,"right":60},
      {"field":"to_id","left":60,"right":80},
      {"field":"to_pin","left":80,"right":100}
    ]
  }]
}
```
bounds 为 `[left,bottom,right,top]`。表不得重叠。可选列：`color,size,material,length,multicore,option,from_loc,to_loc,from_name,to_name,from_part,to_part,terminal1,terminal2,seal1,seal2`。`length` 永远是原值，只有来源单位确认为 mm 才能直接映射 LengthMm。

## 独立孔位表

不得由导线表反生成校核数据。每条针脚记录真实取自接口表，字段不存在则不填。evidence 指向这些字段的原单元格，或可核对的表行。跨版数据单独做版本差异，不冒充同版通过。
```json
[{
  "source_id":"drawing-A-rev1","harness":"FLH","connector":"BD001","pin":"01","wire_id":"W001",
  "values":{"color":"R","size":"0.35","material":"FLRY-B","option":"ALL","multicore":null,"terminal":"原表值","seal":"-"},
  "evidence":{"source_id":"drawing-A-rev1","table":"pin-BD001","handles":["A21","A22"]}
}]
```

## 新表输出

`export_xlsx.mjs merged.json mapping.json output.xlsx` 创建数据表及原始记录、复核清单、来源页。通过 `RUNTIME_NODE_MODULES` 找到依赖工具返回的模块目录。它不复制复杂模板样式或原工作簿历史数据；严格模板/增量修改使用 spreadsheets 技能。

导出器拒绝超出 Excel 单元格长度、单位未知却映射 LengthMm、以及以单引号紧接等号开头的特殊原文。后者是当前运行库的文字转义限制；保留 JSON，转交能逐字回验的表格流程，不删字符凑成功。会生成配套首屏 `.preview.png`，仍需回读 Excel 并检查其他关键区域。
