import sys
import json
import gnupg

# Check out the link to see its return code. Should a failure stop the verify process


if __name__ == '__main__':
  c = open('allowed_committers.json', 'r')
  data = c.read()
  c.close()
  committers = json.loads(data)
  f =  open('bsl.json', 'r')
  data = f.read()
  f.close()
  data = json.loads(data)
  gpg = gnupg.GPG()
  for idx, i in enumerate(data):
    r = json.loads(i)
    b = r['body']
    v = gpg.verify(b)
    if not v:
      print('ERROR FAILED TO VERIFY BSL ENTRY: {}'.format(b))
      sys.exit(1)
    if v.key_id not in committers:
      print('ERROR KEY ID FOR BSL ENTRY DOES NOT MATCH AN ALLOWED COMMITTER: {}'.format(v.key_id))
      sys.exit(1)
  print('SUCCESS: All BSL entries are valid')
  sys.exit(0)
