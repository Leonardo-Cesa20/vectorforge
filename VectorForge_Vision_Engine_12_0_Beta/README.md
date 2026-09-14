# VectorForge Vision Engine 12.0 Beta

Nova arquitetura centrada na preparação da imagem antes da vetorização.

## Vision Engine

A imagem passa por:

1. recorte automático;
2. normalização de contraste;
3. redução de ruído;
4. geração de múltiplas segmentações;
5. avaliação automática;
6. escolha do melhor método;
7. reconstrução raster;
8. vetorização conservadora.

## Métodos de segmentação

- Otsu;
- Adaptive Gaussian;
- Sauvola;
- Wolf;
- Niblack;
- Local Darkness;
- Percentis.

O programa mostra a nota de cada método e permite selecionar manualmente outro resultado.

## Reconstrução raster

- remoção de componentes pequenos;
- remoção de ruído que encosta nas bordas;
- fechamento de falhas;
- preenchimento opcional de pequenos buracos;
- preservação de bordas.

## Vetorização

- preservação dos caminhos originais;
- preservação de furos;
- limite de nós por caminho;
- conversão geométrica desativada para logos por padrão;
- editor com movimentação e exclusão;
- SVG e DXF com alterações do editor.

## Presets

- Logo limpo;
- Logo com ruído;
- Desenho técnico.

## Limitações

- não possui edição individual de nós;
- não possui ajuste Bézier profissional;
- não possui operações booleanas;
- não possui modelo de IA treinado;
- é uma Beta funcional e não substitui integralmente CorelDRAW ou LightBurn.
