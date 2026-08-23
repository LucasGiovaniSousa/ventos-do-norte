# -*- coding: utf-8 -*-
"""Catálogo da Ventos do Norte — fonte única de verdade.

Daqui saem o CSV de importação e a publicação pela Admin API. Um produto
define-se uma vez; se o preço ou a descrição mudarem, mudam aqui e os dois
destinos ficam iguais. É a regra do _PADRAO-LOJA: «o preço vive na folha e no
CSV; o site é destino, não fonte».

AS DESCRIÇÕES
Escritas de raiz, não copiadas do fornecedor — texto duplicado entre
revendedores não posiciona ninguém, e o do fornecedor vem em português do
Brasil. Cada uma segue a mesma espinha:

  1. O que é, numa frase directa.
  2. Como se comporta — a informação prática que decide a compra.
  3. Para quem é / quando se usa.
  4. Ficha técnica em negrito.
  5. Uma nota de uso ou cuidado.

Português europeu. Atenção ao vocabulário que entra pelas fichas brasileiras:
«tela» → «ecrã», «time» → «equipa», «pneu» → igual, «grama» → «relva».
"""

# ─────────────────────────────────────────────────────────────────────────
# Cada produto: handle, título, categoria, etiquetas, descrição, variantes.
# Variantes: (valor da opção, preço, preço de comparação, stock, sufixo SKU)
# ─────────────────────────────────────────────────────────────────────────

