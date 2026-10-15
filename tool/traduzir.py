#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera /en e /es a partir das paginas em portugues.

POR QUE UM GERADOR, e nao tres arquivos escritos a mao: mantidos a mao, os
tres divergem no primeiro conserto de texto que alguem fizer so num deles.
Aqui o portugues e a fonte; en e es saem dele, e qualquer bloco que eu
esquecer de traduzir e DENUNCIADO pela varredura no fim, em vez de passar
despercebido num idioma que eu leio menos.

Uso:  python -I tool/traduzir.py
"""

import io
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://amaromiranda.github.io/astro-stitch-releases'


# --------------------------------------------------------------------------
# Blocos de texto. Cada entrada e (portugues, ingles, espanhol) e TEM de
# casar exatamente uma vez no arquivo — se nao casar, o gerador para.
# --------------------------------------------------------------------------

INDEX = [
# --- cabecalho do documento
("""<title>AstroStitch</title>""",
 """<title>AstroStitch</title>""",
 """<title>AstroStitch</title>"""),

("""<meta name="description" content="Mosaicos de Lua, Sol, céu profundo e panoramas a partir dos seus painéis. Para Windows e Android.">""",
 """<meta name="description" content="Mosaics of the Moon, the Sun, deep sky and landscapes from your own panels. For Windows and Android.">""",
 """<meta name="description" content="Mosaicos de Luna, Sol, cielo profundo y panorámicas a partir de tus paneles. Para Windows y Android.">"""),

("""<meta property="og:description" content="Mosaicos de Lua, Sol, céu profundo e panoramas a partir dos seus painéis.">""",
 """<meta property="og:description" content="Mosaics of the Moon, the Sun, deep sky and landscapes from your own panels.">""",
 """<meta property="og:description" content="Mosaicos de Luna, Sol, cielo profundo y panorámicas a partir de tus paneles.">"""),

# --- navegacao
("""<a class="pular" href="#conteudo">Pular para o conteúdo</a>""",
 """<a class="pular" href="#conteudo">Skip to content</a>""",
 """<a class="pular" href="#conteudo">Saltar al contenido</a>"""),

("""aria-label="AstroStitch — início\"""",
 """aria-label="AstroStitch — home\"""",
 """aria-label="AstroStitch — inicio\""""),

("""<nav class="navegacao" aria-label="Principal">
      <a href="releases.html">Notas de versão</a>""",
 """<nav class="navegacao" aria-label="Main">
      <a href="releases.html">Release notes</a>""",
 """<nav class="navegacao" aria-label="Principal">
      <a href="releases.html">Notas de versión</a>"""),

("""<span class="nav-rotulo">Baixar</span>""",
 """<span class="nav-rotulo">Download</span>""",
 """<span class="nav-rotulo">Descargar</span>"""),

# --- heroi
("""<h1>Una seus painéis<br>em um mosaico.</h1>""",
 """<h1>Join your panels<br>into one mosaic.</h1>""",
 """<h1>Une tus paneles<br>en un mosaico.</h1>"""),

("""Mosaicos de Lua, Sol, céu profundo e panoramas, montados a partir das
        suas capturas. O processamento acontece no seu aparelho — as fotos
        não saem dele.""",
 """Mosaics of the Moon, the Sun, deep sky and landscapes, built from your
        own captures. Everything is processed on your device — your photos
        never leave it.""",
 """Mosaicos de Luna, Sol, cielo profundo y panorámicas, montados a partir
        de tus capturas. El procesamiento ocurre en tu dispositivo: las fotos
        no salen de él."""),

("""<strong>Baixar para Windows</strong>
            <small>Grátis · x64 · .zip</small>""",
 """<strong>Download for Windows</strong>
            <small>Free · x64 · .zip</small>""",
 """<strong>Descargar para Windows</strong>
            <small>Gratis · x64 · .zip</small>"""),

("""<strong>Ver na Google Play</strong>
            <small>Android · aplicativo pago</small>""",
 """<strong>Get it on Google Play</strong>
            <small>Android · paid app</small>""",
 """<strong>Ver en Google Play</strong>
            <small>Android · aplicación de pago</small>"""),

("""Versão <span class="dado">0.56.2</span> para Windows ·
        <a href="releases.html">o que mudou</a>""",
 """Version <span class="dado">0.56.2</span> for Windows ·
        <a href="releases.html">what changed</a>""",
 """Versión <span class="dado">0.56.2</span> para Windows ·
        <a href="releases.html">qué cambió</a>"""),

("""alt="Mosaico lunar composto pelo AstroStitch: a Lua gibosa, com os mares
                  em tom azulado da cor mineral real realçada pelo app.\"""",
 """alt="Lunar mosaic composed by AstroStitch: the gibbous Moon, its maria in
                  the bluish tone of the real mineral colour the app brings out.\"""",
 """alt="Mosaico lunar compuesto por AstroStitch: la Luna gibosa, con los mares
                  en el tono azulado del color mineral real que resalta la app.\""""),

("""Mosaico de <span class="dado">11</span> painéis, saída de
        <span class="dado">2169 × 2299</span>, com a Lua Mineral ligada.
        Composto no AstroStitch para Windows.""",
 """A mosaic of <span class="dado">11</span> panels, output
        <span class="dado">2169 × 2299</span>, with Mineral Moon on.
        Composed in AstroStitch for Windows.""",
 """Mosaico de <span class="dado">11</span> paneles, salida de
        <span class="dado">2169 × 2299</span>, con Luna Mineral activada.
        Compuesto en AstroStitch para Windows."""),

# --- como se usa
("""<p class="rotulo">Como se usa</p>
      <h2>Você escolhe os painéis. O app alinha e compõe.</h2>""",
 """<p class="rotulo">How it works</p>
      <h2>You pick the panels. The app aligns and composes.</h2>""",
 """<p class="rotulo">Cómo se usa</p>
      <h2>Tú eliges los paneles. La app alinea y compone.</h2>"""),

("""Sem camadas, sem máscaras, sem passo a passo de edição. O modo escolhido
        já ajusta projeção, costura e recorte — e o que você vê na tela é o que
        sai no arquivo.""",
 """No layers, no masks, no editing walkthrough. The mode you choose already
        sets projection, stitching and cropping — and what you see on screen is
        what lands in the file.""",
 """Sin capas, sin máscaras, sin pasos de edición. El modo elegido ya ajusta
        proyección, costura y recorte, y lo que ves en pantalla es lo que sale
        en el archivo."""),

("""alt="Janela do AstroStitch para Windows com doze painéis lunares
                    importados: a fita de miniaturas embaixo, o painel selecionado
                    no centro e os controles de saída à direita.\"""",
 """alt="The AstroStitch window on Windows with twelve lunar panels imported:
                    the thumbnail strip below, the selected panel in the centre
                    and the output controls on the right.\"""",
 """alt="Ventana de AstroStitch en Windows con doce paneles lunares
                    importados: la tira de miniaturas abajo, el panel seleccionado
                    en el centro y los controles de salida a la derecha.\""""),

