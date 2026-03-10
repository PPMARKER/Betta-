with open('ui/components.py', 'r') as f:
    content = f.read()

draw_old = """    def draw(self, surface):
        if not self.visible: return
        c = (60, 100, 150) if self.is_hovered else (40, 70, 110)
        pygame.draw.rect(surface, c, self.rect, border_radius=15)
        pygame.draw.rect(surface, (255, 215, 0) if self.is_hovered else (200, 200, 200), self.rect, width=2, border_radius=15)
        # Glow effect if hovered
        if self.is_hovered:
            glow = pygame.Surface((self.rect.width+6, self.rect.height+6), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 215, 0, 50), glow.get_rect(), border_radius=18)
            surface.blit(glow, (self.rect.x-3, self.rect.y-3))

        t = get_font("Tahoma", 16, bold=True).render(self.text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=self.rect.center))"""

draw_new = """    def draw(self, surface):
        if not self.visible: return
        # Draw background with gradient look
        color_top = (100, 150, 255) if self.is_hovered else (60, 100, 180)
        color_bot = (60, 100, 180) if self.is_hovered else (40, 70, 120)

        # Simple vertical gradient
        for i in range(self.rect.height):
            ratio = i / self.rect.height
            c = [int(color_top[j] * (1 - ratio) + color_bot[j] * ratio) for j in range(3)]
            pygame.draw.line(surface, c, (self.rect.x, self.rect.y + i), (self.rect.right, self.rect.y + i))

        # Draw border
        pygame.draw.rect(surface, (255, 255, 255) if self.is_hovered else (200, 200, 200), self.rect, width=2, border_radius=0) # line gradients don't support border radius well, keeping it sharp or using a mask

        if self.is_hovered:
            glow = pygame.Surface((self.rect.width+10, self.rect.height+10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 40), glow.get_rect())
            surface.blit(glow, (self.rect.x-5, self.rect.y-5))

        t = get_font("Tahoma", 15, bold=True).render(self.text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=self.rect.center))"""

# Actually, border radius is better. Let's use a simpler but polished draw.
draw_new_polished = """    def draw(self, surface):
        if not self.visible: return
        c_bg = (70, 120, 220) if self.is_hovered else (50, 90, 160)
        c_border = (255, 255, 255) if self.is_hovered else (180, 180, 180)

        # Outer Glow
        if self.is_hovered:
            for i in range(1, 4):
                pygame.draw.rect(surface, (255, 255, 255, 20), (self.rect.x-i, self.rect.y-i, self.rect.width+i*2, self.rect.height+i*2), border_radius=15+i)

        pygame.draw.rect(surface, c_bg, self.rect, border_radius=15)
        pygame.draw.rect(surface, c_border, self.rect, width=2, border_radius=15)

        t = get_font("Tahoma", 14, bold=True).render(self.text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=self.rect.center))"""

content = content.replace(draw_old, draw_new_polished)
with open('ui/components.py', 'w') as f:
    f.write(content)
