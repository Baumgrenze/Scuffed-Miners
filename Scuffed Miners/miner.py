"""
miner.py — Datenhaltung für einen einzelnen Miner.

Wichtig: Miner haben KEINEN eigenen Timer mehr — alle Miner im selben Schacht
teilen einen gemeinsamen Timer (in MineShaft). So minen alle gleichzeitig.
"""

class Miner:
    def __init__(self):
        self.active = False  # Schürft gerade (Timer läuft)
        self.ready  = False  # Fertig, wartet auf nächsten Klick (nur ohne Manager)

    def start(self):
        """Startet den Schürfvorgang."""
        self.active = True
        self.ready  = False

    def click(self):
        """Reagiert auf den 'Schürfen'-Klick des Spielers."""
        if not self.active:
            self.start()
