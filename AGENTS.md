# ARK Router & Development Guidelines

## Project Context
ARK Router is an advanced, lightweight operating system interface and networking distribution built on OpenWrt / LuCI for embedded routers (primary target: D-Link DGL-5500 with 128 MB RAM and 16 MB SPI Flash).

## Core Directives

### 1. Hardware Budget, Flash (16 MB) & Memory (Strict)
- **RAM Constraint**: 128 MB (DGL-5500) to 256 MB (Cudy WR3000). Under normal conditions, maintain > 80 MB free RAM on 128 MB devices and > 60 MB on 256 MB devices.
- **Flash Constraint**: 16 MB total SPI Flash. Partition is shared between Kernel, SquashFS ROM, and writable `/overlay` (`rootfs_data`).
  - Keep `/overlay` free space > 2 MB.
  - Never save growing logs, metrics or history CSVs directly in `/etc` on Flash. Use `/tmp` (RAM) with rotation or strictly capped small files.
- **Minification & Asset Pipeline**:
  - Source code in development (`root/www/...`) remains 100% readable, formatted, and commented.
  - Deployed assets to router and packaging builds MUST be minified via `scripts/build_minified_assets.py` (esbuild/terser) with `node --check` validation.
  - Minification reduces JS/CSS by 60-70%, preventing `/overlay` exhaustion on live routers and keeping compressed SquashFS tiny.
  - Theme CSS + JS combined target budget: keep total footprint under 60 KB compressed. Never bundle heavy npm libraries or runtime engines.

### 2. Dual OpenWrt Architecture (Antigo vs. Novo)
ARK Router must remain compatible with both generations:
- **OpenWrt legado (19.07 - 21.02, como padrão)**:
  - Reference hardware: D-Link DGL-5500 (Atheros QCA9558), 128 MB RAM, 16 MB Flash.
  - Package manager: `opkg` (`/etc/opkg.conf`, `opkg install/status`).
  - Firewall engine: `iptables` / `firewall3` (`/etc/config/firewall`).
  - LuCI DOM: Rendered with both `<table>` and div-based tables (`<div class="table">`, `.tr`, `.td`).
- **OpenWrt atual (22.03+ como padrão; confirme no dispositivo)**:
  - Reference hardware: Cudy WR3000 v1 (MediaTek MT7981 Filogic 820), 256 MB RAM, 16 MB Flash.
  - Package manager: `opkg` até 24.10; `apk` a partir de 25.12. Detecte no dispositivo.
  - Firewall engine: `nftables` / `firewall4` (`table inet ...`).
  - Backend: `ucode` templates (`*.ut`) and modern RPC.
- **Portability Rule**: Detect the available package manager and active firewall service independently; release number is context, not proof. Keep shell scripts compatible with BusyBox ash (`/bin/sh`).

### 3. UI, Botões e Modais: O Que Dá Certo vs. O Que NÃO Dá
- **Área de Toque (Mobile First)**: Todo botão, badge clicável ou switch deve ter altura mínima útil de **40px** (`min-height: 40px`).
- **Anti-Zoom e Seleção**: Aplicar `user-select: none; -webkit-tap-highlight-color: transparent;` em botões e controles rápidos para evitar zoom no duplo toque em celulares.
- **Safety Confirmation (Fase de Captura)**:
  - Ações críticas (Reboot, Reset, Flash, Mudança de perfil) DEVEM usar `addEventListener('click', fn, true)` (fase de captura) para interceptar antes de qualquer listener do LuCI ou submissão acidental de formulário.
  - Trava visual obrigatória de 2 segundos no botão final com contador decrescente e token efêmero validado no backend (`/tmp`).
- **Desacoplamento de Backdrop e Modal**:
  - O backdrop escuro (`#modal_overlay`) é fixo em tela inteira (`position: fixed; inset: 0; width: 100vw; height: 100dvh; pointer-events: none` quando inativo).
  - A caixa de diálogo (`.modal`, `.cbi-modal`) é o cartão central. NUNCA aplicar largura fixa ou margens diretamente em `#modal_overlay`.
