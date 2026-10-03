# Lessons from ARK Router

These are reusable engineering observations drawn from the local ARK Router checkout (`GitHub/luci-app-ark-router`, remote [Despensativo/ark-router](https://github.com/Despensativo/ark-router)). Paths below refer to that checkout and may be ahead of the published revision. They describe implemented patterns, not a certification of every router, firmware image, or release. Check the current source and target device before applying them.

## Runtime compatibility

- Treat package management and firewall as separate capabilities. Standard OpenWrt 24.10 and older images use `opkg`; 25.12 and newer use `apk`. Standard OpenWrt 22.03 and newer images use `fw4`/nftables. A custom image may differ, so inspect the installed commands and active service.
- Do not invoke `iptables` merely to probe a `fw4` router. ARK Router's `root/usr/lib/ark/common.sh` provides `is_fw4` and `is_fw3`; scripts using it select one backend. DSA versus `swconfig` also depends on the target, not just the release number.

## Cheap status on small CPUs

- Cache expensive hardware, station, fingerprint, and performance queries in bounded files under `/tmp`. The implementation uses timestamp files and short TTLs in `root/usr/lib/ark/modules/{system,devices}.sh`.
- Invalidate only affected entries from DHCP hooks and `hotplug.d/net` or `hotplug.d/iface`. See `root/usr/lib/ark/dhcp_fingerprint.sh` and `root/etc/hotplug.d/{net,iface}/95-ark-cache-invalidate`. A cache must tolerate missing or corrupt timestamps and a reboot that clears `/tmp`.
- `mwan3` track files in `/var/run/mwan3track` can provide cheap status snapshots; ARK Router's `mwan_status_fast` in `root/usr/lib/ark/modules/network.sh` uses them. Tracker status is not proof of end-to-end traffic or failover. Verify with route and traffic tests when changing policy.
- Measure cold and warm paths separately, under the same load, and report the router model, firmware and code revision. Historical timing claims in a changelog do not automatically transfer to other devices.

## LuCI layout and browser cache

- For a content area with a sidebar, `100vw` may include the desktop scrollbar gutter and create horizontal overflow. Use a width relative to the containing element where appropriate, and test the actual scroll owner. The ARK theme's `cascade.css` and `mobile.css` contain the corresponding layout fixes.
- Build radio controls from detected radios rather than assuming two bands. ARK Router's `ark-theme.js` uses `getOrCreateRadioCard()` for a variable radio count. Preserve LuCI custom elements such as `<cbi-dropdown>` while translating or restyling surrounding content.
- A modal backdrop must continue to cover the viewport while its card remains responsive. Restore scroll and pointer state after closing the modal, including error paths.
- For split locale bundles and cached assets, stamp the bundle and locale files from one version source. ARK Router's `scripts/build_frontend_bundle.py`, `src/core/i18n/loader.js`, and `src/modules/render.js` show this pattern. Test a version mismatch and each locale in a browser; a successful build alone does not prove loading.

## Wi-Fi and SQM safety

- When offering per-band Wi-Fi switches, reject a request that disables every available management band in both the UI and backend. ARK Router's `src/modules/wifi.js` and `root/usr/lib/ark/modules/wifi.sh` implement this guard. An alternate wired management path should still be verified before changing a live router.
- CAKE throughput is device, topology, and configuration dependent. Do not promise a fixed ceiling or assume PPE and SQM can accelerate the same traffic path. Test latency under load, throughput, and CPU with and without offload. An upload-only shaper is a possible compromise when measured upload congestion is the bottleneck, not a universal fix.

## Evidence and release hygiene

- Distinguish static inspection, simulator or browser checks, virtual machine tests, and physical router tests. Record the code or package revision for each result; a generated report or old screenshot does not prove a new build survived reboot or preserved traffic.
- Keep firmware images, backups, packet captures, credentials and private operating notes out of this skills repository. Publish redistributable binary artifacts through a release channel only after target, hash, compatibility and provenance checks.

## External references

- [OpenWrt package management](https://openwrt.org/docs/guide-user/additional-software/managing_packages)
- [OpenWrt 22.03 release notes on firewall4](https://openwrt.org/releases/22.03/notes-22.03.0)
- [OpenWrt firewall configuration](https://openwrt.org/docs/guide-user/firewall/firewall_configuration)
