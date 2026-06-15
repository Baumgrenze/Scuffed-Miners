"""
game.py — Hauptklasse: koordiniert alle Spielobjekte und verarbeitet Eingaben.
verarbeitet Input (wie Input.GetMouseButtonDown()),
und ruft Update() + Draw() jeden Frame auf.

Drücke F11 für Vollbild.
"""

import pygame
import sys
import visuals
from mine_shaft import MineShaft, MANAGER_COST as SHAFT_MGR_COST
from lift import Lift, LIFT_CAP_UPGRADES, LIFT_SPEED_UPGRADES, MANAGER_COST as LIFT_MGR_COST
from cart import Cart, CART_CAP_UPGRADES, CART_SPEED_UPGRADES
from ui import Button

# --- Bildschirm ---
SCREEN_W = 1060
SCREEN_H  = 680
FPS       = 60
# --- Position der Hauptstation (oben links, Andockpunkt für den Lift) ---
LIFT_X    = 55
STATION_X = 35
STATION_Y = 100
STATION_W = 64
STATION_H = 42
# --- Lore-Schiene ---
CART_LINE_Y    = STATION_Y + STATION_H // 2 + 4
CART_STATION_X = 940
# --- Schacht-Layout ---
SHAFT_X       = 108
SHAFT_W       = 590
SHAFT_H       = 110
SHAFT_GAP     = 8
SHAFT_START_Y = 152
NUM_SHAFTS    = 4
# --- Button-Panel rechts neben den Schächten ---
PANEL_X = SHAFT_X + SHAFT_W + 6
PANEL_W = 180                       # Breiter für "Manager"-Text
BTN_H   = 24

def _is_won(shafts, lift, cart):
    """Gibt True zurück wenn alles vollständig ausgebaut ist."""
    all_shafts_maxed = True
    for s in shafts:
        if not (s.unlocked and s.has_manager and len(s.miners) == 10):
            all_shafts_maxed = False
            break

    lift_maxed = (lift.cap_level   >= len(LIFT_CAP_UPGRADES) and
                  lift.speed_level >= len(LIFT_SPEED_UPGRADES) and
                  lift.has_manager)
    cart_maxed = (cart.cap_level   >= len(CART_CAP_UPGRADES) and
                  cart.speed_level >= len(CART_SPEED_UPGRADES))
    return all_shafts_maxed and lift_maxed and cart_maxed

