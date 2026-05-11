try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ModuleNotFoundError:  # pragma: no cover - depends on system Tk installation
    tk = None
    ttk = None
    messagebox = None

from recruitment_ranker import (
    DEFAULT_FEATURES,
    load_weights,
    normalize_feature_map,
    rank_candidates,
)


class RecruitmentRankerGUI:
    CANDIDATE_SLOTS = 100
    INITIAL_WIDTH = 1120
    INITIAL_HEIGHT = 760
    MIN_WIDTH = 980
    MIN_HEIGHT = 680

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Recruitment Ranker")
        self.root.geometry(f"{self.INITIAL_WIDTH}x{self.INITIAL_HEIGHT}")
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        self.palette = {
            "bg": "#f4f6fb",
            "card": "#ffffff",
            "text": "#0f172a",
            "muted": "#475569",
            "accent": "#2563eb",
            "accent_dark": "#1d4ed8",
            "accent_text": "#1e40af",
            "border": "#e2e8f0",
            "soft_border": "#cbd5f5",
            "input_bg": "#f8fafc",
            "highlight": "#dbeafe",
            "success": "#0b5ed7",
        }
        self.root.configure(background=self.palette["bg"])

        self.weights = load_weights()
        self.job_inputs = {}
        self.candidate_name_entries = []
        self.candidate_text_entries = []
        self._latest_ranked = []
        self._candidate_canvas_window = None
        self.candidate_canvas = None
        self.score_bar_canvas = None
        self.score_trend_canvas = None

        self._build_style()
        self._build_layout()
        self._prefill_defaults()

    def _build_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        palette = self.palette

        style.configure("TFrame", background=palette["bg"])
        style.configure("App.TFrame", background=palette["bg"])
        style.configure("Card.TFrame", background=palette["card"])
        style.configure("Card.TLabelframe", background=palette["card"], relief="solid", borderwidth=1)
        style.configure(
            "Card.TLabelframe.Label",
            background=palette["card"],
            foreground=palette["text"],
            font=("TkDefaultFont", 11, "bold"),
        )
        style.configure(
            "Header.TLabel",
            background=palette["bg"],
            foreground=palette["text"],
            font=("TkDefaultFont", 22, "bold"),
        )
        style.configure(
            "Subheader.TLabel",
            background=palette["bg"],
            foreground=palette["muted"],
            font=("TkDefaultFont", 11),
        )
        style.configure(
            "Card.TLabel",
            background=palette["card"],
            foreground=palette["text"],
            font=("TkDefaultFont", 10),
        )
        style.configure(
            "Muted.TLabel",
            background=palette["card"],
            foreground=palette["muted"],
            font=("TkDefaultFont", 9),
        )
        style.configure(
            "Primary.TButton",
            font=("TkDefaultFont", 10, "bold"),
            padding=(18, 10),
            background=palette["accent"],
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", palette["accent_dark"]), ("!disabled", palette["accent"])],
            foreground=[("disabled", palette["soft_border"]), ("!disabled", "white")],
        )
        style.configure(
            "Secondary.TButton",
            font=("TkDefaultFont", 10),
            padding=(16, 10),
            background=palette["border"],
            foreground=palette["text"],
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", palette["soft_border"]), ("!disabled", palette["border"])],
        )
        style.configure(
            "Modern.TEntry",
            fieldbackground=palette["input_bg"],
            background=palette["input_bg"],
            foreground=palette["text"],
            relief="flat",
        )
        style.map(
            "Modern.TEntry",
            fieldbackground=[("focus", palette["card"]), ("!disabled", palette["input_bg"])],
        )
        style.configure(
            "Modern.Treeview",
            background=palette["card"],
            fieldbackground=palette["card"],
            foreground=palette["text"],
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Modern.Treeview.Heading",
            background=palette["border"],
            foreground=palette["text"],
            font=("TkDefaultFont", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", palette["highlight"])],
            foreground=[("selected", palette["accent_text"])],
        )

    def _build_layout(self):
        container = ttk.Frame(self.root, padding=20, style="App.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="App.TFrame")
        header.pack(fill="x")
        title = ttk.Label(header, text="Smart Recruitment Ranker", style="Header.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(
            header,
            text="Set job requirements, enter resumes, and rank candidates instantly.",
            style="Subheader.TLabel",
        )
        subtitle.pack(anchor="w", pady=(4, 16))

        ttk.Separator(container).pack(fill="x", pady=(0, 16))

        body = ttk.Frame(container, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(body, style="App.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right_panel = ttk.Frame(body, style="App.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        self._build_job_requirements(left_panel)
        self._build_candidate_inputs(left_panel)
        self._build_results(right_panel)

    def _build_job_requirements(self, parent):
        frame = ttk.LabelFrame(
            parent,
            text="Job Requirements",
            style="Card.TLabelframe",
            padding=(14, 12),
        )
        frame.pack(fill="x", pady=(0, 12))

        ttk.Label(
            frame,
            text="Enter target levels from 0.0 (low) to 1.0 (high).",
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(0, 10))

        key_features = [
            "Python",
            "Machine Learning",
            "Cloud Computing",
            "SQL",
            "Years of Experience",
        ]
        for index, feature in enumerate(key_features, start=1):
            ttk.Label(frame, text=feature, style="Card.TLabel").grid(
                row=index, column=0, sticky="w", padx=6, pady=6
            )
            entry = ttk.Entry(frame, width=12, style="Modern.TEntry")
            entry.grid(row=index, column=1, sticky="w", padx=6, pady=6)
            self.job_inputs[feature] = entry

    def _build_candidate_inputs(self, parent):
        frame = ttk.LabelFrame(
            parent,
            text="Candidate Resumes",
            style="Card.TLabelframe",
            padding=(14, 12),
        )
        frame.pack(fill="both", expand=True, pady=(0, 12))

        list_container = ttk.Frame(frame, style="Card.TFrame")
        list_container.pack(fill="both", expand=True)

        self.candidate_canvas = tk.Canvas(
            list_container,
            background=self.palette["card"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.candidate_canvas.yview)
        self.candidate_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.candidate_canvas.pack(side="left", fill="both", expand=True)

        scrollable_frame = ttk.Frame(self.candidate_canvas, style="Card.TFrame")
        self._candidate_canvas_window = self.candidate_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw"
        )

        def _update_scroll_region(event):
            self.candidate_canvas.configure(scrollregion=self.candidate_canvas.bbox("all"))

        def _resize_canvas(event):
            self.candidate_canvas.itemconfigure(self._candidate_canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", _update_scroll_region)
        self.candidate_canvas.bind("<Configure>", _resize_canvas)

        for i in range(self.CANDIDATE_SLOTS):
            row_base = i * 3
            ttk.Label(scrollable_frame, text=f"Candidate {i + 1} Name", style="Card.TLabel").grid(
                row=row_base, column=0, sticky="w", padx=8, pady=(8, 2)
            )
            name_entry = ttk.Entry(scrollable_frame, style="Modern.TEntry")
            name_entry.grid(row=row_base, column=1, sticky="ew", padx=8, pady=(8, 2))
            self.candidate_name_entries.append(name_entry)

            ttk.Label(scrollable_frame, text=f"Candidate {i + 1} Resume Text", style="Card.TLabel").grid(
                row=row_base + 1, column=0, sticky="nw", padx=8, pady=(2, 8)
            )
            resume_text = tk.Text(
                scrollable_frame,
                height=4,
                wrap="word",
                background=self.palette["input_bg"],
                foreground=self.palette["text"],
                highlightbackground=self.palette["border"],
                highlightcolor=self.palette["accent"],
                highlightthickness=1,
                relief="flat",
            )
            resume_text.grid(row=row_base + 1, column=1, sticky="ew", padx=8, pady=(2, 8))
            self.candidate_text_entries.append(resume_text)

        scrollable_frame.columnconfigure(1, weight=1)

        button_row = ttk.Frame(parent, style="App.TFrame")
        button_row.pack(fill="x")
        ttk.Button(
            button_row,
            text="Rank Candidates",
            style="Primary.TButton",
            command=self.rank,
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            button_row,
            text="Reset",
            style="Secondary.TButton",
            command=self.reset_fields,
        ).pack(side="left")

    def _build_results(self, parent):
        frame = ttk.LabelFrame(
            parent,
            text="Ranking Results",
            style="Card.TLabelframe",
            padding=(14, 12),
        )
        frame.pack(fill="both", expand=True)

        self.top_candidate_var = tk.StringVar(value="Top Candidate: —")
        top_candidate = ttk.Label(
            frame,
            textvariable=self.top_candidate_var,
            font=("TkDefaultFont", 12, "bold"),
            foreground=self.palette["success"],
            background=self.palette["card"],
        )
        top_candidate.pack(anchor="w", pady=(4, 6))

        ttk.Label(
            frame,
            text="Scores are normalized between 0 and 1. Higher is better.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        tree_container = ttk.Frame(frame, style="Card.TFrame")
        tree_container.pack(fill="both", expand=True)

        columns = ("rank", "name", "score")
        self.result_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=14,
            style="Modern.Treeview",
        )
        self.result_tree.heading("rank", text="Rank")
        self.result_tree.heading("name", text="Candidate")
        self.result_tree.heading("score", text="Score")
        self.result_tree.column("rank", width=60, anchor="center")
        self.result_tree.column("name", width=170, anchor="w")
        self.result_tree.column("score", width=90, anchor="center")
        self.result_tree.tag_configure("odd", background=self.palette["input_bg"])
        self.result_tree.tag_configure("even", background=self.palette["card"])
        result_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=result_scrollbar.set)
        self.result_tree.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")

        charts_frame = ttk.Frame(frame, style="Card.TFrame")
        charts_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(charts_frame, text="Top Scores (Bar Chart)", style="Card.TLabel").pack(anchor="w")
        self.score_bar_canvas = tk.Canvas(
            charts_frame,
            height=150,
            background=self.palette["card"],
            highlightbackground=self.palette["border"],
            highlightthickness=1,
        )
        self.score_bar_canvas.pack(fill="x", pady=(4, 10))

        ttk.Label(charts_frame, text="Score Trend (All Candidates)", style="Card.TLabel").pack(anchor="w")
        self.score_trend_canvas = tk.Canvas(
            charts_frame,
            height=150,
            background=self.palette["card"],
            highlightbackground=self.palette["border"],
            highlightthickness=1,
        )
        self.score_trend_canvas.pack(fill="x", pady=(4, 0))

        self.score_bar_canvas.bind("<Configure>", self._refresh_charts)
        self.score_trend_canvas.bind("<Configure>", self._refresh_charts)
        self._clear_charts()

    def _prefill_defaults(self):
        defaults = {
            "Python": "1.0",
            "Machine Learning": "0.9",
            "Cloud Computing": "0.6",
            "SQL": "0.5",
            "Years of Experience": "0.7",
        }
        for feature, value in defaults.items():
            self.job_inputs[feature].insert(0, value)

        seed_data = [
            (
                "Alice",
                "5 years experience in Python, ML projects, SQL, AWS cloud.",
            ),
            (
                "Bob",
                "3 years experience in frontend, JavaScript, React, some DevOps.",
            ),
            (
                "Charlie",
                "2 years Python developer, good communication, certifications in ML.",
            ),
        ]
        for i, (name, text) in enumerate(seed_data):
            self.candidate_name_entries[i].insert(0, name)
            self.candidate_text_entries[i].insert("1.0", text)

    def _refresh_charts(self, event=None):
        if self._latest_ranked:
            self._render_charts(self._latest_ranked)
        else:
            self._clear_charts()

    def _clear_charts(self):
        self._draw_empty_chart(self.score_bar_canvas, "Run ranking to see score bars.")
        self._draw_empty_chart(self.score_trend_canvas, "Run ranking to see score trend.")

    def _draw_empty_chart(self, canvas, message):
        if canvas is None:
            return
        canvas.delete("all")
        width = canvas.winfo_width() or int(canvas["width"])
        height = canvas.winfo_height() or int(canvas["height"])
        canvas.create_text(
            width / 2,
            height / 2,
            text=message,
            fill=self.palette["muted"],
            font=("TkDefaultFont", 9),
        )

    def _render_charts(self, ranked):
        if not ranked:
            self._clear_charts()
            return
        top_items = ranked[: min(10, len(ranked))]
        self._draw_bar_chart(self.score_bar_canvas, top_items)
        self._draw_line_chart(self.score_trend_canvas, ranked)

    def _draw_bar_chart(self, canvas, ranked):
        canvas.delete("all")
        if not ranked:
            return
        width = canvas.winfo_width() or int(canvas["width"])
        height = canvas.winfo_height() or int(canvas["height"])
        padding = 24
        chart_width = max(1, width - padding * 2)
        chart_height = max(1, height - padding * 2)
        max_score = max(score for _, score in ranked)
        if max_score <= 0:
            max_score = 1.0
        bar_width = chart_width / max(len(ranked), 1)

        canvas.create_line(padding, height - padding, width - padding, height - padding, fill=self.palette["border"])
        canvas.create_text(
            padding - 6,
            padding,
            text=f"{max_score:.2f}",
            fill=self.palette["muted"],
            anchor="e",
            font=("TkDefaultFont", 8),
        )
        canvas.create_text(
            padding - 6,
            height - padding,
            text="0",
            fill=self.palette["muted"],
            anchor="e",
            font=("TkDefaultFont", 8),
        )

        for index, (_, score) in enumerate(ranked):
            x0 = padding + index * bar_width + 4
            x1 = padding + (index + 1) * bar_width - 4
            if x1 <= x0:
                x1 = x0 + 1
            bar_height = chart_height * (score / max_score)
            y1 = height - padding
            y0 = y1 - bar_height
            canvas.create_rectangle(x0, y0, x1, y1, fill=self.palette["accent"], outline="")
            canvas.create_text(
                (x0 + x1) / 2,
                y1 + 10,
                text=str(index + 1),
                fill=self.palette["muted"],
                font=("TkDefaultFont", 8),
            )

    def _draw_line_chart(self, canvas, ranked):
        canvas.delete("all")
        if not ranked:
            return
        width = canvas.winfo_width() or int(canvas["width"])
        height = canvas.winfo_height() or int(canvas["height"])
        padding = 24
        chart_width = max(1, width - padding * 2)
        chart_height = max(1, height - padding * 2)
        scores = [score for _, score in ranked]
        max_score = max(scores)
        if max_score <= 0:
            max_score = 1.0
        count = len(scores)

        canvas.create_line(padding, height - padding, width - padding, height - padding, fill=self.palette["border"])
        canvas.create_line(padding, padding, padding, height - padding, fill=self.palette["border"])
        canvas.create_text(
            padding - 6,
            padding,
            text=f"{max_score:.2f}",
            fill=self.palette["muted"],
            anchor="e",
            font=("TkDefaultFont", 8),
        )
        canvas.create_text(
            padding - 6,
            height - padding,
            text="0",
            fill=self.palette["muted"],
            anchor="e",
            font=("TkDefaultFont", 8),
        )

        points = []
        for index, score in enumerate(scores):
            ratio = index / (count - 1) if count > 1 else 0.5
            x = padding + ratio * chart_width
            y = height - padding - (score / max_score) * chart_height
            points.append((x, y))

        if len(points) > 1:
            canvas.create_line(
                [coord for point in points for coord in point],
                fill=self.palette["accent"],
                width=2,
            )
        for x, y in points:
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=self.palette["accent"], outline="")

    def _parse_job_requirements(self):
        job_req = {}
        for feature, entry in self.job_inputs.items():
            value = entry.get().strip()
            if not value:
                job_req[feature] = 0.0
                continue
            try:
                job_req[feature] = float(value)
            except ValueError as exc:
                raise ValueError(f"Invalid value for '{feature}'. Use a number between 0 and 1.") from exc
        return normalize_feature_map(job_req)

    def _collect_resumes(self):
        resumes = []
        for i in range(self.CANDIDATE_SLOTS):
            name = self.candidate_name_entries[i].get().strip() or f"Candidate {i + 1}"
            text = self.candidate_text_entries[i].get("1.0", "end").strip()
            if text:
                resumes.append((name, text))
        if not resumes:
            raise ValueError("Please enter at least one candidate resume text.")
        return resumes

    def rank(self):
        try:
            job_req = self._parse_job_requirements()
            resumes = self._collect_resumes()
            ranked = rank_candidates(resumes, job_req, self.weights, top_k=len(resumes))
        except ValueError as error:
            messagebox.showerror("Input Error", str(error))
            return

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for i, (name, score) in enumerate(ranked, start=1):
            tag = "even" if i % 2 == 0 else "odd"
            self.result_tree.insert("", "end", values=(i, name, f"{score:.3f}"), tags=(tag,))

        if ranked:
            best_name, best_score = ranked[0]
            self.top_candidate_var.set(f"Top Candidate: {best_name} ({best_score:.3f})")
        else:
            self.top_candidate_var.set("Top Candidate: —")
        self._latest_ranked = ranked
        self._render_charts(ranked)

    def reset_fields(self):
        for entry in self.job_inputs.values():
            entry.delete(0, "end")
        for entry in self.candidate_name_entries:
            entry.delete(0, "end")
        for text_widget in self.candidate_text_entries:
            text_widget.delete("1.0", "end")
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.top_candidate_var.set("Top Candidate: —")
        self._latest_ranked = []
        self._clear_charts()
        if self.candidate_canvas is not None:
            self.candidate_canvas.yview_moveto(0)
        self._prefill_defaults()


if __name__ == "__main__":
    if tk is None:
        raise RuntimeError(
            "Tkinter is not available in this Python environment. "
            "Please install Python with Tk support to run the GUI."
        )
    root = tk.Tk()
    app = RecruitmentRankerGUI(root)
    root.mainloop()
