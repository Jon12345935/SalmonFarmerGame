import json
import math
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk


class SalmonFarmGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tide & Tackle | Salmon Farm")
        self.root.geometry("1480x940")
        self.root.minsize(1180, 760)
        self.root.configure(bg="#edf3ef")

        self.week = 1
        self.year = 1
        self.cash = 200008000
        self.fish = 24000
        self.average_weight = 0.32
        self.feed = 8200.0
        self.health = 91
        self.water = 84
        self.oxygen = 79
        self.lice = 9
        self.actions = 4
        self.harvested_kg = 0.0
        self.total_sales = 0
        self.market_price = 8.4
        self.weather = "Calm seas"
        self.game_over = False
        self.log_entries: list[str] = []
        self.reputation = 12
        self.experience = 0
        self.level = 1
        self.crew_level = 0
        self.lifetime_deliveries = 0
        self.lifetime_revenue = 0
        self.achievements: set[str] = set()
        self.loan_debt = 0
        self.upgrades = {"aeration": 0, "biofilter": 0, "truck": 0, "feed_efficiency": 0}
        self.contract = self._new_contract()
        self.player_x = 0.12
        self.player_y = 0.78
        self.in_truck = False
        self.truck_cargo_kg = 0.0
        self.location_text = "ON THE FARM"

        self.drive_keys: set[str] = set()
        self.truck_speed = 0.0
        self.truck_steering = 0.0
        self.truck_fuel = 12.0
        self.truck_damage = 0
        self.truck_lane = 0.0
        self.truck_temperature = 2.0
        self.delivery_streak = 0
        self.route_distance = 0.0
        self.route_length = 5200.0
        self.road_scroll = 0.0
        self.route_curve = 0.0
        self.route_weather = "Clear"
        self.hazards: list[tuple[float, float, str]] = []
        self.hit_hazards: set[int] = set()
        self.drive_timer: str | None = None
        self.save_path = Path(__file__).with_name("salmon_farm_save.json")
        self._style()
        self._build_ui()
        self.root.bind_all("<KeyPress>", self._on_keypress)
        self.root.bind_all("<KeyRelease>", self._on_keyrelease)
        self._log("Your first cohort is in the pen. Keep the water clean and the books in the black.")
        self._refresh()

    def _style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#edf3ef")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#edf3ef", foreground="#133c3a", font=("Georgia", 25, "bold"))
        style.configure("Sub.TLabel", background="#edf3ef", foreground="#52706b", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#ffffff", foreground="#173f3b", font=("Segoe UI", 11, "bold"))
        style.configure("Metric.TLabel", background="#ffffff", foreground="#173f3b", font=("Segoe UI", 17, "bold"))
        style.configure("Small.TLabel", background="#ffffff", foreground="#627974", font=("Segoe UI", 9))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 9))
        style.configure("Advance.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 11), background="#176c60", foreground="white")
        style.map("Advance.TButton", background=[("active", "#10564c"), ("disabled", "#9cafaa")])

    def _build_ui(self) -> None:
        header = ttk.Frame(self.root, padding=(26, 18, 26, 12))
        header.pack(fill="x")
        title_area = ttk.Frame(header)
        title_area.pack(side="left")
        ttk.Label(title_area, text="TIDE & TACKLE", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_area, text="A living salmon-farming career on the North Atlantic", style="Sub.TLabel").pack(anchor="w", pady=(2, 0))
        header_tools = ttk.Frame(header)
        header_tools.pack(side="right", anchor="center")
        self.week_label = tk.Label(header_tools, text="WEEK 01  /  YEAR 01  /  SPRING", bg="#edf3ef", fg="#176c60", font=("Segoe UI", 11, "bold"))
        self.week_label.pack(side="left", padx=(8, 14))
        ttk.Button(header_tools, text="SAVE", command=self.save_game).pack(side="left", padx=3)
        ttk.Button(header_tools, text="LOAD", command=self.load_game).pack(side="left", padx=3)

        body = ttk.Frame(self.root, padding=(24, 0, 24, 20))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3, uniform="main")
        body.columnconfigure(1, weight=2, uniform="main")
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.scene = tk.Canvas(left, height=500, bg="#d7e8de", highlightthickness=0)
        self.scene.pack(fill="x", pady=(0, 12))
        self.scene.bind("<Configure>", lambda _event: self._draw_scene())

        actions_panel = ttk.Frame(left, style="Panel.TFrame", padding=16)
        actions_panel.pack(fill="both", expand=True)
        action_head = ttk.Frame(actions_panel, style="Panel.TFrame")
        action_head.pack(fill="x", pady=(0, 9))
        ttk.Label(action_head, text="FARM ACTIONS", style="PanelTitle.TLabel").pack(side="left")
        self.action_label = tk.Label(action_head, text="3 ACTIONS LEFT", bg="#ffffff", fg="#176c60", font=("Segoe UI", 9, "bold"))
        self.action_label.pack(side="right")
        self.location_label = tk.Label(actions_panel, text="MOVE: WASD / ARROWS     INTERACT: E", bg="#ffffff", fg="#52706b", font=("Segoe UI", 9, "bold"), anchor="w")
        self.location_label.pack(fill="x", pady=(0, 8))

        action_grid = ttk.Frame(actions_panel, style="Panel.TFrame")
        action_grid.pack(fill="both", expand=True)
        action_grid.columnconfigure((0, 1), weight=1, uniform="actions")
        action_grid.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="actions")
        options = [
            ("Feed the stock", "Use 750 kg feed · improves health", self.feed_fish),
            ("Clean the nets", "$1,200 · improve water quality", self.clean_nets),
            ("Run aerators", "$750 · raise dissolved oxygen", self.run_aerators),
            ("Treat sea lice", "$1,600 · protect fish health", self.treat_lice),
            ("Buy feed", "$2,400 · add 2,000 kg to stores", self.buy_feed),
            ("Upgrade the farm", "Invest in permanent infrastructure", self.upgrade_farm),
            ("Develop your crew", "Train staff to improve farm output", self.train_crew),
            ("Repair the truck", "Restore truck condition", self.repair_truck),
            ("Order young salmon", "$8,000 · add 5,000 smolts", self.order_smolts),
        ]
        for index, (name, detail, command) in enumerate(options):
            button = ttk.Button(action_grid, text=f"{name}\n{detail}", style="Action.TButton", command=command)
            button.grid(row=index // 2, column=index % 2, sticky="nsew", padx=4, pady=4)
            setattr(self, f"action_button_{index}", button)

        stats_panel = ttk.Frame(right, style="Panel.TFrame", padding=16)
        stats_panel.pack(fill="x", pady=(0, 12))
        ttk.Label(stats_panel, text="PEN CONDITIONS", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.metric_labels: dict[str, tk.Label] = {}
        self.bars: dict[str, ttk.Progressbar] = {}
        for key, label in (("health", "Fish health"), ("water", "Water quality"), ("oxygen", "Dissolved oxygen"), ("lice", "Sea lice pressure")):
            row = ttk.Frame(stats_panel, style="Panel.TFrame")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg="#ffffff", fg="#48645e", font=("Segoe UI", 9)).pack(side="left")
            value = tk.Label(row, text="", bg="#ffffff", fg="#173f3b", font=("Segoe UI", 9, "bold"))
            value.pack(side="right")
            self.metric_labels[key] = value
            bar = ttk.Progressbar(stats_panel, maximum=100, mode="determinate", length=240)
            bar.pack(fill="x", pady=(0, 2))
            self.bars[key] = bar

        economy_panel = ttk.Frame(right, style="Panel.TFrame", padding=16)
        economy_panel.pack(fill="x", pady=(0, 12))
        ttk.Label(economy_panel, text="FARM LEDGER", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.cash_label = self._ledger_line(economy_panel, "Cash on hand")
        self.fish_label = self._ledger_line(economy_panel, "Fish in pen")
        self.feed_label = self._ledger_line(economy_panel, "Feed in store")
        self.market_label = self._ledger_line(economy_panel, "Market price")
        self.harvest_label = self._ledger_line(economy_panel, "Sold this season")
        self.career_label = self._ledger_line(economy_panel, "Career / reputation")
        self.debt_label = self._ledger_line(economy_panel, "Credit balance")
        self.contract_label = self._ledger_line(economy_panel, "Active contract")

        log_panel = ttk.Frame(right, style="Panel.TFrame", padding=14)
        log_panel.pack(fill="both", expand=True, pady=(0, 12))
        ttk.Label(log_panel, text="FIELD NOTES", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 7))
        self.log_text = tk.Text(log_panel, height=10, wrap="word", bg="#ffffff", fg="#48645e", font=("Segoe UI", 9), relief="flat", state="disabled", padx=2, pady=2)
        self.log_text.pack(fill="both", expand=True)

        footer = ttk.Frame(right)
        footer.pack(fill="x")
        self.weather_label = tk.Label(footer, text="WEATHER  ·  CALM SEAS", bg="#edf3ef", fg="#52706b", font=("Segoe UI", 9, "bold"))
        self.weather_label.pack(side="left", pady=8)
        self.advance_button = ttk.Button(footer, text="END WEEK  →", style="Advance.TButton", command=self.advance_week)
        self.advance_button.pack(side="right")

    def _ledger_line(self, parent: ttk.Frame, title: str) -> tk.Label:
        line = ttk.Frame(parent, style="Panel.TFrame")
        line.pack(fill="x", pady=3)
        tk.Label(line, text=title, bg="#ffffff", fg="#627974", font=("Segoe UI", 9)).pack(side="left")
        value = tk.Label(line, text="", bg="#ffffff", fg="#173f3b", font=("Segoe UI", 9, "bold"))
        value.pack(side="right")
        return value

    def _draw_scene(self) -> None:
        canvas = self.scene
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 300)
        canvas.delete("all")
        if self.in_truck:
            self._draw_driving_scene(width, height)
            return

        sx, sy = width / 160, height / 90

        def block(x: int, y: int, w: int, h: int, color: str, outline: str = "") -> None:
            canvas.create_rectangle(x * sx, y * sy, (x + w) * sx, (y + h) * sy, fill=color, outline=outline)

        block(0, 0, 160, 90, "#75c3c1")
        block(0, 34, 160, 28, "#37949a")
        block(0, 39, 160, 2, "#56aeb0")
        block(0, 53, 160, 2, "#56aeb0")
        block(0, 61, 160, 29, "#8eaf70")
        block(0, 67, 160, 23, "#c6b27b")
        for x, y in ((8, 42), (22, 49), (66, 38), (86, 53), (139, 44), (151, 56)):
            block(x, y, 5, 1, "#b8e1cb")
            block(x + 2, y + 1, 3, 1, "#b8e1cb")

        for x, y, label, seed in ((49, 35, "PEN A", 17), (72, 43, "PEN B", 29)):
            block(x - 10, y - 7, 22, 15, "#286e70", "#e2e3b5")
            block(x - 8, y - 5, 18, 11, "#48a9a2")
            block(x - 11, y - 8, 2, 17, "#d8dab0")
            block(x + 11, y - 8, 2, 17, "#d8dab0")
            rng = random.Random(self.week * seed)
            for _ in range(10):
                fish_x = x + rng.randrange(-7, 8)
                fish_y = y + rng.randrange(-4, 5)
                block(fish_x, fish_y, 2, 1, "#f5a369")
                block(fish_x - 1, fish_y, 1, 1, "#d97859")
            canvas.create_text((x + 1) * sx, (y + 10) * sy, text=label, fill="#f5f4d8", font=("Consolas", 8, "bold"))

        for x, y in ((18, 64), (27, 72), (112, 66), (131, 73), (144, 65)):
            block(x, y, 3, 5, "#456b4f")
            block(x - 2, y - 3, 7, 4, "#367a58")
            block(x - 1, y - 5, 5, 3, "#55905b")

        for x, y in ((9, 75), (29, 72), (48, 76), (67, 72), (87, 75), (107, 72), (127, 75), (148, 72)):
            block(x, y, 13, 4, "#b9a47c")
            block(x + 1, y, 11, 1, "#dfcca0")

        block(111, 23, 20, 15, "#eee2b8", "#624e43")
        block(108, 20, 26, 4, "#a95145")
        block(112, 18, 6, 3, "#a95145")
        block(124, 18, 6, 3, "#a95145")
        block(119, 30, 4, 8, "#765943")
        block(107, 39, 27, 2, "#75563c")
        canvas.create_text(121 * sx, 42 * sy, text="OFFICE", fill="#f7f0cf", font=("Consolas", 8, "bold"))

        block(105, 70, 14, 5, "#a45643", "#503d37")
        block(109, 66, 7, 4, "#d7e9d1", "#503d37")
        block(107, 75, 3, 2, "#303f40")
        block(116, 75, 3, 2, "#303f40")
        block(149, 69, 8, 8, "#dfa34e", "#624e43")
        block(151, 66, 4, 3, "#bd7148")
        canvas.create_text(153 * sx, 80 * sy, text="MKT", fill="#fff1c6", font=("Consolas", 7, "bold"))

        player_x, player_y = int(self.player_x * 160), int(self.player_y * 90)
        block(player_x - 2, player_y - 5, 4, 3, "#f0c18a")
        block(player_x - 3, player_y - 2, 6, 5, "#245e57")
        block(player_x - 2, player_y + 3, 2, 3, "#493e3a")
        block(player_x + 1, player_y + 3, 2, 3, "#493e3a")
        block(2, 2, 39, 5, "#edf2d1")
        canvas.create_text(4 * sx, 4.5 * sy, anchor="w", text="NORTH ATLANTIC  /  SITE 04", fill="#315a50", font=("Consolas", 8, "bold"))
        cargo_text = f"TRUCK CARGO {self.truck_cargo_kg:,.0f} KG" if self.truck_cargo_kg else f"STOCK {self.fish:,} SALMON"
        canvas.create_text(3 * sx, 87 * sy, anchor="sw", text=f"{self.weather.upper()}  /  {cargo_text}", fill="#f4fff7", font=("Consolas", 8, "bold"))

    def _draw_driving_scene(self, width: int, height: int) -> None:
        canvas = self.scene
        sx, sy = width / 160, height / 90

        def block(x: int, y: int, w: int, h: int, color: str, outline: str = "") -> None:
            canvas.create_rectangle(x * sx, y * sy, (x + w) * sx, (y + h) * sy, fill=color, outline=outline)

        sky_color = {"Rain": "#789a9e", "Fog": "#a9bbb1", "Storm": "#667b83"}.get(self.route_weather, "#72c5c2")
        verge_color = {"Rain": "#9da682", "Fog": "#b5b59b", "Storm": "#7b806f"}.get(self.route_weather, "#bfce91")
        canvas.create_rectangle(0, 0, width, height, fill=sky_color, outline="")
        block(0, 26, 160, 14, verge_color)
        block(0, 31, 160, 4, "#879c69" if self.route_weather != "Storm" else "#626f62")
        for x, y in ((5, 24), (18, 22), (30, 25), (129, 23), (141, 20), (154, 25)):
            block(x, y, 5, 12, "#42694f")
            block(x - 2, y - 4, 9, 5, "#397652")
            block(x - 1, y - 7, 7, 4, "#548b55")

        horizon = 38
        bend = math.sin(self.route_distance / 540) * self.route_curve
        steer_shift = int(-self.truck_lane * 24 + bend * 11)
        road_top_left = 77 + steer_shift
        road_top_right = 83 + steer_shift
        road_bottom_left = 17
        road_bottom_right = 143
        canvas.create_polygon(road_top_left * sx, horizon * sy, road_top_right * sx, horizon * sy, road_bottom_right * sx, 76 * sy, road_bottom_left * sx, 76 * sy, fill="#55575a", outline="")
        canvas.create_polygon(0, horizon * sy, road_top_left * sx, horizon * sy, road_bottom_left * sx, 76 * sy, 0, 76 * sy, fill="#b9b487", outline="")
        canvas.create_polygon(road_top_right * sx, horizon * sy, width, horizon * sy, width, 76 * sy, road_bottom_right * sx, 76 * sy, fill="#b9b487", outline="")
        for y in range(40, 76, 4):
            left_edge = int(road_top_left + (road_bottom_left - road_top_left) * ((y - horizon) / (76 - horizon)))
            right_edge = int(road_top_right + (road_bottom_right - road_top_right) * ((y - horizon) / (76 - horizon)))
            block(left_edge - 2, y, 2, 2, "#eee3aa")
            block(right_edge, y, 2, 2, "#eee3aa")

        lane_center_top = (road_top_left + road_top_right) // 2
        lane_center_bottom = (road_bottom_left + road_bottom_right) // 2
        phase = int(self.road_scroll / 22) % 2
        for index in range(9):
            y = 43 + index * 5
            if (index + phase) % 2 == 0:
                progress = (y - horizon) / (76 - horizon)
                lane_center = int(lane_center_top + (lane_center_bottom - lane_center_top) * progress)
                dash_w = max(1, int(progress * 3))
                block(lane_center - dash_w // 2, y, dash_w, max(1, int(progress * 3)), "#e9d894")

        hazard_colors = {"crate": "#bd7044", "pothole": "#32373a", "tire": "#30383a", "barrel": "#e1a351", "van": "#c56a50"}
        for index, (hazard_distance, hazard_lane, hazard_type) in enumerate(self.hazards):
            if index in self.hit_hazards:
                continue
            ahead = hazard_distance - self.route_distance
            if 0 < ahead < 800:
                depth = 1 - ahead / 800
                y = int(horizon + depth * 34)
                lane_center = int(lane_center_top + (lane_center_bottom - lane_center_top) * depth)
                x = lane_center + int((hazard_lane - self.truck_lane) * depth * 54)
                size = max(2, int(depth * 10))
                hazard_color = hazard_colors.get(hazard_type, "#bd7044")
                block(x - size, y - size, size * 2, size, hazard_color, "#554a42")
                if hazard_type == "pothole":
                    block(x - size + 1, y - size + 1, size * 2 - 2, max(1, size // 2), "#22282b")
                elif hazard_type == "van":
                    block(x - size, y - size * 2, size * 2, size, "#e0ddd0", "#554a42")
                    block(x - size // 2, y - size * 2 + 1, size, max(1, size // 2), "#a7c3c0")
                else:
                    block(x - size // 2, y - size * 2, size, size, "#e0a35e")

        distance_left = max(0, self.route_length - self.route_distance)
        sign_x = int(lane_center_top + (lane_center_bottom - lane_center_top) * .20) + 34
        block(sign_x, 29, 2, 10, "#624d3f")
        block(sign_x - 9, 26, 21, 7, "#326c55", "#f1e5b6")
        canvas.create_text((sign_x + 1) * sx, 29.5 * sy, text=f"MARKET {max(0, int(distance_left / 100)) / 10:.1f} KM", fill="#fff1c9", font=("Consolas", 6, "bold"))

        block(0, 76, 160, 14, "#2d373b")
        block(0, 79, 160, 3, "#445353")
        canvas.create_polygon(0, 90 * sy, 8 * sx, 76 * sy, 39 * sx, 76 * sy, 58 * sx, 90 * sy, fill="#23343a", outline="")
        canvas.create_polygon(160 * sx, 90 * sy, 152 * sx, 76 * sy, 121 * sx, 76 * sy, 102 * sx, 90 * sy, fill="#23343a", outline="")
        block(58, 85, 44, 5, "#171f24")
        block(64, 82, 32, 6, "#263238")
        wheel_x = 80 + int(self.truck_steering * 7)
        block(wheel_x - 2, 81, 4, 8, "#d7c398")
        block(wheel_x - 8, 86, 16, 2, "#d7c398")

        block(3, 3, 38, 18, "#1e3338")
        canvas.create_text(5 * sx, 6 * sy, anchor="w", text="SPEED", fill="#a8c9ac", font=("Consolas", 7, "bold"))
        canvas.create_text(22 * sx, 15 * sy, text=f"{int(self.truck_speed):02d}", fill="#f4d27c", font=("Consolas", 16, "bold"))
        block(121, 3, 36, 18, "#1e3338")
        canvas.create_text(123 * sx, 6 * sy, anchor="w", text="FUEL", fill="#a8c9ac", font=("Consolas", 7, "bold"))
        block(123, 10, 31, 5, "#374b47")
        block(124, 11, max(0, int(29 * self.truck_fuel / 12)), 3, "#f4d27c" if self.truck_fuel > 3 else "#e87959")
        canvas.create_text(155 * sx, 18 * sy, anchor="e", text=f"{self.truck_fuel:.1f}L", fill="#f1edd3", font=("Consolas", 6, "bold"))

        cargo_label = f"CARGO {self.truck_cargo_kg:,.0f} KG"
        status = f"{self.route_weather.upper()}  DIST {int(distance_left):04d} M   {cargo_label}   DAMAGE {self.truck_damage}%"
        canvas.create_text(80 * sx, 73 * sy, text=status, fill="#f5efda", font=("Consolas", 8, "bold"))

        if self.route_weather in ("Rain", "Storm"):
            rain_color = "#d5e4d8" if self.route_weather == "Rain" else "#aebbc0"
            for streak in range(9):
                rain_x = (streak * 23 + int(self.road_scroll * 3)) % 160
                rain_y = 34 + (streak * 17 + int(self.road_scroll * 5)) % 40
                block(rain_x, rain_y, 1, 3, rain_color)

    def _refresh(self) -> None:
        self.week_label.configure(text=f"WEEK {(self.week - 1) % 12 + 1:02d}  /  YEAR {(self.week - 1) // 12 + 1:02d}  /  {self._season()}")
        self.action_label.configure(text=f"{self.actions} ACTION{'S' if self.actions != 1 else ''} LEFT")
        self.metric_labels["health"].configure(text=f"{self.health}%")
        self.metric_labels["water"].configure(text=f"{self.water}%")
        self.metric_labels["oxygen"].configure(text=f"{self.oxygen}%")
        self.metric_labels["lice"].configure(text=f"{self.lice}%")
        for key, amount in (("health", self.health), ("water", self.water), ("oxygen", self.oxygen), ("lice", self.lice)):
            self.bars[key]["value"] = amount
        self.cash_label.configure(text=f"${self.cash:,.0f}", fg="#176c60" if self.cash >= 0 else "#b34b3d")
        self.fish_label.configure(text=f"{self.fish:,}  ·  {self.average_weight:.2f} kg avg")
        self.feed_label.configure(text=f"{self.feed:,.0f} kg")
        self.market_label.configure(text=f"${self.market_price:.2f} / kg")
        self.harvest_label.configure(text=f"{self.harvested_kg:,.0f} kg  ·  ${self.total_sales:,.0f}")
        self.career_label.configure(text=f"Lv {self.level}  ·  {self.reputation} rep  ·  {self.experience} XP  ·  {len(self.achievements)} records")
        self.debt_label.configure(text=f"${self.loan_debt:,.0f}")
        self.contract_label.configure(text=f"{self.contract['name']}  ·  {self.contract['delivered']:,.0f}/{self.contract['target']:,.0f} kg")
        self.weather_label.configure(text=f"WEATHER  ·  {self.weather.upper()}")
        self.location_label.configure(text=self.location_text)
        self.advance_button.configure(state="disabled" if self.game_over or self.in_truck else "normal")
        for index in range(9):
            getattr(self, f"action_button_{index}").configure(state="disabled" if self.game_over or self.actions <= 0 or self.in_truck else "normal")
        self._draw_scene()

    def _season(self) -> str:
        return ("SPRING", "SUMMER", "AUTUMN", "WINTER")[(self.week - 1) % 12 // 3]

    def _new_contract(self) -> dict[str, int | float | str]:
        contracts = (
            ("Harbor Co-op", 1800, 3600, 7200),
            ("Northshore Grocers", 2600, 5200, 9800),
            ("Fjordline Kitchens", 1200, 2800, 6500),
            ("Blue Current Export", 4000, 7000, 14500),
        )
        name, low, high, reward = random.choice(contracts)
        return {
            "name": name,
            "target": random.randint(low, high),
            "delivered": 0.0,
            "reward": reward,
            "deadline": self.week + random.randint(6, 10),
        }

    def _gain_experience(self, amount: int) -> None:
        self.experience += amount
        while self.experience >= self.level * 120:
            self.experience -= self.level * 120
            self.level += 1
            self.reputation = min(100, self.reputation + 3)
            self.cash += 5000 * self.level
            self._log(f"Farm level {self.level} reached. Reputation rose and a ${5000 * self.level:,} development grant arrived.")

    def _check_achievements(self) -> None:
        milestones = (
            ("first-delivery", self.lifetime_deliveries >= 1, "First delivery: +1 reputation and $2,000."),
            ("ten-deliveries", self.lifetime_deliveries >= 10, "Reliable carrier: +3 reputation and $12,000."),
            ("million-kg", self.harvested_kg >= 1_000_000, "Million-kilo milestone: +5 reputation and $100,000."),
            ("five-years", self.week >= 61, "Five-year operator: +5 reputation and $75,000."),
            ("top-reputation", self.reputation >= 75, "Industry leader: +5 reputation and $50,000."),
            ("level-ten", self.level >= 10, "Major producer: +5 reputation and $100,000."),
        )
        rewards = {"first-delivery": 2000, "ten-deliveries": 12000, "million-kg": 100000, "five-years": 75000, "top-reputation": 50000, "level-ten": 100000}
        for key, achieved, message in milestones:
            if achieved and key not in self.achievements:
                self.achievements.add(key)
                self.cash += rewards[key]
                self.reputation = min(100, self.reputation + (1 if key == "first-delivery" else 3))
                self._log(f"CAREER RECORD  ·  {message}")

    def upgrade_farm(self) -> None:
        choices = (
            "1 · Aeration network ($18,000) — better oxygen each week\n"
            "2 · Biofilter system ($24,000) — cleaner water each week\n"
            "3 · Truck refrigeration ($16,000) — less cargo spoilage\n"
            "4 · Feed research ($20,000) — use less feed each week"
        )
        selection = simpledialog.askinteger("Farm development", choices, parent=self.root, minvalue=1, maxvalue=4)
        if selection is None:
            return
        upgrade = ("aeration", "biofilter", "truck", "feed_efficiency")[selection - 1]
        costs = {"aeration": 18000, "biofilter": 24000, "truck": 16000, "feed_efficiency": 20000}
        if self.upgrades[upgrade] >= 5:
            self.location_text = f"{upgrade.replace('_', ' ').upper()} IS FULLY DEVELOPED"
            self._refresh()
            return
        cost = costs[upgrade] * (self.upgrades[upgrade] + 1)
        if self.cash < cost:
            self.location_text = f"NEED ${cost - self.cash:,.0f} MORE FOR THIS UPGRADE"
            self._refresh()
            return
        self.cash -= cost
        self.upgrades[upgrade] += 1
        self._take_action(f"Farm upgrade installed: {upgrade.replace('_', ' ')} level {self.upgrades[upgrade]}.")

    def train_crew(self) -> None:
        cost = 9000 * (self.crew_level + 1)
        if self.crew_level >= 10:
            self.location_text = "YOUR CREW IS FULLY TRAINED"
            self._refresh()
            return
        if self.cash < cost:
            self.location_text = f"CREW TRAINING NEEDS ${cost:,.0f}"
            self._refresh()
            return
        self.cash -= cost
        self.crew_level += 1
        self._take_action(f"Crew completed advanced husbandry training. Crew level is now {self.crew_level}.")

    def repair_truck(self) -> None:
        if self.in_truck:
            self.location_text = "PARK AT THE FARM WORKSHOP BEFORE REPAIRS"
            self.location_label.configure(text=self.location_text)
            return
        if self.truck_damage <= 0:
            self.location_text = "TRUCK IS IN GOOD CONDITION"
            self.location_label.configure(text=self.location_text)
            return
        cost = self.truck_damage * 95
        if self.cash < cost:
            self.location_text = f"TRUCK REPAIR NEEDS ${cost:,.0f}"
            self.location_label.configure(text=self.location_text)
            return
        self.cash -= cost
        self.truck_damage = 0
        self._take_action(f"Truck repaired at the workshop for ${cost:,.0f}.")

    def order_smolts(self) -> None:
        cost = 8000
        if self.cash < cost:
            self.location_text = "SMOLT ORDER NEEDS $8,000"
            self._refresh()
            return
        self.cash -= cost
        self.fish += 5000
        self.average_weight = max(.24, self.average_weight * .85)
        self.health = min(100, self.health + 2)
        self._take_action("A new group of 5,000 healthy smolts arrived at the pens.")

    def _log(self, message: str) -> None:
        self.log_entries.insert(0, f"W{self.week:02d}  {message}")
        self.log_entries = self.log_entries[:7]
        if hasattr(self, "log_text"):
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", "\n\n".join(self.log_entries))
            self.log_text.configure(state="disabled")

    def _take_action(self, message: str) -> None:
        if self.game_over or self.actions <= 0:
            return
        self.actions -= 1
        self._log(message)
        self._refresh()
        self.save_game(show_message=False)

    def _on_keypress(self, event: tk.Event) -> None:
        if self.game_over or self.root.grab_current() not in (None, self.root):
            return
        key = event.keysym.lower()
        if self.in_truck:
            if key == "r" and self.truck_fuel <= 0 and self.truck_speed <= 0:
                self._roadside_rescue()
                return
            if key == "e":
                if self.route_distance >= self.route_length:
                    self._deliver_truck()
                else:
                    self.location_text = f"MARKET IN {int(self.route_length - self.route_distance)} M  ·  KEEP DRIVING"
                    self.location_label.configure(text=self.location_text)
                return
            if key in ("w", "up", "s", "down", "a", "left", "d", "right", "space"):
                self.drive_keys.add(key)
                if self.drive_timer is None:
                    self.drive_timer = self.root.after(50, self._drive_tick)
                return
            return
        if key == "e":
            self._interact()
            return
        directions = {
            "w": (0, -1), "up": (0, -1),
            "s": (0, 1), "down": (0, 1),
            "a": (-1, 0), "left": (-1, 0),
            "d": (1, 0), "right": (1, 0),
        }
        if key not in directions:
            return
        dx, dy = directions[key]
        speed = 0.024
        self.player_x = min(.97, max(.03, self.player_x + dx * speed))
        self.player_y = min(.94, max(.08, self.player_y + dy * speed))
        self.location_text = "ON THE FARM  ·  WALK TO A PEN OR THE OFFICE"
        self._draw_scene()
        self.location_label.configure(text=self.location_text)

    def _on_keyrelease(self, event: tk.Event) -> None:
        self.drive_keys.discard(event.keysym.lower())

    def _drive_tick(self) -> None:
        self.drive_timer = None
        if not self.in_truck or self.game_over:
            return
        self._drive_step(0.05)
        self._draw_scene()
        if self.route_distance >= self.route_length:
            self.route_distance = self.route_length
            self.truck_speed = 0
            self.drive_keys.clear()
            self.location_text = "MARKET ARRIVED  ·  PRESS E TO UNLOAD THE FISH"
            self.location_label.configure(text=self.location_text)
            self._draw_scene()
            return
        if self.truck_fuel <= 0 and self.truck_speed <= 0:
            self.location_text = "OUT OF FUEL  ·  PRESS R FOR ROADSIDE SERVICE"
            self.location_label.configure(text=self.location_text)
            return
        self.location_text = f"DRIVING  ·  {int(self.truck_speed)} KM/H  ·  MARKET {int(self.route_length - self.route_distance)} M"
        self.location_label.configure(text=self.location_text)
        self.drive_timer = self.root.after(50, self._drive_tick)

    def _drive_step(self, delta: float) -> None:
        if any(key in self.drive_keys for key in ("w", "up")) and self.truck_fuel > 0:
            self.truck_speed = min(85, self.truck_speed + 38 * delta)
        elif any(key in self.drive_keys for key in ("s", "down", "space")):
            self.truck_speed = max(0, self.truck_speed - 80 * delta)
        else:
            self.truck_speed = max(0, self.truck_speed - 4 * delta)

        handling = max(.45, 1 - self.truck_damage / 150)
        if self.route_weather in ("Rain", "Storm"):
            handling *= .68
        if any(key in self.drive_keys for key in ("a", "left")):
            self.truck_steering = max(-1, self.truck_steering - 2.2 * delta)
            self.truck_lane -= .68 * delta * handling
        elif any(key in self.drive_keys for key in ("d", "right")):
            self.truck_steering = min(1, self.truck_steering + 2.2 * delta)
            self.truck_lane += .68 * delta * handling
        else:
            self.truck_steering *= max(0, 1 - 1.1 * delta)

        bend = math.sin(self.route_distance / 540) * self.route_curve
        self.truck_lane -= bend * self.truck_speed / 85 * delta * .11
        self.truck_lane = max(-1.2, min(1.2, self.truck_lane))

        if abs(self.truck_lane) > .88 and self.truck_speed > 20:
            self.truck_speed = max(8, self.truck_speed - 18 * delta)
            self.truck_damage = min(100, self.truck_damage + 2 * delta)

        distance = self.truck_speed / 3.6 * delta
        self.route_distance += distance
        self.road_scroll += distance * 2.8
        fuel_rate = .0015 * (1 - .06 * self.upgrades["truck"])
        if self.route_weather in ("Rain", "Storm"):
            fuel_rate *= 1.25
        self.truck_fuel = max(0, self.truck_fuel - distance * fuel_rate)
        temperature_gain = .018 if self.route_weather in ("Clear", "Heatwave") else .010
        self.truck_temperature += max(0, temperature_gain - self.upgrades["truck"] * .005) * delta

        for index, (hazard_distance, hazard_lane, hazard_type) in enumerate(self.hazards):
            ahead = hazard_distance - self.route_distance
            if index not in self.hit_hazards and -12 <= ahead <= 12:
                if abs(self.truck_lane - hazard_lane) < .23 and self.truck_speed > 12:
                    self.hit_hazards.add(index)
                    damage = 30 if hazard_type == "van" else 18
                    self.truck_damage = min(100, self.truck_damage + damage)
                    self.truck_speed *= .38 if hazard_type == "van" else .52
                    self._log(f"Truck struck a {hazard_type}. Speed dropped and vehicle damage increased.")
                    if self.truck_damage >= 45 and self.truck_cargo_kg > 0:
                        spoiled = self.truck_cargo_kg * .04
                        self.truck_cargo_kg -= spoiled
                        self._log(f"The rough impact spoiled {spoiled:,.0f} kg of the fish cargo.")
            elif ahead < -20:
                self.hit_hazards.add(index)

    def _roadside_rescue(self) -> None:
        fee = 8500 + self.truck_damage * 80
        if self.cash < fee:
            advance = fee - self.cash
            self.loan_debt += int(advance * 1.12)
            self.cash = 0
        else:
            self.cash -= fee
        self.truck_fuel = 15
        self.truck_damage = min(100, self.truck_damage + 5)
        self._log(f"Roadside service delivered fuel and a tow-start for ${fee:,.0f}.")
        self.location_text = "ROAD SERVICE COMPLETE  ·  PRESS W TO CONTINUE"
        self._refresh()

    def _interact(self) -> None:
        if self.in_truck:
            if self.route_distance >= self.route_length:
                self._deliver_truck()
            else:
                self.location_text = f"MARKET IN {int(self.route_length - self.route_distance)} M  ·  DRIVE THERE FIRST"
                self.location_label.configure(text=self.location_text)
            return
        width = max(self.scene.winfo_width(), 420)
        height = max(self.scene.winfo_height(), 260)
        spots = {
            "pen": (.31, .39),
            "pen_b": (.45, .48),
            "office": (.75, .34),
            "market": (.92, .77),
        }
        nearest = min(spots, key=lambda name: (self.player_x - spots[name][0]) ** 2 * width ** 2 + (self.player_y - spots[name][1]) ** 2 * height ** 2)
        distance = ((self.player_x - spots[nearest][0]) * width) ** 2 + ((self.player_y - spots[nearest][1]) * height) ** 2
        if distance > 52 ** 2:
            self.location_text = "NOTHING NEARBY  ·  WALK CLOSER TO A PEN, OFFICE, OR MARKET"
            self.location_label.configure(text=self.location_text)
            return
        if self.in_truck:
            if nearest == "market":
                self._deliver_truck()
            else:
                self.location_text = "DRIVE THE TRUCK TO THE MARKET GATE TO UNLOAD"
                self.location_label.configure(text=self.location_text)
        elif nearest in ("pen", "pen_b"):
            self._load_truck()
        elif nearest == "office":
            self._hold_meeting()
        else:
            self.location_text = "THE MARKET GATE IS FOR TRUCK DELIVERIES"
            self.location_label.configure(text=self.location_text)

    def _load_truck(self) -> None:
        if self.actions <= 0:
            self.location_text = "NO ACTIONS LEFT THIS WEEK  ·  LOAD THE TRUCK NEXT WEEK"
            self.location_label.configure(text=self.location_text)
            return
        if self.truck_cargo_kg > 0:
            self.location_text = "TRUCK IS ALREADY LOADED  ·  DRIVE TO THE MARKET"
            self.location_label.configure(text=self.location_text)
            return
        if self.fish < 1000:
            self.location_text = "NOT ENOUGH FISH FOR A TRUCKLOAD"
            self.location_label.configure(text=self.location_text)
            return
        capacity_kg = 4200 + self.upgrades["truck"] * 1800
        max_fish = min(self.fish, int(capacity_kg / max(self.average_weight, .01)))
        if max_fish < 1:
            self.location_text = "TRUCK CAPACITY IS TOO LOW FOR THE CURRENT FISH SIZE. UPGRADE THE TRUCK."
            self.location_label.configure(text=self.location_text)
            return
        fish_count = simpledialog.askinteger("Load the fish truck", f"How many salmon should go to market?\n{self.fish:,} fish available. Truck capacity: {capacity_kg:,} kg.", parent=self.root, minvalue=1, maxvalue=max_fish, initialvalue=min(2000, max_fish))
        if fish_count is None:
            return
        self.fish -= fish_count
        self.truck_cargo_kg = fish_count * self.average_weight
        self.in_truck = True
        self.route_distance = 0
        self.truck_speed = 0
        self.truck_steering = 0
        self.truck_lane = 0
        self.truck_temperature = 2
        self.route_length = random.randint(4800, 7600) + self.level * 100
        self.route_curve = random.uniform(-1, 1)
        self.route_weather = random.choice(("Clear", "Clear", "Rain", "Fog", "Storm", "Heatwave"))
        hazard_count = random.randint(8, 13)
        hazard_types = ("crate", "pothole", "tire", "barrel", "van")
        self.hazards = [
            (random.randint(380, int(self.route_length - 260)), random.choice((-.68, -.34, 0.0, .34, .68)), random.choice(hazard_types))
            for _ in range(hazard_count)
        ]
        self.hazards.sort(key=lambda hazard: hazard[0])
        self.truck_fuel = 28 + self.upgrades["truck"] * 5
        self.truck_damage = 0
        self.hit_hazards.clear()
        self.drive_keys.clear()
        self.location_text = "TRUCK LOADED  ·  W/UP ACCELERATE  ·  A/D STEER  ·  S/SPACE BRAKE"
        self._take_action(f"Loaded {fish_count:,} salmon ({self.truck_cargo_kg:,.0f} kg). {self.route_weather} route, {self.route_length:,.0f} m to market. Avoid hazards and mind your lane.")

    def _deliver_truck(self) -> None:
        if self.route_distance < self.route_length:
            self.location_text = f"MARKET IN {int(self.route_length - self.route_distance)} M  ·  DRIVE THERE FIRST"
            self.location_label.configure(text=self.location_text)
            return
        delivered_kg = self.truck_cargo_kg
        if self.truck_temperature > 8:
            spoiled_fraction = min(.35, (self.truck_temperature - 8) * .025)
            spoiled = delivered_kg * spoiled_fraction
            self.truck_cargo_kg -= spoiled
            delivered_kg = self.truck_cargo_kg
            self._log(f"Refrigeration warning: {spoiled:,.0f} kg lost to warm cargo.")
        sale_price = self.market_price * (1 + self.reputation / 1000)
        revenue = delivered_kg * sale_price
        transport_cost = 450 + self.truck_damage * 12
        self.cash += revenue - transport_cost
        self.harvested_kg += delivered_kg
        self.total_sales += int(revenue)
        delivered = delivered_kg
        self.lifetime_deliveries += 1
        self.lifetime_revenue += int(revenue)
        self.delivery_streak += 1
        self.contract["delivered"] = float(self.contract["delivered"]) + delivered
        contract_message = ""
        if float(self.contract["delivered"]) >= float(self.contract["target"]):
            reward = int(self.contract["reward"])
            contract_name = str(self.contract["name"])
            self.cash += reward
            self.reputation = min(100, self.reputation + 5)
            self._gain_experience(90)
            contract_message = f" Contract complete for {contract_name}: bonus ${reward:,}."
            self._log(contract_message.strip())
            self.contract = self._new_contract()
        streak_bonus = 2500 * (self.delivery_streak // 3) if self.delivery_streak % 3 == 0 else 0
        if streak_bonus:
            self.cash += streak_bonus
            self.reputation = min(100, self.reputation + 2)
            self._log(f"Reliable carrier streak: ${streak_bonus:,} bonus and +2 reputation.")
        self._gain_experience(max(10, int(delivered / 100)))
        self._check_achievements()
        self.truck_cargo_kg = 0.0
        self.in_truck = False
        self.drive_keys.clear()
        self.player_x, self.player_y = .92, .77
        self.location_text = f"DELIVERED {delivered:,.0f} KG  ·  {self.delivery_streak} DELIVERY STREAK"
        self._log(f"Delivered {delivered:,.0f} kg at ${sale_price:.2f}/kg. Sale: ${revenue:,.0f}, less ${transport_cost:,.0f} transport and repairs.{contract_message}")
        self._refresh()
        self.save_game(show_message=False)

    def _hold_meeting(self) -> None:
        if self.actions <= 0:
            self.location_text = "NO ACTIONS LEFT THIS WEEK  ·  MEETING CAN'T BE HELD"
            self.location_label.configure(text=self.location_text)
            return
        choice = messagebox.askyesnocancel("Weekly operations meeting", "The crew has two proposals.\n\nYES: Spend $1,800 on water maintenance (+15 water, +5 oxygen).\n\nNO: Sign a sales partnership (+$0.55/kg market price).\n\nCANCEL: Leave the meeting.", parent=self.root)
        if choice is True:
            if self.cash < 1800:
                self.location_text = "MEETING: NOT ENOUGH CASH FOR MAINTENANCE"
                self.location_label.configure(text=self.location_text)
                return
            self.cash -= 1800
            self.water = min(100, self.water + 15)
            self.oxygen = min(100, self.oxygen + 5)
            self._take_action("Operations meeting: approved water maintenance for the site.")
        elif choice is False:
            self.market_price = min(11.5, round(self.market_price + .55, 2))
            self._take_action("Operations meeting: signed a sales partnership and improved the fish price.")
        else:
            return
        self.location_text = "MEETING COMPLETE  ·  WALK BACK TO THE PENS"
        self._refresh()

    def feed_fish(self) -> None:
        if self.feed < 750:
            self._log("Feed stores are too low. Buy a delivery before feeding the whole pen.")
            return
        self.feed -= 750
        self.health = min(100, self.health + 5)
        self._take_action("Fed the pen. The fish are active and feeding well.")

    def clean_nets(self) -> None:
        if self.cash < 1200:
            self._log("Not enough cash to hire the net-cleaning crew.")
            return
        self.cash -= 1200
        self.water = min(100, self.water + 18)
        self.oxygen = max(0, self.oxygen - 2)
        self._take_action("Net crew cleared fouling. Water flow through the pen improved.")

    def run_aerators(self) -> None:
        if self.cash < 750:
            self._log("Not enough cash to run the backup aerators.")
            return
        self.cash -= 750
        self.oxygen = min(100, self.oxygen + 22)
        self._take_action("Aerators restored oxygen levels across the pen.")

    def treat_lice(self) -> None:
        if self.cash < 1600:
            self._log("Not enough cash for a sea-lice treatment.")
            return
        self.cash -= 1600
        self.lice = max(0, self.lice - 28)
        self.health = min(100, self.health + 3)
        self._take_action("Lice treatment complete. The fish are looking more comfortable.")

    def buy_feed(self) -> None:
        if self.cash < 2400:
            self._log("Not enough cash to pay for a feed delivery.")
            return
        self.cash -= 2400
        self.feed += 2000
        self._take_action("Feed delivery arrived: 2,000 kg added to the store.")

    def harvest(self) -> None:
        if self.fish < 1000:
            self._log("The remaining stock is too small for a commercial harvest.")
            return
        batch = int(self.fish * 0.15)
        weight = batch * self.average_weight
        revenue = weight * self.market_price
        self.fish -= batch
        self.cash += revenue - 450
        self.harvested_kg += weight
        self.total_sales += int(revenue)
        self._take_action(f"Sold {batch:,} salmon ({weight:,.0f} kg) for ${revenue:,.0f}, less packing costs.")

    def advance_week(self) -> None:
        if self.game_over or self.in_truck:
            return
        previous_season = self._season()
        self.week += 1
        self.actions = 4
        self.cash -= 2450 + self.loan_debt * .0012
        weekly_ration = self.fish * self.average_weight * max(.012, .025 - self.upgrades["feed_efficiency"] * .002 - self.crew_level * .0004)
        if self.feed >= weekly_ration:
            self.feed -= weekly_ration
            self.health = min(100, self.health + 1 + (1 if self.crew_level >= 3 else 0))
            self.average_weight += 0.075
            self._log(f"Routine costs were $2,450. Fish gained weight; weekly feed use was {weekly_ration:,.0f} kg.")
        else:
            self.feed = 0
            self.health = max(0, self.health - 9)
            self._log("Feed ran out. The stock is underfed and health is falling.")

        self.water = max(0, self.water - random.randint(2, 5) + self.upgrades["biofilter"] * 2)
        self.oxygen = max(0, self.oxygen - random.randint(2, 5) + self.upgrades["aeration"] * 2)
        self.lice = min(100, self.lice + max(1, random.randint(1, 5) - self.crew_level // 3))
        self.market_price = round(max(5.2, min(11.5, self.market_price + random.uniform(-0.8, 0.9))), 2)

        event = random.random()
        if event < 0.13:
            self.weather = "Rough swell"
            self.water = max(0, self.water - 7)
            self.oxygen = max(0, self.oxygen - 5)
            self._log("A rough swell hit the site. Water quality and oxygen took a knock.")
        elif event < 0.25:
            self.weather = "Bright & warm"
            self.lice = min(100, self.lice + 8)
            self._log("Warm weather brought a sea-lice spike. Keep an eye on the stock.")
        elif event < 0.36:
            self.weather = "Algal bloom"
            bloom_damage = max(4, 12 - self.upgrades["biofilter"] * 2)
            self.water = max(0, self.water - bloom_damage)
            self.health = max(0, self.health - max(1, bloom_damage // 3))
            self._log(f"An algal bloom reduced water quality by {bloom_damage} points. Biofilters limit the damage.")
        elif event < 0.47:
            self.weather = "Market surge"
            self.market_price = min(11.5, self.market_price + 1.15)
            self._log("Restaurant demand surged this week. Fish prices rose across the region.")
        elif event < 0.56:
            self.weather = "Inspection day"
            if self.health >= 75 and self.water >= 65 and self.lice <= 35:
                bonus = 12000
                self.cash += bonus
                self.reputation = min(100, self.reputation + 2)
                self._log(f"The inspector awarded a clean-site bonus of ${bonus:,} and +2 reputation.")
            else:
                self.reputation = max(0, self.reputation - 1)
                self._log("The inspection found issues to address before the next audit. Reputation fell by 1.")
        elif event < 0.66:
            self.weather = "Feed shortage"
            shortage_cost = 5000
            self.cash -= shortage_cost
            self._log(f"An emergency feed shipment cost ${shortage_cost:,} after a supplier missed its delivery.")
        else:
            self.weather = random.choice(("Calm seas", "Light rain", "Fresh breeze"))

        stress = max(0, 45 - self.water) // 8 + max(0, 40 - self.oxygen) // 7 + max(0, self.lice - 55) // 8
        if stress:
            losses = min(self.fish, int(self.fish * stress * 0.012))
            self.fish -= losses
            self.health = max(0, self.health - stress * 3)
            if losses:
                self._log(f"Environmental stress caused losses of {losses:,} fish. Improve pen conditions quickly.")

        if self.contract["deadline"] <= self.week:
            self.reputation = max(0, self.reputation - 2)
            self._log(f"Contract with {self.contract['name']} expired. Reputation fell by 2; a new offer is available.")
            self.contract = self._new_contract()

        if self.week % 12 == 1:
            year_number = (self.week - 1) // 12 + 1
            seasonal_grant = 2500 * self.reputation
            self.cash += seasonal_grant
            self.reputation = min(100, self.reputation + 1)
            self._log(f"Year {year_number} begins. Sustainability grant: ${seasonal_grant:,}. Your operation continues.")
        elif previous_season != self._season():
            self._log(f"A new season begins: {self._season().title()}. The farm keeps running year-round.")

        if self.cash < 0:
            emergency_credit = max(50000, int(-self.cash * 1.15))
            self.cash += emergency_credit
            self.loan_debt += emergency_credit
            self.reputation = max(0, self.reputation - 1)
            self._log(f"Emergency operating credit of ${emergency_credit:,} kept the farm open. Review costs and sales.")

        if self.fish <= 0 or self.health <= 0:
            restock_cost = 25000
            if self.cash < restock_cost:
                advance = restock_cost - self.cash
                self.loan_debt += int(advance * 1.1)
                self.cash = 0
            else:
                self.cash -= restock_cost
            self.fish = 6000
            self.average_weight = .24
            self.health = 62
            self.water = max(45, self.water)
            self.oxygen = max(45, self.oxygen)
            self.reputation = max(0, self.reputation - 8)
            self._log("A recovery cohort was stocked after a major loss. The farm survives, but reputation took a hit.")

        self._check_achievements()
        self._refresh()
        self.save_game(show_message=False)

    def save_game(self, show_message: bool = True) -> None:
        state = {
            "version": 2,
            "week": self.week,
            "cash": self.cash,
            "fish": self.fish,
            "average_weight": self.average_weight,
            "feed": self.feed,
            "health": self.health,
            "water": self.water,
            "oxygen": self.oxygen,
            "lice": self.lice,
            "actions": self.actions,
            "harvested_kg": self.harvested_kg,
            "total_sales": self.total_sales,
            "market_price": self.market_price,
            "weather": self.weather,
            "reputation": self.reputation,
            "experience": self.experience,
            "level": self.level,
            "crew_level": self.crew_level,
            "lifetime_deliveries": self.lifetime_deliveries,
            "lifetime_revenue": self.lifetime_revenue,
            "achievements": sorted(self.achievements),
            "loan_debt": self.loan_debt,
            "upgrades": self.upgrades,
            "contract": self.contract,
            "log_entries": self.log_entries,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "in_truck": self.in_truck,
            "truck_cargo_kg": self.truck_cargo_kg,
            "truck_speed": self.truck_speed,
            "truck_steering": self.truck_steering,
            "truck_fuel": self.truck_fuel,
            "truck_damage": self.truck_damage,
            "truck_lane": self.truck_lane,
            "truck_temperature": self.truck_temperature,
            "delivery_streak": self.delivery_streak,
            "route_distance": self.route_distance,
            "route_length": self.route_length,
            "route_curve": self.route_curve,
            "route_weather": self.route_weather,
            "road_scroll": self.road_scroll,
            "hazards": self.hazards,
            "hit_hazards": sorted(self.hit_hazards),
        }
        try:
            self.save_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            if show_message:
                messagebox.showinfo("Career saved", f"Your farm career was saved to {self.save_path.name}.", parent=self.root)
        except OSError as error:
            if show_message:
                messagebox.showerror("Save failed", str(error), parent=self.root)

    def load_game(self) -> None:
        try:
            state = json.loads(self.save_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showerror("Load failed", f"Could not read {self.save_path.name}: {error}", parent=self.root)
            return
        if not isinstance(state, dict) or state.get("version") != 2:
            messagebox.showerror("Load failed", "This save file version is not supported.", parent=self.root)
            return
        fields = (
            "week", "cash", "fish", "average_weight", "feed", "health", "water", "oxygen", "lice", "actions",
            "harvested_kg", "total_sales", "market_price", "weather", "reputation", "experience", "level",
            "crew_level", "lifetime_deliveries", "lifetime_revenue", "loan_debt", "contract", "log_entries",
            "player_x", "player_y", "in_truck", "truck_cargo_kg", "truck_speed", "truck_steering", "truck_fuel",
            "truck_damage", "truck_lane", "truck_temperature", "delivery_streak", "route_distance", "route_length",
            "route_curve", "route_weather", "road_scroll",
        )
        for field in fields:
            if field in state:
                setattr(self, field, state[field])
        self.upgrades.update(state.get("upgrades", {}))
        self.achievements = set(state.get("achievements", []))
        self.hazards = [tuple(hazard) for hazard in state.get("hazards", [])]
        self.hit_hazards = set(state.get("hit_hazards", []))
        self.drive_keys.clear()
        self.game_over = False
        self.location_text = "CAREER LOADED  ·  WELCOME BACK"
        self._refresh()
        self._log("Career loaded. Your farm is right where you left it.")
        if self.in_truck:
            self.drive_timer = self.root.after(50, self._drive_tick)

def main() -> None:
    from salmon_open_world import main as open_world_main

    open_world_main()


if __name__ == "__main__":
    main()