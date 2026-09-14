#!/usr/bin/env python3
"""
OpenWrt Hardware Query Tool (ARK Router)
Searches and inspects the complete official OpenWrt Table of Hardware (3,000+ devices).
Offline-first with automatic local compressed cache.
"""

import os
import sys
import gzip
import json
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CACHE_FILE = os.path.join(DATA_DIR, 'openwrt_toh_cache.json.gz')
SCRATCH_TEST = os.path.join(PROJECT_ROOT, 'scratch', 'test_toh.json')
TOH_URL = "https://openwrt.org/toh.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
REFERER = "https://toh.openwrt.org/"


def ensure_data_directory():
    os.makedirs(DATA_DIR, exist_ok=True)


def download_toh(force=False):
    ensure_data_directory()
    if os.path.exists(CACHE_FILE) and not force:
        return

    # Check if scratch test file exists
    temp_json = None
    if os.path.exists(SCRATCH_TEST) and not force:
        temp_json = SCRATCH_TEST
    else:
        print("[*] Baixando a base oficial da OpenWrt Table of Hardware (3.000+ modelos)...")
        temp_download = os.path.join(DATA_DIR, 'temp_toh.json')
        cmd = [
            'curl.exe' if sys.platform == 'win32' else 'curl',
            '-s',
            '-A', USER_AGENT,
            '-e', REFERER,
            TOH_URL,
            '-o', temp_download
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, check=True)
            temp_json = temp_download
        except Exception as e:
            print(f"[!] Erro ao baixar toh.json via curl: {e}", file=sys.stderr)
            if os.path.exists(SCRATCH_TEST):
                temp_json = SCRATCH_TEST
            else:
                sys.exit(1)

    print("[*] Compactando e indexando base de dados localmente...")
    with open(temp_json, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)

    with gzip.open(CACHE_FILE, 'wt', encoding='utf-8') as f:
        json.dump(data, f)

    if temp_json != SCRATCH_TEST and os.path.exists(temp_json):
        try:
            os.remove(temp_json)
        except OSError:
            pass
    print(f"[+] Base OpenWrt gravada com sucesso em {CACHE_FILE} ({os.path.getsize(CACHE_FILE) // 1024} KB)")


