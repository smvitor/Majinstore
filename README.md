# MajinStore 3.0 — versão inicial

## Publicação pelo iPhone
Envie **todos os arquivos e pastas** deste projeto ao repositório público `smvitor/Majinstore`, substituindo `index.html` na raiz. O GitHub Pages já está habilitado na branch `main`, pasta `/ (root)`. O painel lê `data/offers.json`.

## Atualização a cada 6 horas
O arquivo `.github/workflows/collect.yml` define a agenda (UTC). Após enviar `collector.py`, `links.txt` e o workflow, abra **Actions > MajinStore monitor 6h > Run workflow** para testar. A agenda pode atrasar. Verifique permissões de escrita em **Settings > Actions > General > Workflow permissions**. Se o site continuar exibindo dados antigos, confira logs e commits.

O coletor é conservador: acessa somente anúncios públicos GGMAX, não contorna bloqueios e não inventa preço por variante. O workflow coleta apenas o preço principal do anúncio, que **não** pode ser usado como preço individual de Netflix 7/15/20 dias. Variantes devem ser confirmadas e cadastradas no painel; ficam salvas localmente no iPhone, não sincronizadas.

## Telegram
Opcional: configure os secrets `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no GitHub; nunca coloque credenciais em arquivos públicos. Os alertas iniciais cobrem alterações do preço principal e falhas, não variantes.

## Limitações reais
- Dashboard administrativo é interface de gestão **sem autenticação**; GitHub Pages é público.
- Histórico de variantes e alertas por variante dependem de um extrator validado de opções específicas, ainda não implementado.
- Detecção automática de novos produtos/estoque e histórico por variante estão planejados, não ativos.
- O painel permite até 100 URLs locais, mas é necessário exportar `links.txt` e publicá-lo para o workflow monitorar.
- Cálculo fiscal é estimativo e configurável, não aconselhamento tributário.
- Um dos anúncios fornecidos declara expressamente que não fornece para revenda; o painel sinaliza isso.
- Não armazene dados privados ou tokens em repositório público.