("""<strong>1. Os painéis entram.</strong>
          Arraste a pasta ou escolha os arquivos — RAW de câmera, TIFF, PNG ou JPG,
          em 8 ou 16 bits. O app confere tamanhos e avisa se um deles destoa.""",
 """<strong>1. The panels come in.</strong>
          Drag the folder or pick the files — camera RAW, TIFF, PNG or JPG, at 8
          or 16 bits. The app checks sizes and warns you if one of them is odd.""",
 """<strong>1. Entran los paneles.</strong>
          Arrastra la carpeta o elige los archivos: RAW de cámara, TIFF, PNG o JPG,
          de 8 o 16 bits. La app comprueba los tamaños y avisa si alguno desentona."""),

("""alt="A mesma janela depois de compor: o mosaico pronto no centro,
                    e à direita a resolução, o formato de saída e a opção Lua
                    Mineral ligada.\"""",
 """alt="The same window after composing: the finished mosaic in the centre,
                    and on the right the resolution, the output format and the
                    Mineral Moon switch turned on.\"""",
 """alt="La misma ventana después de componer: el mosaico terminado en el
                    centro y, a la derecha, la resolución, el formato de salida y
                    la opción Luna Mineral activada.\""""),

("""<strong>2. O mosaico sai pronto.</strong>
          Resolução total ou reduzida, TIFF de 16 bits para continuar editando,
          PNG ou JPG para publicar. A <em>Lua Mineral</em> realça a cor mineral
          real do solo — titânio puxando para o azul, ferro para o laranja.""",
 """<strong>2. The mosaic comes out finished.</strong>
          Full or reduced resolution, 16-bit TIFF to keep editing elsewhere, PNG
          or JPG to publish. <em>Mineral Moon</em> brings out the real mineral
          colour of the soil — titanium towards blue, iron towards orange.""",
 """<strong>2. El mosaico sale terminado.</strong>
          Resolución total o reducida, TIFF de 16 bits para seguir editando, PNG
          o JPG para publicar. La <em>Luna Mineral</em> resalta el color mineral
          real del suelo: el titanio tira al azul y el hierro al naranja."""),

# --- detalhe
("""alt="Recorte em escala real do mosaico, mostrando crateras pequenas
                    e o relevo do terreno perto do terminador.\"""",
 """alt="A full-scale crop of the mosaic, showing small craters and the relief
                    of the terrain near the terminator.\"""",
 """alt="Recorte a escala real del mosaico, con cráteres pequeños y el relieve
                    del terreno cerca del terminador.\""""),

("""<p class="rotulo">Detalhe do mosaico</p>
        <h2>O detalhe que a vista geral esconde.</h2>""",
 """<p class="rotulo">Mosaic detail</p>
        <h2>The detail the wide view hides.</h2>""",
 """<p class="rotulo">Detalle del mosaico</p>
        <h2>El detalle que la vista general esconde.</h2>"""),

("""Um recorte de <span class="dado">900 × 900</span> pixels do arquivo
          exportado — o mosaico inteiro tem <span class="dado">2169 × 2299</span> —
          redimensionado aqui para caber na página.""",
 """A <span class="dado">900 × 900</span> pixel crop of the exported file — the
          whole mosaic is <span class="dado">2169 × 2299</span> — resized here to
          fit the page.""",
 """Un recorte de <span class="dado">900 × 900</span> píxeles del archivo
          exportado — el mosaico entero mide <span class="dado">2169 × 2299</span> —
          redimensionado aquí para caber en la página."""),

("""A costura não mora na foto inteira — mora aqui, onde dois painéis se
          encontram e o relevo precisa continuar de um para o outro.""",
 """Stitching does not live in the whole picture — it lives here, where two
          panels meet and the relief has to carry on from one into the other.""",
 """La costura no vive en la foto entera: vive aquí, donde dos paneles se
          encuentran y el relieve tiene que continuar de uno al otro."""),

# --- lua mineral
("""<p class="rotulo">Lua Mineral</p>
      <h2>A cor já estava lá.</h2>""",
 """<p class="rotulo">Mineral Moon</p>
      <h2>The colour was already there.</h2>""",
 """<p class="rotulo">Luna Mineral</p>
      <h2>El color ya estaba ahí.</h2>"""),

("""A Lua não é cinza. O solo muda de química de uma região para a outra, e
        isso muda a cor: basalto com muito titânio reflete mais para o azul,
        solo rico em ferro puxa para o laranja. A sua câmera registra essa
        diferença — ela é só fraca demais para o olho achar sozinho.""",
 """The Moon is not grey. Its soil changes chemistry from one region to the
        next, and that changes the colour: basalt rich in titanium reflects
        bluer, iron-rich soil pulls towards orange. Your camera does record that
        difference — it is just too faint for the eye to find on its own.""",
 """La Luna no es gris. El suelo cambia de química de una región a otra, y eso
        cambia el color: el basalto con mucho titanio refleja más hacia el azul y
        el suelo rico en hierro tira al naranja. Tu cámara sí registra esa
        diferencia; solo es demasiado débil para que el ojo la encuentre solo."""),

("""A <em>Lua Mineral</em> amplia o que já está no arquivo, sem mexer no
        brilho e sem inventar cor. Abaixo, o mesmo recorte do mesmo mosaico:
        à esquerda como saiu da costura, à direita com vibração em
        <span class="dado">70%</span> e redução de ruído de cor no máximo.""",
 """<em>Mineral Moon</em> amplifies what is already in the file, without
        touching brightness and without inventing colour. Below, the same crop of
        the same mosaic: on the left as it came out of the stitch, on the right
        with vibrance at <span class="dado">70%</span> and colour noise reduction
        at maximum.""",
 """La <em>Luna Mineral</em> amplía lo que ya está en el archivo, sin tocar el
        brillo y sin inventar color. Abajo, el mismo recorte del mismo mosaico: a
        la izquierda tal como salió de la costura y a la derecha con vibración al
        <span class="dado">70%</span> y reducción de ruido de color al máximo."""),

("""alt="Recorte do mosaico com a Lua Mineral desligada: a fronteira
                    entre dois mares aparece só como dois tons de cinza.\"""",
 """alt="A crop of the mosaic with Mineral Moon off: the boundary between two
                    maria shows up only as two shades of grey.\"""",
 """alt="Recorte del mosaico con la Luna Mineral desactivada: la frontera
                    entre dos mares aparece solo como dos tonos de gris.\""""),

("""<figcaption><strong>Desligada.</strong> Dois mares vizinhos, e nada
          além de cinza para separá-los.</figcaption>""",
 """<figcaption><strong>Off.</strong> Two neighbouring maria, and nothing but
          grey to tell them apart.</figcaption>""",
 """<figcaption><strong>Desactivada.</strong> Dos mares vecinos y nada más que
          gris para separarlos.</figcaption>"""),

("""alt="O mesmo recorte com a Lua Mineral ligada: o mar da esquerda
                    puxa para o laranja e o da direita para o azul, revelando a
                    fronteira entre dois solos de química diferente.\"""",
 """alt="The same crop with Mineral Moon on: the mare on the left pulls towards
                    orange and the one on the right towards blue, revealing the
                    boundary between two soils of different chemistry.\"""",
 """alt="El mismo recorte con la Luna Mineral activada: el mar de la izquierda
                    tira al naranja y el de la derecha al azul, revelando la
                    frontera entre dos suelos de química distinta.\""""),