class Game:
    """
    Hauptklasse des Spiels.
    """
    def __init__(self):
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Scuffed Miners  |  F11 = Vollbild")
        self.clock = pygame.time.Clock()

        self.font_large  = pygame.font.SysFont(None, 34)
        self.font_medium = pygame.font.SysFont(None, 21)
        self.font_small  = pygame.font.SysFont(None, 17)
        self.font_win    = pygame.font.SysFont(None, 80)
        self.font_win2   = pygame.font.SysFont(None, 36)

        self.coins         = 0
        self.message       = ""
        self.message_timer = 0.0
        self.avg_ore_value = 1.0  # Durchschnittlicher Münzwert pro Erz
        self.won           = False

        # Explosionsanimationen beim Freischalten von Schächten
        self.explosions = []

        # Schächte gleichmäßig untereinander erstellen
        self.shafts = [
            MineShaft(i, SHAFT_X, SHAFT_START_Y + i * (SHAFT_H + SHAFT_GAP), SHAFT_W, SHAFT_H)
            for i in range(NUM_SHAFTS)
        ]

        # Lift: fährt von der Station bis zum untersten Schacht
        shaft_centers_y = []
        for s in self.shafts:
            shaft_centers_y.append(s.y + s.h // 2)

        shaft_bottom_y = self.shafts[-1].y + self.shafts[-1].h
        self.lift = Lift(LIFT_X, STATION_Y + STATION_H, shaft_bottom_y, shaft_centers_y, SHAFT_H)

        # Lore: fährt zwischen Lift und Münzstation
        self.cart = Cart(STATION_X + STATION_W // 2, CART_STATION_X, CART_LINE_Y)

        self._build_buttons()

    #  Vollbild
    def toggle_fullscreen(self):
        """Schaltet zwischen Vollbild und Fenster-Modus um (F11)."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            flags = pygame.FULLSCREEN
        else:
            flags = 0   #flags ist eine zustandsvariable des fullscreens
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)

    #  Buttons erstellen
    def _build_buttons(self):
        half_w = (PANEL_W - 4) // 2  # Halbe Panel-Breite für zwei nebeneinander liegende Buttons

        # Je Schacht: Schürfen, Manager kaufen, Miner kaufen, Freischalten
        self.btn_mine      = []
        self.btn_manager   = []
        self.btn_add_miner = []
        self.btn_unlock    = []

        i = 0
        for shaft in self.shafts:
            row1_y   = shaft.y + 5
            row2_y   = shaft.y + 5 + BTN_H + 5
            center_y = shaft.y + (SHAFT_H - BTN_H) // 2

            self.btn_mine.append(
                Button(PANEL_X,              row1_y, half_w,  BTN_H, "Schuerfen",        (40, 100, 50)))
            self.btn_manager.append(
                Button(PANEL_X + half_w + 4, row1_y, half_w,  BTN_H,
                    f"Manager ({SHAFT_MGR_COST})",                                     (85, 45, 125), font_size=15))
            self.btn_add_miner.append(
                Button(PANEL_X,              row2_y, PANEL_W, BTN_H, "+Miner",            (65, 90, 145)))
            self.btn_unlock.append(
                Button(PANEL_X,              center_y, PANEL_W, BTN_H, "Freischalten",   (135, 80, 15)))

            i += 1

        # Lift-Buttons (unter den Schächten)
        lift_btn_y = self.shafts[-1].y + SHAFT_H + 12
        self.btn_lift_click   = Button(PANEL_X,              lift_btn_y,            half_w,  BTN_H,
                                       "Lift",                                               (40, 110, 170))
        self.btn_lift_mgr     = Button(PANEL_X + half_w + 4, lift_btn_y,            half_w,  BTN_H,
                                       f"Manager ({LIFT_MGR_COST})",                         (85, 45, 125), font_size=15)
        self.btn_lift_cap     = Button(PANEL_X,              lift_btn_y + BTN_H + 5, half_w,  BTN_H,
                                       "Lift Kap.",                                          (125, 80, 20))
        self.btn_lift_speed   = Button(PANEL_X + half_w + 4, lift_btn_y + BTN_H + 5, half_w,  BTN_H,
                                       "Lift Speed",                                         (80, 120, 30))

        # Lore-Buttons (oben rechts, über dem Panel)
        self.btn_cart_cap   = Button(PANEL_X,              8, half_w,  BTN_H + 2, "Lore Kap.",   (85, 115, 40))
        self.btn_cart_speed = Button(PANEL_X + half_w + 4, 8, half_w,  BTN_H + 2, "Lore Speed",  (40, 115, 85))

    #  Events verarbeiten
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Tastatur-Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

            if self.won:
                return  # Nach dem Sieg keine weiteren Eingaben

            # Schacht-Buttons
            i = 0
            for shaft in self.shafts:
                if not shaft.unlocked:
                    if self.btn_unlock[i].is_clicked(event):
                        if self._spend(shaft.unlock_cost, shaft.unlock,
                                    f"Schacht {i+1} freigeschaltet!"):
                            # Explosionsanimation starten
                            cx = shaft.x + shaft.w // 2
                            cy = shaft.y + shaft.h // 2
                            self.explosions.append(visuals.Explosion(cx, cy))
                else:
                    if self.btn_mine[i].is_clicked(event):
                        shaft.click_miners()
                    if self.btn_manager[i].is_clicked(event) and not shaft.has_manager:
                        self._spend(SHAFT_MGR_COST, shaft.hire_manager,
                                    f"Manager für Schacht {i+1} eingestellt!")
                    if self.btn_add_miner[i].is_clicked(event):
                        cost = shaft.next_miner_cost()
                        if cost is not None:
                            self._spend(cost, shaft.add_miner, f"+Miner in Schacht {i+1}!")
                        else:
                            self._msg("Schacht voll! (Max 10 Miner)")

                i += 1

            # Lift-Buttons
            if self.btn_lift_click.is_clicked(event):
                self.lift.click()
            if self.btn_lift_mgr.is_clicked(event) and not self.lift.has_manager:
                self._spend(LIFT_MGR_COST, self.lift.hire_manager, "Lift-Manager eingestellt!")
            if self.btn_lift_cap.is_clicked(event):
                upg = self.lift.next_cap_upgrade()
                if upg:
                    self._spend(upg[1], self.lift.do_cap_upgrade, f"Lift: {upg[0]}!")
            if self.btn_lift_speed.is_clicked(event):
                upg = self.lift.next_speed_upgrade()
                if upg:
                    self._spend(upg[1], self.lift.do_speed_upgrade, f"Lift: {upg[0]}!")

            # Lore-Buttons
            if self.btn_cart_cap.is_clicked(event):
                upg = self.cart.next_cap_upgrade()
                if upg:
                    self._spend(upg[1], self.cart.do_cap_upgrade, f"Lore: {upg[0]}!")
            if self.btn_cart_speed.is_clicked(event):
                upg = self.cart.next_speed_upgrade()
                if upg:
                    self._spend(upg[1], self.cart.do_speed_upgrade, f"Lore: {upg[0]}!") #preis, funktion, nachricht

    #  Helpers
    def _spend(self, cost, action, msg=""):
        """Gibt Münzen aus wenn genug vorhanden. Gibt True zurück bei Erfolg."""
        if self.coins >= cost:
            self.coins -= cost
            action()
            self._msg(msg)
            if _is_won(self.shafts, self.lift, self.cart):
                self.won = True
            return True
        else:
            self._msg(f"Zu wenig! (Brauche {cost})")
            return False

    def _msg(self, text):
        self.message       = text
        self.message_timer = 2.5

    #  Update — Spiellogik pro Frame
    def update(self, dt):
        """
        dt = Deltazeit (Sekunden seit letztem Frame), wie Time.deltaTime.
        """
        for shaft in self.shafts:
            shaft.update(dt)

        # Durchschnittlichen Münzwert berechnen (Mittelwert aller freigeschalteten Schächte)
        unlocked = []
        for s in self.shafts:
            if s.unlocked:
                unlocked.append(s)

        if unlocked:
            total = 0
            for s in unlocked:
                total += s.ore_value
            self.avg_ore_value = total / len(unlocked)

        # Lift: prüfen ob neues Erz in der Station angekommen ist
        ore_before       = self.lift.station_ore
        self.lift.update(dt, self.shafts)
        newly_deposited  = self.lift.station_ore - ore_before
        if newly_deposited > 0:
            self.cart.notify_ore(newly_deposited)

        # Lore: ore_loaded = sofort aus Anzeige abziehen, ore_delivered = Münzen gutschreiben
        ore_loaded, ore_delivered = self.cart.update(dt)
        if ore_loaded > 0:
            self.lift.station_ore = max(0, self.lift.station_ore - ore_loaded)
        if ore_delivered > 0:
            self.coins += int(ore_delivered * self.avg_ore_value)

        # Explosionen aktualisieren und fertige entfernen
        for e in self.explosions:
            e.update(dt)
        self.explosions = [e for e in self.explosions if not e.done]

        if self.message_timer > 0:
            self.message_timer -= dt

        self._update_button_labels()

    def _update_button_labels(self):
        """Button-Texte mit aktuellen Preisen und Status aktualisieren."""
        for i, shaft in enumerate(self.shafts):
            cost = shaft.next_miner_cost()
            self.btn_add_miner[i].text = f"+Miner ({cost})" if cost else "Miner MAX"
            self.btn_unlock[i].text    = f"Freischalten ({shaft.unlock_cost})"

        upg = self.lift.next_cap_upgrade()
        self.btn_lift_cap.text   = f"{upg[0]} ({upg[1]})" if upg else "Kap. MAX"
        upg = self.lift.next_speed_upgrade()
        self.btn_lift_speed.text = f"{upg[0]} ({upg[1]})" if upg else "Speed MAX"

        upg = self.cart.next_cap_upgrade()
        self.btn_cart_cap.text   = f"{upg[0]} ({upg[1]})" if upg else "Kap. MAX"
        upg = self.cart.next_speed_upgrade()
        self.btn_cart_speed.text = f"{upg[0]} ({upg[1]})" if upg else "Speed MAX"

    #  Draw — alles zeichnen
    def draw(self):

        visuals.draw_background(self.screen, SCREEN_W, SCREEN_H, SHAFT_START_Y)
        visuals.draw_hud(self.screen, SCREEN_W, self.coins,
                         self.message, self.message_timer,
                         self.font_large, self.font_medium, self.font_small)

        self.cart.draw(self.screen, self.avg_ore_value)
        self.lift.draw(self.screen, STATION_X, STATION_Y, STATION_W, STATION_H, self.avg_ore_value)

        # Panel-Hintergrund hinter den Schacht-Buttons
        panel_top = SHAFT_START_Y - 2
        panel_bot = self.shafts[-1].y + SHAFT_H + 2
        visuals.draw_panel(self.screen, PANEL_X, panel_top, PANEL_W, panel_bot - panel_top)

        # Schächte zeichnen
        i = 0
        for shaft in self.shafts:
            shaft.draw(self.screen)
            pygame.draw.line(self.screen, (55, 55, 75),
                            (PANEL_X - 3, shaft.y), (PANEL_X - 3, shaft.y + SHAFT_H), 1)

            if shaft.unlocked:
                if shaft.has_manager:
                    self.screen.blit(
                        self.font_small.render("Manager aktiv", True, (60, 230, 60)),
                        (PANEL_X + 4, shaft.y + 8))
                else:
                    self.btn_mine[i].draw(self.screen)
                    self.btn_manager[i].draw(self.screen)

                if shaft.next_miner_cost():
                    self.btn_add_miner[i].draw(self.screen)
                else:
                    self.screen.blit(
                        self.font_small.render("Miner: MAX", True, (130, 130, 130)),
                        (PANEL_X + 4, shaft.y + BTN_H + 12))
            else:
                self.btn_unlock[i].draw(self.screen)

            i += 1

        # Explosionsanimationen über den Schächten zeichnen
        for e in self.explosions:
            e.draw(self.screen)

        # Lift-Buttons
        lift_btn_y = self.shafts[-1].y + SHAFT_H + 12
        visuals.draw_panel(self.screen, PANEL_X, lift_btn_y - 2, PANEL_W, BTN_H * 2 + 14)
        self.btn_lift_click.draw(self.screen)
        if self.lift.has_manager:
            self.screen.blit(
                self.font_small.render("Manager aktiv", True, (60, 230, 60)),
                (PANEL_X + (PANEL_W // 2) + 2, lift_btn_y + 5))
        else:
            self.btn_lift_mgr.draw(self.screen)
        self.btn_lift_cap.draw(self.screen)
        self.btn_lift_speed.draw(self.screen)

        # Lore-Buttons (oben)
        self.btn_cart_cap.draw(self.screen)
        self.btn_cart_speed.draw(self.screen)

        # Farblegende
        legend = [
            ("Gelb   = Miner bereit",  (255, 220, 50)),
            ("Orange = am Minen",      (200, 140, 30)),
            ("Blau   = Lift",          (60,  140, 220)),
            ("Gruen  = Lore",          (60,  180,  80)),
        ]
        legend_y = self.shafts[-1].y + SHAFT_H + 14
        j = 0
        for text, color in legend:
            self.screen.blit(self.font_small.render(text, True, color),
                            (SHAFT_X, legend_y + j * 16))
            j += 1

        if self.won:
            visuals.draw_win_screen(self.screen, SCREEN_W, SCREEN_H, self.coins,
                                    self.font_win, self.font_win2, self.font_medium)

        pygame.display.flip()

    #  Hauptschleife
    def run(self):

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
