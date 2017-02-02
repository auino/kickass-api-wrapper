# kickass-api-wrapper

### Description ###

This program allows you to set up a [KickassTorrents](https://it.wikipedia.org/wiki/KickassTorrents) (a.k.a. KAT) RSS API wrapper to be used with services like [SickBeard](http://sickbeard.com), [SickRage](https://sickrage.github.io) or [Sonarr](https://sonarr.tv).

By using this program, it is possible to retrieve data from raw HTML pages served by KAT clones, hence provide results as RSS feeds to be used by different software programs.

### Installation ###

 1. Clone the repository on your server:

    ```sh
    git clone https://github.com/auino/kickass-api-wrapper.git
    ```

 2. `cd` into the directory:

    ```sh
    cd kickass-api-wrapper
    ```

 3. Install program Python dependencies:

    ```sh
    pip install -r requirements.txt
    ```

It may be required to install `xml.etree.ElementTree` library.
In this case, download it from http://effbot.org/downloads#elementtree and proceed with a manual installation.

### Configuration ###

It's possible to configure program behavior by customizing [kat.py](https://github.com/auino/kickass-api-wrapper/blob/master/kat.py) variables values on the relative section.

### Execution ###

To run the service daemon, run the following command:

```sh
python kat.py
```

If you wish to run the daemon at system boot, insert the command inside of the `/etc/rc.local` file, by specifying the whole path of the Python script.
The program will be executed as `root`.

#### Sonarr Configuration ####

At this point, you can set up your [Sonarr](https://sonarr.tv) (or similar) software by adding a custom KickassTorrents indexer pointing to the following address (default configuration on `localhost` machine):

```
http://127.0.0.1:8123
```

### Notes ###

Based on an [Alfred script based on Python](http://www.packal.org/workflow/kat-search) by Emanuele Munafò.

### Updates ###

After a few days after the release of this script, official [Jackett](https://github.com/Jackett/Jackett) developers relased an update to the official program to support KickassTorrents.
Therefore, being Jackett a reliable well-known program supporting additional indexers, we personally suggest to use Jackett instead of this tool.
Nevertheless, for archive and to support code analysis, extension and forking, this repository will not die.

### Contacts ###

You can find me on Twitter as [@auino](https://twitter.com/auino).