("""<figcaption><strong>Ligada.</strong> O mesmo arquivo: um mar puxa para
          o laranja, o vizinho para o azul. A fronteira entre eles é química,
          não contraste.</figcaption>""",
 """<figcaption><strong>On.</strong> The same file: one mare pulls towards
          orange, its neighbour towards blue. The boundary between them is
          chemistry, not contrast.</figcaption>""",
 """<figcaption><strong>Activada.</strong> El mismo archivo: un mar tira al
          naranja y el vecino al azul. La frontera entre ambos es química, no
          contraste.</figcaption>"""),

("""Medido no disco, entre as duas saídas acima: a saturação média sobe de
      <span class="dado">1,31%</span> para <span class="dado">6,35%</span> —
      <span class="dado">4,9×</span>. O brilho não foi tocado.""",
 """Measured across the disc, between the two outputs above: mean saturation
      rises from <span class="dado">1.31%</span> to <span class="dado">6.35%</span>
      — <span class="dado">4.9×</span>. Brightness was not touched.""",
 """Medido en el disco, entre las dos salidas de arriba: la saturación media
      sube de <span class="dado">1,31%</span> a <span class="dado">6,35%</span> —
      <span class="dado">4,9×</span>. El brillo no se tocó."""),

("""alt="O mosaico lunar inteiro com a Lua Mineral ligada: os mares
                  aparecem em tons distintos de azul e castanho conforme o
                  mineral dominante.\"""",
 """alt="The whole lunar mosaic with Mineral Moon on: the maria show distinct
                  shades of blue and brown according to the dominant mineral.\"""",
 """alt="El mosaico lunar entero con la Luna Mineral activada: los mares
                  aparecen en tonos distintos de azul y marrón según el mineral
                  dominante.\""""),

("""O mesmo mosaico de <span class="dado">11</span> painéis da abertura
        desta página, com os ajustes acima aplicados.""",
 """The same <span class="dado">11</span>-panel mosaic from the top of this
        page, with the settings above applied.""",
 """El mismo mosaico de <span class="dado">11</span> paneles del inicio de esta
        página, con los ajustes de arriba aplicados."""),

# --- modos
("""<p class="rotulo">Quatro assuntos</p>
      <h2>Cada um com a sua geometria.</h2>""",
 """<p class="rotulo">Four subjects</p>
      <h2>Each with its own geometry.</h2>""",
 """<p class="rotulo">Cuatro temas</p>
      <h2>Cada uno con su geometría.</h2>"""),

("""<h3>Lua</h3>
        <p>Disco inteiro ou close-up. Reconhece o contorno do limbo ângulo a
          ângulo, em vez de recortar por uma elipse com folga.</p>""",
 """<h3>Moon</h3>
        <p>Whole disc or close-up. It traces the limb angle by angle instead of
          cropping to a loose ellipse.</p>""",
 """<h3>Luna</h3>
        <p>Disco entero o primer plano. Reconoce el contorno del limbo ángulo a
          ángulo, en vez de recortar con una elipse holgada.</p>"""),

("""<h3>Sol</h3>
        <p>Mesma geometria de disco da Lua, com o tratamento de borda que a
          granulação solar pede.</p>""",
 """<h3>Sun</h3>
        <p>The same disc geometry as the Moon, with the edge handling that solar
          granulation calls for.</p>""",
 """<h3>Sol</h3>
        <p>La misma geometría de disco que la Luna, con el tratamiento de borde
          que pide la granulación solar.</p>"""),

("""<h3>Céu profundo</h3>
        <p>Alinhamento por estrelas e equalização fotométrica entre painéis,
          para o fundo de céu não dar degrau.</p>""",
 """<h3>Deep sky</h3>
        <p>Star-based alignment and photometric equalisation between panels, so
          the sky background does not step.</p>""",
 """<h3>Cielo profundo</h3>
        <p>Alineación por estrellas y ecualización fotométrica entre paneles,
          para que el fondo de cielo no haga escalón.</p>"""),

("""<h3>Panorama</h3>
        <p>Paisagem terrestre, com projeção esférica ou plana conforme o
          fechamento de laço medido nos seus painéis.</p>""",
 """<h3>Panorama</h3>
        <p>Landscape on the ground, with spherical or planar projection according
          to the loop closure measured on your own panels.</p>""",
 """<h3>Panorámica</h3>
        <p>Paisaje terrestre, con proyección esférica o plana según el cierre de
          lazo medido en tus paneles.</p>"""),

# --- atualizacao
("""<p class="rotulo">Atualização mais recente</p>
      <h2>v0.56.2 — Redução do degrau no limbo da Lua</h2>""",
 """<p class="rotulo">Latest update</p>
      <h2>v0.56.2 — Less stepping on the Moon's limb</h2>""",
 """<p class="rotulo">Actualización más reciente</p>
      <h2>v0.56.2 — Reducción del escalón en el limbo de la Luna</h2>"""),

("""<p><strong>Degrau no limbo quase eliminado.</strong> Em mosaicos com muitos
          painéis, a borda do disco podia dar um salto bem na emenda entre
          dois deles.</p>""",
 """<p><strong>The step on the limb is nearly gone.</strong> In mosaics with many
          panels, the edge of the disc could jump right at the seam between two
          of them.</p>""",
 """<p><strong>El escalón del limbo casi desapareció.</strong> En mosaicos con
          muchos paneles, el borde del disco podía dar un salto justo en la unión
          entre dos de ellos.</p>"""),

("""<p class="medicao">No conjunto de teste, o salto caiu de
          <span class="dado">11,7</span> para <span class="dado">1,5</span> pixel.</p>""",
 """<p class="medicao">On the test set, the jump dropped from
          <span class="dado">11.7</span> to <span class="dado">1.5</span> pixels.</p>""",
 """<p class="medicao">En el conjunto de prueba, el salto bajó de
          <span class="dado">11,7</span> a <span class="dado">1,5</span> píxeles.</p>"""),

("""<p><strong>Mais disco aproveitado.</strong> Com os painéis caindo no
          lugar certo, o contorno da Lua é reconhecido na volta inteira em vez de
          em pedaços.</p>""",
 """<p><strong>More of the disc kept.</strong> With the panels landing in the
          right place, the Moon's outline is traced all the way round instead of
          in pieces.</p>""",
 """<p><strong>Más disco aprovechado.</strong> Con los paneles cayendo en el
          lugar correcto, el contorno de la Luna se reconoce en toda la vuelta en
          vez de a trozos.</p>"""),

("""<p class="medicao">Num mosaico de celular com 16 painéis, a cobertura da
          borda subiu de <span class="dado">47%</span> para
          <span class="dado">64%</span>.</p>""",
 """<p class="medicao">On a 16-panel phone mosaic, edge coverage rose from
          <span class="dado">47%</span> to <span class="dado">64%</span>.</p>""",
 """<p class="medicao">En un mosaico de móvil con 16 paneles, la cobertura del
          borde subió de <span class="dado">47%</span> a
          <span class="dado">64%</span>.</p>"""),

("""Ver o histórico completo""",
 """See the full history""",
 """Ver el historial completo"""),

# --- baixar
("""<p class="rotulo">Baixar</p>
      <h2>Escolha a sua plataforma.</h2>""",
 """<p class="rotulo">Download</p>
      <h2>Pick your platform.</h2>""",
 """<p class="rotulo">Descargar</p>
      <h2>Elige tu plataforma.</h2>"""),

