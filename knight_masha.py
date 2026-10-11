"""A tiny pixel-art action game prototype made with pygame-ce.
Controls: A/D or arrows = move, SPACE = jump, J = attack, R = restart.
"""

import sys
import pygame

pygame.init()

# Draw at a small resolution, then enlarge it for a pixel-art look.
WIDTH, HEIGHT = 320, 180
SCALE = 3
WINDOW = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
pygame.display.set_caption("Knight: Save Princess Masha")
CANVAS = pygame.Surface((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 8, bold=True)
BIG_FONT = pygame.font.SysFont("consolas", 13, bold=True)
GROUND_Y = 151

SKY = (20, 29, 57)
WHITE = (245, 240, 218)
GOLD = (246, 199, 77)
GREEN = (71, 133, 75)
DARK_GREEN = (37, 78, 57)
BROWN = (105, 67, 54)
RED = (194, 66, 66)


def new_game():
    now = pygame.time.get_ticks()
    return {
        "player": pygame.Rect(35, GROUND_Y - 22, 10, 22),
        "vy": 0.0,
        "hp": 5,
        "facing": 1,
        "invulnerable_until": 0,
        "attack_until": 0,
        "next_attack": 0,
        "enemies": [],
        "killed": 0,
        "last_spawn": now - 1100,
        "boss": None,
        "state": "playing",
    }


def draw_text(surface, text, x, y, color=WHITE, font=FONT):
    surface.blit(font.render(text, False, color), (x, y))


def draw_background(surface):
    surface.fill(SKY)
    # Stars
    for x, y in [(20, 18), (70, 30), (112, 13), (170, 27), (223, 16), (289, 33)]:
        surface.fill(WHITE, (x, y, 1, 1))
    # Distant mountains
    pygame.draw.polygon(surface, (39, 52, 78), [(0, 118), (42, 66), (85, 118)])
    pygame.draw.polygon(surface, (32, 46, 69), [(65, 122), (131, 77), (192, 122)])
    pygame.draw.polygon(surface, (39, 52, 78), [(190, 120), (251, 61), (320, 120)])
    # Ground and little grass pixels
    pygame.draw.rect(surface, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(surface, GREEN, (0, GROUND_Y, WIDTH, 4))
    for x in range(3, WIDTH, 17):
        surface.fill(DARK_GREEN, (x, GROUND_Y + 8 + (x % 3), 5, 2))
        surface.fill((135, 89, 61), (x + 7, GROUND_Y + 18, 4, 2))


def draw_knight(surface, player, facing, attacking, invulnerable):
    # Blink after being hit.
    if invulnerable and pygame.time.get_ticks() // 90 % 2 == 0:
        return
    x, y = player.x, player.y
    # Boots, legs, body, helmet and visor
    pygame.draw.rect(surface, (48, 45, 61), (x + 1, y + 17, 4, 5))
    pygame.draw.rect(surface, (48, 45, 61), (x + 6, y + 17, 4, 5))
    pygame.draw.rect(surface, (55, 100, 143), (x + 1, y + 9, 9, 9))
    pygame.draw.rect(surface, (177, 189, 196), (x, y + 3, 11, 8))
    pygame.draw.rect(surface, (220, 225, 219), (x + 2, y, 7, 5))
    pygame.draw.rect(surface, (37, 45, 57), (x + (7 if facing > 0 else 1), y + 4, 3, 2))
    # Sword
    sword_x = x + 10 if facing > 0 else x - 5
    pygame.draw.rect(surface, (230, 230, 209), (sword_x, y + 10, 5, 2))
    if attacking:
        slash_x = x + 13 if facing > 0 else x - 15
        pygame.draw.rect(surface, GOLD, (slash_x, y + 6, 12, 2))
        pygame.draw.rect(surface, WHITE, (slash_x + 3, y + 4, 6, 1))


def draw_monster(surface, rect):
    pygame.draw.rect(surface, DARK_GREEN, (rect.x, rect.y + 4, rect.w, rect.h - 4))
    pygame.draw.rect(surface, (91, 169, 86), (rect.x + 1, rect.y, rect.w - 2, 9))
    pygame.draw.rect(surface, (248, 228, 175), (rect.x + 2, rect.y + 3, 2, 2))
    pygame.draw.rect(surface, (248, 228, 175), (rect.x + rect.w - 4, rect.y + 3, 2, 2))
    pygame.draw.rect(surface, (37, 47, 42), (rect.x + 3, rect.y + rect.h - 2, 3, 2))
    pygame.draw.rect(surface, (37, 47, 42), (rect.x + rect.w - 5, rect.y + rect.h - 2, 3, 2))


def draw_dragon(surface, rect):
    # Deliberately simple, blocky dragon placeholder.
    pygame.draw.polygon(surface, (119, 55, 69), [
        (rect.x + 4, rect.y + 10), (rect.x + 1, rect.y),
        (rect.x + 14, rect.y + 5), (rect.x + 21, rect.y + 2),
        (rect.x + 26, rect.y + 11),
    ])
    pygame.draw.rect(surface, (47, 128, 81), (rect.x + 4, rect.y + 8, 19, 13))
    pygame.draw.rect(surface, (66, 158, 94), (rect.x + 17, rect.y + 4, 12, 9))
    pygame.draw.rect(surface, (222, 75, 57), (rect.x + 27, rect.y + 8, 5, 3))
    pygame.draw.rect(surface, GOLD, (rect.x + 22, rect.y + 6, 2, 2))
    pygame.draw.rect(surface, (227, 210, 166), (rect.x + 7, rect.y + 20, 4, 4))
    pygame.draw.rect(surface, (227, 210, 166), (rect.x + 18, rect.y + 20, 4, 4))


def draw_princess(surface):
    x, y = 283, GROUND_Y - 20
    pygame.draw.rect(surface, (235, 198, 160), (x + 4, y, 7, 7))
    pygame.draw.rect(surface, GOLD, (x + 3, y - 2, 9, 3))
    pygame.draw.rect(surface, (180, 88, 139), (x + 2, y + 7, 11, 11))
    pygame.draw.rect(surface, (244, 220, 186), (x + 4, y + 18, 3, 3))
    pygame.draw.rect(surface, (244, 220, 186), (x + 9, y + 18, 3, 3))


def start_attack(game, now):
    if now < game["next_attack"]:
        return
    player = game["player"]
    facing = game["facing"]
    game["attack_until"] = now + 140
    game["next_attack"] = now + 360

    # Hit at most one monster per swing.
    for enemy in game["enemies"][:]:
        distance = (enemy["rect"].centerx - player.centerx) * facing
        close_enough = 0 < distance < 25
        aligned = abs(enemy["rect"].centery - player.centery) < 18
        if close_enough and aligned:
            enemy["hp"] -= 1
            if enemy["hp"] <= 0:
                game["enemies"].remove(enemy)
                game["killed"] += 1
            return

    boss = game["boss"]
    if boss:
        distance = (boss["rect"].centerx - player.centerx) * facing
        if 0 < distance < 31 and abs(boss["rect"].centery - player.centery) < 22:
            boss["hp"] -= 1
            if boss["hp"] <= 0:
                game["boss"] = None
                game["state"] = "won"


def main():
    game = new_game()
    running = True

    while running:
        dt = min(CLOCK.tick(60) / 16.6667, 2.0)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game["state"] != "playing":
                    game = new_game()
                elif event.key == pygame.K_j and game["state"] == "playing":
                    start_attack(game, now)

        keys = pygame.key.get_pressed()
        player = game["player"]

        if game["state"] == "playing":
            # Movement
            move = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move += 1
            if move:
                player.x += round(move * 1.6 * dt)
                game["facing"] = 1 if move > 0 else -1
            player.x = max(2, min(WIDTH - player.w - 2, player.x))

            # Jump and gravity
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and player.bottom >= GROUND_Y:
                game["vy"] = -4.4
            game["vy"] += 0.25 * dt
            player.y += round(game["vy"] * dt)
            if player.bottom >= GROUND_Y:
                player.bottom = GROUND_Y
                game["vy"] = 0

            # Spawn up to five monsters, then introduce the dragon.
            if game["killed"] < 5 and len(game["enemies"]) < 2 and now - game["last_spawn"] > 1650:
                monster = pygame.Rect(WIDTH - 24, GROUND_Y - 14, 12, 14)
                game["enemies"].append({"rect": monster, "hp": 2})
                game["last_spawn"] = now

            if game["killed"] >= 5 and not game["enemies"] and game["boss"] is None:
                game["boss"] = {"rect": pygame.Rect(WIDTH - 52, GROUND_Y - 25, 32, 25), "hp": 10}

            # Monsters follow the knight.
            for enemy in game["enemies"]:
                rect = enemy["rect"]
                if rect.centerx < player.centerx:
                    rect.x += max(1, round(0.45 * dt))
                elif rect.centerx > player.centerx:
                    rect.x -= max(1, round(0.45 * dt))
                rect.bottom = GROUND_Y
                if player.colliderect(rect) and now > game["invulnerable_until"]:
                    game["hp"] -= 1
                    game["invulnerable_until"] = now + 850
                    if game["hp"] <= 0:
                        game["state"] = "lost"

            # The dragon slowly closes the distance.
            boss = game["boss"]
            if boss:
                rect = boss["rect"]
                if rect.centerx < player.centerx - 24:
                    rect.x += max(1, round(0.35 * dt))
                elif rect.centerx > player.centerx + 24:
                    rect.x -= max(1, round(0.35 * dt))
                rect.bottom = GROUND_Y
                if player.colliderect(rect) and now > game["invulnerable_until"]:
                    game["hp"] -= 1
                    game["invulnerable_until"] = now + 850
                    if game["hp"] <= 0:
                        game["state"] = "lost"

        # Render everything at low resolution for crisp pixel scaling.
        draw_background(CANVAS)
        for enemy in game["enemies"]:
            draw_monster(CANVAS, enemy["rect"])
        if game["boss"]:
            draw_dragon(CANVAS, game["boss"]["rect"])
            draw_text(CANVAS, "DRAGON", 251, 7, (255, 165, 133))
            pygame.draw.rect(CANVAS, (65, 38, 45), (247, 18, 58, 5))
            pygame.draw.rect(CANVAS, RED, (248, 19, max(0, 56 * game["boss"]["hp"] // 10), 3))
        if game["state"] == "won":
            draw_princess(CANVAS)
        draw_knight(
            CANVAS,
            player,
            game["facing"],
            now < game["attack_until"],
            now < game["invulnerable_until"],
        )

        # HUD
        draw_text(CANVAS, f"HP: {max(0, game['hp'])}", 6, 6, (255, 150, 150))
        draw_text(CANVAS, f"MONSTERS: {game['killed']}/5", 6, 17)
        draw_text(CANVAS, "A/D: MOVE  SPACE: JUMP  J: ATTACK", 6, HEIGHT - 10, (220, 220, 203))

        if game["killed"] < 5 and game["state"] == "playing":
            draw_text(CANVAS, "Defeat the monsters!", 103, 6, GOLD)
        elif game["killed"] >= 5 and game["boss"] and game["state"] == "playing":
            draw_text(CANVAS, "THE DRAGON!", 116, 6, GOLD)

        if game["state"] == "won":
            pygame.draw.rect(CANVAS, (17, 28, 37), (42, 58, 236, 43))
            pygame.draw.rect(CANVAS, GOLD, (42, 58, 236, 43), 2)
            draw_text(CANVAS, "YOU SAVED PRINCESS MASHA!", 69, 69, GOLD, BIG_FONT)
            draw_text(CANVAS, "Press R to play again", 102, 88)
        elif game["state"] == "lost":
            pygame.draw.rect(CANVAS, (17, 28, 37), (70, 64, 180, 35))
            pygame.draw.rect(CANVAS, RED, (70, 64, 180, 35), 2)
            draw_text(CANVAS, "THE KNIGHT HAS FALLEN", 88, 73, (255, 150, 150), BIG_FONT)
            draw_text(CANVAS, "Press R to try again", 103, 88)

        pygame.transform.scale(CANVAS, WINDOW.get_size(), WINDOW)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
