import copy
import ipaddress
import json
import re
import socket
import struct
from dataclasses import dataclass

import dns.resolver


@dataclass
class TextStyle:
    bold: bool | None = None
    italic: bool | None = None
    underlined: bool | None = None
    strikethrough: bool | None = None

    @classmethod
    def from_text_component(cls,textcomp:dict)->"TextStyle":
        return cls(
            bold = textcomp.get("bold"),
            italic = textcomp.get("italic"),
            underlined = textcomp.get("underlined"),
            strikethrough = textcomp.get("strikethrough"),
        )
    def overwrite_soft(self,overriding_style:"TextStyle"):
        if overriding_style.strikethrough is not None:
            self.strikethrough = overriding_style.strikethrough
        if overriding_style.underlined is not None:
            self.underlined = overriding_style.underlined
        if overriding_style.italic is not None:
            self.italic = overriding_style.italic
        if overriding_style.bold is not None:
            self.bold = overriding_style.bold



def write_var_int(value:int):
    out =  bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            out.append(byte | 0x80) # 7 bits + 1 continuation bit
        else:
            out.append(byte)   # 7 bits + nothing cause the continuation bit is already 0(e.g. no continuation since we are at the end)
            break
    return out

def read_var_int_from_stream(sock: socket.socket) -> int:
    value = 0
    shift = 0
    for _ in range(5):
        raw = sock.recv(1)
        if not raw:
            raise ConnectionError("Socket closed while reading VarInt")
        byte = raw[0]
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return value
        shift += 7
    raise ValueError("VarInt too long") # varint only can be 5 long

def read_bytes_for(sock: socket.socket, length: int) -> bytes:
    buf = bytearray()
    while len(buf) < length:
        chunk = sock.recv(length - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed while reading data")
        buf += chunk
    return bytes(buf)


def decode_var_int(bytes:bytes, offset=0):
    value = 0
    shift = 0
    for i in range(5):
      byte = bytes[i + offset]
      value |= (byte & 0x7F) << shift
      if not (byte & 0x80):
        return value, i + 1
      shift += 7
    raise ValueError("VarInt too long") # varint only can be 5 long

def write_string(s: str):
    data = s.encode('utf-8')
    return write_var_int(len(data)) + data

def build_handshake_packet(ip:str,port:int,protocol_version:int):
    packet = write_var_int(0x00) # packet id
    packet += write_var_int(protocol_version) # protocol version
    packet += write_string(ip) # server ip
    packet += struct.pack('>H', port) # port
    packet += write_var_int(1) # status state
    packet_length = write_var_int(len(packet))
    return packet_length + packet

def is_literal_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def resolve_server_ip(ip:str,port:int):
    if is_literal_ip(ip):
        return ip,port
    
    try:
        answers = dns.resolver.resolve(f"_minecraft._tcp.{ip}", "SRV")
        srv = answers[0]
        target_host = str(srv.target).rstrip(".")
        target_port = srv.port
        return target_host, target_port

    except BaseException:
      return ip, port
    

def query_server_status(ip:str,port:int=25565, protocol_version:int=777)-> dict: # 777 protocol version for 26.3
    target_ip,target_port = resolve_server_ip(ip,port)


    packet = build_handshake_packet(target_ip,target_port,protocol_version)
    status_packet = write_var_int(0x00)
    status_packet = write_var_int(len(status_packet)) + status_packet

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.settimeout(5)
      s.connect((target_ip, target_port))
      s.sendall(packet)
      s.sendall(status_packet)
      packet_length = read_var_int_from_stream(s)
      packet_data = read_bytes_for(s, packet_length)

      packet_id, offset = decode_var_int(packet_data)

      json_length, consumed = decode_var_int(packet_data,offset)
      offset += consumed

      json_bytes = packet_data[offset : offset + json_length]

      status = json.loads(json_bytes.decode("utf-8"))
      return status



def apply_text_effects(text:str,style:TextStyle)-> str:
    if not text.strip(): # dont apply for space only text components
        return text

    text = text.replace("*","\\*")
    text = text.replace("_","\\_")
    text = text.replace("~","\\~")
    if style.italic is True:
        text = "*" + text + "*"
    if style.bold is True:
        text = "**" + text + "**"
    if style.underlined is True:
        text = "__" + text + "__"
    if style.strikethrough is True:
        text = "~~" + text + "~~"
    return text


def loop_through_textlist(textlist:list,parentStyle:TextStyle)-> str:
    result = ""
    for textComp in textlist:
        if isinstance(textComp,str):
            result = result + textComp
            continue
        result = result + process_text_component(textComp,parentStyle)
    return result

def process_text_component(textcomp:dict,parentStyle:TextStyle)-> str:
    result = ""
    text = textcomp.get("text")
    if text is None: return "" # prevent non text component types

    style_copy = copy.deepcopy(parentStyle)
    textStyle = TextStyle.from_text_component(textcomp)
    style_copy.overwrite_soft(textStyle)
    newStyle = style_copy

    result = result + apply_text_effects(text,newStyle)
    if textcomp.get("extra") is not None:
        result = result + loop_through_textlist(textcomp.get("extra"),newStyle)
    return result

def collapse_markers(text: str) -> str:
    for marker in ["**", "__", "~~"]:
        pattern = re.escape(marker) + r'(.+?)' + re.escape(marker) + re.escape(marker) + r'(.+?)' + re.escape(marker)
        replacement = marker + r'\1\2' + marker
        prev = None
        while prev != text:
            prev = text
            text = re.sub(pattern, replacement, text)
    return text

def convert_raw_motd_to_markdown(description) -> str:
    if isinstance(description,list):
        result = loop_through_textlist(description,TextStyle())
    elif isinstance(description,dict):
        result =  process_text_component(description,TextStyle())
    elif isinstance(description,str):
        result =  apply_text_effects(description,TextStyle())
    else:
        return ""
    return collapse_markers(result)
