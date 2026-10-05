# Reflexão sobre o Uso de IA — Grupo 02 (EONET)

> Este documento é uma **análise crítica do grupo**, não um relatório gerado
> pela IA. Os tópicos abaixo estão estruturados como roteiro — cada um deve
> ser preenchido com a avaliação real da equipe, feita em conjunto após usar
> o código e testar o pipeline.

## 1. Onde a IA ajudou

_Preencher: em que etapas a IA realmente acelerou o trabalho ou evitou
erros? Ex.: estruturar o SQL com RLS e GRANTs corretos de primeira, lembrar
da deduplicação antes do upsert, etc. Seja específico — cite a etapa, não
apenas "ajudou em tudo"._

## 2. Onde a IA errou ou deixou lacunas

_Preencher: o que precisou de correção, complementação ou não funcionou de
primeira? Exemplos de pontos conhecidos deste projeto que o grupo deve
verificar e relatar com a própria experiência:_

- _O script assume que a geometria mais recente de um evento é sempre um
  ponto; eventos com geometria em polígono ficam sem latitude/longitude
  diretas. Isso afetou a visualização de algum evento específico?_
- _O agendamento (cron) do workflow foi definido com um horário padrão —
  fez sentido para o grupo ou precisou ser ajustado?_
- _Alguma tentativa de nomear ou organizar arquivos (como o `setup.sql`)
  precisou ser corrigida pelo grupo?_

## 3. O que o grupo corrigiu ou decidiu por conta própria

_Preencher: decisões de modelagem, valores de configuração (`EONET_DAYS`,
`BATCH_SIZE`, horário do cron), textos do painel, cores, ou qualquer ajuste
que não veio pronto da IA e exigiu critério do grupo._

## 4. O que o grupo aprendeu no processo

_Preencher: conceitos técnicos que ficaram mais claros ao revisar o código
gerado (ex.: por que RLS é necessário, como funciona um upsert com
constraint UNIQUE, diferença entre a chave anon e a service_role). O
objetivo aqui é mostrar compreensão real, não só reprodução do código._

## 5. Limitações percebidas no uso de IA para este tipo de tarefa

_Preencher: em que momentos ficou claro que a revisão humana era
indispensável? Houve algo que a IA não podia verificar sozinha (ex.: se os
dados fazem sentido cientificamente, se a interface está realmente legível,
se as credenciais foram configuradas certas)?_

## 6. Conclusão do grupo

_Preencher: uma avaliação final e honesta — o uso de IA valeu a pena neste
projeto? Em que tipo de etapa vocês confiariam mais nela, e em qual menos?_
