// Create a new mapped workbook; preserve original text and evidence separately.
import fs from 'node:fs/promises';
import {constants} from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const [input, mapping, output] = process.argv.slice(2);
if (!input || !mapping || !output || !process.env.RUNTIME_NODE_MODULES) {
  console.error('Usage: export_xlsx.mjs merged.json mapping.json NEW.xlsx; set RUNTIME_NODE_MODULES from load_workspace_dependencies');
  process.exit(1);
}
const read = async p => JSON.parse((await fs.readFile(p, 'utf8')).replace(/^\uFEFF/, ''));
const literal = v => {
  if (v == null || v === '') return null;
  if (!['string','number','boolean'].includes(typeof v)) throw Error('Non-scalar cell');
  if (typeof v === 'string' && v.length > 32767) throw Error('Cell exceeds Excel text limit; keep full evidence in JSON');
  // shortcut: this runtime consumes a leading apostrophe before '='; refuse that rare source value until exact-cell transfer is implemented.
  if (typeof v === 'string' && v.startsWith("'=")) throw Error('Source text beginning apostrophe-equals needs exact-text spreadsheet handling; JSON remains unchanged');
  return typeof v === 'string' && v.startsWith('=') ? "'" + v : v;
};
const col = n => {
  let s = '';
  for (; n; n = Math.floor((n-1)/26)) s = String.fromCharCode(65+(n-1)%26)+s;
  return s;
};

