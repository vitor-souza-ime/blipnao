# BLIP-NAO

Este repositório contém um sistema de **visão computacional para o robô NAO** integrado ao modelo **BLIP (Bootstrapped Language-Image Pretraining)**, permitindo capturar imagens das câmeras do NAO, gerar legendas automáticas e reproduzi-las em áudio pelo robô. O projeto inclui exibição em tempo real das imagens e legendas, além de salvar todas as capturas e textos em diretórios organizados por timestamp.

O arquivo principal do projeto é `main.py`.

---

## Requisitos

* **Hardware:** Robô NAO com câmeras funcionais.
* **Sistema:** Linux (testado no Ubuntu e Linux Mint).
* **Python:** >=3.8
* **Bibliotecas Python:**

```bash
pip install torch transformers pillow matplotlib qi numpy
```

* **Conexão:** IP do NAO acessível na rede local.

---

## Como usar

1. **Clonar o repositório:**

```bash
git clone https://github.com/vitor-souza-ime/blipnao.git
cd blipnao
```

2. **Editar IP do NAO:**
   No arquivo `main.py`, altere a linha:

```python
session = connect_to_nao("172.15.1.29", 9559)
```

para o IP do seu robô.

3. **Executar o script:**

```bash
python3 main.py
```

4. **Interação:**

* O script capturará imagens continuamente da câmera superior do NAO.
* Cada imagem será processada pelo **BLIP** para gerar uma legenda.
* A legenda será exibida na tela e falada pelo NAO.
* As imagens e legendas serão salvas automaticamente em um diretório criado com timestamp (`nao_captures_YYYYMMDD_HHMMSS`).
* Pressione **Ctrl+C** para interromper o programa.

---

## Funcionalidades

* Captura de imagens em tempo real das câmeras do NAO.
* Processamento com **BLIP** para gerar legendas automáticas.
* Exibição em janela interativa com **matplotlib**, mostrando imagem e legenda.
* Salvamento automático de imagens e legendas em arquivos separados.
* Síntese de voz do NAO para reproduzir a legenda.
* Estrutura modular para fácil expansão e integração com outros sensores ou algoritmos.

---

## Estrutura do Repositório

```
blipnao/
│
├─ main.py                 # Código principal do sistema
├─ README.md               # Este arquivo
├─ requirements.txt        # (opcional) Dependências do projeto
└─ nao_captures_YYYYMMDD_HHMMSS/   # Diretórios de saída gerados automaticamente
```

---

## Observações

* O BLIP pode ser carregado nas versões `base` ou `large`. Este projeto usa `blip-image-captioning-large`.
* Ajuste o FPS e resolução da câmera no `main.py` se houver problemas de performance.
* Para integração com o NAO, é necessário ter o **NAOqi** instalado e funcionando.

---

## Referências

* Gouaillier et al., 2008. *The NAO humanoid: a combination of mechanical, electrical and software design.*
* Salesforce BLIP: [https://huggingface.co/Salesforce/blip-image-captioning-base](https://huggingface.co/Salesforce/blip-image-captioning-base)
* Aldebaran Robotics, 2021. *NAO Hardware Documentation.*

