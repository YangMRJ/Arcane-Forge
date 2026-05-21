# 🔮 Forja Arcana (Arcane Forge)

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-blueviolet?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge)

**Forja Arcana** é um motor conceitual de conjuração de magias táticas em tempo real baseado em **Geometria Sagrada** e **Metamágia Vetorial**. Desenvolvido em Python utilizando a biblioteca Pygame, o projeto simula um artefato místico onde magos inscrevem runas e moldam glifos com giz elemental para criar feitiços customizados e dinâmicos.

---

## 🧭 Círculos de Transmutação e Mecânicas Core

O sistema divide a criação de magias em duas esferas lógicas complementares:

### 1. O Sigilo Primordial (Círculo Externo Central)
* **A Essência do Feitiço:** Uma lousa geométrica rígida com 24 nós de ancoragem fixos espaçados a exatos 15°.
* **Regras de Estabilidade:** Aceita apenas **linhas retas**. O motor matemático analisa em tempo real os ângulos internos gerados nas quinas e a fricção molecular (cruzamentos de linhas).
* **Comportamento Base:** * Pontas afiadas/agudas geram magias do tipo **Projétil/Raio**.
  * Formas quadradas/regulares moldam **Barreiras/Escudos**.
  * Cruzamentos excessivos adicionam caos, tornando o feitiço **Instável** ou de **Área de Efeito (AoE)**.

### 2. Os Satélites de Metamágia (Círculos Menores Orbitais)
Uma mecânica inspirada no sistema *High Risk, High Reward*. Cinco satélites menores de 8 nós orbitam o núcleo, funcionando como placas de argila ou páginas de grimório para modificadores de efeito.
* **Geometria Estável (Linhas Retas):** Quando os glifos internos possuem apenas quinas retas, os satélites mostram os ângulos internos em tempo real e emitem um brilho estático ressonante com a cor do elemento ativo.
* **Geometria Selvagem (Linhas Curvas):** Utilizando **Curvas de Bézier Quadráticas**, o jogador pode segurar `SHIFT` ou usar a ferramenta **Moldar** para clicar no meio de uma linha e puxá-la com o mouse, deformando o giz. 
* **Efeito Aurora Boreal:** Ao entortar a geometria útil, os ângulos se dissipam e o satélite ganha uma **Aurora Boreal procedural pulsante**, aplicando modificadores selvagens de alta potência com chances críticas de anomalias mágicas.

---

## 🎨 Imersão Visual e Feedback Tátil

* **Motor de Giz Procedural (Chalk Physics):** As linhas não são traçadas instantaneamente. O giz possui uma velocidade de arrasto e é renderizado através de centenas de grãos com variação de opacidade e dispersão angular (*jitter*), mimetizando a textura real de lousa.
* **Poeira de Giz Física (Falling Dust):** Durante o traçado das linhas, floquinhos de poeira de giz se desprendem e caem pela tela em tempo real, sofrendo efeitos simulados de gravidade e dissipação de opacidade (*fade out*).
* **Controle de Órbita Dinâmica:** Os satélites rotacionam em torno do núcleo. O jogador possui um interruptor funcional para congelar a órbita, permitindo a inscrição precisa de glifos, que passam a girar junto com o sistema mecânico assim que a rotação é reativada.

---

## ⌨️ Controles do Alquimista

| Comando | Ação no Jogo |
| :--- | :--- |
| `Botão Esquerdo do Mouse (LMB)` | Marcar pontos nos nós focados (Modo Desenhar). |
| `SHIFT` ou `CTRL` + `LMB` | Clicar e arrastar uma linha nos círculos menores para curvá-la (Modo Moldar). |
| `Botão Direito do Mouse (RMB)` | Limpar instantaneamente toda a geometria do círculo focado. |
| `Botão [Parar/Girar Órbita]` | Congela os modificadores para desenhar ou reativa a dança orbital. |
| `Botão [Ferramenta: Desenhar/Moldar]`| Alterna permanentemente o comportamento do clique útil do mouse. |
| `Teclas [DELETE] / [BACKSPACE]` | Desfaz o último nó inserido. |
| `Tecla [ENTER]` | Conjura a fórmula mágica atual, gerando a explosão de partículas e o relatório. |
| `Tecla [ESC]` | Limpa e reinicia todos os círculos da Forja de uma vez. |

---

## ⚙️ Pré-requisitos e Instalação

Certifique-se de ter o Python 3.9 ou superior instalado em sua máquina.

1. Clone este repositório:
```bash
git clone [https://github.com/SEU_USUARIO/forja-arcana.git](https://github.com/SEU_USUARIO/forja-arcana.git)
cd forja-arcana