- **Isolamento de Scroll no LuCI**:
  - No LuCI (Argon / Bootstrap), o `body` tem `overflow: hidden; height: 100vh;`. Quem rola é o contêiner `.main-right`. Ao abrir modais ou menu lateral, travar `.main-right` com `overflow: hidden !important; pointer-events: none !important;`.
- **Contenção Flex/Grid**:
  - SEMPRE usar `min-width: 0` em filhos diretos de `display: flex` e `display: grid` para evitar que endereços MAC, hostnames longos ou URLs empurrem a tela horizontalmente.
- **O que NÃO fazer (Proibido)**:
  - ❌ NÃO usar `alert()`, `confirm()` ou `prompt()` síncronos (eles congelam o loop do LuCI e causam falhas no mobile).
  - ❌ NÃO definir larguras fixas em pixels (`width: 600px`) sem limites responsivos (`max-width: 100%`).
  - ❌ NÃO confiar em preenchimento automático de senhas (o LuCI insere dummy inputs `left: -100000px` que devem ser ignorados).
  - ❌ NÃO subir arquivos de desenvolvimento sem minificar para o `/overlay` do roteador.

### 4. OpenWrt POSIX Shell & UCI
- All shell scripts must run under BusyBox ash (`/bin/sh`). No bash-isms (`[[ ]]`, `${var//}`, arrays).
- Quote UCI paths: `uci get "network.lan.ipaddr"`.
- Commit changes cleanly and restart services conditionally.

### 5. Active Specialized Agent Skills (.agents/skills/)
1. `posix-shell`: Strict POSIX BusyBox ash compliance, UCI atomicity, no bashisms.
2. `security-auditor`: Command injection, ubus ACLs, ephemeral tokens in /tmp, auth.
3. `systematic-debugging`: Scientific root-cause troubleshooting, dmesg, logread, ubus.
4. `openwrt-network-firewall`: Dual firewall (fw3/iptables vs fw4/nftables), DSA switch, anti-lockout.
5. `ark-theme-ui`: LuCI DOM, 40px touch targets, .main-right scroll lock, modal decoupling, esbuild.
6. `openwrt-imagebuilder`: ImageBuilder CLI, 16MB Flash budgeting (<14.5MB bin), sysupgrade -T.
7. `openwrt-hardware-offloading`: MediaTek Filogic PPE/WED vs Atheros flow offload, SQM conflicts.
8. `openwrt-wifi-mesh`: 802.11r/k/v fast roaming, usteer, 802.11s mesh backhaul.
9. `openwrt-sqm-bufferbloat`: CAKE, cake-mq multi-core, FQ-CoDel, framing overhead, A+ grade.
10. `openwrt-storage-failsafe`: MTD partition table, factory/ART backup, Telnet failsafe, U-Boot TFTP.
11. `openwrt-luci-modern`: Modern LuCI JavaScript views (L.view.extend), E() DOM builder, JSON menus, RPC ACLs, no Lua CBI.

### 6. Skill Distribution
- Maintain skills in `skills/`; mirror them to `.agents/skills/` and run `python scripts/check_skill_mirrors.py` before publishing.
- This repository ships skills and documentation. Cursor commands from other ARK workspaces are not part of this checkout.

### 7. Native ROM Firmware & ImageBuilder (Cudy WR3000 v1 / filogic)
- This repository does not contain a ROM image or firmware runbook. Verify the exact board, image source, SHA-256 and current runbook in the ARK Router project before any firmware operation.
- When ARK Router files are built into SquashFS, do not preserve duplicate `/usr` or `/www` paths via `/etc/sysupgrade.conf`; measure free `/overlay` after first boot. A later package install can still consume the writable overlay.

### 8. Git Hygiene & Artifact Release Directive (No Binary Bloat)
- **Do NOT commit binary builds to Git**: Firmware images (`.bin`, `.img`), full kernel tarballs, or toolchains must NOT be pushed directly to Git history.
- **GitHub Free Storage Boundaries**: Git repositories should stay < 1 GB (soft limit) with individual files strictly < 100 MB.
- **Distribution via GitHub Releases**: Large pre-compiled sysupgrade binaries and packages must be published as assets in **GitHub Releases** (supports up to 2 GB per file for free) rather than inflating Git clone size.
