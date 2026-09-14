---
name: openwrt-wifi-mesh
description: OpenWrt wireless roaming, 802.11r/k/v fast transition, mesh 802.11s, and band steering (usteer/DAWN) specialist.
---

# OpenWrt Wi-Fi Roaming, 802.11r/k/v & Mesh (ARK Router)

## Objetivo
Configurar transição rápida e roaming contínuo entre pontos de acesso (APs), além de redes Mesh 802.11s e direcionamento inteligente de banda (*band steering*), com foco em estabilidade e compatibilidade com dispositivos Apple, Android e IoT.

---

## 1. Fast Roaming (802.11r, 802.11k e 802.11v)

Para que dispositivos se desloquem pela casa sem queda em chamadas de voz ou jogos, os três protocolos devem operar em conjunto no `/etc/config/wireless`:

### Configuração em Cada `wifi-iface`:
```uci
config wifi-iface 'default_radio0'
    option device 'radio0'
    option network 'lan'
    option mode 'ap'
    option ssid 'ARK_Router'
    option encryption 'sae-mixed'
    option key 'SuaSenhaSegura123'

    # 802.11r (Fast Transition)
    option ieee80211r '1'
    option ft_over_ds '1'
    option mobility_domain '4f57' # 4 caracteres hexadecimais idênticos em todos os APs
    option ft_psk_generate_local '1'

    # 802.11k (Radio Resource Measurement)
    option ieee80211k '1'
    option rrm_neighbor_report '1'
    option rrm_beacon_report '1'

    # 802.11v (BSS Transition Management)
    option ieee80211v '1'
    option bss_transition '1'
    option wnm_sleep_mode '1'
    option time_advertisement '2'
    option time_zone 'UTC0'
```

---

## 2. Band Steering Leve com `usteer`

Em vez de suites pesadas que consomem muita RAM, o ARK Router utiliza o **`usteer`** para coordenar a troca de bandas:
- Força dispositivos com suporte a 5 GHz a abandonarem o canal 2.4 GHz congestionado.
- Recomenda a troca quando o sinal cair abaixo de **-73 dBm**.
- Desconecta clientes zumbis abaixo de **-82 dBm** com probe response blocking.

### Configuração UCI (`/etc/config/usteer`):
```uci
config usteer
    option min_snr '15'
    option band_steering_threshold '20'
    option kick_threshold '-78'
    option max_retries '3'
```

---

## 3. Rede Mesh 802.11s (Ponto a Ponto sem Fio)

Quando não houver cabo Ethernet entre os cômodos, criar uma interface Mesh dedicada no rádio de 5 GHz:
```uci
config wifi-iface 'mesh5'
    option device 'radio0'
    option mode 'mesh'
    option mesh_id 'ark-mesh-backhaul'
    option mesh_fwding '1'
    option encryption 'sae'
    option key 'ChaveSuperSecretaMesh'
    option network 'lan'
```
- **Vantagem:** O protocolo 802.11s faz roteamento na camada 2 (MAC), permitindo que DHCP e mDNS atravessem a malha sem necessidade de WDS proprietário.