("""<p class="cartao-preco">Grátis, sem instalador</p>""",
 """<p class="cartao-preco">Free, no installer</p>""",
 """<p class="cartao-preco">Gratis, sin instalador</p>"""),

("""Descompacte e abra. Compõe em resolução total, com saída em TIFF de
          16 bits para você continuar editando onde preferir.""",
 """Unzip it and open it. It composes at full resolution, with 16-bit TIFF
          output so you can carry on editing wherever you prefer.""",
 """Descomprime y abre. Compone a resolución total, con salida en TIFF de
          16 bits para que sigas editando donde prefieras."""),

("""<li><span>versão</span><span class="dado">0.56.2</span></li>
          <li><span>arquitetura</span><span class="dado">x64</span></li>
          <li><span>tamanho</span><span class="dado">36,6 MB</span></li>""",
 """<li><span>version</span><span class="dado">0.56.2</span></li>
          <li><span>architecture</span><span class="dado">x64</span></li>
          <li><span>size</span><span class="dado">36.6 MB</span></li>""",
 """<li><span>versión</span><span class="dado">0.56.2</span></li>
          <li><span>arquitectura</span><span class="dado">x64</span></li>
          <li><span>tamaño</span><span class="dado">36,6 MB</span></li>"""),

("""Baixar o .zip""",
 """Download the .zip""",
 """Descargar el .zip"""),

("""<p class="cartao-preco">Aplicativo pago, na Google Play</p>""",
 """<p class="cartao-preco">Paid app, on Google Play</p>""",
 """<p class="cartao-preco">Aplicación de pago, en Google Play</p>"""),

("""O mesmo motor de costura no celular ou no tablet, com as fotos
          processadas no próprio aparelho.""",
 """The same stitching engine on your phone or tablet, with the photos
          processed on the device itself.""",
 """El mismo motor de costura en el móvil o la tableta, con las fotos
          procesadas en el propio dispositivo."""),

("""<li><span>requer</span><span class="dado">Android 7.0</span></li>
          <li><span>atualização</span><span class="dado">pela loja</span></li>""",
 """<li><span>requires</span><span class="dado">Android 7.0</span></li>
          <li><span>updates</span><span class="dado">via the store</span></li>""",
 """<li><span>requiere</span><span class="dado">Android 7.0</span></li>
          <li><span>actualización</span><span class="dado">por la tienda</span></li>"""),

("""alt="Disponível no Google Play\"""",
 """alt="Get it on Google Play\"""",
 """alt="Disponible en Google Play\""""),

# --- apoio
("""<p class="rotulo">Apoie o projeto</p>
      <h2>A versão para Windows é gratuita.<br>Ela continua assim.</h2>""",
 """<p class="rotulo">Support the project</p>
      <h2>The Windows version is free.<br>It stays that way.</h2>""",
 """<p class="rotulo">Apoya el proyecto</p>
      <h2>La versión para Windows es gratuita.<br>Y seguirá siéndolo.</h2>"""),

("""Sem anúncio, sem conta, sem telemetria. Não há servidor para pagar: o
        app roda inteiro na sua máquina e as suas fotos não saem dela — por
        isso não existe plano, nem assinatura, nem nada para vender depois.""",
 """No ads, no account, no telemetry. There is no server to pay for: the app
        runs entirely on your machine and your photos never leave it — which is
        why there is no plan, no subscription and nothing to sell you later.""",
 """Sin anuncios, sin cuenta, sin telemetría. No hay servidor que pagar: la
        app funciona entera en tu máquina y tus fotos no salen de ella, y por eso
        no hay plan, ni suscripción, ni nada que venderte después."""),

("""O que custa é o tempo. Cada correção nas notas de versão só entra
        depois de medida em um conjunto de teste, e é a medição — não o
        código — que leva os dias. É assim que o <em>degrau no limbo</em> saiu
        de <span class="dado">11,7</span> para <span class="dado">1,5</span>
        pixel em vez de só <em>parecer</em> melhor.""",
 """What it costs is time. Every fix in the release notes only ships after
        being measured on a test set, and it is the measuring — not the code —
        that takes the days. That is how the <em>step on the limb</em> went from
        <span class="dado">11.7</span> to <span class="dado">1.5</span> pixels
        instead of merely <em>looking</em> better.""",
 """Lo que cuesta es el tiempo. Cada corrección de las notas de versión solo
        entra después de medirse en un conjunto de prueba, y es la medición —no el
        código— la que lleva los días. Así fue como el <em>escalón del limbo</em>
        pasó de <span class="dado">11,7</span> a <span class="dado">1,5</span>
        píxeles en lugar de solo <em>parecer</em> mejor."""),

("""Se o AstroStitch te poupou uma noite de trabalho, uma doação paga a
        próxima correção.""",
 """If AstroStitch saved you a night of work, a donation pays for the next
        fix.""",
 """Si AstroStitch te ahorró una noche de trabajo, una donación paga la
        próxima corrección."""),

("""<strong>Doar pelo PayPal</strong>
          <small>Você escolhe o valor · sem recorrência</small>""",
 """<strong>Donate with PayPal</strong>
          <small>You choose the amount · no recurring charge</small>""",
 """<strong>Donar con PayPal</strong>
          <small>Tú eliges el importe · sin recurrencia</small>"""),

# --- rodape
("""As suas fotos são processadas no seu aparelho e não são enviadas a
        lugar nenhum.""",
 """Your photos are processed on your own device and are not sent anywhere.""",
 """Tus fotos se procesan en tu propio dispositivo y no se envían a ninguna
        parte."""),

("""<nav class="rodape-links" aria-label="Rodapé">
      <a href="releases.html">Notas de versão</a>
      <a href="#apoiar">Apoiar o projeto</a>
      <a href="privacy-policy.html">Política de privacidade</a>
      <a href="privacy-policy.en.html">Privacy policy (EN)</a>
      <a href="third-party-sources/">Fontes de terceiros</a>""",
 """<nav class="rodape-links" aria-label="Footer">
      <a href="releases.html">Release notes</a>
      <a href="#apoiar">Support the project</a>
      <a href="privacy-policy.en.html">Privacy policy</a>
      <a href="privacy-policy.html">Política de privacidade (PT)</a>
      <a href="third-party-sources/">Third-party sources</a>""",
 """<nav class="rodape-links" aria-label="Pie de página">
      <a href="releases.html">Notas de versión</a>
      <a href="#apoiar">Apoyar el proyecto</a>
      <a href="privacy-policy.en.html">Privacy policy (EN)</a>
      <a href="privacy-policy.html">Política de privacidade (PT)</a>
      <a href="third-party-sources/">Fuentes de terceros</a>"""),
]


