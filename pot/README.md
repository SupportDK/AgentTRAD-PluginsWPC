# Carpeta `pot/` — archivos de origen a traducir

Deja aquí el archivo de cada plugin que quieras traducir, con el **slug del
plugin** como nombre:

- `pot/<slug-del-plugin>.pot`  ← plantilla en inglés (recomendado), o
- `pot/<slug-del-plugin>.po`   ← un `.po` con los `msgstr` vacíos

Ejemplo: para traducir el plugin `wp-connect-foo`, deja `pot/wp-connect-foo.pot`.

Luego ejecuta:

```
/traducir wp-connect-foo fr
```

El resultado se genera en la raíz como `wp-connect-foo-fr.po`, reutilizando todas
las cadenas que ya existan traducidas en los `.po` del mismo idioma (el registro).
