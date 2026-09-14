---
name: openwrt-imagebuilder
description: OpenWrt ImageBuilder compilation specialist. Calculates exact SquashFS sizing for 16MB SPI flash, manages package manifests, profiles, and sysupgrade integrity.
---

# OpenWrt ImageBuilder & Firmware Engineering (ARK Router)

## Objetivo
Orientar a geração, compilação e validação de imagens de firmware OpenWrt personalizadas utilizando o OpenWrt ImageBuilder (em ambiente WSL ou Linux), garantindo conformidade com o orçamento estrito de memória Flash (16 MB SPI Flash).

---

## 1. Orçamento Rígido de Memória Flash (16 MB SPI-NOR)

- **Geometria de Particionamento:**
  - `u-boot` + `env` + `factory`: ~1 MB
  - `kernel`: ~3 MB a 4 MB
  - `rootfs` (SquashFS comprimido): deve ficar entre **8 MB e 10.5 MB**
  - `rootfs_data` (`/overlay` writable): DEVE manter **> 2.8 MB livres** no primeiro boot.
- **Tamanho Máximo do Binário Sysupgrade:**
  - O arquivo final `*-sysupgrade.bin` NUNCA deve ultrapassar **14.5 MB** (alvo seguro no ARK Router: ~12.5 MB a 13.0 MB).
- **Atenção a Revisões de Hardware (Alerta Fórum OpenWrt 243547):**
  - O Cudy WR3000 v1 padrão utiliza flash SPI-NOR padrão (`filogic / cudy_wr3000-v1`).
  - Lotes recentes de modelos variantes (WR3000E, WR3000H, AP3000 com seriais $\ge 2543$) possuem chips de flash alternativos que exigem checagem de DTS específico.

---

## 2. Operação do ImageBuilder (Linha de Comando)

### Sintaxe Canônica
```bash
make image \
    PROFILE="cudy_wr3000-v1" \
    PACKAGES="luci luci-ssl \
              kmod-mt7981-firmware mt7981-wo-firmware \
              -dnsmasq dnsmasq-full \
              adguardhome nlbwmon \
              -ppp-mod-pppoe ppp-mod-pppoe" \
    FILES="files" \
    BIN_DIR="bin/targets/mediatek/filogic"
```

### Regras de Ouro para o Pacote de Imagem:
1. **Substituição Limpa de Pacotes:**
   - Para substituir um pacote padrão, use `-pacote-antigo +pacote-novo` (ex: `-dnsmasq dnsmasq-full` ou `-wpad-basic-mbedtls wpad-mbedtls`).
2. **Inclusão de Configurações Nativas (`FILES="files"`):**
   - Arquivos colocados em `files/` são incorporados diretamente na partição SquashFS (ROM somente leitura), consumindo zero bytes no `/overlay`!
   - Ideal para: temas pré-instalados (`files/www/...`), scripts de inicialização (`files/etc/uci-defaults/...`) e configurações base de rede.
3. **Zero-Waste no `/etc/sysupgrade.conf`:**
   - Nunca adicione caminhos em `/usr` ou `/www` no `/etc/sysupgrade.conf`. O sysupgrade deve preservar apenas configurações de `/etc/config` para manter o `/overlay` livre.

---

## 3. Validação de Integridade e Flashing

1. **Checagem de Hash SHA-256 Obrigatória:**
   - Sempre gere e confira a soma de verificação antes de qualquer upload via SCP:
     ```bash
     sha256sum openwrt-*-sysupgrade.bin
     ```
2. **Teste de Compatibilidade do Sysupgrade (`-T`):**
   - No roteador via SSH antes do flash real:
     ```sh
     sysupgrade -T /tmp/firmware.bin
     ```
   - O teste valida as assinaturas de metadata do dispositivo (`board_name`), tamanho máximo da imagem e integridade do tar/squashfs.
3. **Flashing Seguro:**
   - Preservando configurações: `sysupgrade -v /tmp/firmware.bin`
   - Limpeza de fábrica (Clean Flash): `sysupgrade -v -n /tmp/firmware.bin`