RELEASES = [
("""<title>Notas de versão — AstroStitch</title>""",
 """<title>Release notes — AstroStitch</title>""",
 """<title>Notas de versión — AstroStitch</title>"""),

("""<a class="pular" href="#conteudo">Pular para o conteúdo</a>""",
 """<a class="pular" href="#conteudo">Skip to content</a>""",
 """<a class="pular" href="#conteudo">Saltar al contenido</a>"""),

("""aria-label="AstroStitch — início\"""",
 """aria-label="AstroStitch — home\"""",
 """aria-label="AstroStitch — inicio\""""),

("""<nav class="navegacao" aria-label="Principal">
      <a href="releases.html" aria-current="page">Notas de versão</a>""",
 """<nav class="navegacao" aria-label="Main">
      <a href="releases.html" aria-current="page">Release notes</a>""",
 """<nav class="navegacao" aria-label="Principal">
      <a href="releases.html" aria-current="page">Notas de versión</a>"""),

("""<span class="nav-rotulo">Baixar</span>""",
 """<span class="nav-rotulo">Download</span>""",
 """<span class="nav-rotulo">Descargar</span>"""),

("""      Voltar ao início
    </a>
    <h1>Notas de versão</h1>""",
 """      Back to home
    </a>
    <h1>Release notes</h1>""",
 """      Volver al inicio
    </a>
    <h1>Notas de versión</h1>"""),

("""Cada correção aqui tem o efeito em uma frase e a medição que a fechou
      logo abaixo. O número vale para o conjunto de teste citado — não é uma
      promessa geral sobre qualquer imagem.""",
 """Every fix here states its effect in one sentence, with the measurement
      that closed it right below. The number holds for the test set named — it
      is not a general promise about any image.""",
 """Cada corrección aquí tiene su efecto en una frase y, justo debajo, la
      medición que la cerró. El número vale para el conjunto de prueba citado:
      no es una promesa general sobre cualquier imagen."""),

("""As versões para Windows ficam em
      <a href="https://github.com/AmaroMiranda/astro-stitch-releases/releases">releases do GitHub</a>.
      O aplicativo Android é atualizado pela""",
 """The Windows builds live on
      <a href="https://github.com/AmaroMiranda/astro-stitch-releases/releases">GitHub releases</a>.
      The Android app is updated through""",
 """Las versiones para Windows están en
      <a href="https://github.com/AmaroMiranda/astro-stitch-releases/releases">releases de GitHub</a>.
      La aplicación de Android se actualiza por"""),

# --- datas: o formato muda de idioma para idioma
("""<time class="versao-data" datetime="2026-10-06">06/10/2026</time>""",
 """<time class="versao-data" datetime="2026-10-06">6 Oct 2026</time>""",
 """<time class="versao-data" datetime="2026-10-06">06/10/2026</time>"""),
("""<time class="versao-data" datetime="2026-10-05">05/10/2026</time>""",
 """<time class="versao-data" datetime="2026-10-05">5 Oct 2026</time>""",
 """<time class="versao-data" datetime="2026-10-05">05/10/2026</time>"""),
("""<time class="versao-data" datetime="2026-10-04">04/10/2026</time>""",
 """<time class="versao-data" datetime="2026-10-04">4 Oct 2026</time>""",
 """<time class="versao-data" datetime="2026-10-04">04/10/2026</time>"""),

# --- 0.56.2
("""<h2>Redução do degrau no limbo da Lua</h2>

        <p><strong>A borda do disco quase não dá mais salto entre painéis.</strong>
          Em mosaicos com muitos painéis, o limbo descia, fazia um patamar e
          descia de novo, bem nas emendas da composição. A causa era um
          erro de geometria na passagem do alinhamento para a montagem: cada
          painel era colocado com um desvio proporcional à sua escala e à
          distância do centro, chegando a 10 pixels.</p>
        <p class="medicao">No conjunto de teste, o salto no limbo caiu de
          <span class="dado">11,7</span> para <span class="dado">1,5</span> pixel.</p>""",
 """<h2>Less stepping on the Moon's limb</h2>

        <p><strong>The edge of the disc barely jumps between panels now.</strong>
          In mosaics with many panels the limb would drop, flatten out and drop
          again, right at the seams of the composition. The cause was a geometry
          error on the way from alignment into assembly: each panel was placed
          with an offset proportional to its scale and to its distance from the
          centre, reaching 10 pixels.</p>
        <p class="medicao">On the test set, the jump at the limb fell from
          <span class="dado">11.7</span> to <span class="dado">1.5</span> pixels.</p>""",
 """<h2>Reducción del escalón en el limbo de la Luna</h2>

        <p><strong>El borde del disco ya casi no salta entre paneles.</strong>
          En mosaicos con muchos paneles el limbo bajaba, hacía un escalón y
          volvía a bajar, justo en las uniones de la composición. La causa era un
          error de geometría al pasar de la alineación al montaje: cada panel se
          colocaba con una desviación proporcional a su escala y a su distancia
          del centro, llegando a 10 píxeles.</p>
        <p class="medicao">En el conjunto de prueba, el salto en el limbo bajó de
          <span class="dado">11,7</span> a <span class="dado">1,5</span> píxeles.</p>"""),

("""<p><strong>Mais disco aproveitado.</strong> Com os painéis caindo no
          lugar certo, o contorno da Lua passou a ser reconhecido na volta
          inteira em vez de em pedaços.</p>
        <p class="medicao">Num mosaico de celular com 16 painéis, a cobertura da
          borda subiu de <span class="dado">47%</span> para
          <span class="dado">64%</span>, e o disco saiu
          <span class="dado">2,4%</span> maior — sem mudar a escala da imagem.</p>

        <p>A correção vale para Lua e Sol, e não altera panorama nem céu profundo.</p>""",
 """<p><strong>More of the disc kept.</strong> With the panels landing in the
          right place, the Moon's outline is now traced all the way round instead
          of in pieces.</p>
        <p class="medicao">On a 16-panel phone mosaic, edge coverage rose from
          <span class="dado">47%</span> to <span class="dado">64%</span>, and the
          disc came out <span class="dado">2.4%</span> larger — without changing
          the scale of the image.</p>

        <p>The fix applies to Moon and Sun, and changes neither panorama nor deep
          sky.</p>""",
 """<p><strong>Más disco aprovechado.</strong> Con los paneles cayendo en el
          lugar correcto, el contorno de la Luna pasó a reconocerse en toda la
          vuelta en vez de a trozos.</p>
        <p class="medicao">En un mosaico de móvil con 16 paneles, la cobertura
          del borde subió de <span class="dado">47%</span> a
          <span class="dado">64%</span>, y el disco salió un
          <span class="dado">2,4%</span> mayor, sin cambiar la escala de la
          imagen.</p>

        <p>La corrección vale para Luna y Sol, y no altera panorámica ni cielo
          profundo.</p>"""),

# --- 0.56.1
("""<h2>A faixa em volta da Lua acabou</h2>

        <p><strong>Quem compôs um mosaico de Lua cheia via uma faixa clara em
          volta do disco</strong>, com uma borda nítida contra o fundo.</p>

        <p>O diagnóstico mudou o entendimento do problema: <strong>a faixa não
          era dado inventado pelo app.</strong> O perfil do limbo foi medido em
          três pontos — no arquivo que sai do stacker, no painel já alinhado e
          tratado, e no mosaico final.</p>""",
 """<h2>The halo around the Moon is gone</h2>

        <p><strong>Anyone composing a full Moon mosaic used to see a bright band
          around the disc</strong>, with a sharp edge against the background.</p>

        <p>The diagnosis changed what the problem even was: <strong>the band was
          not data invented by the app.</strong> The limb profile was measured at
          three points — in the file coming out of the stacker, in the panel once
          aligned and processed, and in the final mosaic.</p>""",
 """<h2>Se acabó la franja alrededor de la Luna</h2>

        <p><strong>Quien componía un mosaico de Luna llena veía una franja clara
          alrededor del disco</strong>, con un borde nítido contra el fondo.</p>

        <p>El diagnóstico cambió la comprensión del problema: <strong>la franja
          no era un dato inventado por la app.</strong> El perfil del limbo se
          midió en tres puntos: en el archivo que sale del stacker, en el panel ya
          alineado y tratado, y en el mosaico final.</p>"""),

("""aria-label="Brilho a cada distância da borda">
          <table>
            <caption class="rotulo">Brilho a cada distância da borda</caption>
            <thead>
              <tr><th>distância</th><th>entrada</th><th>após alinhar</th><th>mosaico (antes)</th></tr>""",
 """aria-label="Brightness at each distance from the edge">
          <table>
            <caption class="rotulo">Brightness at each distance from the edge</caption>
            <thead>
              <tr><th>distance</th><th>input</th><th>after aligning</th><th>mosaic (before)</th></tr>""",
 """aria-label="Brillo a cada distancia del borde">
          <table>
            <caption class="rotulo">Brillo a cada distancia del borde</caption>
            <thead>
              <tr><th>distancia</th><th>entrada</th><th>tras alinear</th><th>mosaico (antes)</th></tr>"""),

("""              <tr><td>+10 px</td><td>33,20</td><td>31,84</td><td>31,42</td></tr>
              <tr><td>+20 px</td><td>25,62</td><td>24,92</td><td>24,50</td></tr>
              <tr><td>+30 px</td><td>19,87</td><td>19,84</td><td>0,19</td></tr>
              <tr><td>+80 px</td><td>14,06</td><td>14,22</td><td>0,00</td></tr>""",
 """              <tr><td>+10 px</td><td>33.20</td><td>31.84</td><td>31.42</td></tr>
              <tr><td>+20 px</td><td>25.62</td><td>24.92</td><td>24.50</td></tr>
              <tr><td>+30 px</td><td>19.87</td><td>19.84</td><td>0.19</td></tr>
              <tr><td>+80 px</td><td>14.06</td><td>14.22</td><td>0.00</td></tr>""",
 """              <tr><td>+10 px</td><td>33,20</td><td>31,84</td><td>31,42</td></tr>
              <tr><td>+20 px</td><td>25,62</td><td>24,92</td><td>24,50</td></tr>
              <tr><td>+30 px</td><td>19,87</td><td>19,84</td><td>0,19</td></tr>
              <tr><td>+80 px</td><td>14,06</td><td>14,22</td><td>0,00</td></tr>"""),

("""<p>A luz em volta do disco está no arquivo que <strong>entra</strong> —
          é o halo da própria captura, 27 sigmas acima do ruído do céu. O app a
          reproduzia fielmente até +20 px e então <strong>cortava</strong>: 24
          níveis em 10 px, onde a captura continuaria caindo suavemente por mais
          100 px. O aro se via porque tinha <strong>borda</strong>, não porque
          tinha luz.</p>

        <p><strong>O que mudou:</strong> o corte morre por rampa, ao longo de 5%
          do raio do disco.</p>""",
 """<p>The light around the disc is in the file that goes <strong>in</strong> —
          it is the halo of the capture itself, 27 sigma above the sky noise. The
          app reproduced it faithfully up to +20 px and then <strong>cut</strong>:
          24 levels in 10 px, where the capture would have gone on falling gently
          for another 100 px. The ring was visible because it had an
          <strong>edge</strong>, not because it had light.</p>

        <p><strong>What changed:</strong> the cut now dies off as a ramp, over 5%
          of the disc radius.</p>""",
 """<p>La luz alrededor del disco está en el archivo que <strong>entra</strong>:
          es el halo de la propia captura, 27 sigmas por encima del ruido del
          cielo. La app lo reproducía fielmente hasta +20 px y entonces
          <strong>cortaba</strong>: 24 niveles en 10 px, donde la captura habría
          seguido cayendo suavemente otros 100 px. El aro se veía porque tenía
          <strong>borde</strong>, no porque tuviera luz.</p>

        <p><strong>Qué cambió:</strong> el corte muere en rampa, a lo largo del 5%
          del radio del disco.</p>"""),

("""aria-label="Réguas antes e depois da correção">
          <table>
            <thead>
              <tr><th>régua</th><th>antes</th><th>agora</th></tr>
            </thead>
            <tbody>
              <tr><td>degrau na borda (de 255)</td><td>9,63</td><td>0,75</td></tr>
              <tr><td>quanto do contorno tem ele</td><td>100%</td><td>0,0%</td></tr>
              <tr><td>visibilidade do aro</td><td>1,6</td><td>0,1</td></tr>
              <tr><td>pixels que escureceram</td><td>—</td><td>0</td></tr>""",
 """aria-label="Yardsticks before and after the fix">
          <table>
            <thead>
              <tr><th>yardstick</th><th>before</th><th>now</th></tr>
            </thead>
            <tbody>
              <tr><td>step at the edge (of 255)</td><td>9.63</td><td>0.75</td></tr>
              <tr><td>how much of the outline has it</td><td>100%</td><td>0.0%</td></tr>
              <tr><td>visibility of the ring</td><td>1.6</td><td>0.1</td></tr>
              <tr><td>pixels that got darker</td><td>—</td><td>0</td></tr>""",
 """aria-label="Reglas antes y después de la corrección">
          <table>
            <thead>
              <tr><th>regla</th><th>antes</th><th>ahora</th></tr>
            </thead>
            <tbody>
              <tr><td>escalón en el borde (de 255)</td><td>9,63</td><td>0,75</td></tr>
              <tr><td>cuánto del contorno lo tiene</td><td>100%</td><td>0,0%</td></tr>
              <tr><td>visibilidad del aro</td><td>1,6</td><td>0,1</td></tr>
              <tr><td>píxeles que se oscurecieron</td><td>—</td><td>0</td></tr>"""),

("""<p>Nenhum pixel ficou mais escuro do que a versão anterior entregava.
          Nada foi removido da sua imagem.</p>""",
 """<p>No pixel came out darker than the previous version delivered. Nothing
          was removed from your image.</p>""",
 """<p>Ningún píxel quedó más oscuro de lo que entregaba la versión anterior.
          No se quitó nada de tu imagen.</p>"""),

# --- 0.56.0
("""<h2>O recorte do disco passou a seguir o limbo medido</h2>

        <p><strong>Lua cheia.</strong> O recorte do disco deixou de ser feito por
          uma elipse com folga e passou a seguir o <strong>contorno do limbo
          medido</strong>, ângulo a ângulo — 1440 deles.</p>
        <p class="medicao">No conjunto de teste: a faixa cai de
          <span class="dado">0,112R</span> presente em
          <span class="dado">100%</span> dos ângulos para <strong>zero</strong>;
          a gradação do limbo até o preto cai de <span class="dado">297</span>
          para <span class="dado">28</span> px; e nenhum pixel do disco é
          perdido.</p>

        <p>A elipse nunca poderia resolver isso: o limbo varia cerca de ±10 px
          entre ângulos, e uma elipse é uma só — qualquer folga larga o bastante
          para não morder o disco num ponto deixa faixa em todos os outros.</p>""",
 """<h2>Disc cropping now follows the measured limb</h2>

        <p><strong>Full Moon.</strong> The disc is no longer cropped by a loose
          ellipse; it now follows the <strong>measured outline of the limb</strong>,
          angle by angle — 1440 of them.</p>
        <p class="medicao">On the test set: the band falls from
          <span class="dado">0.112R</span> present at
          <span class="dado">100%</span> of angles to <strong>zero</strong>; the
          gradient from limb to black falls from <span class="dado">297</span> to
          <span class="dado">28</span> px; and not one pixel of the disc is
          lost.</p>

        <p>An ellipse could never have fixed this: the limb varies by about ±10 px
          between angles, and an ellipse is a single curve — any margin wide enough
          not to bite into the disc at one point leaves a band at every other.</p>""",
 """<h2>El recorte del disco pasó a seguir el limbo medido</h2>

        <p><strong>Luna llena.</strong> El recorte del disco dejó de hacerse con
          una elipse holgada y pasó a seguir el <strong>contorno del limbo
          medido</strong>, ángulo a ángulo: 1440 de ellos.</p>
        <p class="medicao">En el conjunto de prueba: la franja cae de
          <span class="dado">0,112R</span> presente en el
          <span class="dado">100%</span> de los ángulos a <strong>cero</strong>;
          la gradación del limbo hasta el negro cae de <span class="dado">297</span>
          a <span class="dado">28</span> px; y no se pierde ni un píxel del
          disco.</p>

        <p>La elipse nunca podría resolverlo: el limbo varía unos ±10 px entre
          ángulos, y una elipse es una sola; cualquier holgura ancha para no morder
          el disco en un punto deja franja en todos los demás.</p>"""),

("""<p><strong>Fases parciais (Lua gibosa, crescente).</strong> O céu
          observado de cada painel passou a ser preservado, e a faixa artificial
          desapareceu. O fundo só fica preto com a opção “Fundo preto” ligada.</p>

        <p class="medicao"><strong>Observação honesta:</strong> em resolução
          reduzida a faixa diminui muito, mas não chega a zero. A descrição
          correta é <em>redução</em> da faixa — zerada na resolução total,
          residual nas escalas menores.</p>

        <p><strong>Também nesta versão:</strong> a barra de progresso da análise
          deixou de ficar parada e saltar para o fim — agora mostra o avanço
          real, em quatro etapas.</p>""",
 """<p><strong>Partial phases (gibbous, crescent).</strong> The observed sky of
          each panel is now preserved, and the artificial band is gone. The
          background only turns black with the “Black background” option on.</p>

        <p class="medicao"><strong>An honest note:</strong> at reduced resolution
          the band shrinks a great deal but does not reach zero. The correct
          description is <em>reduction</em> of the band — zero at full resolution,
          residual at smaller scales.</p>

        <p><strong>Also in this version:</strong> the analysis progress bar no
          longer sits still and then jumps to the end — it now shows real progress,
          in four stages.</p>""",
 """<p><strong>Fases parciales (Luna gibosa, creciente).</strong> El cielo
          observado de cada panel pasó a conservarse y la franja artificial
          desapareció. El fondo solo queda negro con la opción «Fondo negro»
          activada.</p>

        <p class="medicao"><strong>Nota honesta:</strong> en resolución reducida la
          franja disminuye mucho, pero no llega a cero. La descripción correcta es
          <em>reducción</em> de la franja: nula a resolución total, residual en las
          escalas menores.</p>

        <p><strong>También en esta versión:</strong> la barra de progreso del
          análisis dejó de quedarse quieta y saltar al final; ahora muestra el
          avance real, en cuatro etapas.</p>"""),

# --- botoes de download por versao e rodape
("""Baixar v0.56.2 para Windows""",
 """Download v0.56.2 for Windows""",
 """Descargar v0.56.2 para Windows"""),
("""Baixar v0.56.1 para Windows""",
 """Download v0.56.1 for Windows""",
 """Descargar v0.56.1 para Windows"""),
("""Baixar v0.56.0 para Windows""",
 """Download v0.56.0 for Windows""",
 """Descargar v0.56.0 para Windows"""),

("""<span class="versao-tag">anteriores</span>""",
 """<span class="versao-tag">earlier</span>""",
 """<span class="versao-tag">anteriores</span>"""),

("""O histórico das versões mais antigas, com os arquivos de cada uma,
          fica na aba de releases do repositório.""",
 """The history of older versions, with the files for each one, lives on the
          releases tab of the repository.""",
 """El historial de las versiones más antiguas, con los archivos de cada una,
          está en la pestaña de releases del repositorio."""),

("""Ver todas as versões no GitHub""",
 """See every version on GitHub""",
 """Ver todas las versiones en GitHub"""),

("""As suas fotos são processadas no seu aparelho e não são enviadas a
        lugar nenhum.""",
 """Your photos are processed on your own device and are not sent anywhere.""",
 """Tus fotos se procesan en tu propio dispositivo y no se envían a ninguna
        parte."""),

("""<nav class="rodape-links" aria-label="Rodapé">
      <a href="./">Início</a>""",
 """<nav class="rodape-links" aria-label="Footer">
      <a href="./">Home</a>""",
 """<nav class="rodape-links" aria-label="Pie de página">
      <a href="./">Inicio</a>"""),

(""">Baixar para Windows</a>""",
 """>Download for Windows</a>""",
 """>Descargar para Windows</a>"""),

("""<a href="privacy-policy.html">Política de privacidade</a>
      <a href="privacy-policy.en.html">Privacy policy (EN)</a>
      <a href="third-party-sources/">Fontes de terceiros</a>""",
 """<a href="privacy-policy.en.html">Privacy policy</a>
      <a href="privacy-policy.html">Política de privacidade (PT)</a>
      <a href="third-party-sources/">Third-party sources</a>""",
 """<a href="privacy-policy.en.html">Privacy policy (EN)</a>
      <a href="privacy-policy.html">Política de privacidade (PT)</a>
      <a href="third-party-sources/">Fuentes de terceros</a>"""),
]


