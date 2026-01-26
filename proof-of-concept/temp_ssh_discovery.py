import argparse
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Adjust the import path to find switch_auth and rc4_crypto
# Assuming temp_ssh_discovery.py is in proof-of-concept/
# and switch_auth.py, rc4_crypto.py are also in proof-of-concept/
# If they are at the root, the import would be 'from switch_auth import SwitchSession'
try:
    from switch_auth import SwitchSession, SwitchAuthError, SwitchConnectionError
except ImportError:
    # Fallback if running from a different directory structure
    sys.path.append(str(Path(__file__).resolve().parent))
    from switch_auth import SwitchSession, SwitchAuthError, SwitchConnectionError


def main():
    parser = argparse.ArgumentParser(
        description="Discover SSH-related pages on a Binardat switch."
    )
    parser.add_argument("host", help="IP address or hostname of the switch")
    parser.add_argument("username", help="Username for switch login")
    parser.add_argument("password", help="Password for switch login")
    args = parser.parse_args()

    # Keywords to search for on pages
    ssh_keywords = [
        "ssh",
        "secure shell",
        "telnet",
        "remote access",
        "services",
        "service control",
        "enable",
        "disable",
        "port",
        "administration",
        "security",
        "management",
    ]

    print(f"Attempting to connect to http://{args.host}...")
    try:
        with SwitchSession(host=args.host) as session:
            print("Logging in...")
            if session.login(args.username, args.password):
                print("Login successful.")
            else:
                print("Login failed. Exiting.")
                return

            all_discovered_pages = []
            seen_urls = set()

            print("Fetching main page to discover navigation...")
            main_page_html = session.get_main_page()
            print("\n--- Main Page HTML Content (first 1000 chars) ---")
            print(main_page_html[:1000])
            print("---------------------------------------------------\n")



            # Helper function to mimic httpPostGet for GET requests
            def get_dynamic_page_content(path, params=None):
                timestamp = int(datetime.now().timestamp() * 1000) # Milliseconds timestamp
                query_params = f"stamp={timestamp}&page=inside"
                if params:
                    query_params += f"&{params}"
                full_path = f"{path.lstrip('/')}?{query_params}"
                return session.get_page(full_path)

            # Discover pages from initial HTML
            initial_pages = session.discover_pages(main_page_html)
            for item in initial_pages:
                if item["url"] not in seen_urls:
                    all_discovered_pages.append(item)
                    seen_urls.add(item["url"])

            print("--- Analyzing utility.js for menu data link ---")
            try:
                utility_js_content = session.get_page("/js/utility.js")
                # Search for menudatalink assignment
                match = re.search(r"menudatalink\s*=\s*['\"]([^'\"]+)['\"]", utility_js_content)
                if match:
                    menu_data_url = match.group(1)
                    print(f"Found menudatalink: {menu_data_url}")
                    if menu_data_url:
                        print(f"Attempting to fetch menu data from: {menu_data_url}")
                        try:
                            menu_data_content = session.get_page(menu_data_url)
                            print(f"--- Menu Data Content (first 500 chars) ---")
                            print(menu_data_content[:500])
                            print("------------------------------------------")
                            
                            js_menu_items = session.extract_menu_from_js(menu_data_content)
                            if js_menu_items:
                                for item in js_menu_items:
                                    if item["url"] not in seen_urls:
                                        all_discovered_pages.append(item)
                                        seen_urls.add(item["url"])
                                print(f"Successfully extracted {len(js_menu_items)} menu items from {menu_data_url}")
                            else:
                                print(f"No menu items extracted from {menu_data_url} using extract_menu_from_js.")

                        except (SwitchConnectionError, SwitchAuthError) as e:
                            print(f"Error fetching menu data from {menu_data_url}: {e}")
                        except Exception as e:
                            print(f"Unexpected error processing menu data from {menu_data_url}: {e}")
                else:
                    print("menudatalink assignment not found in utility.js")
            except (SwitchConnectionError, SwitchAuthError) as e:
                print(f"Error fetching /js/utility.js: {e}")
            except Exception as e:
                print(f"Unexpected error processing /js/utility.js: {e}")
            
            # --- Focus on ssh_get.cgi ---
            print("\n--- Fetching and printing content of ssh_get.cgi ---")
            try:
                ssh_config_html = get_dynamic_page_content("ssh_get.cgi")
                print(ssh_config_html)
            except (SwitchConnectionError, SwitchAuthError) as e:
                print(f"Error fetching ssh_get.cgi: {e}")
            except Exception as e:
                print(f"Unexpected error fetching ssh_get.cgi: {e}")
            print("----------------------------------------------------\n")




    except SwitchAuthError as e:
        print(f"Authentication error: {e}")
    except SwitchConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
