---
name: openwrt-sqm-bufferbloat
description: Smart Queue Management (SQM), CAKE / FQ-CoDel, cake-mq multi-core scaling, framing overhead calculation, and bufferbloat elimination specialist for OpenWrt.
---

# OpenWrt SQM & Bufferbloat Mitigation (ARK Router)

## Objetivo
Eliminar a latência induzida por congestionamento (*Bufferbloat*) em conexões de alta e média velocidade, mantendo o ping abaixo de 10ms mesmo quando múltiplos usuários estiverem baixando torrents ou realizando uploads massivos.

---

## 1. O Que É o Bufferbloat e Como Combatê-lo

Quando uma conexão atinge o limite do link, os buffers do modem da operadora ou do roteador enchem, gerando filas de espera de centenas de milissegundos.
- **Solução:** O Smart Queue Management (SQM) limita a taxa do roteador para ligeiramente abaixo do gargalo da operadora (regra dos **90% a 95%**), assumindo o controle total da fila e descartando ou marcando pacotes (ECN) antes do estouro do buffer.

---

## 2. Algoritmos: CAKE, cake-mq vs FQ-CoDel

- **CAKE (`piece_of_cake.qos`):**
  - O algoritmo mais avançado do Linux.
  - Combina modelagem de tráfego (*shaper*), isolamento justo por host/fluxo (*Flow Isolation*) e diferenciação de tráfego por DSCP.
  - **Recomendado para o Cudy WR3000 (MT7981):** A CPU Dual-Core ARM Cortex-A53 a 1.3 GHz roda CAKE a até ~600 Mbps mono-thread.
- **Avanço OpenWrt 25.12: `cake-mq` (Multi-Queue):**
  - O branch 25.12 incorporou suporte a instâncias multi-core do CAKE. Em roteadores dual-core ou quad-core como o MT7981, os núcleos distribuem o enfileiramento, permitindo que conexões próximas de 1 Gbps rodem com SQM ativo!
- **FQ-CoDel (`simple.qos`):**
  - Mais leve para CPUs com menos poder de processamento (DGL-5500 QCA9558 a 720 MHz mono-core).

---

## 3. Configuração UCI (`/etc/config/sqm`)

Exemplo de configuração para um link de **500 Mbps Download / 250 Mbps Upload** via GPON/Fibra:

```sh
uci -q batch <<EOF
set sqm.wan=queue
set sqm.wan.interface='wan'
set sqm.wan.enabled='1'
set sqm.wan.qdisc='cake'
set sqm.wan.script='piece_of_cake.qos'
set sqm.wan.download='475000' # 95% de 500 Mbps
set sqm.wan.upload='235000'   # 94% de 250 Mbps
set sqm.wan.linklayer='ethernet'
set sqm.wan.overhead='44'     # Overhead de enquadramento fibra/PPPoE
set sqm.wan.qdisc_really_really_advanced='1'
set sqm.wan.qdisc_advanced_options='diffserv4 nat wash'
commit sqm
EOF
/etc/init.d/sqm restart
```

### Parâmetros Avançados do CAKE:
- `nat`: Faz o CAKE enxergar o IP real de cada cliente da rede local antes do Masquerade/NAT, impedindo que um único dispositivo monopolize a banda.
- `wash`: Limpa tags DSCP malformadas que chegam da internet.
- `diffserv4`: Cria 4 classes de prioridade (Bulk, Best Effort, Video, Voice/Gaming).

---

## 4. Auditoria e Validação
- **Teste de Carga:** Rodar o teste em `waveform.com/tools/bufferbloat` antes e depois da ativação.
- **Nota Alvo no ARK Router:** **A+** (acréscimo de ping < 5ms durante saturação total).
