# OpenWrt-Skills 🌐🤖

> **The Definitive Agentic AI Skills, Rules & Tooling Suite for OpenWrt & LuCI Development.**  
> Built for embedded networking, low-footprint hardware (16 MB SPI Flash / 128–256 MB RAM), and dual-generation OpenWrt architectures (`fw3`/`iptables` vs `fw4`/`nftables` and `opkg` vs `apk`).

[![OpenWrt Version](https://img.shields.io/badge/OpenWrt-19.07_%E2%86%92_25.12+-blue?logo=openwrt)](https://openwrt.org)
[![Skills Count](https://img.shields.io/badge/Agentic%20Skills-10%20Production%20Ready-success)](https://github.com/Despensativo/OpenWrt-Skills)
[![Hardware Database](https://img.shields.io/badge/ToH%20Models-3%2C030%20Offline%20Cached-orange)](https://github.com/Despensativo/OpenWrt-Skills)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Overview

**OpenWrt-Skills** equips modern AI coding assistants (Google Antigravity, Cursor AI, Claude Code, Windsurf, Roo Code, ChatGPT) with deep, production-grade domain knowledge of OpenWrt firmware engineering, embedded POSIX shell scripting, LuCI web user interface design, and kernel networking.

### Why OpenWrt-Skills?
Developing for resource-constrained routers (e.g. 16 MB SPI Flash and 128 MB RAM) is unforgiving:
* Standard LLMs hallucinate non-existent bashisms (`[[ ]]`, `${var//}`) that crash BusyBox ash.
* Generic code writes large logs to `/etc`, exhausting the writable `/overlay` partition and bricking the router.
* Frontend code uses heavy npm libraries and synchronous `alert()`, freezing the LuCI event loop on mobile phones.
* Firewall scripts assume `iptables` and fail silently on modern OpenWrt 23.05–25.x running `nftables` (`firewall4`).

**OpenWrt-Skills fixes this completely.**

---

## 🧩 The 10 Specialized Agent Skills

Each skill adheres to the open Agentic Skill format (`SKILL.md` with standard YAML frontmatter) located in both `.agents/skills/` and `skills/`:

| # | Skill Name | Domain & Scope | Key Capabilities |
| :---: | :--- | :--- | :--- |
| 1 | **[`posix-shell`](skills/posix-shell/SKILL.md)** | BusyBox ash & Shell Compliance | Forbids bashisms, enforces safe variable quoting, atomic UCI batch commits, memory efficiency. |
| 2 | **[`security-auditor`](skills/security-auditor/SKILL.md)** | Embedded Security & RPC ACLs | Command injection prevention in `sys.exec`, ubus ACL auditing, ephemeral tokens in `/tmp`. |
| 3 | **[`systematic-debugging`](skills/systematic-debugging/SKILL.md)** | Root-Cause Diagnostics | Enforces log analysis (`dmesg`, `logread`, `ubus status`) before proposing any code edits. |
| 4 | **[`openwrt-network-firewall`](skills/openwrt-network-firewall/SKILL.md)** | Dual Firewall & DSA Switch | Dynamic detection of `fw3`/`iptables` vs `fw4`/`nftables`, DSA bridge VLAN filtering, anti-lockout safety. |
| 5 | **[`ark-theme-ui`](skills/ark-theme-ui/SKILL.md)** | LuCI Mobile UI & Theming | 40px touch targets, `.main-right` scroll lock, modal backdrop decoupling, esbuild asset minification (<60 KB). |
| 6 | **[`openwrt-imagebuilder`](skills/openwrt-imagebuilder/SKILL.md)** | Custom Firmware Compilation | Exact 16 MB Flash partition budgeting, package manifests, zero-waste `/overlay`, Cudy SPI flash revisions. |
| 7 | **[`openwrt-hardware-offloading`](skills/openwrt-hardware-offloading/SKILL.md)** | Silicon Acceleration | MediaTek PPE (Packet Processing Engine) + WED (Wireless Ethernet Dispatch) vs Qualcomm NSS, SQM conflicts. |
| 8 | **[`openwrt-wifi-mesh`](skills/openwrt-wifi-mesh/SKILL.md)** | Roaming & 802.11s Mesh | 802.11r/k/v Fast Transition, lightweight `usteer` band steering (-73 dBm threshold), SAE mesh backhaul. |
| 9 | **[`openwrt-sqm-bufferbloat`](skills/openwrt-sqm-bufferbloat/SKILL.md)** | CAKE & Latency Mitigation | CAKE (`piece_of_cake.qos`), OpenWrt 25.12 multi-core `cake-mq`, PPPoE/fiber framing overhead, A+ grade tuning. |
| 10 | **[`openwrt-storage-failsafe`](skills/openwrt-storage-failsafe/SKILL.md)** | MTD & Unbrick Recovery | `/proc/mtd` partition tables, `factory`/ART backup preservation, Telnet Failsafe mode, U-Boot TFTP rescue. |

---

## 🛠️ Table of Hardware (ToH) Offline Query Tool

Included in `scripts/openwrt_hardware_query.py`, this tool queries a local compressed database (`data/openwrt_toh_cache.json.gz`) of **3,030 official OpenWrt devices** across 74 attributes.

### CLI Usage
```bash
# Query any router model (instant offline search)
python scripts/openwrt_hardware_query.py "Cudy WR3000"

# Query by brand, SoC, or architecture
python scripts/openwrt_hardware_query.py "Archer C7"
python scripts/openwrt_hardware_query.py "filogic"
```

### Automatic Channel Width Deduction (80 MHz vs 160 MHz)
The query tool analyzes chipset combinations (e.g. MediaTek MT7981 + MT7976C) to accurately report Wi-Fi 6 channel capabilities (`HE160` vs `HE80` vs `VHT80`) along with stock vs sysupgrade installation methods.

---

## 🛡️ Master AI Reviewer Prompt

Need a second opinion on a pull request, shell script, or LuCI modification?  
We include a battle-tested master reviewer prompt in [`docs/PROMPT-REVISOR-MESTRE-IA.md`](docs/PROMPT-REVISOR-MESTRE-IA.md).

Paste this prompt into Claude, ChatGPT, or Gemini before submitting code to enforce:
1. Flash & RAM budget impact analysis.
2. Dual OpenWrt generation compatibility (`fw3` vs `fw4`, `opkg` vs `apk`).
3. POSIX shell verification (no bashisms).
4. Mobile-first LuCI DOM containment (`min-width: 0`, 40px touch).
5. Anti-lockout and brick risk assessment.

---

## 🚀 Installation & Integration

### Google Antigravity / Gemini CLI
Clone or copy the skills into your workspace:
```bash
cp -r .agents/skills/ /path/to/your/workspace/.agents/skills/
```

### Cursor AI
Add this repository to your project or reference the rules in `.cursor/rules/`:
```bash
cp AGENTS.md /path/to/your/workspace/.cursorrules
```

### Claude Code / Windsurf / Roo Code / Cline
Simply point your agent workspace to `skills/` or `.agents/skills/`. All `SKILL.md` files feature standard YAML frontmatter recognized automatically by agentic frameworks.

---

## 📜 Architectural Directives Summary

1. **Hardware Budget**: Maintain `/overlay` free space $> 2.0\text{ MB}$. Keep theme compressed assets $< 60\text{ KB}$.
2. **Dual Generation**: Dynamically detect package manager (`which apk opkg`) and firewall backend (`command -v nft`).
3. **Touch Targets**: Minimum 40px useful height for buttons, badges, and toggles.
4. **Scroll Isolation**: Trapping scroll in LuCI requires locking `.main-right`, not `body`.
5. **No Synchronous Popups**: Never use `alert()` or `confirm()`.

---

## 🤝 Contributing

Contributions, bug reports, and new hardware profiles are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

Distributed under the [MIT License](LICENSE).