try {
  for (const p of [output, output+'.preview.png']) {
    try { await fs.access(p); throw Error('Refusing to overwrite: '+p); }
    catch (e) { if (e.code !== 'ENOENT') throw e; }
  }
  const data = await read(input), spec = await read(mapping), columns = spec.columns;
  if (data.schema !== 'harness-wire-list/v1' || !data.records?.length || !data.audit) throw Error('Expected nonempty assembled wire list');
  if (!Array.isArray(columns) || !columns.length || columns.some(c => typeof c.header !== 'string' || !c.header || !(c.field === null || typeof c.field === 'string')) || new Set(columns.map(c=>c.header)).size !== columns.length) throw Error('Invalid or repeated mapping headers');
  const sources = new Map(data.sources.map(s=>[s.id,s]));
  const fields = [...new Set(data.records.flatMap(r=>Object.keys(r.values)))];
  const allowed = new Set([...fields, 'record_id', 'source_id', 'harness']);
  for (const c of columns) {
    if (c.field !== null && !allowed.has(c.field)) throw Error('Unknown mapping field: '+c.field);
    if (c.header === 'LengthMm' && c.field !== null && (c.field !== 'length' || data.sources.some(s=>s.length_unit !== 'mm'))) throw Error('LengthMm requires confirmed mm source units');
  }
  const rows = data.records.map(r=>columns.map(c=> {
    if (c.field === null) return null;
    let v = ['record_id','source_id','harness'].includes(c.field) ? r[c.field] : r.values[c.field];
    if (['length','size'].includes(c.field) && typeof v === 'string' && /^\d+(\.\d+)?$/.test(v) && Number.isFinite(Number(v)) && v.replace(/[^0-9]/g,'').length <= 15) v = Number(v);
    if (!sources.has(r.source_id)) throw Error('Missing record source');
    return v ?? null;
  }));
  const require = createRequire(import.meta.url);
  const entry = require.resolve('@oai/artifact-tool', {paths:[process.env.RUNTIME_NODE_MODULES]});
  const {Workbook, SpreadsheetFile} = await import(pathToFileURL(entry).href);
  const wb = Workbook.create();
  function sheet(name, headers, body, tableName) {
    if (body.length+1 > 1048576 || headers.length > 16384) throw Error('Excel dimensions exceeded');
    const s = wb.worksheets.add(name), last = col(headers.length), end = body.length+1;
    const all = s.getRange(`A1:${last}${end}`);
    all.values = [headers,...body].map(row=>row.map(literal));
    all.format.font = {name:'Arial',size:10,color:'#17212B'};
    all.format.rowHeight = 22;
    all.format.verticalAlignment = 'center';
    all.format.columnWidth = 20;
    all.setNumberFormat('@');
    if (body.length) s.tables.add(`A1:${last}${end}`,true,tableName);
    s.getRange(`A1:${last}1`).format = {fill:'#243D59',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:52,horizontalAlignment:'center',verticalAlignment:'center'};
    s.freezePanes.freezeRows(1);
    s.freezePanes.freezeColumns(1);
    s.showGridLines = false;
    return s;
  }
  const main = sheet('Wire list', columns.map(c=>c.header), rows, 'WireList');
  main.tabColor = '#243D59';
  for (let i=0;i<columns.length;i++) {
    const f=columns[i].field, area=main.getRange(`${col(i+1)}2:${col(i+1)}${rows.length+1}`);
    if (['size','length'].includes(f)) { area.setNumberFormat('0.###'); area.format.horizontalAlignment='right'; }
    main.getRange(`${col(i+1)}1:${col(i+1)}${rows.length+1}`).format.columnWidth = /name|option/.test(f || '') ? 32 : /pin|size|color/.test(f || '') ? 15 : 22;
  }
  const raw = sheet('原始记录', ['记录ID','源图ID','线束','表','行',...fields,'单元格证据'], data.records.map(r=>[r.record_id,r.source_id,r.harness,r.table,r.row,...fields.map(f=>r.values[f]??null),JSON.stringify(r.evidence)]), 'RawRecords');
  raw.getRange(`A1:A${rows.length+1}`).format.columnWidth=48;
  const reviews = data.issues.map(p=>[p.code,p.record_id??p.source_id??'',p.end??'',p.field??'',JSON.stringify(p)]);
  const review = sheet('复核清单',['问题','记录/源图','端点','字段','详情与证据'],reviews,'ReviewItems');
  review.getRange(`A1:B${reviews.length+1}`).format.columnWidth=42;
  review.getRange(`E1:E${reviews.length+1}`).format.columnWidth=90;
  const info = [['总体','状态',data.status],['总体','记录数',rows.length],['总体','问题数',reviews.length]];
  for (const [k,v] of Object.entries(data.audit)) info.push(['端点校核',k,v]);
  for (const s of data.sources) {
    for (const k of ['project','drawing_number','revision','harness','sha256','entity_file_sha256','length_unit','size_unit','method']) info.push([s.id,k,s[k]??null]);
    info.push([s.id,'源文件',path.basename(s.path.replaceAll('\\','/'))],[s.id,'未覆盖区域',JSON.stringify(s.uncovered)]);
  }
  for (const t of data.tables) info.push([t.source_id,t.table,`预期 ${t.expected}；实际 ${t.actual}`]);
  for (const c of columns.filter(c=>c.field === null)) info.push(['模板空列',c.header,'未取得来源字段，留空']);
  const src = sheet('来源',['范围','字段','内容'],info,'SourceInfo');
  src.getRange(`C1:C${info.length+1}`).format.columnWidth=76;
  wb.recalculate();
  const formulas = await wb.inspect({kind:'formula',sheetId:'Wire list',range:`A1:${col(columns.length)}${rows.length+1}`,maxChars:1000,options:{maxResults:5}});
  console.log(formulas.ndjson);
  await fs.mkdir(path.dirname(output),{recursive:true});
  const preview = await wb.render({sheetName:'Wire list',range:`A1:${col(Math.min(columns.length,8))}${Math.min(rows.length+1,9)}`,scale:1.5,format:'png'});
  await fs.writeFile(output+'.preview.png',new Uint8Array(await preview.arrayBuffer()),{flag:'wx'});
  const xlsx = await SpreadsheetFile.exportXlsx(wb);
  const temp = await fs.mkdtemp(path.join(path.dirname(output),'.wirelist-export-'));
  try {
    const staged = path.join(temp,'workbook.xlsx');
    await xlsx.save(staged);
    await fs.copyFile(staged,output,constants.COPYFILE_EXCL);
  } finally {
    const resolved = await fs.realpath(temp);
    if (path.dirname(resolved) !== await fs.realpath(path.dirname(output)) || !path.basename(resolved).startsWith('.wirelist-export-')) throw Error('Unexpected temporary export path');
    await fs.rm(resolved,{recursive:true,force:true});
  }
  console.log(JSON.stringify({output,records:rows.length,issues:reviews.length,status:data.status}));
} catch (e) { console.error(e.message); process.exitCode=1; }
