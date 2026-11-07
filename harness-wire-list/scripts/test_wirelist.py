"""Small synthetic checks; no customer CAD data is stored in this skill."""
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import wirelist as w


class WireListTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        src = Path(self.tmp.name) / 'drawing.txt'
        src.write_text('independent fixture identity', encoding='utf8')
        self.fields = ['wire_id','from_id','from_pin','to_id','to_pin','size','length','seal1']
        self.vals = [['W01','BD01','01','BD02','1_PB','0.350','100','-'],
                     ['W02','BD01','2-1','BD02','D1','0.5','0',None]]
        self.plan = {'source':dict(id='A',path=str(src),sha256=w.digest(src),harness='FLH',drawing_number='123',revision='AA',project='测试',length_unit='mm',size_unit='mm2',method='synthetic',uncovered=[]),
                     'tables':[dict(id='t',space='Model',bounds=[0,0,80,30],rows_y=[24,7],tolerance=.4,expected_records=2,
                                    columns=[dict(field=f,left=i*10,right=(i+1)*10) for i,f in enumerate(self.fields)])]}
        self.es = [dict(space='Model',handle=f'{r}-{c}',x=c*10+2,y=[24,7][r],text=v)
                   for r,row in enumerate(self.vals) for c,v in enumerate(row) if v is not None]

    def extracted(self):
        return w.extract(self.es,self.plan)

    def pins(self):
        return [dict(source_id='A',harness='FLH',connector='BD01',pin='01',wire_id='W01',values={'size':'0.35','seal':'-'},
                     evidence={'source_id':'A','table':'independent-pin-table','handles':['P01','P02']})]

    def test_layout_and_identifiers(self):
        original = self.extracted()
        self.assertEqual(original['issues'],[])
        self.assertEqual([list(r['values'].values()) for r in original['records']],self.vals)
        p=copy.deepcopy(self.plan); es=copy.deepcopy(self.es)
        t=p['tables'][0]; t['bounds']=[100,40,340,100]; t['rows_y']=[88,54]; t['tolerance']=.8
        for i,c in enumerate(t['columns']): c.update(left=100+i*30,right=130+i*30)
        for e in es: e.update(x=100+e['x']*3,y=40+e['y']*2)
        self.assertEqual([r['values'] for r in w.extract(es,p)['records']], [r['values'] for r in original['records']])

    def test_variable_column_width(self):
        edges=[0,5,22,25,40,49,65,70,80]
        for i,c in enumerate(self.plan['tables'][0]['columns']): c.update(left=edges[i],right=edges[i+1])
        for e in self.es:
            c=int(e['handle'].split('-')[1]); e['x']=(edges[c]+edges[c+1])/2
        self.assertEqual([list(r['values'].values()) for r in self.extracted()['records']],self.vals)

    def test_ambiguity_unassigned_and_count(self):
        self.es.append(dict(self.es[0],handle='duplicate',text='OTHER'))
        self.es.append(dict(space='Model',handle='outside-row',x=4,y=15,text='unassigned'))
        self.plan['tables'][0]['expected_records']=3
        result=self.extracted(); codes={p['code'] for p in result['issues']}
        self.assertTrue({'multiple_cell_values','unassigned_text','row_count_mismatch','missing_required_value'} <= codes)
        self.assertIsNone(result['records'][0]['values']['wire_id'])
        self.assertEqual(len(result['records'][0]['evidence']['wire_id']),2)

    def test_pin_namespace_and_conflicts(self):
        batch=self.extracted(); pins=self.pins()
        result=w.assemble([batch],pins)
        self.assertEqual(result['audit']['matched_endpoints'],1)
        self.assertEqual(result['audit']['unmatched_endpoints'],3)
        self.assertEqual(result['audit']['differences'],0)
        pins[0]['values']['seal']='OTHER'
        self.assertEqual(w.assemble([batch],pins)['audit']['differences'],1)
        pins[0]['harness']='IPH'
        self.assertEqual(w.assemble([batch],pins)['audit']['matched_endpoints'],0)

    def test_ambiguous_pin_and_unknown(self):
        pins=self.pins(); pins[0]['values']['seal']=None
        r=w.assemble([self.extracted()],pins)
        self.assertEqual(r['audit']['compared_fields'],1)
        self.assertEqual(r['audit']['not_comparable_fields'],6)
        r=w.assemble([self.extracted()],pins+copy.deepcopy(pins))
        self.assertEqual(r['audit']['ambiguous_endpoints'],1)

    def test_duplicates_preserved_and_repeat_input_rejected(self):
        batch=self.extracted(); batch['records'][1]['values']['wire_id']='W01'
        r=w.assemble([batch],[])
        self.assertEqual(len(r['records']),2); self.assertEqual(len(r['duplicate_groups']),1)
        with self.assertRaises(ValueError): w.assemble([batch,batch],[])
        other=copy.deepcopy(batch)
        for s in other['sources']: s['id']='B';s['harness']='IPH'
        for r in other['records']: r['source_id']='B';r['harness']='IPH';r['record_id']='B'+r['record_id']
        self.assertEqual(len(w.assemble([batch,other],[])['records']),4)

    def test_input_guards(self):
        with self.assertRaises(ValueError): w.entities(self.es+[self.es[0]])
        pins=self.pins();pins[0]['evidence']={}
        with self.assertRaises(ValueError): w.assemble([self.extracted()],pins)
        self.plan['source']['sha256']='bad'
        with self.assertRaises(ValueError): self.extracted()
        with self.assertRaises(ValueError): w.assemble([],[])

    def test_no_overwrite(self):
        out=Path(self.tmp.name)/'out.json';w.write(out,{'original':True})
        with self.assertRaises(FileExistsError): w.write(out,{'original':False})
        self.assertTrue(w.read(out)['original'])

    def test_invalid_numeric_and_uncovered(self):
        self.es[5]['text']='NaN'
        self.plan['source']['uncovered']=['unread rotated table']
        result=self.extracted()
        self.assertEqual(result['records'][0]['values']['size'],'NaN')
        self.assertTrue({'invalid_numeric_text','uncovered_source_area'} <= {p['code'] for p in result['issues']})

    def test_cli_provenance_and_review_exit(self):
        p=Path(self.tmp.name);es=p/'entities.json';plan=p/'plan.json';out=p/'extracted.json';merged=p/'merged.json'
        w.write(es,self.es);w.write(plan,self.plan)
        command=[sys.executable,str(Path(w.__file__))]
        r=subprocess.run(command+['extract','--entities',str(es),'--plan',str(plan),'--output',str(out)],capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        r=subprocess.run(command+['assemble','--inputs',str(out),'--output',str(merged)],capture_output=True)
        self.assertEqual(r.returncode,2,r.stderr)
        data=w.read(merged)
        self.assertEqual(data['sources'][0]['entity_file_sha256'],w.digest(es))
        self.assertEqual(data['audit']['unmatched_endpoints'],4)


if __name__ == '__main__':
    unittest.main()
