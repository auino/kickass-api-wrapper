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

TODO

### Notes ###

Based on a Python script by Emanuele Munafò.

### Contacts ###

You can find me on Twitter as [@auino](https://twitter.com/auino).