CATALOGO = [
  dict(
    handle="pipa-estrelas-rosa",
    titulo="Pipa Estrelas Rosa",
    marca="Ventos do Norte",
    tipo="Pipas",
    etiquetas=["Pipas", "Iniciante", "Papel de seda"],
    opcao="Tamanho",
    variantes=[("Média — 60 cm", "6.90", "", 24, "60"),
               ("Grande — 75 cm", "8.90", "", 18, "75")],
    sku="VDN-PIPA-EST", gramas=90,
    linha_tecnica="Papel de seda · vento fraco",
    imagens=["pipa-estrelas-rosa-recorte.jpg"],
    alt="Pipa de papel de seda com estampa de estrelas rosa, fundo branco",
    seo_titulo="Pipa Estrelas Rosa em papel de seda | Ventos do Norte",
    seo_desc="Pipa artesanal de papel de seda, leve e fácil de subir. Sobe com vento fraco. Envio de Portugal em 24–48h.",
    descricao=[
      "Pipa artesanal em papel de seda, com estampa de estrelas em degradê rosa e estrutura de vara de bambu.",
      "É das que sobem com pouco vento. O papel de seda é leve o suficiente para levantar com uma brisa que mal se sente na cara, e a estrutura em cruz mantém-na estável sem exigir correcções constantes na linha. Perdoa os erros de quem está a aprender: se mergulhar, tende a recuperar sozinha assim que a linha alivia.",
      "É a pipa certa para a primeira tarde, para levar com crianças, ou para quem quer simplesmente pôr uma coisa no ar e ficar a olhar. Em vento forte não é a melhor escolha — o papel de seda rasga, e aí compensa a laminada.",
      "<strong>Material:</strong> papel de seda e vara de bambu<br><strong>Vento ideal:</strong> fraco a moderado, 5 a 15 km/h<br><strong>Tamanhos:</strong> 60 cm e 75 cm de envergadura",
      "Vem com a linha de armação já montada. A linha de voo e a rabiola vendem-se à parte — e a rabiola faz diferença assim que o vento fica irregular.",
    ],
  ),

  dict(
    handle="pipa-caveira-neon",
    titulo="Pipa Caveira Neon",
    marca="Ventos do Norte",
    tipo="Pipas",
    etiquetas=["Pipas", "Intermédio", "Papel de seda"],
    opcao="Tamanho",
    variantes=[("Média — 60 cm", "7.90", "", 20, "60"),
               ("Grande — 75 cm", "9.90", "", 14, "75")],
    sku="VDN-PIPA-CAV", gramas=95,
    linha_tecnica="Papel de seda · bordas reforçadas",
    imagens=["pipa-caveira-neon.jpg"],
    alt="Pipa de papel de seda com caveira encapuzada em rosa neon, fundo branco",
    seo_titulo="Pipa Caveira Neon com bordas reforçadas | Ventos do Norte",
    seo_desc="Pipa de papel de seda com caveira neon e bordas reforçadas. Resposta rápida em vento moderado.",
    descricao=[
      "Pipa de papel de seda com caveira encapuzada em rosa neon sobre fundo escuro, e as bordas reforçadas com fita adesiva em toda a volta.",
      "A fita nas bordas muda o comportamento: a pipa fica mais rígida, responde ao puxão quase de imediato e vira num espaço curto. Em contrapartida exige mão — se se puxar a linha com força em vento forte, ela sobe depressa e sai da posição. É uma pipa que se pilota, não uma que se larga.",
      "Para quem já domina o básico e quer começar a fazer curvas de propósito, em vez de as apanhar por acidente. Também é a que aguenta mais tardes: o reforço das bordas é onde uma pipa de papel costuma ceder primeiro.",
      "<strong>Material:</strong> papel de seda e vara de bambu<br><strong>Reforço:</strong> fita em todo o perímetro<br><strong>Vento ideal:</strong> moderado, 12 a 25 km/h",
      "As bordas reforçadas aumentam a durabilidade, mas nenhuma pipa de papel gosta de chuva. Se apanhar humidade, deixa secar aberta antes de guardar.",
    ],
  ),

  dict(
    handle="pipa-ilustrada",
    titulo="Pipa Ilustrada",
    marca="Ventos do Norte",
    tipo="Pipas",
    etiquetas=["Pipas", "Crianças", "Laminada"],
    opcao="Cor",
    variantes=[("Multicolor", "5.90", "", 30, "MUL"),
               ("Azul", "5.90", "", 22, "AZU"),
               ("Rosa", "5.90", "", 22, "ROS")],
    sku="VDN-PIPA-ILU", gramas=80,
    linha_tecnica="Plástico laminado · estampa sortida",
    imagens=["pipa-personagem-gato.jpg", "pipa-personagem-heroi.jpg",
             "pipa-personagem-palhaco.jpg", "pipa-personagem-amarelos.jpg"],
    alt="Pipa ilustrada em plástico laminado, fundo branco",
    seo_titulo="Pipa Ilustrada em plástico laminado | Ventos do Norte",
    seo_desc="Pipa colorida em plástico laminado, resistente à humidade. Estampa sortida. Ideal para os mais novos.",
    descricao=[
      "Pipa em plástico laminado com estampa colorida de página inteira e estrutura de bambu.",
      "O laminado é o que a distingue: não rasga com a mesma facilidade do papel e não se estraga se apanhar humidade ou cair na areia molhada. Voa um pouco mais pesada do que uma de papel de seda, o que na prática significa que precisa de um pouco mais de vento para levantar — mas aguenta muito melhor uma tarde de praia.",
      "É a escolha para os mais novos e para quem vai levar a pipa para sítios onde ela vai apanhar. Também é a mais barata do catálogo, o que ajuda quando se leva mais do que uma.",
      "<strong>Material:</strong> plástico laminado e vara de bambu<br><strong>Vento ideal:</strong> fraco a moderado, 8 a 20 km/h<br><strong>Resistência:</strong> à humidade e à areia",
      "A estampa é sortida dentro da cor escolhida — cada envio pode trazer um desenho diferente. A estrutura e o desempenho são iguais em todas.",
    ],
  ),

  dict(
    handle="linha-encerada",
    titulo="Linha Encerada para Pipa",
    marca="Ventos do Norte",
    tipo="Linhas",
    etiquetas=["Linhas", "Encerada", "Acessórios"],
    opcao="Comprimento",
    variantes=[("250 m", "6.50", "", 40, "250"),
               ("500 m", "10.90", "", 30, "500"),
               ("1000 m", "18.90", "", 18, "1000")],
    sku="VDN-LINHA-ENC", gramas=200,
    linha_tecnica="Algodão encerado · baixo atrito",
    imagens=[],
    alt="Rolo de linha encerada para pipa, fundo branco",
    seo_titulo="Linha Encerada para Pipa — 250 a 1000 m | Ventos do Norte",
    seo_desc="Linha de algodão encerado, baixo atrito e resistente. Em 250, 500 e 1000 metros. Envio de Portugal em 24–48h.",
    descricao=[
      "Linha de voo em algodão encerado, o fio que liga a mão à pipa.",
      "A cera faz duas coisas. Reduz o atrito, e por isso a linha corre solta no carretel em vez de prender e dar solavancos — o que se nota logo na primeira soltada. E sela as fibras do algodão, o que impede que a linha desfie quando roça na aresta de um telhado ou num ramo. Ao contrário do nylon, tem pouca elasticidade: o que a pipa faz sente-se na mão quase sem atraso.",
      "Não confundir com a linha de armação, que já vem montada na pipa e serve só para lhe dar forma. Esta é a que se compra à parte e se enrola no carretel.",
      "<strong>Material:</strong> algodão encerado<br><strong>Comprimentos:</strong> 250, 500 e 1000 metros<br><strong>Elasticidade:</strong> baixa — resposta directa",
      "<strong>Não vendemos linha com cerol.</strong> Linha com vidro moído corta pessoas em motos e bicicletas, mata todos os anos no Brasil e é crime. Aqui não entra, em tamanho nenhum.",
    ],
  ),

  dict(
    handle="carretel-madeira",
    titulo="Carretel de Madeira Estampado",
    marca="Ventos do Norte",
    tipo="Carretéis",
    etiquetas=["Carretéis", "Madeira", "Acessórios"],
    opcao="Tamanho",
    variantes=[("Pequeno — 18 cm", "14.90", "", 16, "18"),
               ("Grande — 24 cm", "19.90", "", 10, "24")],
    sku="VDN-CARR-MAD", gramas=380,
    linha_tecnica="Madeira compensada · até 500 m",
    imagens=[],
    alt="Carretel de madeira estampado para linha de pipa, fundo branco",
    seo_titulo="Carretel de Madeira Estampado para Pipa | Ventos do Norte",
    seo_desc="Carretel de madeira com furos de alívio e estampa pintada à mão. Comporta até 500 m de linha.",
    descricao=[
      "Carretel em madeira compensada, com furos de alívio nas faces e estampa pintada à mão, uma a uma.",
      "Numa tarde inteira é o carretel que faz a diferença, não a pipa. Um que rode solto poupa o pulso e evita o pior problema de todos: a linha a prender a meio de uma soltada, com a pipa a puxar do outro lado. Os furos não são decoração — tiram peso e deixam a mão agarrar melhor quando a linha está toda fora.",
      "O de 18 cm chega para 250 metros e é mais fácil de segurar por quem tem mãos pequenas. O de 24 cm leva 500 metros e é o que se usa quando se quer mesmo mandar a pipa longe.",
      "<strong>Material:</strong> madeira compensada<br><strong>Capacidade:</strong> até 250 m (18 cm) ou 500 m (24 cm)<br><strong>Acabamento:</strong> pintado à mão",
      "Cada carretel é pintado à mão — a estampa que recebes não é exactamente igual à da fotografia. É a mesma técnica, não é a mesma pintura.",
    ],
  ),

  dict(
    handle="rabiola-colorida",
    titulo="Rabiola Colorida",
    marca="Ventos do Norte",
    tipo="Rabiolas",
    etiquetas=["Rabiolas", "Acessórios", "Estabilidade"],
    opcao="Comprimento",
    variantes=[("1,5 m", "3.90", "", 45, "150"),
               ("3 m", "5.90", "", 35, "300")],
    sku="VDN-RABI-COL", gramas=45,
    linha_tecnica="Fita de polipropileno",
    imagens=[],
    alt="Rabiola de fitas coloridas para pipa, fundo branco",
    seo_titulo="Rabiola Colorida para Pipa — 1,5 e 3 m | Ventos do Norte",
    seo_desc="Rabiola em fita colorida que estabiliza a pipa em vento irregular. Montagem em segundos.",
    descricao=[
      "Rabiola em fita de polipropileno, presa na ponta inferior da pipa.",
      "Se a pipa roda sobre si mesma, oscila de um lado para o outro ou mergulha sem aviso, o problema quase nunca é falta de jeito — é falta de rabiola. A fita arrasta no ar e puxa a ponta de baixo para trás, o que impede a pipa de girar sobre o próprio eixo. É o mesmo princípio da pena numa seta.",
      "A regra prática: quanto mais forte o vento, mais comprida deve ser a rabiola. Com 1,5 m resolve-se a maioria das tardes; os 3 m são para dias em que a pipa não pára quieta.",
      "<strong>Material:</strong> fita de polipropileno<br><strong>Comprimentos:</strong> 1,5 m e 3 m<br><strong>Montagem:</strong> prende na ponta inferior, em segundos",
      "Rabiola a mais também tem custo: acima do necessário, tira sustentação e a pipa precisa de mais vento para subir. Começa pela curta e sobe se for preciso.",
    ],
  ),

  dict(
    handle="peteca-altiva-sport",
    titulo="Peteca Altiva Sport",
    marca="Altiva",
    tipo="Petecas",
    etiquetas=["Petecas", "Altiva", "Praia", "Pena natural"],
    opcao="Cor",
    variantes=[("Branco", "9.90", "", 26, "BRA"),
               ("Tricolor", "10.90", "", 20, "TRI"),
               ("Neon", "10.90", "", 20, "NEO")],
    sku="ALT-PETE-SPT", gramas=35,
    linha_tecnica="Pena natural · base de borracha",
    imagens=["peteca-altiva-branca.jpg", "peteca-altiva-tricolor.jpg", "peteca-altiva-neon.jpg"],
    alt="Peteca Altiva Sport com penas naturais, fundo branco",
    seo_titulo="Peteca Altiva Sport com penas naturais | Ventos do Norte",
    seo_desc="Peteca oficial Altiva Sport, penas naturais e base de borracha. Voo estável para a roda na praia.",
    descricao=[
      "Peteca oficial Altiva Sport, com penas naturais seleccionadas e base de borracha montada em camadas.",
      "A base em camadas é o que faz o voo ser previsível. Cada disco de borracha absorve uma parte do impacto, o que trava a peteca sem a devolver descontrolada — sobe direita e desce no mesmo sítio. As penas naturais têm curvatura irregular, e é isso que dá o travão suave no fim da subida, coisa que a pena sintética não reproduz.",
      "É a peteca da roda: praia, jardim, parque, entre pessoas que só querem que ela não caia. Também serve para jogo a sério, mas é na roda que o voo estável se nota mais — ninguém tem de correr atrás dela.",
      "<strong>Penas:</strong> naturais seleccionadas<br><strong>Base:</strong> borracha em camadas<br><strong>Peso:</strong> cerca de 35 g<br><strong>Marca:</strong> Altiva",
      "Guarda em local seco e sem peso por cima. Pena natural molhada perde a forma ao secar, e uma peteca com pena torta deixa de voar a direito.",
    ],
  ),

  dict(
    handle="bola-futevolei-altinha",
    titulo="Bola Oficial de Futevôlei Altinha",
    marca="Ventos do Norte",
    tipo="Futevôlei",
    etiquetas=["Futevôlei", "Altinha", "Praia", "Bolas"],
    opcao="Tamanho",
    variantes=[("Oficial", "24.90", "", 20, "OFI")],
    sku="VDN-BOLA-ALT", gramas=420,
    linha_tecnica="PU premium · 6–8 lbs",
    imagens=["bola-futevolei-vdn-marca.jpg", "bola-futevolei-ultratermo.jpg",
             "bola-futevolei-approved.jpg", "bola-futevolei-frente.jpg"],
    alt="Bola de futevôlei da Ventos do Norte, fundo branco",
    seo_titulo="Bola Oficial de Futevôlei Altinha em PU | Ventos do Norte",
    seo_desc="Bola oficial de futevôlei e altinha em PU, toque macio e costura reforçada. Para praia, parque e jardim.",
    descricao=[
      "A nossa bola oficial, com revestimento em PU de toque macio e costura reforçada, calibrada para o altinha.",
      "O equilíbrio é tudo neste jogo. Uma bola pesada magoa no toque de cabeça ao fim de meia hora; uma leve demais é levada pelo vento da praia e a roda desfaz-se. Esta fica no meio: tem massa suficiente para manter a trajectória com vento lateral e revestimento macio para aguentar uma tarde inteira de cabeceios sem deixar a testa a arder.",
      "A costura reforçada é o que a mantém redonda depois de muitas horas na areia — é aí que uma bola barata começa a ganhar bicos e a saltar torta.",
      "<strong>Revestimento:</strong> PU premium<br><strong>Pressão recomendada:</strong> 6 a 8 lbs<br><strong>Peso:</strong> cerca de 420 g<br><strong>Uso:</strong> praia, parque, jardim e treino",
      "Lubrifica a agulha antes de encher e não passes das 8 lbs. Acima disso a costura sofre, e é a costura que segura a bola redonda.",
    ],
  ),

  dict(
    handle="kit-primeira-pipa",
    titulo="Kit Primeira Pipa",
    marca="Ventos do Norte",
    tipo="Kits",
    etiquetas=["Kits", "Iniciante", "Presente", "Pipas"],
    opcao="Tamanho",
    variantes=[("Kit completo", "29.90", "34.20", 12, "COMP")],
    sku="VDN-KIT-PRIM", gramas=700,
    linha_tecnica="4 artigos · poupa 4,30 €",
    componentes=["Pipa Ilustrada (estampa sortida)", "Carretel de Madeira 18 cm",
                 "Linha Encerada 250 m", "Rabiola Colorida 1,5 m"],
    para="Para quem vai empinar pela primeira vez",
    imagens=[],
    alt="Kit com pipa, carretel, linha e rabiola, fundo branco",
    seo_titulo="Kit Primeira Pipa — pipa, linha e carretel | Ventos do Norte",
    seo_desc="Kit completo para começar: pipa, carretel de madeira, 250 m de linha encerada e rabiola. Poupa 4,30 €.",
    descricao=[
      "Tudo o que é preciso para a primeira tarde de vento, numa só caixa.",
      "Quem nunca empinou compra a pipa e descobre em casa que falta a linha. Compra a linha e descobre no parque que sem carretel não se solta. Este kit existe para essa segunda viagem não acontecer: sai da caixa e vai voar.",
      "Escolhemos a pipa laminada de propósito — é a que aguanta os erros do início, e no início erra-se muito. A rabiola de 1,5 m vem incluída porque é o acessório que a maioria dos principiantes não sabe que precisa, e é o que separa uma tarde boa de uma tarde a ver a pipa rodopiar.",
      "<strong>Poupança:</strong> 4,30 € face aos artigos comprados em separado",
      "A pipa vem com estampa sortida. Se preferires escolher, compra os artigos em separado — sai um pouco mais caro, mas escolhes o desenho.",
    ],
  ),

  dict(
    handle="kit-praia",
    titulo="Kit Praia",
    marca="Ventos do Norte",
    tipo="Kits",
    etiquetas=["Kits", "Praia", "Futevôlei", "Petecas"],
    opcao="Tamanho",
    variantes=[("Kit completo", "42.90", "46.80", 10, "COMP")],
    sku="VDN-KIT-PRAIA", gramas=520,
    linha_tecnica="3 artigos · poupa 3,90 €",
    componentes=["Bola Oficial de Futevôlei Altinha",
                 "Peteca Altiva Sport (cor sortida)",
                 "Peteca Altiva Sport (cor sortida)"],
    para="Para quem passa o dia na praia com amigos",
    imagens=["bola-futevolei-vdn-marca.jpg"],
    alt="Kit com bola de futevôlei e duas petecas, fundo branco",
    seo_titulo="Kit Praia — bola de futevôlei e petecas | Ventos do Norte",
    seo_desc="Bola oficial de futevôlei e duas petecas Altiva num só kit. Poupa 3,90 € face aos artigos em separado.",
    descricao=[
      "A bola oficial de futevôlei e duas petecas Altiva, para o dia não depender de um jogo só.",
      "Um dia inteiro de praia não se joga todo da mesma maneira. A bola pede espaço e gente disposta a correr; quando isso cansa, ou quando a roda encolhe para três pessoas, passa-se à peteca — que se joga parado e com qualquer número. E quando o vento levanta a meio da tarde, a peteca continua a funcionar onde a bola já não obedece.",
      "São duas petecas de propósito: uma perde-se na água, fica presa numa sombra, ou vai embora com alguém. Com duas o jogo não acaba por causa disso.",
      "<strong>Poupança:</strong> 3,90 € face aos artigos comprados em separado",
      "As cores das petecas são sortidas. A bola vai sempre com a marca Ventos do Norte impressa.",
    ],
  ),
]


def corpo_html(produto):
    """Junta os parágrafos da descrição em HTML."""
    return "".join(f"<p>{p}</p>" for p in produto["descricao"])
