import pygame
import sys
from mine_shaft import MineShaft, MANAGER_COST as SHAFT_MANAGER_COST
from lift import Lift, LIFT_UPGRADE_COSTS, MANAGER_COST as LIFT_MANAGER_COST
from cart import Cart, CART_UPGRADE_COSTS
from ui import Button

# ------------------------------------------------------------------ #
#  Konstanten
# ------------------------------------------------------------------ #
SCREEN_W  = 900
SCREEN_H  = 620
FPS       = 60

BG_COLOR   = (18, 18, 28)
GOLD_COLOR = (255, 210, 50)
WHITE      = (255, 255, 255)

NUM_SHAFTS  = 4
SHAFT_X     = 100       # Schächte fangen hier an (links ist Lift)
SHAFT_W     = 660
SHAFT_H     = 90
SHAFT_GAP   = 10        # Abstand zwischen Schächten
SHAFT_START_Y = 140     # Y des ersten Schachts

LIFT_X      = 60        # X-Position des Lifts (links von Schächten)
CART_LINE_Y = 75        # Y der Fahrlinie für die Lore
STATION_X   = 820       # X der Münzstation (rechts)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Scuffed Miners")
        self.clock  = pygame.time.Clock()

        self.font_large  = pygame.font.SysFont(None, 38)
        self.font_medium = pygame.font.SysFont(None, 24)
        self.font_small  = pygame.font.SysFont(None, 19)

        self.coins = 0

        # ---- Schächte ----
        self.shafts = []
        for i in range(NUM_SHAFTS):
            y = SHAFT_START_Y + i * (SHAFT_H + SHAFT_GAP)
            self.shafts.append(MineShaft(i, SHAFT_X, y, SHAFT_W, SHAFT_H))

        # ---- Lift ----
        shaft_mid_ys = [s.y + s.h // 2 for s in self.shafts]
        bottom_y     = self.shafts[-1].y + self.shafts[-1].h
        self.lift    = Lift(LIFT_X, CART_LINE_Y, bottom_y, shaft_mid_ys, SHAFT_H)

        # ---- Lore ----
        self.cart = Cart(LIFT_X + 12, STATION_X, CART_LINE_Y)

        # ---- Buttons (rechts, Panel) ----
        self._build_buttons()

        self.message      = ""      # Feedback-Text oben
        self.message_timer = 0.0

    # ------------------------------------------------------------------ #
    #  Button-Aufbau
    # ------------------------------------------------------------------ #
    def _build_buttons(self):
        """Baut alle Buttons für Schächte, Lift und Lore."""
        bx = SHAFT_X + SHAFT_W + 5   # Rechts vom Schacht-Bereich... passt nicht, Panel links
        # Buttons sind rechts im Schacht selbst (schmaler Streifen)
        # Wir nutzen die letzten 160px des Schachts als Button-Bereich

        btn_x  = SHAFT_X + SHAFT_W - 158
        btn_w  = 75
        btn_w2 = 75
        btn_h  = 22

        self.btn_click_shaft = []   # Manuell klicken
        self.btn_manager     = []   # Manager einstellen
        self.btn_add_miner   = []   # Miner hinzufügen
        self.btn_unlock      = []   # Schacht freischalten

        for i, s in enumerate(self.shafts):
            sy = s.y
            self.btn_click_shaft.append(
                Button(btn_x,      sy + 4,  btn_w, btn_h, "Schürfen",  (50, 110, 60)))
            self.btn_manager.append(
                Button(btn_x + btn_w + 4, sy + 4,  btn_w2, btn_h,
                       f"MGR ({SHAFT_MANAGER_COST})", (100, 60, 140)))
            self.btn_add_miner.append(
                Button(btn_x,      sy + 30, btn_w, btn_h, "+Miner",     (80, 100, 160)))
            self.btn_unlock.append(
                Button(btn_x,      sy + s.h // 2 - 11, 154, 22,
                       f"Freischalten ({s.unlock_cost})", (150, 90, 20)))

        # Lift-Buttons (unter den Schächten)
        ly = self.shafts[-1].y + SHAFT_H + 15
        self.btn_lift_click   = Button(LIFT_X - 10, ly,      80, 22, "Lift",        (50, 120, 180))
        self.btn_lift_mgr     = Button(LIFT_X + 74, ly,      90, 22,
                                       f"L-MGR ({LIFT_MANAGER_COST})", (100, 60, 140))
        self.btn_lift_upgrade = Button(LIFT_X - 10, ly + 26, 164, 22, "Lift Upg.",  (140, 90, 30))

        # Lore-Button (oben links neben Münzen)
        self.btn_cart_upgrade = Button(450, 10, 130, 28,
                                       "Lore Upg.", (100, 130, 50))

    # ------------------------------------------------------------------ #
    #  Events
    # ------------------------------------------------------------------ #
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Schacht-Buttons
            for i, shaft in enumerate(self.shafts):
                if not shaft.unlocked:
                    if self.btn_unlock[i].is_clicked(event):
                        self._try_spend(shaft.unlock_cost, shaft.unlock,
                                        f"Schacht {i+1} freigeschaltet!")
                else:
                    # Manuell schürfen
                    if self.btn_click_shaft[i].is_clicked(event):
                        shaft.click_miners()

                    # Manager
                    if self.btn_manager[i].is_clicked(event):
                        if not shaft.has_manager:
                            self._try_spend(SHAFT_MANAGER_COST, shaft.hire_manager,
                                            f"Manager für Schacht {i+1}!")

                    # Miner hinzufügen
                    if self.btn_add_miner[i].is_clicked(event):
                        cost = shaft.next_miner_cost()
                        if cost is not None:
                            self._try_spend(cost, shaft.add_miner,
                                            f"+Miner in Schacht {i+1}!")
                        else:
                            self._msg("Schacht {i+1} ist voll (5 Miner)!")

            # Lift-Buttons
            if self.btn_lift_click.is_clicked(event):
                self.lift.click()

            if self.btn_lift_mgr.is_clicked(event):
                if not self.lift.has_manager:
                    self._try_spend(LIFT_MANAGER_COST, self.lift.hire_manager,
                                    "Lift-Manager eingestellt!")

            if self.btn_lift_upgrade.is_clicked(event):
                cost = self.lift.next_upgrade_cost()
                if cost is not None:
                    label = "ALLE SCHÄCHTE" if self.lift.upgrade_level == len(LIFT_UPGRADE_COSTS) - 1 \
                        else "Lift upgegraded!"
                    self._try_spend(cost, self.lift.upgrade, label)

            # Lore-Button
            if self.btn_cart_upgrade.is_clicked(event):
                cost = self.cart.next_upgrade_cost()
                if cost is not None:
                    self._try_spend(cost, self.cart.upgrade, "Lore upgegraded!")

    # ------------------------------------------------------------------ #
    #  Hilfsfunktionen
    # ------------------------------------------------------------------ #
    def _try_spend(self, cost, action, success_msg=""):
        if self.coins >= cost:
            self.coins -= cost
            action()
            self._msg(success_msg)
        else:
            self._msg(f"Zu wenig Münzen! ({cost} benötigt)")

    def _msg(self, text):
        self.message       = text
        self.message_timer = 2.5

    # ------------------------------------------------------------------ #
    #  Update
    # ------------------------------------------------------------------ #
    def update(self, dt):
        for shaft in self.shafts:
            shaft.update(dt)

        # Lift updaten – gibt Erzmenge zurück die oben abgeladen wurde
        ore_unloaded = self.lift.update(dt, self.shafts)
        if ore_unloaded > 0:
            # Durchschnittswert berechnen (alle freigeschalteten Schächte)
            # Lift trägt gemischtes Erz → Münzwert = Erzmenge * Durchschnittswert
            unlocked = [s for s in self.shafts if s.unlocked]
            avg_value = sum(s.ore_value for s in unlocked) / len(unlocked) if unlocked else 1
            self.cart.notify_ore_available(ore_unloaded)
            self._pending_ore_value = getattr(self, '_pending_ore_value', 0) + avg_value

        # Lore updaten – gibt Anzahl abgeliefertes Erz zurück
        ore_delivered = self.cart.update(dt, self.shafts)
        if ore_delivered > 0:
            value = getattr(self, '_pending_ore_value', 1)
            self.coins += int(ore_delivered * value)
            self._pending_ore_value = 0

        # Nachricht-Timer
        if self.message_timer > 0:
            self.message_timer -= dt

        # Button-Texte aktualisieren (Kosten können sich ändern)
        self._update_button_labels()

    def _update_button_labels(self):
        for i, shaft in enumerate(self.shafts):
            cost = shaft.next_miner_cost()
            label = f"+Miner ({cost})" if cost else "+Miner (MAX)"
            self.btn_add_miner[i].text = label

        uc = self.lift.next_upgrade_cost()
        if uc:
            last = self.lift.upgrade_level == len(LIFT_UPGRADE_COSTS) - 1
            self.btn_lift_upgrade.text = f"{'ALLE ' if last else ''}Lift Upg. ({uc})"
        else:
            self.btn_lift_upgrade.text = "Lift MAX"

        cc = self.cart.next_upgrade_cost()
        self.btn_cart_upgrade.text = f"Lore Upg. ({cc})" if cc else "Lore MAX"

    # ------------------------------------------------------------------ #
    #  Draw
    # ------------------------------------------------------------------ #
    def draw(self):
        self.screen.fill(BG_COLOR)

        # Obere Linie (Fahrlinie der Lore)
        # wird in cart.draw() gezeichnet

        # ---- Titel & Münzen ----
        title = self.font_large.render("Scuffed Miners", True, GOLD_COLOR)
        self.screen.blit(title, (10, 8))

        coins_surf = self.font_large.render(f"Münzen: {int(self.coins)}", True, GOLD_COLOR)
        self.screen.blit(coins_surf, (230, 8))

        # ---- Feedback-Nachricht ----
        if self.message_timer > 0:
            msg_surf = self.font_medium.render(self.message, True, (100, 255, 150))
            self.screen.blit(msg_surf, (10, 48))

        # ---- Trennlinie ----
        pygame.draw.line(self.screen, (60, 60, 80), (0, SHAFT_START_Y - 10),
                         (SCREEN_W, SHAFT_START_Y - 10), 1)

        # ---- Lore & Fahrlinie ----
        self.cart.draw(self.screen, CART_LINE_Y)

        # ---- Schächte ----
        for i, shaft in enumerate(self.shafts):
            shaft.draw(self.screen)
            if shaft.unlocked:
                self.btn_click_shaft[i].draw(self.screen)
                if not shaft.has_manager:
                    self.btn_manager[i].draw(self.screen)
                cost = shaft.next_miner_cost()
                if cost:
                    self.btn_add_miner[i].draw(self.screen)
            else:
                self.btn_unlock[i].draw(self.screen)

        # ---- Lift ----
        self.lift.draw(self.screen)

        # Lift-Buttons
        self.btn_lift_click.draw(self.screen)
        if not self.lift.has_manager:
            self.btn_lift_mgr.draw(self.screen)
        self.btn_lift_upgrade.draw(self.screen)

        # Lore-Upgrade Button
        self.btn_cart_upgrade.draw(self.screen)

        # ---- Legende ----
        legend = [
            ("■ Gelb = Miner bereit",   (255, 220, 50)),
            ("■ Dunkelgelb = am Minen", (200, 140, 30)),
            ("■ Blau = Lift",           (60, 140, 220)),
            ("■ Grün = Lore",           (60, 160, 80)),
        ]
        for j, (txt, col) in enumerate(legend):
            s = self.font_small.render(txt, True, col)
            self.screen.blit(s, (SCREEN_W - 200, SHAFT_START_Y + j * 18))

        pygame.display.flip()

    # ------------------------------------------------------------------ #
    #  Game Loop
    # ------------------------------------------------------------------ #
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
