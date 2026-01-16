"""
Module Environnement - Jeu du Morpion (Tic-Tac-Toe)
Gère les règles du jeu, les coups légaux, l'application des coups et la détection de fin de partie.
"""

import numpy as np
from typing import Tuple, List, Optional


class TicTacToeEnv:
    """
    Environnement du jeu de Morpion.

    Représentation du plateau:
    - 0: case vide
    - 1: joueur X
    - 2: joueur O

    Le plateau est représenté comme un tableau 1D de 9 cases (indices 0-8):
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
    """

    # Combinaisons gagnantes (indices des 3 cases alignées)
    WINNING_COMBINATIONS = [
        [0, 1, 2],  # Ligne du haut
        [3, 4, 5],  # Ligne du milieu
        [6, 7, 8],  # Ligne du bas
        [0, 3, 6],  # Colonne gauche
        [1, 4, 7],  # Colonne milieu
        [2, 5, 8],  # Colonne droite
        [0, 4, 8],  # Diagonale principale
        [2, 4, 6],  # Diagonale secondaire
    ]

    def __init__(self):
        """Initialise l'environnement."""
        self.board = None
        self.current_player = None
        self.done = None
        self.winner = None
        self.reset()

    def reset(self) -> Tuple[tuple, int]:
        """
        Réinitialise le jeu pour une nouvelle partie.

        Returns:
            Tuple contenant (état du plateau, joueur courant)
        """
        self.board = np.zeros(9, dtype=np.int8)
        self.current_player = 1  # X commence toujours
        self.done = False
        self.winner = None
        return self.get_state()

    def get_state(self) -> Tuple[tuple, int]:
        """
        Retourne l'état actuel du jeu.

        Returns:
            Tuple (plateau sous forme de tuple hashable, joueur courant)
        """
        return (tuple(self.board), self.current_player)

    def get_state_key(self) -> tuple:
        """
        Retourne une clé hashable pour la Q-table.
        Inclut le plateau ET le joueur courant pour éviter l'ambiguïté.

        Returns:
            Tuple hashable représentant l'état complet
        """
        return (tuple(self.board), self.current_player)

    def legal_actions(self, state: Optional[Tuple[tuple, int]] = None) -> List[int]:
        """
        Retourne la liste des actions légales (cases vides).

        Args:
            state: État optionnel (si None, utilise l'état courant)

        Returns:
            Liste des indices des cases vides
        """
        if state is not None:
            board = state[0]
        else:
            board = self.board

        return [i for i in range(9) if board[i] == 0]

    def step(self, action: int) -> Tuple[Tuple[tuple, int], float, bool]:
        """
        Exécute une action (placer un pion) et retourne le résultat.

        Args:
            action: Indice de la case où jouer (0-8)

        Returns:
            Tuple (nouvel_état, récompense, done)

        Raises:
            ValueError: Si l'action est illégale
        """
        if self.done:
            raise ValueError("La partie est terminée. Utilisez reset() pour commencer une nouvelle partie.")

        if action not in self.legal_actions():
            raise ValueError(f"Action {action} illégale. Actions légales: {self.legal_actions()}")

        # Appliquer le coup
        player_who_played = self.current_player
        self.board[action] = self.current_player

        # Vérifier si la partie est terminée
        reward = 0.0

        if self._check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player
            # Récompense du point de vue du joueur qui vient de jouer
            reward = 1.0
        elif len(self.legal_actions()) == 0:
            # Match nul
            self.done = True
            self.winner = None
            reward = 0.0
        else:
            # Partie continue - changer de joueur
            self.current_player = 3 - self.current_player  # 1 -> 2 ou 2 -> 1
            reward = 0.0

        return self.get_state(), reward, self.done

    def _check_winner(self, player: int) -> bool:
        """
        Vérifie si un joueur a gagné.

        Args:
            player: Le joueur à vérifier (1 ou 2)

        Returns:
            True si le joueur a gagné, False sinon
        """
        for combo in self.WINNING_COMBINATIONS:
            if all(self.board[i] == player for i in combo):
                return True
        return False

    def get_reward_for_player(self, player: int) -> float:
        """
        Retourne la récompense finale du point de vue d'un joueur spécifique.

        Args:
            player: Le joueur (1 ou 2)

        Returns:
            +1 si victoire, -1 si défaite, 0 si nul ou partie en cours
        """
        if not self.done:
            return 0.0
        if self.winner is None:
            return 0.0  # Match nul
        if self.winner == player:
            return 1.0  # Victoire
        return -1.0  # Défaite

    def render(self) -> str:
        """
        Retourne une représentation textuelle du plateau.

        Returns:
            Chaîne de caractères représentant le plateau
        """
        symbols = {0: '.', 1: 'X', 2: 'O'}
        lines = []
        for row in range(3):
            line = ' | '.join(symbols[self.board[row * 3 + col]] for col in range(3))
            lines.append(line)
        return '\n---------\n'.join(lines)

    def copy(self) -> 'TicTacToeEnv':
        """
        Crée une copie de l'environnement.

        Returns:
            Nouvelle instance avec le même état
        """
        env_copy = TicTacToeEnv()
        env_copy.board = self.board.copy()
        env_copy.current_player = self.current_player
        env_copy.done = self.done
        env_copy.winner = self.winner
        return env_copy


# Test unitaire simple
if __name__ == "__main__":
    env = TicTacToeEnv()
    print("État initial:")
    print(env.render())
    print(f"\nActions légales: {env.legal_actions()}")
    print(f"État (hashable): {env.get_state_key()}")

    # Simuler quelques coups
    print("\n--- Test de quelques coups ---")
    actions = [4, 0, 1, 3, 7]  # X gagne en diagonal

    for action in actions:
        state, reward, done = env.step(action)
        print(f"\nJoueur {3 - env.current_player if not done else env.winner} joue case {action}")
        print(env.render())
        print(f"Récompense: {reward}, Terminé: {done}")
        if done:
            if env.winner:
                print(f"Gagnant: Joueur {env.winner} ({'X' if env.winner == 1 else 'O'})")
            else:
                print("Match nul!")
            break
