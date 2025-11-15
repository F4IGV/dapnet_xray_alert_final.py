# dapnet_xray_alert_final.py


Pré-requis:

Installer python sur votre ordinateur sous windows. Assurer vous ensuite d'avoir REQUESTS installés

Version python stable — Script python permettant d'envoyer des alertes sur le dapnet en cas de tempête solaire. Seuil de rayon X pour le declenchement de l'alerte configurable.
Le Script envoie une message quand le seuil de rayon X configurer est dépasser. Si pas de changement pas de message envoyé. Si le flux de rayon X repasse en dessous du seuil le scrpit envoye un message pour annoncé la fin de l'evenement.

Dans les constantes: Vous devez modifier les entrées "DAPNET_USER" et "DAPNET_PASS" avec vos identifiant DAPNET. Dans "CALLSIGNS" vous devez entrer les indicatifs des om's a qui seront envoyés les messages en pocsag Dans "TX_GROUP" vous devez renseigner sur quel groupe d'emetteurs seront envoyés les messages en pocsag

Vous pour automatiser le script avec le fichier .bat sous windows. Atention à bien renseigner le chemin vers le fichier "dapnet_solar_pocsag_final" dans le fichier .bat. Un log est automatiquement généré dans le fichier spécifié dans le .bat. Vous pouvez créer une tache recurente avec le planificateur de tache sous windows pour executer le script toutes le X minutes. ( atention a ne pas saturer le reseau )

je n'assure pas le SAV ;)

Documentation pour le dapnet: https://hampager.de/dokuwiki/doku.php

Vous souhaitez vous équiper d'un Pager? voici la meilleur adresse: https://www.bi7jta.org/

Version finale et stable du script by F4IGV 11/2025

exemple de log généré:

<img width="1187" height="618" alt="screen_log_orage_solair" src="https://github.com/user-attachments/assets/6145674f-fb7d-43d4-b057-12181bfd4b6e" />
