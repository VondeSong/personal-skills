"""Runtime integration checks: set RUNTIME_NODE_BIN and RUNTIME_NODE_MODULES."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from openpyxl import load_workbook  # Readback only; authoring uses artifact-tool.


@unittest.skipUnless(os.environ.get('RUNTIME_NODE_BIN') and os.environ.get('RUNTIME_NODE_MODULES'), 'Bundled Node runtime required')
class ExportTests(unittest.TestCase):
    def test_export_literal_values_units_and_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);script=Path(__file__).with_name('export_xlsx.mjs')
            labels=['=1+1','+SUM(A1:A2)','@X','-X',"'literal",'中文线号']
            fields=['wire_id','from_pin','to_pin','size','length','seal1']
            records=[dict(record_id=f'R{i}',source_id='S',harness='FLH',table='t',row=i+1,
                          values=dict(zip(fields,[v,'01','1_PB','0.350','100','-' if i==0 else None])),
                          evidence={}) for i,v in enumerate(labels)]
            data=dict(schema='harness-wire-list/v1',sources=[dict(id='S',path='D:/private/source.dwg',length_unit='mm',size_unit='mm2',uncovered=[])],records=records,audit={'total_endpoints':12,'matched_endpoints':0,'unmatched_endpoints':12},issues=[],tables=[],status='synthetic_export_test')
            mapping={'columns':[dict(header='LengthMm' if f=='length' else f,field=f) for f in fields]}
            inp=p/'input.json';mp=p/'mapping.json';out=p/'test.xlsx'
            def save():
                inp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
                mp.write_text(json.dumps(mapping),encoding='utf8')
            def run():
                return subprocess.run([os.environ['RUNTIME_NODE_BIN'],str(script),str(inp),str(mp),str(out)],capture_output=True,text=True,encoding='utf8',timeout=180)
            save();result=run();self.assertEqual(result.returncode,0,result.stderr)
            wb=load_workbook(out,data_only=False);self.addCleanup(wb.close)
            ws=wb['Wire list'];raw=wb['原始记录']
            for i,v in enumerate(labels,2):
                self.assertEqual(ws.cell(i,1).value,v)
                self.assertEqual(ws.cell(i,2).value,'01')
                self.assertEqual(ws.cell(i,3).value,'1_PB')
                self.assertEqual(ws.cell(i,4).value,.35)
                self.assertEqual(ws.cell(i,5).value,100)
                self.assertEqual(raw.cell(i,9).value,'0.350')
            self.assertEqual(ws.cell(2,6).value,'-');self.assertIsNone(ws.cell(3,6).value)
            self.assertEqual(ws.max_row,len(labels)+1)
            for s in wb:
                self.assertFalse(any(c.data_type=='f' for row in s for c in row))
                self.assertFalse(any('D:/private' in str(c.value) for row in s for c in row))
            self.assertTrue(Path(str(out)+'.preview.png').exists())
            before=out.read_bytes();self.assertNotEqual(run().returncode,0);self.assertEqual(out.read_bytes(),before)
            out=p/'wrong-units.xlsx';data['sources'][0]['length_unit']='unknown';save()
            bad=run();self.assertNotEqual(bad.returncode,0);self.assertIn('confirmed mm',bad.stderr)
            self.assertFalse(out.exists())
            out=p/'apostrophe-equals.xlsx';data['sources'][0]['length_unit']='mm';data['records'][0]['values']['wire_id']="'=literal";save()
            bad=run();self.assertNotEqual(bad.returncode,0);self.assertIn('exact-text',bad.stderr)
            self.assertFalse(out.exists())


if __name__=='__main__':
    unittest.main()
