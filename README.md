# Jev OpenTofu Plan Review

## Français

**But.** Comparer l'intention écrite d'un changement d'infrastructure avec les actions du plan OpenTofu, avant `apply`. Le résultat est un avis `aligned`, `mismatch` ou `review`, accompagné des chemins `resource_changes` à examiner. Un changement destructeur ou touchant aux contrôles d'accès impose toujours `review`, même si Jev répond `aligned`. Le programme ne lance jamais `apply`.

**Entrée.** Un JSON `{"intent":"...","plan":{...}}` contenant la sortie de `tofu show -json plan.bin`. La [documentation OpenTofu](https://opentofu.org/docs/internals/json-format/) précise ce format. Jusqu'à 50 changements sont évalués par appel ; un plan plus grand doit être découpé par module sans ignorer de ressources. Seuls adresses, types, actions, noms d'attributs modifiés et présence de valeurs sensibles partent vers Jev. Les valeurs `before` et `after`, y compris les secrets, ne sont pas transmises.

**Utilisation.** Installez `python3 -m pip install -r requirements.txt`. Lancez `python3 app.py --demo` pour un cas fictif. Pour un vrai dossier, préparez le JSON d'entrée dans un répertoire privé, chargez `TYPESAFE_API_KEY` dans l'environnement, puis lancez `python3 app.py --input chemin/vers/dossier.json`. Le fichier d'entrée peut contenir des valeurs sensibles provenant du plan : protégez-le et supprimez-le selon votre politique interne. Tests : `python3 -m unittest discover -s tests -v`. Ce premier livrable est un contrôle CLI et CI ; il ne publie pas de commentaire de PR automatiquement.

## English

**Purpose.** Compare a written infrastructure change intent with OpenTofu plan actions before `apply`. Output is an advisory `aligned`, `mismatch`, or `review` decision with `resource_changes` paths to inspect. Destructive or access-control changes always force `review`, even when Jev chooses `aligned`. This tool never runs `apply`.

**Input.** A JSON `{"intent":"...","plan":{...}}` containing `tofu show -json plan.bin` output. See the [OpenTofu format documentation](https://opentofu.org/docs/internals/json-format/). At most 50 changes are evaluated per call; larger plans must be split by module without dropping resources. Jev receives only addresses, types, actions, changed attribute names, and whether sensitive values exist. `before` and `after` values, including secrets, are excluded.

**Run.** Install `python3 -m pip install -r requirements.txt`. Run `python3 app.py --demo` for fictional input. For a real case, prepare the input JSON in a private directory, load `TYPESAFE_API_KEY` into the environment, then run `python3 app.py --input path/to/case.json`. The input file may contain sensitive plan values: protect and dispose of it according to your policy. Tests: `python3 -m unittest discover -s tests -v`. This initial release is a CLI and CI check; it does not post PR comments automatically.

## Español

**Objetivo.** Comparar la intención escrita de un cambio de infraestructura con las acciones de un plan OpenTofu antes de `apply`. El resultado es un dictamen `aligned`, `mismatch` o `review`, con rutas `resource_changes` para inspección. Los cambios destructivos o de control de acceso siempre fuerzan `review`, incluso si Jev elige `aligned`. La herramienta nunca ejecuta `apply`.

**Entrada.** Un JSON `{"intent":"...","plan":{...}}` con la salida de `tofu show -json plan.bin`. Consulte la [documentación del formato OpenTofu](https://opentofu.org/docs/internals/json-format/). Se evalúan hasta 50 cambios por llamada; un plan mayor debe dividirse por módulo sin omitir recursos. Jev recibe solo direcciones, tipos, acciones, nombres de atributos modificados y la presencia de valores sensibles. Se excluyen los valores `before` y `after`, incluidos los secretos.

**Uso.** Instale `python3 -m pip install -r requirements.txt`. Ejecute `python3 app.py --demo` para un caso ficticio. Para un caso real, prepare el JSON en un directorio privado, cargue `TYPESAFE_API_KEY` en el entorno y ejecute `python3 app.py --input ruta/al/caso.json`. El archivo de entrada puede contener valores sensibles del plan: protéjalo y elimínelo según su política interna. Pruebas: `python3 -m unittest discover -s tests -v`. Esta primera versión es una comprobación CLI y CI; no publica comentarios en PR automáticamente.

## Pipeline / Pipeline / Canalización

FR : avec `jq`, cette commande construit le dossier en mémoire ; protégez le plan binaire. EN: with `jq`, this builds the case in memory; protect the binary plan. ES: con `jq`, esto crea el expediente en memoria; proteja el plan binario.

```sh
mkdir -p .local
umask 077
tofu plan -out=.local/plan.bin
tofu show -json .local/plan.bin | jq -c --rawfile intent change-intent.txt '{intent:$intent,plan:.}' | python3 app.py --input -
```

MIT · v0.1.0
