# Cross-check of ARK Router Markdown

Inventory and targeted review of the Markdown in the local sibling `GitHub/luci-app-ark-router` checkout on 2026-10-03. High-risk claims were compared with current source where indicated; this was not a line-by-line audit or release approval. The ARK Router checkout was read only; its untracked files were left untouched. Source paths below refer to that checkout and may be ahead of its public GitHub revision.

## Conflicts to resolve in the ARK Router repository

| Priority | Evidence in ARK Router | Finding | Suggested correction |
| --- | --- | --- | --- |
| High | `AGENTS.md`, `docs/network-diagnostics.md`, `docs/VIRTUALBOX_TEST_ENVIRONMENT.md` | Across these guides, OpenWrt 22.03 is grouped with `fw3` and 24.10 with `apk`. These release boundaries are wrong for standard OpenWrt images. | Document package manager and firewall separately: `fw4` default since 22.03; `opkg` through 24.10; `apk` since 25.12. Still inspect custom images. |
| High | `docs/CUDY_WR3000_TFTP_RECOVERY.md` section 4 | Calls APK installation "sem mexer na Flash". A normal package install can consume writable `/overlay`; only files built into SquashFS avoid that cost at first boot. The same guide calls a three-file image check a guarantee of bootability. | Describe the APK path as avoiding firmware replacement, with an overlay space check. Treat build-time checks as necessary but insufficient for boot verification. |
| Medium | `README.md` later release paragraph, `docs/CUDY_WR3000_TFTP_RECOVERY.md`, `VERSION`, `Makefile` | Narrative calls 1.5.1 current or gives 1.5.1 install examples while the local source declares 1.5.8. A release tag and package still need separate verification. | Separate historical examples from current source version and published release; update examples at release time. |
| Medium | `docs/RELEASES.md` versus `docs/PUBLISHING.md` and `.github/workflows/build-packages.yml` | One guide presents tag-triggered GitHub Actions as the normal path, while the other recommends local packaging and direct upload. The workflow can run on tags or manual dispatch. | Choose one primary publishing runbook; describe the other as an alternative, then verify the final uploaded assets. |
| Medium | `docs/LIFECYCLE_INSTALL_AND_UNINSTALL_GUIDE.md` section 2.2 | Its example treats any matching XHR failure as success. A dropped RPC connection does not establish that uninstall finished. | Defer `rpcd`/`uhttpd` restart until after the response when possible, then query actual package/service state after reconnect. |
| Medium | `docs/hardware-budget.md`, `docs/PACKAGE_PROFILES.md`, `scripts/install.sh` | The guides describe 3500 KB Lite and 35000 KB Full as hard installation cutoffs. The shell check currently returns success when `df -k /overlay` reports no available space or cannot identify the mount, to accommodate rootfs-only environments. | Describe this exception and verify the filesystem type; on a flash-backed target, an unreadable space check should not be mistaken for sufficient space. |

The older `docs/audit/STATUS.md` explicitly identifies itself as a dated checkpoint and instructs readers to check Git; its 1.5.2 snapshot should not be presented as current evidence. Documentation-only or mocked checks do not prove an installed package, reboot, traffic or physical radio behavior.

## Practices worth carrying into skills

- **Size profiles:** `scripts/install.sh` defines an automatic Full choice at 480000 KB RAM and 35000 KB free `/overlay`, a Lite preinstall cutoff at 3500 KB, and a Lite warning below 6000 KB. These are ARK Router package thresholds, distinct from the general goal of keeping free overlay after installation. Recalculate from the actual unpacked footprint and dependencies whenever the package changes.
- **Install paths:** `docs/INSTALL.md`, `docs/PACKAGE_PROFILES.md` and `scripts/install.sh` distinguish manager-installed `.apk`/`.ipk` packages from source copying. Source mode does not register a package. A backup under `/tmp` is lost on reboot unless copied elsewhere.
- **DNS rollback:** `root/usr/lib/ark/modules/adblock.sh` captures previous DNS-related UCI values and restores them when disabling the local blocker. When designing such a flow, preserve user settings and test resolver failure/recovery. The code also has a fallback to public DNS when no saved servers are found; that is a product policy, not a universal safe default.
- **RPC lifecycle:** `root/usr/lib/ark/modules/{adblock,speedify}.sh` defers some web-service restarts in the background. Test the response and verify final state after reconnect; elapsed time or an HTTP response alone is not proof.

## External references

- [OpenWrt 22.03 release notes: firewall4](https://openwrt.org/releases/22.03/notes-22.03.0)
- [OpenWrt package management by release](https://openwrt.org/docs/guide-user/additional-software/managing_packages)
- [OpenWrt sysupgrade test and backup options](https://openwrt.org/docs/techref/sysupgrade)
