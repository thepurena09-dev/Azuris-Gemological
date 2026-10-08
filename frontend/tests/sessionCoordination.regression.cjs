const fs=require('fs'),vm=require('vm'),assert=require('assert'),ts=require('typescript');
const code=ts.transpileModule(fs.readFileSync(require('path').resolve(__dirname, '../src/lib/api.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
const storage=new Map([['azuris_access','old'],['azuris_refresh','old-refresh']]);
const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)};
let queue=Promise.resolve(),rotations=0,mode='success';
const locks={request:(name,callback)=>{const result=queue.then(callback);queue=result.catch(()=>{});return result}};
const fetch=async(path,opts)=>{
 if(path.endsWith('/refresh')){
  rotations++;
  if(mode==='network')throw new Error('network');
  if(mode==='server')return {ok:false,status:503};
  return {ok:true,status:200,json:async()=>({access_token:'new',refresh_token:'new-refresh'})};
 }
 return {ok:opts.headers.get('Authorization')==='Bearer new',status:opts.headers.get('Authorization')==='Bearer new'?200:401};
};
function tab(){const c={exports:{},require:()=>({appConfig:{api:{baseUrl:''}}}),localStorage,navigator:{locks},fetch,Headers,FormData,Promise};vm.runInNewContext(code,c);return c.exports}
async function run(){
 const [a,b]=[tab(),tab()];const results=await Promise.all([a.apiFetch('/api/admin/certificates'),b.apiFetch('/api/admin/gemstones')]);
 assert(results.every(r=>r.status===200));assert.equal(rotations,1);assert.equal(storage.get('azuris_access'),'new');
 for(const failure of ['network','server']){
  storage.set('azuris_access','old');storage.set('azuris_refresh','old-refresh');mode=failure;
  const response=await tab().apiFetch('/api/admin/certificates');assert.equal(response.status,401);assert.equal(storage.get('azuris_refresh'),'old-refresh');
 }
 console.log(JSON.stringify({passed:5,concurrentTabs:2,successfulRotations:1,sessionPreservedOnTransientFailure:true}));
}
run().catch(e=>{console.error(e);process.exit(1)});
