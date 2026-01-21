# API

## Example

Pour pouvoir importer le package :

```python
import sys

sys.path.insert(0, "path to /src/")
```

Puis les imports :

```python
from api.raspConnection import Connection, create_ports
```

______________________________________________________________________

Pour créer des ports virtuels, il suffit de créer une variable qui appelle [create_ports](#create_ports-function) avec en argument deux noms de ports sous la forme `/tmp/ttyVX` où `X` est un nombre.

```python
proc = create_ports("/tmp/ttyV0", "/tmp/ttyV1")
```

REMARQUE : Ne pas oubliez de tuer le process à la fin du code

```python
proc.kill()
```

______________________________________________________________________

Une fois les ports créés, on peut créer un object [Connection](#connection-class) en mettant l'un de nos ports en argument (l'autre servira pour un autre object Connection). Une fois l'object créé on le lance avec la function [start()](#connectionstart-function).

```python
conn = Connection("/tmp/ttyV0")

conn.start()
```

______________________________________________________________________

Pour envoyer des données, il suffit d'utiliser la function [send()](#connectionsend-function).

```python
conn.send("example", "ceci n'est pas un message")
```

Le premier argument est l'ordre et le second les data que l'ont cherche à envoyer.

**REMARQUE** : On peut aussi envoyer des messages sans ordre

```python
conn.sendRaw("example", "ceci n'est pas un message")
```

______________________________________________________________________

Pour recevoir les messages, il faut créer un handler.

```python
@conn.on("example")
def handler(data):
    print(data)
```

Ici à chaque message reçu avec l'ordre `example`, les data seront print sur le terminal.

**REMARQUE** : On peut aussi recevoir n'importe quelle message

```python
@conn.onMessage()
def handler(data):
    print(data)
```

Ou que les messages sans ordre

```python
@conn.onRaw()
def handler(data):
    print(data)
```

______________________________________________________________________

Pour arrêter la connection, il faut utiliser la function [stop()](#connectionstop-function).

```python
conn.stop(0)
```

Le premier argument est le code de sortie. `0` si le code a bien marché, sinon `9`

______________________________________________________________________

### Example complete

```python
import sys

sys.path.insert(0, "path to /src/")

from api.raspConnection import Connection, create_ports

proc = create_ports("/tmp/ttyV0", "/tmp/ttyV1")

conn1 = Connection("/tmp/ttyV0")
conn2 = Connection("/tmp/ttyV1")

@conn.on("example")
def handler(data):
    print(data)

conn1.start()
conn2.start()

conn1.send("example", "ceci n'est pas un message")

conn1.stop(0)
conn2.stop(0)

proc.kill()
```

## Functions et Classes

### [create_ports](../src/api/raspConnection.py#L313-336) (function)

Crée des ports à l'aide d'une commande socat.

***arguments :***

- **port1** {str} : Premier nom de port utilisé par socat dans la création des ports.

- **port2** {str} : Second nom de port utilisé par socat dans la création des ports.

  **REMARQUE** : Doit-être de la forme `/tmp/ttyVX` où `X` est un nombre.

______________________________________________________________________

### [Connection](../src/api/raspConnection.py#L15-L310) (class)

L'objet permettant d'envoyer et recevoir des données sur un port

***arguments :***

- **port** {str} : Port où l'objet doit se connecter.

______________________________________________________________________

#### [Connection.start()](../src/api/raspConnection.py#L159-L285) (function)

Démarre la connection.

______________________________________________________________________

#### [Connection.stop()](../src/api/raspConnection.py#L287-L310) (function)

Stoppe la connection.

***arguments :***

- **code** {int} : Code de sortie (`0` : succès | `9` : erreur)

______________________________________________________________________

#### [Connection.send()](../src/api/raspConnection.py#L122-L132) (function)

Envoie des data avec un ordre.

***arguments :***

- **ordre** {str} : Ordre avec lequel lire le message.
- **data** {any} : Data a envoyée.

______________________________________________________________________

#### [Connection.sendRaw()](../src/api/raspConnection.py#L134-L143) (function)

Envoie des data sans ordre.

***arguments :***

- **data** {bytes} : Data a envoyée.

______________________________________________________________________

#### [Connection.isRunning()](../src/api/raspConnection.py#L145-L150) (function)

Vérifie si la connection est toujours en cours.

______________________________________________________________________

#### [Connection.isLate()](../src/api/raspConnection.py#L152-L157) (function)

Vérifie si il y a trop de message en attente.
