import hashlib
import os
import struct
import sys
from pathlib import Path

import pygame

Q = 127707000586261266406140258152342164811114836442218367658989756920303451547391
P = 257
DIM = 512
PASSWORD_SHA256 = "fed99ec1e1ba1e504a432aede0f32956f2562d51b485aef41fdbc04e5ba33697"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
CANVAS_SIZE = 512
CELL_SIZE = CANVAS_SIZE // DIM
CANVAS_X = 40
CANVAS_Y = 40
DATA_PATH = Path("data.bin")
ENC_PATH = Path("enc.bin")
ENC_MAGIC = b"BDRW"
LWE_VALUE_BYTES = (Q.bit_length() + 7) // 8
STR_A_TO_Z = "abcdefghijklmnopqrstuvwxyz_0OABCDEFG"

def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def derive_secret(password_bytes):
    return [int.from_bytes(hashlib.sha256(bytes([b])).digest(), "big") for b in password_bytes]


def derive_message_vector(key_bytes):
    return list(key_bytes)


def mat_vec_mul(matrix, vector):
    out = []
    for row in matrix:
        total = 0
        for i in range(DIM):
            total = (total + row[i] * vector[i]) % Q
        out.append(total)
    return out


def build_matrix(grid):
    return [row[:] for row in grid]


def stream_xor_encrypt(plaintext, key_material):
    out = bytearray()
    for i, value in enumerate(plaintext):
        if i == 0:
            stream = key_material[i]
        else:
            stream = (key_material[i] * plaintext[i - 1]) & 0xff
        out.append(value ^ stream)
    return bytes(out)


def stream_xor_decrypt(ciphertext, key_material):
    out = bytearray()
    for i, value in enumerate(ciphertext):
        if i == 0:
            stream = key_material[i]
        else:
            stream = (key_material[i] * out[i - 1]) & 0xff
        out.append(value ^ stream)
    return bytes(out)


def pack_encrypted_payload(ciphertext, lwe):
    header = ENC_MAGIC + struct.pack(">I", len(ciphertext))
    body = b"".join(value.to_bytes(LWE_VALUE_BYTES, "big") for value in lwe)
    return header + ciphertext + body


def unpack_encrypted_payload(blob):
    min_size = len(ENC_MAGIC) + 4 + DIM * LWE_VALUE_BYTES
    if len(blob) < min_size:
        raise ValueError("enc.bin is too short")
    if blob[: len(ENC_MAGIC)] != ENC_MAGIC:
        raise ValueError("invalid enc.bin magic")
    ciphertext_len = struct.unpack(">I", blob[len(ENC_MAGIC) : len(ENC_MAGIC) + 4])[0]
    offset = len(ENC_MAGIC) + 4
    expected_size = offset + ciphertext_len + DIM * LWE_VALUE_BYTES
    if len(blob) != expected_size:
        raise ValueError("invalid enc.bin size")
    ciphertext = blob[offset : offset + ciphertext_len]
    c_offset = offset + ciphertext_len
    lwe = [
        int.from_bytes(
            blob[
                c_offset + i * LWE_VALUE_BYTES : c_offset + (i + 1) * LWE_VALUE_BYTES
            ],
            "big",
        )
        for i in range(DIM)
    ]
    return ciphertext, lwe


def encrypt_payload(grid, secret, plaintext):
    key_material = os.urandom(len(plaintext))
    message = derive_message_vector(key_material)
    error_bytes = os.urandom(DIM)
    error = list(error_bytes)
    matrix = build_matrix(grid)
    product = mat_vec_mul(matrix, secret)
    lwe = [(product[i] + P * error[i] + message[i]) % Q for i in range(DIM)]
    ciphertext = stream_xor_encrypt(plaintext, key_material)
    ENC_PATH.write_bytes(pack_encrypted_payload(ciphertext, lwe))
    return {"c": lwe, "e": error}