def load_toh():
    download_toh()
    with gzip.open(CACHE_FILE, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('columns', []), data.get('entries', [])


def format_val(v):
    if v is None:
        return "-"
    s = str(v).strip()
    return s if s else "-"


def determine_pkg_manager(rel):
    s = str(rel).lower()
    if any(v in s for v in ['24.', '25.', 'snapshot', 'master']):
        return 'apk'
    return 'opkg'


def deduce_channel_width(d):
    wlan5 = str(d.get('wlan50ghz', '')).lower()
    wlan6 = str(d.get('wlan600ghz', '')).lower()
    hw = str(d.get('wlanhardware', '')).lower()
    comm = str(d.get('wlancomments', '')).lower()
    model = str(d.get('model', '')).lower()

    if '160' in comm or '160mhz' in comm:
        return "Até 160 MHz (Confirmado em comentários)"

    if wlan6 and wlan6 != '-' and wlan6 != 'none':
        return "Até 160 MHz / 320 MHz (Wi-Fi 6E / Wi-Fi 7)"

    # Chips Wi-Fi 6 com suporte nativo a 160 MHz (HE160)
    chips_160 = ['mt7976', 'mt7986', 'mt7915', 'ipq807', 'ipq60', 'qcn9074', 'qcn9024', 'bcm43684', 'ax200', 'ax210']
    if any(c in hw for c in chips_160) or any(m in model for m in ['3000', '5400', '6000', '11000']):
        if 'ax' in wlan5:
            return "Até 160 MHz (HE160 - Alta velocidade 2.4 Gbps)"

    # Wi-Fi 5 com Wave 2 (160 MHz)
    if any(c in hw for c in ['qca9984', 'bcm4366']):
        return "Até 160 MHz (VHT160 / 80+80 MHz)"

    # Wi-Fi 6 de entrada (80 MHz)
    if 'ax' in wlan5:
        return "Até 80 MHz (HE80)"

    # Wi-Fi 5 padrão (80 MHz)
    if 'ac' in wlan5:
        return "Até 80 MHz (VHT80)"

    # Wi-Fi 4 (40 MHz)
    if 'n' in wlan5 or 'n' in str(d.get('wlan24ghz', '')).lower():
        return "Até 40 MHz (HT40)"

    return "20 MHz / Desconhecido"


def search_devices(entries, cols, args):
    results = []
    q = args.query.lower() if args.query else None
    b = args.brand.lower() if args.brand else None
    m = args.model.lower() if args.model else None
    s = args.soc.lower() if args.soc else None
    t = args.target.lower() if args.target else None

    for entry in entries:
        d = dict(zip(cols, entry))
        brand = str(d.get('brand', '')).lower()
        model = str(d.get('model', '')).lower()
        cpu = str(d.get('cpu', '')).lower()
        target = str(d.get('target', '')).lower()
        subtarget = str(d.get('subtarget', '')).lower()
        wlan2 = str(d.get('wlan24ghz', '')).lower()
        wlan5 = str(d.get('wlan50ghz', '')).lower()
        rel = str(d.get('supportedcurrentrel', '')).lower()

        # Free-text search
        if q:
            blob = f"{brand} {model} {cpu} {target} {subtarget} {wlan2} {wlan5} {rel}"
            if q not in blob:
                continue

        if b and b not in brand:
            continue
        if m and m not in model:
            continue
        if s and s not in cpu:
            continue
        if t and (t not in target and t not in subtarget):
            continue

        if args.min_ram:
            try:
                ram = float(d.get('rammb', 0) or 0)
                if ram < args.min_ram:
                    continue
            except (ValueError, TypeError):
                continue

        if args.min_flash:
            try:
                flash = float(d.get('flashmb', 0) or 0)
                if flash < args.min_flash:
                    continue
            except (ValueError, TypeError):
                continue

        results.append(d)

    return results


def print_device_card(d, idx, verbose=False):
    brand = format_val(d.get('brand'))
    model = format_val(d.get('model'))
    version = format_val(d.get('version'))
    cpu = format_val(d.get('cpu'))
    cores = format_val(d.get('cpucores'))
    mhz = format_val(d.get('cpumhz'))
    ram = format_val(d.get('rammb'))
    flash = format_val(d.get('flashmb'))
    target = format_val(d.get('target'))
    subtarget = format_val(d.get('subtarget'))
    wlan2 = format_val(d.get('wlan24ghz'))
    wlan5 = format_val(d.get('wlan50ghz'))
    wlan6 = format_val(d.get('wlan600ghz'))
    wlan_hw = format_val(d.get('wlanhardware'))
    wlan_drv = format_val(d.get('wlandriver'))
    wlan_comm = format_val(d.get('wlancomments'))
    sw_chip = format_val(d.get('switch'))
    eth_100 = format_val(d.get('ethernet100mports'))
    eth_gbe = format_val(d.get('ethernetgbitports'))
    eth_25g = format_val(d.get('ethernet2_5gports'))
    recovery = format_val(d.get('recoverymethods'))
    install = format_val(d.get('installationmethods'))
    rel = format_val(d.get('supportedcurrentrel'))
    pkg_mgr = determine_pkg_manager(rel)
    bandwidth = deduce_channel_width(d)

    print(f"[{idx}] {brand} {model} (Revisão: {version})")
    print(f"  SoC / CPU:       {cpu} ({cores} core(s) @ {mhz} MHz)")
    print(f"  Memória / Flash: RAM {ram} MB | Flash {flash} MB")
    print(f"  OpenWrt Target:  {target} / {subtarget} (Gerenciador: {pkg_mgr})")
    print(f"  Wi-Fi Protocolo: 2.4G: {wlan2} | 5G: {wlan5}" + (f" | 6G: {wlan6}" if wlan6 != '-' else ""))
    print(f"  Largura de Canal:{bandwidth}")
    print(f"  Wi-Fi Hardware:  Chips: {wlan_hw} | Driver Linux: {wlan_drv}")
    if wlan_comm != '-':
        print(f"  MIMO / Antenas:  {wlan_comm}")
    print(f"  Rede / Switch:   Switch: {sw_chip} | 1G: {eth_gbe} | 2.5G: {eth_25g} | 100M: {eth_100}")
    print(f"  Métodos Unbrick: Recuperação: {recovery} | Instalação: {install}")
    print(f"  Versão OpenWrt:  {rel}")
    print("-" * 72)


def main():
    parser = argparse.ArgumentParser(description="Consulta de Hardware e Especificações da OpenWrt Table of Hardware")
    parser.add_argument('query', nargs='?', help="Termo de busca livre (ex: 'wr3000', 'dgl-5500', 'archer')")
    parser.add_argument('--brand', '-b', help="Filtrar por marca (ex: cudy, d-link, tp-link, xiaomi)")
    parser.add_argument('--model', '-m', help="Filtrar por modelo")
    parser.add_argument('--soc', '-s', help="Filtrar por processador/SoC (ex: mt7981, qca9558, mt7621)")
    parser.add_argument('--target', '-t', help="Filtrar por arquitetura OpenWrt (ex: filogic, ath79, ramips)")
    parser.add_argument('--min-ram', type=int, help="Filtrar por RAM mínima em MB (ex: 128)")
    parser.add_argument('--min-flash', type=int, help="Filtrar por Flash mínima em MB (ex: 16)")
    parser.add_argument('--limit', '-l', type=int, default=15, help="Limite de resultados exibidos (padrão 15)")
    parser.add_argument('--json', action='store_true', help="Retornar saída em formato JSON")
    parser.add_argument('--update', action='store_true', help="Forçar atualização da base oficial OpenWrt")

    args = parser.parse_args()

    if args.update:
        download_toh(force=True)
        if not args.query and not args.brand and not args.soc:
            return

    if not args.query and not args.brand and not args.model and not args.soc and not args.target:
        parser.print_help()
        sys.exit(0)

    cols, entries = load_toh()
    matches = search_devices(entries, cols, args)

    if args.json:
        print(json.dumps(matches[:args.limit], indent=2))
        return

    print("=" * 70)
    print(f"OPENWRT HARDWARE QUERY: {len(matches)} resultado(s) encontrado(s) (exibindo até {args.limit})")
    print("=" * 70)

    for i, d in enumerate(matches[:args.limit], 1):
        print_device_card(d, i)

    if len(matches) > args.limit:
        print(f"... e mais {len(matches) - args.limit} dispositivos. Refine sua busca.")


if __name__ == '__main__':
    main()
