# Escolhe o Teu Equilíbrio: Apostas Online

Jogo educativo Scratch 3 sobre o impacto das apostas online no bem-estar de um estudante.

## Como gerar o ficheiro .sb3

### Pré-requisitos
- Python 3.6 ou superior (sem dependências externas)

### Passos
1. Clona ou descarrega este repositório
2. Abre um terminal na pasta do projeto
3. Executa o script:
   ```
   python gerar_scratch.py
   ```
4. Será criado o ficheiro `escolhe_equilibrio.sb3` na mesma pasta
5. Vai a https://scratch.mit.edu
6. Clica em **Ficheiro → Carregar do teu computador**
7. Seleciona `escolhe_equilibrio.sb3`
8. Clica na bandeira verde para jogar!

## Sobre o jogo

**Tema**: Vício em apostas online e impacto no bem-estar de um estudante.

**Objetivo**: Controlar o Kai (setas esquerda/direita) para apanhar bons hábitos (LIVRO, SONO) e desviar dos maus hábitos (BET, FICHA). Tomar decisões em dois momentos-chave que determinam o final.

## Variáveis de estado

| Variável | Descrição | Valor inicial |
|----------|-----------|---------------|
| BemEstar | Bem-estar geral do Kai | 70 |
| Sono | Qualidade do sono | 70 |
| Notas | Desempenho escolar | 70 |
| Relacoes | Relações com amigos | 70 |

## Finais possíveis

- **Final Positivo**: BemEstar≥70, Sono≥60, Notas≥60
- **Final Negativo**: BemEstar<30 ou Sono<30 ou Notas<40
- **Final Intermédio**: todos os outros casos

## Mensagem

Apostas e maus hábitos digitais podem destruir o equilíbrio, mas pedir ajuda e escolher bons hábitos é um acto de coragem.
