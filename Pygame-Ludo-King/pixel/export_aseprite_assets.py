import os
import subprocess

def export_aseprite(file_path, output_dir):
    # Đường dẫn đầy đủ tới aseprite.exe
    aseprite_path = r"C:\Program Files\Aseprite\aseprite.exe"  # Cập nhật đường dẫn này

    # Kiểm tra sự tồn tại của file .aseprite
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    sprite_sheet_path = os.path.join(output_dir, "Warrior_Blue.png")
    json_path = os.path.join(output_dir, "Warrior_Blue.json")

    command = [
        aseprite_path,
        "-b", file_path,
        "--sheet", sprite_sheet_path,
        "--data", json_path,
        "--sheet-pack",
        "--list-tags"
    ]

    subprocess.run(command, check=True)
    print(f"Exported {file_path} to {sprite_sheet_path} and {json_path}")

if __name__ == "__main__":
    # Đường dẫn đầy đủ tới file Warrior_Blue.aseprite
    aseprite_file = r"E:\Ki2_Nam3\tritue\game\Ludo-AI\Pygame-Ludo-King\pixel\Warrior_Blue.aseprite"
    output_directory = "./assets"  # Thư mục xuất file
    os.makedirs(output_directory, exist_ok=True)
    export_aseprite(aseprite_file, output_directory)
