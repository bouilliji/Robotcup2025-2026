pour creer une communication:

```python
from raspConnection import *

communication = Communication("port(a determiner et creer avec socat)")
```

pour envoyer un message:

```python
communication.send("obstacle", {"type":"block","distance":4})
communication.send("donnee random", [4,67,12,76])
```

pour recevoir le message:

```python
@connection.on("obstacle")
async def handler(data):
  assert data == {"type":"block","distance":4}
```

pour creer un default handler:
example on n'a pas creer de handler pour "donnee random" si une donneée est donc envoyer avec ce not d'ordre le default handler est appelé

```
@connection.default()
async def globalHandler(ordre, donnee):
  if ordre=="donnee random":
    assert donnee == [4,67,12,76]
```
