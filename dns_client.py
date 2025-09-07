# dns_client.py
import dns.resolver

def dns_client(domain="example.com"):
    try:
        with open("dns_log.txt", "w") as log:
            # A record
            print("\n=== A Records ===")
            a_records = dns.resolver.resolve(domain, "A")
            for ip in a_records:
                print("A:", ip)
                log.write(f"A: {ip}\n")

            # MX record
            print("\n=== MX Records ===")
            mx_records = dns.resolver.resolve(domain, "MX")
            for mx in mx_records:
                print("MX:", mx)
                log.write(f"MX: {mx}\n")

            # CNAME record
            print("\n=== CNAME Records ===")
            try:
                cname_records = dns.resolver.resolve(domain, "CNAME")
                for cname in cname_records:
                    print("CNAME:", cname)
                    log.write(f"CNAME: {cname}\n")
            except dns.resolver.NoAnswer:
                print("No CNAME record found.")

        print("\nResults logged to dns_log.txt")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    dns_client("openai.com")
