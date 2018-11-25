# Free Wheels

Uma análise da acessibilidade para pessoas com dificuldade de locomoção na cidade de São Paulo.
[Acesse nossa página!](http://interscity.org/apps/acessibilidade/)

## Escopo do projeto

- **O que é:** O objetivo dessa iniciativa é quantificar o grau de acessibilidade de locomoção
nos bairros da cidade de São Paulo em diferentes aspectos, como Mobilidade, Topografia
da cidade e o quão acessíveis são os estabelecimentos das regiões.

- **Como é feito:**
Utilizando dados abertos e dados de empresas parcerias, fizemos uma análise para gerar
informação sobre o tema, obtendo uma **nota de acessibilidade** para cada região de
acordo com três diferentes aspectos, Mobilidade, Topografia e avaliação da
acessibilidade em estabelecimentos como restaurantes, bares, etc.

- **Porque:** A informação gerada pode ser usada para monitorar nossa cidade, incentivar
políticas, práticas e conscientização para torná-la mais inteligente
no quisito acessibilidade para pessoas com dificuldades de locomoção.

### A análise

Consideramos três aspectos para responder o quão acessível é cada bairro:

- **Mobilidade:** Nessa categoria, levamos em consideração informações de acessibilidade
no transporte veicular em cada região com os seguintes dados:

    * Linhas com ônibus acessíveis que passam no bairro com base nos dados da
    [Scipopulis](https://www.scipopulis.com/) e [SPTrans](http://www.sptrans.com.br/).

    * Linhas de metrô.

    * Vagas reservadas para cadeirantes e idosos na Zona Azul.

- **Topografia:** A declividade do bairro foi um quisito considerado um aspecto
também de impacto na acessibilidade de locomoção e também integra o cálculo
da nota. Essa informação foi obtida utilizando dados da  Prefeitura Municipal de São Paulo,
pelo portal [Geosampa](http://geosampa.prefeitura.sp.gov.br/PaginasPublicas/_SBC.aspx).

- **Acessibilidade em estabelecimentos:** A quantidade e qualidade dos estabelecimentos
em relação à acessibilidade é também um importante fator para a análise dos bairros.
Para esse aspecto, utilizamos as seguintes fontes de dados:

  * Avaliações de estabelecimentos com Selo de Acessibilidade emitido pela Prefeitura de São
  Paulo.

  * Avaliações de estabelecimentos pelo aplicativo da empresa [Guia de Rodas](https://www.guiaderodas.com).

### Metodologia

[Detalhes aqui.](http://interscity.org/apps/acessibilidade/scripts/r/smart-sampa.html)

### Visualização dos dados

Para visualização dos dados, foi implementado um dashboard interativo contendo o resultado da análise.
Nele, usuários podem navegar e interagir com o ranking dos bairros em um mapa e em gráficos,
além de ler sobre a metodologia e ver detalhes dos resultados.
Foi elaborado também paper científico do Ranking de acessibilidade dos distritos da cidade de São Paulo,
detalhando a metodologia utilizada e os resultados.

Funcionalidades principais:
- Mapa do município com distritos.
  * Escala de cores vermelho/amarelo/verde representando a "nota de acessibilidade".
  * Usuário pode navegar no mapa, dar zoom, e clicar nos distritos para ver mais detalhes.

- Gráfico "spiderweb" exibindo informações sobre os diferentes componentes da nota dos distritos.
  * Inspirado no Ranking de Smart Cities europeu.
  * Ao clicar em um distrito no mapa, o gráfico é exibido em uma área ao lado do mapa.

- Destaques sobre pontos-chave dos resultados encontrados.
  * Em linguagem simples (ou seja, "não-científica"), acessível para o grande público.

- Seção com detalhes sobre a metodologia.
  * Também em linguagem para o grande público.

- Seção com links para entidades parceiras e incentivo à avaliação colaborativa através do guiaderodas.


## Bibliotecas, ferramentas e linguagens

- **Análise dos dados:** linguagens R e Python. Resultados são exportados em JSONs e arquivos CSV.
- **Visualização dos dados:** Javascript, HTLM e CSS - Bootstrap, Angular.

# Instituições Envolvidas

<img src="img/parceiros.png" style="margin-left: auto; margin-right: auto;">

# Rodando em localhost

1. Instale o Ruby.
1. `gem install bundle`
1. `bundle install --vendor`
1. `bundle exec jekyll server`
   * Use o parâmetro `-w` ou `--watch` para que o servidor detecte mudanças e atualize automaticamente.
1. Acesse a página na porta 4000.

