import asyncio, json, os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from starlette.requests import Request
from fastapi import HTTPException
import api.auth as auth
from repositories.auth import RefreshTokenRepository
from repositories.legality import CertificateRepository
from services.request_limits import client_ip, WindowLimit

results=[]
def passed(name):results.append(name)
def req(ip='172.18.0.4',forwarded='198.51.100.1, 172.18.0.1'):
 return Request({'type':'http','client':(ip,1234),'headers':[(b'x-forwarded-for',forwarded.encode())]})
async def run_checks():
 os.environ['TRUSTED_PROXY_IPS']='172.18.0.4/32,172.18.0.1/32'
 assert client_ip(req())=='198.51.100.1'
 assert client_ip(req(forwarded='203.0.113.99, 198.51.100.1, 172.18.0.1'))=='198.51.100.1'
 assert client_ip(req('198.51.100.5','203.0.113.99'))=='198.51.100.5'
 assert client_ip(req(forwarded='garbage'))=='172.18.0.4'
 passed('trusted proxy traversal and spoof rejection')
 limit=WindowLimit(20)
 for i in range(21):limit.check(client_ip(req(forwarded=f'198.51.100.{i+1}, 172.18.0.1')))
 assert len(limit.buckets)==21
 for i in range(19):limit.check('198.51.100.1')
 try:limit.check('198.51.100.1');assert False
 except HTTPException as e:assert e.status_code==429 and int(e.headers['Retry-After'])>0
 limit.check('198.51.100.2');passed('per-client verification isolation and 429')
 with patch('services.request_limits.time.monotonic',return_value=100):
  bounded=WindowLimit(1,capacity=1);bounded.check('a')
  try:bounded.check('b');assert False
  except HTTPException as e:assert e.status_code==429
 with patch('services.request_limits.time.monotonic',return_value=161):bounded.check('b')
 passed('bounded limiter expiry')
 state={'revoked':False};gate=asyncio.Event();count=0
 class Collection:
  async def update_one(self,query,update):
   assert query['admin_id']=='a' and query['revoked'] is False and '$gt' in query['expires_at']
   if state['revoked']:return SimpleNamespace(modified_count=0)
   state['revoked']=True;return SimpleNamespace(modified_count=1)
 class Tokens(RefreshTokenRepository):
  def __init__(self,db):self.collection=Collection()
  async def is_active(self,jti):
   nonlocal count
   count+=1
   if count==2:gate.set()
   await gate.wait();return True
 class Admins:
  def __init__(self,db):pass
  async def get_by_uuid(self,uid):return SimpleNamespace(uuid='a',is_active=True)
  async def update_by_uuid(self,*args):pass
 issued=AsyncMock(return_value=('access-test','refresh-test'))
 with patch.object(auth,'decode_token',return_value={'type':auth.REFRESH_TYPE,'jti':'same','sub':'a'}),patch.object(auth,'RefreshTokenRepository',Tokens),patch.object(auth,'AdminRepository',Admins),patch.object(auth,'_issue_tokens',issued),patch.object(auth,'write_security_log',AsyncMock()):
  values=await asyncio.gather(*[auth.refresh(auth.RefreshRequest(refresh_token='same-token-test'),req(),None) for _ in range(2)],return_exceptions=True)
 assert issued.await_count==1 and sum(not isinstance(x,Exception) for x in values)==1
 passed('one successful rotation for concurrent token reuse')
 auth._login_ip_limit=WindowLimit(10);auth._login_account_limit=WindowLimit(10)
 repo=SimpleNamespace(get_by_email=AsyncMock(return_value=None))
 with patch.object(auth,'AdminRepository',return_value=repo),patch.object(auth,'write_security_log',AsyncMock()):
  for i in range(11):
   try:await auth.login(auth.LoginRequest(email='audit@example.test',password='invalid'),req(forwarded=f'198.51.100.{i+1}, 172.18.0.1'),None);assert False
   except Exception as e:assert e.status_code==(401 if i<10 else 429)
 assert repo.get_by_email.await_count==10
 passed('login attempts blocked before database access')
 class Cursor:
  async def to_list(self,length):return [{'items':[{'uuid':'page-2'}],'total':[{'count':114}]}]
 class Aggregation:
  def aggregate(self,pipeline):
   facet=pipeline[-1]['$facet'];assert facet['items'][0]=={'$skip':100}
   assert pipeline[3]['$match']['gem.status']=='published'
   assert pipeline[0]['$match']['is_deleted']=={'$ne':True}
   assert '$set' not in str(pipeline) and '$out' not in str(pipeline)
   return Cursor()
 repo=CertificateRepository.__new__(CertificateRepository);repo.collection=Aggregation()
 page=await repo.list_published(2,100);assert page['total']==114 and page['items'][0]['uuid']=='page-2'
 passed('read-only published pagination filters before paging')
 import services.analytics as analytics
 collection=SimpleNamespace(find_one=AsyncMock(return_value={'last_number':114}))
 counter=await analytics._certificate_counter({'counters':collection});assert counter['next_number'].startswith('AGR-{CODE}-000115-')
 passed('counter label without increment')
 import server
 with patch.object(server.settings,'skip_database_init',True),patch.object(server,'init_database',AsyncMock()) as init,patch.object(server.mongodb,'connect',AsyncMock()) as connect:
  await server.on_startup();init.assert_not_awaited();connect.assert_awaited_once()
 passed('deployment startup skips database bootstrap')
def test_live_readiness_regression():
 results.clear()
 asyncio.run(run_checks())

if __name__ == "__main__":
 test_live_readiness_regression()
 print(json.dumps({'passed':len(results),'tests':results},indent=2))
