# Documentation

Protogenie is a tool developed around configuration files written in XML. This design choice was made
to allow for validation and control of configuration (this way, if your configuration file is valid but
it does not do what it should do, we know it's a bug !).

The scheme is available inside the package, and with each version by simply typing `protogenie get-scheme [DESTINATION]`
Protogénie est un outil tournant autour d'un fichier de configuration. Un schéma RelaxNG de validation est disponible 
à l'adresse [https://hipster-philology.github.io/protogenie/schema.rng](https://hipster-philology.github.io/protogenie/schema.rng)

## Démarrage d'une configuration

Une configuration contiendra *a minima* le squelette suivant:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://hipster-philology.github.io/protogenie/protogeneia/schema.rng"
     schematypens="http://relaxng.org/ns/structure/1.0"?>
<config>
    <corpora>
        <corpus path="" column_marker="">
            <splitter /><!-- Need completion-->
            <header /><!-- Need completion-->
        </corpus>
    </corpora>
</config>
```


