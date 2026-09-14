# VectorForge Vision Engine 12.0 Beta

Aplicação desktop em Python para preparação de imagens, segmentação automática e vetorização com exportação em SVG e DXF.

> O código da versão atual está em [`VectorForge_Vision_Engine_12_0_Beta/`](./VectorForge_Vision_Engine_12_0_Beta/).

## Principais recursos

- recorte automático e normalização de contraste;
- redução de ruído e reconstrução raster;
- múltiplos métodos de segmentação com avaliação automática;
- preservação de caminhos, bordas e furos;
- controle do limite de nós por caminho;
- editor para movimentação e exclusão de elementos;
- exportação dos ajustes em SVG e DXF;
- presets para logos e desenhos técnicos.

## Tecnologias

- Python
- PySide6
- OpenCV
- NumPy

## Executando no Windows

```powershell
cd VectorForge_Vision_Engine_12_0_Beta
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Também estão disponíveis arquivos `.bat` para instalação e inicialização.

## Status

Versão Beta funcional e em evolução. O projeto ainda não oferece edição individual de nós, operações booleanas ou reconstrução tipográfica completa.

Desenvolvido por **Leonardo Cesa**.
