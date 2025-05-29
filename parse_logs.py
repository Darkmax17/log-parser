import os
import sys
import json
import re
from collections import Counter

def parse_log_file(filepath):
    total_requests = 0
    method_counter = Counter()
    ip_counter = Counter()
    longest_requests = []

    # Шаблон строки access.log
    log_pattern = re.compile(
        r'(?P<ip>\S+) - - \[(?P<datetime>[^\]]+)\] '
        r'"(?P<method>\S+)\s(?P<url>\S+)\s\S+" '
        r'(?P<status>\d+) (?P<bytes>\S+) '
        r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<duration>\d+)'
    )

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_requests += 1
            match = log_pattern.match(line)
            if not match:
                continue

            data = match.groupdict()
            ip = data["ip"]
            method = data["method"]
            duration = int(data["duration"])

            ip_counter[ip] += 1
            method_counter[method] += 1

            longest_requests.append({
                "ip": ip,
                "method": method,
                "url": data["url"],
                "duration": duration,
                "datetime": data["datetime"]
            })

    # Топ 3 по длительности
    longest_requests = sorted(longest_requests, key=lambda x: x["duration"], reverse=True)[:3]

    return {
        "total_requests": total_requests,
        "methods": dict(method_counter),
        "top_ips": ip_counter.most_common(3),
        "longest_requests": longest_requests
    }

def save_stats_to_json(log_path, stats):
    os.makedirs("results", exist_ok=True)
    base_name = os.path.basename(log_path)
    json_path = os.path.join("results", base_name + ".json")
    with open(json_path, "w") as f:
        json.dump(stats, f, indent=2)

def print_stats_to_console(log_path, stats):
    print(f"\n📄 Статистика для файла: {log_path}")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

def main(path):
    if os.path.isfile(path):
        log_files = [path]
    elif os.path.isdir(path):
        log_files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
    else:
        print(f"❌ Ошибка: путь не найден: {path}")
        return

    for log_file in log_files:
        stats = parse_log_file(log_file)
        save_stats_to_json(log_file, stats)
        print_stats_to_console(log_file, stats)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️ Использование: python parse_logs.py <путь к лог-файлу или директории>")
        sys.exit(1)
    main(sys.argv[1])