from PIL import Image
import os
import random
import hashlib

def generate_key_sequence(key, length):
    random.seed(hashlib.md5(str(key).encode()).hexdigest())
    return [random.randint(1, 255) for _ in range(length)]

def swap_pixels(pixels, width, height, key):
    random.seed(key)
    pixel_list = [(x, y) for x in range(width) for y in range(height)]
    shuffled_list = pixel_list.copy()
    random.shuffle(shuffled_list)

    original = {pos: pixels[pos] for pos in pixel_list}
    for orig, shuf in zip(pixel_list, shuffled_list):
        pixels[orig] = original[shuf]

def unswap_pixels(pixels, width, height, key):
    random.seed(key)
    pixel_list = [(x, y) for x in range(width) for y in range(height)]
    shuffled_list = pixel_list.copy()
    random.shuffle(shuffled_list)

    original = {shuf: pixels[orig] for orig, shuf in zip(pixel_list, shuffled_list)}
    for pos in pixel_list:
        pixels[pos] = original[pos]

def apply_math_encrypt(pixels, width, height, key):
    key_seq = generate_key_sequence(key, width * height)
    idx = 0
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            k = key_seq[idx]
            pixels[x, y] = (
                (r + k) % 256,
                (g + k * 2) % 256,
                (b + k * 3) % 256
            )
            idx += 1

def apply_math_decrypt(pixels, width, height, key):
    key_seq = generate_key_sequence(key, width * height)
    idx = 0
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            k = key_seq[idx]
            pixels[x, y] = (
                (r - k) % 256,
                (g - k * 2) % 256,
                (b - k * 3) % 256
            )
            idx += 1

def safe_save(image, base_path):
    filename, ext = os.path.splitext(base_path)
    counter = 1
    final_path = base_path
    while os.path.exists(final_path):
        final_path = f"{filename}_v{counter}{ext}"
        counter += 1
    image.save(final_path)
    return final_path

def process_image(image_path, key, method, mode='encrypt'):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            pixels = img.load()
            width, height = img.size

            if method == 'mathematical':
                if mode == 'encrypt':
                    apply_math_encrypt(pixels, width, height, key)
                else:
                    apply_math_decrypt(pixels, width, height, key)

            elif method == 'swap':
                if mode == 'encrypt':
                    swap_pixels(pixels, width, height, key)
                else:
                    unswap_pixels(pixels, width, height, key)

            elif method == 'hybrid':
                if mode == 'encrypt':
                    apply_math_encrypt(pixels, width, height, key)
                    swap_pixels(pixels, width, height, key)
                else:
                    unswap_pixels(pixels, width, height, key)
                    apply_math_decrypt(pixels, width, height, key)

            operation = "encrypted" if mode == 'encrypt' else "decrypted"
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            file_ext = os.path.splitext(image_path)[1]
            out_name = f"{operation}_{method}_{base_name}{file_ext}"
            saved_path = safe_save(img, out_name)
            print(f"[✅] Image {operation} successfully: {saved_path}")

    except FileNotFoundError:
        print("[❌] Image not found. Check your path.")
    except Exception as e:
        print(f"[❌] Error: {e}")

def main():
    print("\n🔐 Image Encryption & Decryption Tool")
    print("➤ Supports: Mathematical | Swap | Hybrid methods\n")

    image_path = input("📂 Enter image filename or full path: ").strip()
    if not os.path.exists(image_path):
        print("[❌] Error: File does not exist.")
        return

    print("\n1. Encrypt\n2. Decrypt")
    choice = input("👉 Choose operation (1/2): ").strip()
    if choice not in ['1', '2']:
        print("[❌] Invalid choice.")
        return

    print("\nMethods:\n1. Mathematical\n2. Swap\n3. Hybrid")
    method_map = {'1': 'mathematical', '2': 'swap', '3': 'hybrid'}
    method_input = input("👉 Choose method (1/2/3): ").strip()
    method = method_map.get(method_input)
    if not method:
        print("[❌] Invalid method.")
        return

    try:
        key = int(input("🔑 Enter encryption key (number): ").strip())
    except ValueError:
        print("[❌] Key must be numeric.")
        return

    mode = 'encrypt' if choice == '1' else 'decrypt'
    process_image(image_path, key, method, mode)

if __name__ == "__main__":
    main()