# --------------------------------------------------------------------------

SELETOR = {
    'pt': ('PT', 'pt-BR'),
    'en': ('EN', 'en'),
    'es': ('ES', 'es'),
}


def seletor_html(idioma_atual, pagina):
    """Os tres links de idioma, com o atual marcado para leitor de tela."""
    linhas = []
    for cod, (rotulo, hreflang) in SELETOR.items():
        if cod == 'pt':
            destino = ('../' + pagina) if idioma_atual != 'pt' else pagina
        elif idioma_atual == cod:
            destino = pagina
        elif idioma_atual == 'pt':
            destino = '%s/%s' % (cod, pagina)
        else:
            destino = '../%s/%s' % (cod, pagina)
        if destino.endswith('index.html'):
            destino = destino[:-len('index.html')] or './'
        atual = ' aria-current="true"' if cod == idioma_atual else ''
        linhas.append('      <a href="%s" hreflang="%s" lang="%s"%s>%s</a>'
                      % (destino, hreflang, hreflang, atual, rotulo))
    return ('    <div class="idiomas" role="group" aria-label="Idioma / Language">\n'
            + '\n'.join(linhas) + '\n    </div>')


def alternates(pagina):
    """hreflang: diz ao buscador que as tres paginas sao a mesma coisa."""
    p = '' if pagina == 'index.html' else pagina
    return '\n'.join([
        '<link rel="alternate" hreflang="pt-BR" href="%s/%s">' % (SITE, p),
        '<link rel="alternate" hreflang="en" href="%s/en/%s">' % (SITE, p),
        '<link rel="alternate" hreflang="es" href="%s/es/%s">' % (SITE, p),
        '<link rel="alternate" hreflang="x-default" href="%s/%s">' % (SITE, p),
    ])


