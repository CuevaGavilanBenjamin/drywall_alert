#!/usr/bin/env python3
"""
DryWall Client - Generador de Claves SSH
Equivalente a PuTTYgen en Python para generar pares de claves SSH
"""

import os
import argparse
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

def generate_ssh_key_pair(key_size=2048, output_dir="keys", key_name="drywall_key"):
    """
    Genera un par de claves SSH (privada y pública)
    
    Args:
        key_size (int): Tamaño de la clave en bits
        output_dir (str): Directorio de salida
        key_name (str): Nombre base para los archivos de clave
    """
    
    # Crear directorio si no existe
    keys_dir = Path(output_dir)
    keys_dir.mkdir(exist_ok=True)
    
    print(f"[KEYGEN] Generando par de claves SSH de {key_size} bits...")
    
    # Generar clave privada RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    
    # Obtener clave pública
    public_key = private_key.public_key()
    
    # Rutas de archivos
    private_key_path = keys_dir / f"{key_name}"
    public_key_path = keys_dir / f"{key_name}.pub"
    
    # Guardar clave privada en formato OpenSSH
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(private_key_path, 'wb') as f:
        f.write(private_pem)
    
    # Establecer permisos seguros para la clave privada (solo en Unix)
    if os.name != 'nt':  # No en Windows
        os.chmod(private_key_path, 0o600)
    
    # Guardar clave pública en formato OpenSSH
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    
    # Agregar comentario a la clave pública
    public_ssh_with_comment = f"{public_ssh.decode()} drywall@client\n"
    
    with open(public_key_path, 'w') as f:
        f.write(public_ssh_with_comment)
    
    print(f"[OK] Clave privada guardada: {private_key_path}")
    print(f"[OK] Clave pública guardada: {public_key_path}")
    
    # Mostrar información de la clave
    print(f"\n[INFO] Información de la clave:")
    print(f"  - Algoritmo: RSA")
    print(f"  - Tamaño: {key_size} bits")
    print(f"  - Formato: OpenSSH")
    
    # Mostrar clave pública para copiar
    print(f"\n[CLAVE PUBLICA] Para agregar al servidor:")
    print("=" * 60)
    print(public_ssh_with_comment.strip())
    print("=" * 60)
    
    return private_key_path, public_key_path

def convert_to_putty_format(private_key_path, output_path=None):
    """
    Convierte una clave privada OpenSSH al formato PuTTY (.ppk)
    Nota: Esta es una implementación básica, para uso real se recomienda usar PuTTYgen
    """
    if output_path is None:
        output_path = str(private_key_path) + ".ppk"
    
    print(f"[CONVERT] Convirtiendo a formato PuTTY: {output_path}")
    print("[WARNING] Para uso real, se recomienda usar PuTTYgen oficial")
    
    # Leer clave privada
    with open(private_key_path, 'rb') as f:
        private_key_data = f.read()
    
    # Crear archivo .ppk básico (formato simplificado)
    ppk_content = f"""PuTTY-User-Key-File-2: ssh-rsa
Encryption: none
Comment: drywall@client
Public-Lines: 6
{base64.b64encode(private_key_data).decode()}
Private-Lines: 14
{base64.b64encode(private_key_data).decode()}
Private-MAC: (simplified-format)
"""
    
    with open(output_path, 'w') as f:
        f.write(ppk_content)
    
    print(f"[OK] Archivo PuTTY guardado: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(
        description='Generador de claves SSH (PuTTYgen en Python)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python generate_keys.py                           # Generar con valores por defecto
  python generate_keys.py --key-size 4096          # Clave de 4096 bits
  python generate_keys.py --name mi_clave           # Nombre personalizado
  python generate_keys.py --putty                   # Incluir formato PuTTY
        """
    )
    
    parser.add_argument(
        '--key-size', 
        type=int, 
        default=2048, 
        choices=[1024, 2048, 4096],
        help='Tamaño de la clave en bits (default: 2048)'
    )
    
    parser.add_argument(
        '--output-dir', 
        default='keys',
        help='Directorio de salida (default: keys)'
    )
    
    parser.add_argument(
        '--name', 
        default='drywall_key',
        help='Nombre base para los archivos (default: drywall_key)'
    )
    
    parser.add_argument(
        '--putty', 
        action='store_true',
        help='Generar también formato PuTTY (.ppk)'
    )
    
    args = parser.parse_args()
    
    try:
        # Generar par de claves
        private_key_path, public_key_path = generate_ssh_key_pair(
            key_size=args.key_size,
            output_dir=args.output_dir,
            key_name=args.name
        )
        
        # Convertir a formato PuTTY si se solicita
        if args.putty:
            convert_to_putty_format(private_key_path)
        
        print(f"\n[COMPLETE] Generación de claves completada exitosamente")
        print(f"[NEXT] Copia la clave pública al servidor SFTP autorizado")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar claves: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
