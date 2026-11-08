# Prix de La Popote

Ce dépôt fabrique chaque jeudi les fichiers de prix utilisés par l'app La Popote :

- `prix.json` : environ 37 000 prix relevés en magasin chez No Frills, Metro, Sobeys et Walmart (Project Hammer), avec les spéciaux.
- `statcan-qc.json` : les prix moyens au Québec de Statistique Canada.

## Mise en place (une seule fois)

1. Crée un dépôt public nommé `popote-prix` sur GitHub et téléverse tous les fichiers de ce dossier (y compris le dossier `.github`).
2. Dans le dépôt : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. Onglet **Actions** → « Prix de la semaine » → **Run workflow** pour la première génération (environ 5 minutes).
4. Dans l'app, onglet Réglages, champ « Adresse des prix de la semaine » : `https://TON-NOM.github.io/popote-prix`

Ensuite, tout se fait seul chaque jeudi.

## Mettre l'app à jour sans réinstaller

Le fichier `app.html` de ce dépôt est l'app elle-même. Quand Claude te donne un nouveau `app.html`, remplace-le dans le dépôt (Add file → Upload files). GitHub republie le site en 2-3 minutes; au prochain lancement, l'app prend la nouvelle version.
