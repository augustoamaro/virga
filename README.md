Objetivo do Projeto

Desenvolver uma planilha ou sistema que permita comparar dados de rastreamento de veículos de diferentes fontes, garantindo a consistência e identificando possíveis discrepâncias.

Tarefas de Desenvolvimento

Criação de Planilha ou Sistema

Desenvolver uma planilha (Excel) ou um sistema dedicado, conforme a complexidade e a escalabilidade exigidas.
A ferramenta deve ser capaz de importar dados de diferentes fontes e exibi-los de forma clara e organizada.
Integrações de Dados

CRTI (Excel): Importar dados principais de identificação dos equipamentos da planilha de rastreamento existente do CRTI.
Localiza (API?): Integrar com a API da Localiza (ou outra plataforma de rastreamento) para obter dados de status de comunicação e odômetro do rastreador.
Google Docs: Importar dados de odometria e horometria de uma planilha no Google Docs, onde essas informações são inseridas manualmente. Definir o método de importação (ex.: CSV, API) conforme necessário.
Lógica de Comparação

Implementar uma lógica para comparar os dados de odometria entre as três fontes: CRTI, Localiza e Google Docs.
Destacar visualmente as discrepâncias, por exemplo, com indicadores coloridos (verde/vermelho).
Interface de Visualização

Criar uma interface que facilite a visualização dos dados, com indicadores visuais para o status de comunicação e discrepâncias de odometria.
Opcionalmente, incluir indicadores para status de ignição (ligada/desligada), também com marcadores visuais.
Centralização no CRTI (Futuro)

Avaliar a possibilidade de centralizar todos os dados diretamente no CRTI, eliminando a necessidade de integração com Google Docs.
Consultar a equipe do CRTI para entender as opções de integração com a Localiza e adicionar dados de horometria.
Documentação

Registrar o processo e as funcionalidades desenvolvidas no Notion, para facilitar o uso e a manutenção da ferramenta.
Considerações Adicionais

Formato dos Dados: Verificar a compatibilidade dos dados nas fontes (CRTI, Localiza, Google Docs) para facilitar a importação.
API da Localiza: Confirmar a disponibilidade e documentação da API da Localiza para obter os dados necessários.
Escalabilidade: Considerar a escalabilidade da solução, especialmente se o número de rastreadores aumentar significativamente, pois uma planilha pode não ser adequada para grandes volumes de dados.
Usabilidade: Priorizar a simplicidade e clareza da interface para garantir fácil interpretação e análise dos dados.
