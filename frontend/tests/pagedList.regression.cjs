const fs = require('fs'), vm = require('vm'), assert = require('assert'), ts = require('typescript');
const source = fs.readFileSync(require('path').resolve(__dirname, '../src/lib/pagedList.ts'),'utf8');
const code = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
async function run() {
 let calls=[];
 const context={exports:{},require:(name)=>({apiJson:async(path)=>{
   calls.push(path); const page=Number(new URL('http://test'+path).searchParams.get('page'));
   return {items:Array.from({length:page===1?100:14},(_,i)=>({uuid:String((page-1)*100+i)})),total:114};
 }})};
 vm.runInNewContext(code,context);
 const result=await context.exports.allPages('/api/admin/certificates');
 assert.equal(result.length,114);assert.equal(new Set(result.map(x=>x.uuid)).size,114);
 assert.equal(calls.length,2);assert(calls[1].includes('page=2'));
 calls=[];await context.exports.allPages('/api/admin/gemstones?q=Ruby');assert(calls[0].includes('q=Ruby&page=1'));
 context.require=()=>({apiJson:async()=>{throw new Error('offline')}});
 const failed={exports:{},require:context.require};vm.runInNewContext(code,failed);
 await assert.rejects(failed.exports.allPages('/api/admin/certificates'),/offline/);
 console.log(JSON.stringify({passed:6,allRecords:114,duplicateRecords:0}));
}
run().catch(e=>{console.error(e);process.exit(1)});
