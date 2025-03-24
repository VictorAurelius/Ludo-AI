import pygame
import json

class SpriteAnimation:
    def __init__(self, json_file, sprite_sheet):
        with open(json_file) as f:
            self.data = json.load(f)
        self.sprite_sheet = pygame.image.load(sprite_sheet).convert_alpha()
        self.frames = self.data["frames"]
        self.current_frame = 0
        self.time_accumulator = 0
        self.frame_duration = 0.1  # Thời gian mỗi frame (giây)

    def set_tag(self, tag):
        self.tag = tag
        # Duyệt qua danh sách frameTags để tìm tag phù hợp
        for frame_tag in self.data["meta"]["frameTags"]:
            if frame_tag["name"] == tag:
                self.frame_indices = range(frame_tag["from"], frame_tag["to"] + 1)
                self.current_frame = 0
                return
        raise ValueError(f"Tag '{tag}' not found in frameTags")

    def update(self, dt):
        self.time_accumulator += dt
        if self.time_accumulator >= self.frame_duration:
            self.time_accumulator -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % len(self.frame_indices)

    def draw(self, surface, position):
        frame_index = self.frame_indices[self.current_frame]
        # Tạo khóa phù hợp với định dạng trong JSON
        frame_key = f"Warrior_Blue {frame_index}.aseprite"
        if frame_key not in self.frames:
            raise KeyError(f"Frame key '{frame_key}' not found in frames")
        frame_data = self.frames[frame_key]["frame"]  # Truy cập frame bằng khóa
        rect = pygame.Rect(frame_data["x"], frame_data["y"], frame_data["w"], frame_data["h"])
        surface.blit(self.sprite_sheet, position, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Load Aseprite animation
    aseprite_file = "./assets/Warrior_Blue.json"  # Cập nhật đường dẫn tới thư mục ./assets
    sprite_sheet = "./assets/Warrior_Blue.png"   # Cập nhật đường dẫn tới thư mục ./assets
    warrior = SpriteAnimation(aseprite_file, sprite_sheet)

    warrior.set_tag("Run")  # Đặt tag animation (Idle, Run, Attack, v.v.)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        warrior.update(clock.get_time() / 1000.0)  # Cập nhật animation
        warrior.draw(screen, (400, 300))  # Vẽ animation tại vị trí (400, 300)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