def limpa(s):
    """Tira o que o proprio gerador pos da ultima vez.

    O portugues e FONTE e SAIDA ao mesmo tempo: o arquivo da raiz e lido,
    recebe o seletor de idioma e e gravado por cima de si. Sem esta limpeza,
    rodar o gerador duas vezes empilharia dois seletores e dois conjuntos de
    hreflang — e ninguem perceberia ate alguem abrir o HTML.
    """
    s = re.sub(r'\n?<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
    s = re.sub(r'[ \t]*<div class="idiomas".*?</div>\n', '', s, flags=re.S)
    return s


def gera(arquivo, tabela, idioma, col):
    s = limpa(io.open(os.path.join(RAIZ, arquivo), encoding='utf-8').read())

    for trio in tabela:
        pt = trio[0]
        if pt not in s:
            raise SystemExit('NAO CASOU em %s (%s):\n%s' % (arquivo, idioma, pt[:90]))
        if s.count(pt) != 1:
            raise SystemExit('CASOU %d VEZES em %s:\n%s' % (s.count(pt), arquivo, pt[:90]))
        s = s.replace(pt, trio[col])

    # idioma do documento
    s = s.replace('<html lang="pt-BR">', '<html lang="%s">' % SELETOR[idioma][1], 1)

    # canonical aponta para a propria pagina, e as alternates ficam ao lado
    p = '' if arquivo == 'index.html' else arquivo
    if idioma == 'pt':
        canon = '%s/%s' % (SITE, p)
    else:
        canon = '%s/%s/%s' % (SITE, idioma, p)
    s = re.sub(r'<link rel="canonical" href="[^"]*">',
               '<link rel="canonical" href="%s">\n%s' % (canon, alternates(arquivo)), s, count=1)

    # nas subpastas, tudo que mora na raiz sobe um nivel
    if idioma != 'pt':
        for atrib in ('src="', 'href="', 'srcset="'):
            s = s.replace(atrib + 'assets/', atrib + '../assets/')
        s = s.replace('href="privacy-policy', 'href="../privacy-policy')
        s = s.replace('href="third-party-sources/', 'href="../third-party-sources/')

    # seletor de idioma, dentro da barra de navegacao
    s = s.replace('  </div>\n</header>',
                  seletor_html(idioma, arquivo) + '\n  </div>\n</header>', 1)

    destino = os.path.join(RAIZ, arquivo) if idioma == 'pt' \
        else os.path.join(RAIZ, idioma, arquivo)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    io.open(destino, 'w', encoding='utf-8', newline='').write(s)
    return destino, s


# --------------------------------------------------------------------------
# Varredura: qualquer bloco esquecido fica em portugues, e portugues tem
# marcas que ingles e espanhol nao tem. Melhor um alarme falso do que um
# paragrafo em portugues num site em ingles.
# --------------------------------------------------------------------------

# Marcas que o portugues tem e o idioma de destino NAO tem. Sao listas
# diferentes por idioma de proposito: "esta" e "pela" sao portugues suspeito
# dentro de um texto em ingles, e espanhol legitimo dentro de um em espanhol.
MARCAS = {
    'en': {
        'trechos': ['ção', 'ções', 'ão', 'ões', 'ã', 'õ', 'lh', 'nh', 'ç'],
        'palavras': ['você', 'não', 'são', 'está', 'pela', 'pelo', 'dos seus',
                     'mesmo mosaico', 'arquivo que', 'versão'],
    },
    'es': {
        # o espanhol compartilha quase tudo com o portugues: so os sinais que
        # NAO existem em espanhol servem de alarme.
        'trechos': ['ção', 'ções', 'ões', 'ã', 'õ', 'nh', 'ç', 'lh'],
        'palavras': ['você', 'não', 'são', 'arquivo', 'versão', 'muito mais'],
    },
}

# Texto que e portugues DE PROPOSITO, ou nome proprio: nao e alarme.
PERMITIDO = ['Política de privacidade', 'AstroStitch', 'português', 'pt-BR',
             'Apoio ao AstroStitch']


def varre(texto, idioma, arquivo):
    """Devolve as linhas que ainda cheiram a portugues."""
    if idioma == 'pt':
        return []
    sem_tag = re.sub(r'<(script|style)\b.*?</\1>', '', texto, flags=re.S)
    sem_tag = re.sub(r'<!--.*?-->', '', sem_tag, flags=re.S)
    marcas = MARCAS[idioma]
    suspeitas = []
    for n, linha in enumerate(sem_tag.splitlines(), 1):
        # ATENCAO: uma tag pode se espalhar por varias linhas, e entao a
        # linha solta nao tem o '>' que fecharia. Por isso os atributos saem
        # primeiro, um a um — senao o nome de um arquivo .webp entra como se
        # fosse texto visivel e vira alarme falso.
        legiveis = re.findall(r'(?:alt|content|aria-label|caption)="([^"]*)"', linha)
        sem_attr = re.sub(r'[\w:-]+="[^"]*"', ' ', linha)
        visivel = ' '.join(re.split(r'<[^>]*>?', sem_attr)) + ' ' + ' '.join(legiveis)
        if not visivel.strip():
            continue
        if any(p in visivel for p in PERMITIDO):
            continue
        baixo = visivel.lower()
        achou = ([m for m in marcas['palavras'] if m in baixo]
                 + [m for m in marcas['trechos'] if m in baixo])
        if achou:
            suspeitas.append('  %s:%d  %s  <- %s' % (arquivo, n, visivel.strip()[:88], achou[:3]))
    return suspeitas


def main():
    total = 0
    alarmes = []
    # o portugues entra na lista para ganhar o seletor e os hreflang: ele e
    # fonte e saida ao mesmo tempo, e `limpa` garante que isso seja seguro.
    for idioma, col in (('pt', 0), ('en', 1), ('es', 2)):
        for arquivo, tabela in (('index.html', INDEX), ('releases.html', RELEASES)):
            destino, texto = gera(arquivo, tabela, idioma, col)
            total += 1
            print('gerado  %s' % os.path.relpath(destino, RAIZ).replace('\\', '/'))
            alarmes += varre(texto, idioma, os.path.relpath(destino, RAIZ).replace('\\', '/'))
    print('\n%d paginas geradas.' % total)
    if alarmes:
        print('\nAINDA EM PORTUGUES (%d linhas):' % len(alarmes))
        for a in alarmes:
            print(a)
        sys.exit(1)
    print('varredura limpa: nenhum portugues sobrou.')


if __name__ == '__main__':
    main()
