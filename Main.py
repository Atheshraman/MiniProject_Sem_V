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
    CANDIDATE_SLOTS = 3
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

        for i in range(self.CANDIDATE_SLOTS):
            row_base = i * 3
            ttk.Label(frame, text=f"Candidate {i + 1} Name", style="Card.TLabel").grid(
                row=row_base, column=0, sticky="w", padx=8, pady=(8, 2)
            )
            name_entry = ttk.Entry(frame, style="Modern.TEntry")
            name_entry.grid(row=row_base, column=1, sticky="ew", padx=8, pady=(8, 2))
            self.candidate_name_entries.append(name_entry)

            ttk.Label(frame, text=f"Candidate {i + 1} Resume Text", style="Card.TLabel").grid(
                row=row_base + 1, column=0, sticky="nw", padx=8, pady=(2, 8)
            )
            resume_text = tk.Text(
                frame,
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

        frame.columnconfigure(1, weight=1)

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

        columns = ("rank", "name", "score")
        self.result_tree = ttk.Treeview(
            frame,
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
        self.result_tree.pack(fill="both", expand=True)

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
