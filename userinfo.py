import hashlib
import os
try:
    from Crypto.Cipher import AES
except ImportError:
    print("❌ 缺少加密库，请先运行: pip3 install pycryptodome")
    exit()

AES_KEY = b"39653543fa0d66aa"
SALT = bytes.fromhex("01EE5E1D8BF781576754BE709301FFE9")

def get_cipher_size(total_len):
    # 逻辑：总长度 - 16字节MD5 - 4字节Flag
    # 然后向上取16的倍数，确保能被AES整除
    raw_size = total_len - 20
    return (raw_size // 16) * 16

def decrypt_flow():
    print("\n--- 📂 开始解包流程 (动态兼容版) ---")
    target = "userinfo.dat"
    if not os.path.exists(target):
        print(f"❌ 错误：找不到 {target}")
        return

    file_size = os.path.getsize(target)
    # 动态计算密文长度
    cipher_size = get_cipher_size(file_size)
    
    with open(target, "rb") as f:
        full_data = f.read()

    cipher_text = full_data[:cipher_size]
    print(f"📦 文件总长: {file_size}, 识别密文区域: {cipher_size}")

    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    try:
        # 尝试解密
        decrypted_data = cipher.decrypt(cipher_text).rstrip(b'\x00')
        with open("userinfo_final.plist", "wb") as f:
            f.write(decrypted_data)
        print("✅ 解包成功！")
    except Exception as e:
        print(f"❌ 解密出错: {e}")

def encrypt_flow():
    # 封包时也需要根据原始文件长度来决定结构
    print("\n--- 🔒 开始封包流程 (动态兼容版) ---")
    if not os.path.exists("userinfo_final.plist") or not os.path.exists("userinfo.dat"):
        return

    with open("userinfo.dat", "rb") as f:
        old_data = f.read()
    
    file_size = len(old_data)
    cipher_size = get_cipher_size(file_size)
    flag = old_data[cipher_size : cipher_size + 4]

    with open("userinfo_final.plist", 'rb') as f:
        plist_raw = f.read()
    
    # 动态填充
    padded_data = plist_raw.ljust(cipher_size, b'\x00')[:cipher_size]
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted_payload = cipher.encrypt(padded_data)

    # 计算校验
    hash_input = encrypted_payload + flag + SALT
    final_md5 = hashlib.md5(hash_input).digest()

    with open("userinfo_modified.dat", 'wb') as f:
        f.write(encrypted_payload + flag + final_md5)
    
    print(f"✅ 封包完成，已匹配原始结构长度: {file_size}")


def menu():
    while True:
        print("\n" + "="*30)
        print("   摩尔庄园集成工具 v1.1")
        print("="*30)
        print("1. 解包 (dat -> plist)")
        print("2. 封包 (plist -> dat)")
        print("q. 退出")
        choice = input("\n请选择操作 [1/2/q]: ").strip().lower()

        if choice == '1':
            decrypt_flow()
        elif choice == '2':
            encrypt_flow()
        elif choice == 'q':
            break

if __name__ == "__main__":
    menu()