# Fontes de terceiros usados pelo AstroStitch

Esta pasta existe para cumprir as obrigações de licença das bibliotecas de
terceiros que o AstroStitch distribui dentro do APK. O aplicativo em si é
software proprietário; as bibliotecas abaixo não são, e continuam sob suas
próprias licenças.

## LibRaw 0.21.4 — `libraw/`

Usada para decodificar arquivos RAW de câmera (CR2, CR3, NEF, ARW, DNG, RAF e
outros).

A LibRaw é distribuída sob **dupla licença: LGPL-2.1 ou CDDL-1.0**, à escolha
de quem a utiliza. **O AstroStitch a utiliza sob a CDDL-1.0.** A CDDL é um
copyleft por arquivo: exige que os fontes dos arquivos cobertos por ela sejam
disponibilizados a quem recebe o binário — o que esta pasta faz — sem exigir
que o programa que os incorpora seja aberto.

Os textos das duas licenças acompanham os fontes:

- `libraw/LICENSE.CDDL` — a licença sob a qual utilizamos a biblioteca
- `libraw/LICENSE.LGPL` — a alternativa oferecida pela LibRaw
- `libraw/COPYRIGHT` — os avisos de copyright dos autores

### Modificações

**Nenhuma.** Estes são os fontes da LibRaw 0.21.4 exatamente como obtidos do
projeto original (https://www.libraw.org/). Se em algum momento passarmos a
modificá-los, as modificações serão publicadas aqui junto com os fontes, como
a licença exige.

### Como estes fontes são compilados

São compilados junto com o motor nativo do aplicativo (CMake + Android NDK),
gerando uma única biblioteca compartilhada. Nenhuma alteração de configuração
altera o código-fonte da LibRaw em si.

## OpenCV — não incluído aqui

O AstroStitch usa o OpenCV sob a **Apache License 2.0**, que não exige a
disponibilização dos fontes. Os fontes oficiais estão em
https://github.com/opencv/opencv e a licença acompanha a distribuição binária
usada (OpenCV Android SDK, versão 4.13).