def decrypt_payload(grid, secret, package):
    error = package["e"]
    ciphertext, lwe = unpack_encrypted_payload(ENC_PATH.read_bytes())
    matrix = build_matrix(grid)
    product = mat_vec_mul(matrix, secret)
    message = [(lwe[i] - product[i] - P * error[i]) % Q for i in range(DIM)]
    if any(x > 255 for x in message):
        raise ValueError("invalid canvas or password")
    key_material = bytes(message)
    plaintext = stream_xor_decrypt(ciphertext, key_material)
    DATA_PATH.write_bytes(plaintext)


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen, (30, 30, 30), self.rect, border_radius=6)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class TextInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.value = ""
        self.active = True

    def draw(self, screen, font):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=6)
        masked = "*" * len(self.value)
        text = font.render(masked, True, (0, 0, 0))
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.unicode and event.unicode.isprintable():
                candidate = self.value + event.unicode
                if len(candidate.encode()) <= DIM:
                    self.value = candidate
        return False


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Draw n Crypt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.grid = [[0 for _ in range(DIM)] for _ in range(DIM)]
        self.state = "login"
        self.password_input = TextInput((250, 280, 400, 50))
        self.message = "Enter the 64-byte password"
        self.secret = None
        self.last_package = None
        self.drawing = False
        self.draw_value = 1
        self.encrypt_button = Button((620, 120, 180, 50), "Encrypt")
        self.decrypt_button = Button((620, 190, 180, 50), "Decrypt")
        self.clear_button = Button((620, 260, 180, 50), "Clear")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == "login":
                    self.handle_login(event)
                else:
                    self.handle_canvas(event)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_login(self, event):
        submitted = self.password_input.handle(event)
        if submitted:
            self.try_login()

    def try_login(self):
        password_bytes = self.password_input.value.encode()
        if len(password_bytes) != DIM:
            self.message = "Password must be exactly 64 bytes"
            return
        if sha256_hex(password_bytes) != PASSWORD_SHA256:
            self.message = "password value mismatch"
            return
        for c in self.password_input.value:
            if c not in STR_A_TO_Z:
                self.message = "a~z only"
                return
        self.secret = derive_secret(password_bytes)
        self.state = "canvas"
        self.message = "Ready"

    def handle_canvas(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.encrypt_button.hit(event.pos):
                self.encrypt_file()
                return
            if self.decrypt_button.hit(event.pos):
                self.decrypt_file()
                return
            if self.clear_button.hit(event.pos):
                self.grid = [[0 for _ in range(DIM)] for _ in range(DIM)]
                self.message = "Canvas cleared"
                return
            if self.on_canvas(event.pos):
                self.drawing = True
                row, col = self.canvas_cell(event.pos)
                self.draw_value = 0 if self.grid[row][col] else 1
                self.grid[row][col] = self.draw_value
        elif event.type == pygame.MOUSEBUTTONUP:
            self.drawing = False
        elif event.type == pygame.MOUSEMOTION and self.drawing and self.on_canvas(event.pos):
            row, col = self.canvas_cell(event.pos)
            self.grid[row][col] = self.draw_value

    def encrypt_file(self):
        try:
            plaintext = DATA_PATH.read_bytes()
        except FileNotFoundError:
            self.message = "data.bin not found"
            return
        try:
            self.last_package = encrypt_payload(self.grid, self.secret, plaintext)
            self.message = "enc.bin written"
        except Exception as exc:
            self.message = f"Encrypt failed: {exc}"

    def decrypt_file(self):
        if self.last_package is None:
            self.message = "No LWE state in current session"
            return
        try:
            decrypt_payload(self.grid, self.secret, self.last_package)
            self.message = "data.bin restored"
        except FileNotFoundError:
            self.message = "enc.bin not found"
        except Exception as exc:
            self.message = f"Decrypt failed: {exc}"

    def on_canvas(self, pos):
        x, y = pos
        return CANVAS_X <= x < CANVAS_X + CANVAS_SIZE and CANVAS_Y <= y < CANVAS_Y + CANVAS_SIZE

    def canvas_cell(self, pos):
        x, y = pos
        col = (x - CANVAS_X) // CELL_SIZE
        row = (y - CANVAS_Y) // CELL_SIZE
        return row, col

    def draw_login(self):
        self.screen.fill((230, 230, 230))
        title = self.font.render("Draw n Crypt", True, (0, 0, 0))
        prompt = self.small_font.render("credit @whale120", True, (0, 0, 0))
        hint = self.small_font.render(self.message, True, (120, 0, 0))
        self.screen.blit(title, (300, 180))
        self.screen.blit(prompt, (170, 230))
        self.password_input.draw(self.screen, self.font)
        self.screen.blit(hint, (250, 350))

    def draw_canvas(self):
        self.screen.fill((240, 240, 240))
        for row in range(DIM):
            for col in range(DIM):
                color = (0, 0, 0) if self.grid[row][col] else (255, 255, 255)
                rect = pygame.Rect(CANVAS_X + col * CELL_SIZE, CANVAS_Y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
        for i in range(DIM + 1):
            x = CANVAS_X + i * CELL_SIZE
            y = CANVAS_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, (180, 180, 180), (CANVAS_X, y), (CANVAS_X + CANVAS_SIZE, y), 1)
            pygame.draw.line(self.screen, (180, 180, 180), (x, CANVAS_Y), (x, CANVAS_Y + CANVAS_SIZE), 1)
        pygame.draw.rect(self.screen, (0, 0, 0), (CANVAS_X, CANVAS_Y, CANVAS_SIZE, CANVAS_SIZE), 2)
        self.encrypt_button.draw(self.screen, self.font)
        self.decrypt_button.draw(self.screen, self.font)
        self.clear_button.draw(self.screen, self.font)
        status = self.small_font.render(self.message, True, (0, 0, 0))
        self.screen.blit(status, (620, 340))

    def draw(self):
        if self.state == "login":
            self.draw_login()
        else:
            self.draw_canvas()


if __name__ == "__main__":
    App().run()
