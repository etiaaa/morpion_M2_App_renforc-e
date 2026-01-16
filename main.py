"""
Morpion Q-Learning - Fichier Principal
TP Machine Learning - Master 2 Data Science

Lance l'interface graphique Pygame avec le menu intégré.
"""

from gui import PygameGUI


def main():
    """Point d'entrée principal."""
    gui = PygameGUI()
    gui.run()


if __name__ == "__main__":
    main()
