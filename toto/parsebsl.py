from git import Repo
import collections
import json

repo = Repo('../')
commits = list(repo.iter_commits('bsl'))
content1=""
jsonArr=[]
meta=collections.OrderedDict()
for i in commits:
  content2=str(i.tree.blobs[0].data_stream.read())
  if content1:
    meta['body']=content1.replace(content2,"")
    jsonArr.append(json.dumps(meta))
  content1=content2
  meta['hexsha']=str(i.hexsha)
  meta['author_name']=str(i.author.name)
  meta['authored_date']=str(i.authored_date)
  meta['committer_name']=str(i.committer.name)
  meta['committed_date']=str(i.committed_date)
  meta['message']=str(i.message)
meta['body']=content1
jsonArr.append(json.dumps(meta))
with open('bsl.json','w') as f:
  json.dump(jsonArr,f)
