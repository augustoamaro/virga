Planilha equipamentos CRTI

0:"Responsável cadastro"
1:"CADASTRO SAP"
2:"Descrição*:"
3:"Apelido ou prefixo*:"
4:"Localização/Filial Atual*:"
5:"Horômetro de Chegada na Filial:"
6:"Data Chegada na Localização Atual*:"
7:"Último Horômetro/Hodômetro:"
8:"Horômetro/Hodômetro Acumulado:"
9:"Marca do Equipamento*:"
10:"Grupo do Equipamento*:"
11:"Sub-Grupo do Equipamento*:"
12:"Ano de Fabricação:"
13:"Ano de Modelo:"
14:"Horômetro ou Hodômetro*:"
15:"Tipo de Equipamento:"
16:"Proprietário ou Locador*:"
17:"Contrato:"
18:"Requer Apropriação*:"
19:"Requer Plano de Manutenção*:"
20:"Capacidade Tanque de Combustíve (T):"
21:"Capacidade Reservatório Hidráuico:"
22:"Potência:"
23:"Capacidade:"
24:"Chassis:"
25:"Série:"
26:"Modelo:"
27:"Altura:"
28:"Largura:"
29:"Comprimento:"
30:"Fabricante do Motor:"
31:"Modelo Motor:"
32:"Cor:"
33:"Placa:"
34:"RENAVAM:"
35:"OK"

===============================================================

Planilha de Medições:

Placa
Chassi
Modelo
Fornecedor do Veículo (sublocado)
Cidade
Cliente Contrato
Horímetro Anterior
Data Horímetro Anterior
Horímetro
Data do Horímetro
KM Anterior
Data KM Anterior
KM
Data do KM
H/DIA
Horímetro e KM aproximado
KM/Dia
H/Dia Norm
KM/Dia Norm
Última atualização
Status

===============================================================


API Localiza exemplo:
URL: http://sistema.localizarastreamento.com/integracao/mestre/getVeiculos.php
token: WREPZVgbr6sih8jLgqgPwMo8RgrjhC59zKGObxLLSXb1H3UDaPw5OfHEMFVWoWqi
user: 50282072080
pass: HKJ@iu&0#23i*o9iu60T
[
	{
		"placa": "ESC006",
		"ignicao": "1",
		"velocidade": "0",
		"latitude": "-14.236876",
		"longitude": "-49.428906",
		"odometro": "040860586",
		"horimetro": "8189"
	},
	{
		"placa": "RKW8C90",
		"ignicao": "",
		"velocidade": "",
		"latitude": "",
		"longitude": "",
		"odometro": "",
		"horimetro": "4775"
	},
]

===============================================================

Resultado final esperado:

Placa
Chassi
Modelo
Cliente
Cidade
Status
Funcionamento
Manutenção
