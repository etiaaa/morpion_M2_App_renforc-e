"""
Module Agent - Agent Q-Learning pour le Morpion
Gère le choix d'action (exploration/exploitation) et la mise à jour Q-learning.
"""

import numpy as np
import random
import pickle
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class QLearningAgent:
    """
    Agent Q-Learning tabulaire pour le jeu du Morpion.

    Utilise une Q-table stockée dans un dictionnaire où:
    - Clé: (état, action)
    - Valeur: Q-value

    Politique: ε-greedy avec décroissance optionnelle de ε
    """

    def __init__(
        self,
        alpha: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.9995,
        player: int = 1
    ):
        """
        Initialise l'agent Q-Learning.

        Args:
            alpha: Taux d'apprentissage (learning rate)
            gamma: Facteur de discount
            epsilon: Probabilité d'exploration initiale
            epsilon_min: Valeur minimale d'epsilon
            epsilon_decay: Facteur de décroissance d'epsilon par épisode
            player: Le joueur que l'agent représente (1 pour X, 2 pour O)
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.player = player

        # Q-table: dictionnaire {(state_key, action): q_value}
        self.q_table: Dict[Tuple[tuple, int], float] = defaultdict(float)

        # Statistiques
        self.training_episodes = 0

    def get_q_value(self, state_key: tuple, action: int) -> float:
        """
        Retourne la Q-value pour une paire (état, action).

        Args:
            state_key: Clé de l'état (hashable)
            action: Action (indice de case 0-8)

        Returns:
            Q-value (0.0 si non visitée)
        """
        return self.q_table[(state_key, action)]

    def get_max_q_value(self, state_key: tuple, legal_actions: List[int]) -> float:
        """
        Retourne la Q-value maximale pour un état donné parmi les actions légales.

        Args:
            state_key: Clé de l'état
            legal_actions: Liste des actions légales

        Returns:
            Q-value maximale (0.0 si aucune action légale)
        """
        if not legal_actions:
            return 0.0
        return max(self.get_q_value(state_key, a) for a in legal_actions)

    def choose_action(
        self,
        state_key: tuple,
        legal_actions: List[int],
        training: bool = True
    ) -> int:
        """
        Choisit une action selon la politique ε-greedy.

        Args:
            state_key: Clé de l'état actuel
            legal_actions: Liste des actions légales
            training: Si True, utilise ε-greedy; si False, utilise greedy pur

        Returns:
            Action choisie (indice de case)
        """
        if not legal_actions:
            raise ValueError("Aucune action légale disponible")

        # Exploration: action aléatoire
        if training and random.random() < self.epsilon:
            return random.choice(legal_actions)

        # Exploitation: meilleure action connue
        q_values = [(a, self.get_q_value(state_key, a)) for a in legal_actions]

        # Trouver la Q-value maximale
        max_q = max(q for _, q in q_values)

        # Départager aléatoirement en cas d'égalité
        best_actions = [a for a, q in q_values if q == max_q]
        return random.choice(best_actions)

    def learn(
        self,
        state_key: tuple,
        action: int,
        reward: float,
        next_state_key: tuple,
        next_legal_actions: List[int],
        done: bool
    ):
        """
        Met à jour la Q-table selon la règle Q-learning.

        Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') - Q(s,a)]

        Args:
            state_key: État avant l'action
            action: Action effectuée
            reward: Récompense reçue
            next_state_key: État après l'action
            next_legal_actions: Actions légales dans le nouvel état
            done: True si la partie est terminée
        """
        # Q-value actuelle
        q_old = self.get_q_value(state_key, action)

        # Calcul de la cible (target)
        if done:
            target = reward
        else:
            max_q_next = self.get_max_q_value(next_state_key, next_legal_actions)
            target = reward + self.gamma * max_q_next

        # Mise à jour de la Q-value
        self.q_table[(state_key, action)] = q_old + self.alpha * (target - q_old)

    def decay_epsilon(self):
        """Décroît epsilon après chaque épisode."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.training_episodes += 1

    def save(self, filepath: str):
        """
        Sauvegarde la Q-table et les hyperparamètres dans un fichier.

        Args:
            filepath: Chemin du fichier de sauvegarde
        """
        data = {
            'q_table': dict(self.q_table),
            'alpha': self.alpha,
            'gamma': self.gamma,
            'epsilon': self.epsilon,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'player': self.player,
            'training_episodes': self.training_episodes
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Agent sauvegardé: {len(self.q_table)} entrées Q-table, {self.training_episodes} épisodes")

    def load(self, filepath: str):
        """
        Charge la Q-table et les hyperparamètres depuis un fichier.

        Args:
            filepath: Chemin du fichier à charger
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.q_table = defaultdict(float, data['q_table'])
        self.alpha = data['alpha']
        self.gamma = data['gamma']
        self.epsilon = data['epsilon']
        self.epsilon_min = data['epsilon_min']
        self.epsilon_decay = data['epsilon_decay']
        self.player = data['player']
        self.training_episodes = data['training_episodes']
        print(f"Agent chargé: {len(self.q_table)} entrées Q-table, {self.training_episodes} épisodes")

    def get_stats(self) -> Dict:
        """
        Retourne des statistiques sur l'agent.

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            'q_table_size': len(self.q_table),
            'epsilon': self.epsilon,
            'training_episodes': self.training_episodes,
            'player': self.player
        }


class RandomAgent:
    """
    Agent aléatoire pour servir d'adversaire ou de baseline.
    Joue un coup légal au hasard.
    """

    def __init__(self, player: int = 2):
        """
        Initialise l'agent aléatoire.

        Args:
            player: Le joueur que l'agent représente (1 ou 2)
        """
        self.player = player

    def choose_action(
        self,
        state_key: tuple,
        legal_actions: List[int],
        training: bool = False
    ) -> int:
        """
        Choisit une action aléatoire parmi les actions légales.

        Args:
            state_key: Non utilisé (interface compatible)
            legal_actions: Liste des actions légales
            training: Non utilisé (interface compatible)

        Returns:
            Action choisie aléatoirement
        """
        if not legal_actions:
            raise ValueError("Aucune action légale disponible")
        return random.choice(legal_actions)

    def learn(self, *args, **kwargs):
        """Ne fait rien - l'agent aléatoire n'apprend pas."""
        pass

    def decay_epsilon(self):
        """Ne fait rien - pas d'epsilon."""
        pass


# Test unitaire
if __name__ == "__main__":
    from environment import TicTacToeEnv

    print("=== Test de l'agent Q-Learning ===\n")

    env = TicTacToeEnv()
    agent = QLearningAgent(alpha=0.1, gamma=0.99, epsilon=0.5, player=1)

    # Test du choix d'action
    state = env.get_state_key()
    legal = env.legal_actions()

    print(f"État initial: {state}")
    print(f"Actions légales: {legal}")

    action = agent.choose_action(state, legal, training=True)
    print(f"Action choisie: {action}")

    # Test de l'apprentissage
    next_state, reward, done = env.step(action)
    next_state_key = env.get_state_key()
    next_legal = env.legal_actions()

    agent.learn(state, action, reward, next_state_key, next_legal, done)

    print(f"\nQ-table après 1 transition:")
    for (s, a), q in agent.q_table.items():
        print(f"  Q({s}, {a}) = {q:.4f}")

    print(f"\nStatistiques: {agent.get_stats()}")
