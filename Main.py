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

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Recruitment Ranker")
        self.root.geometry("1000x700")
        self.root.minsize(900, 620)

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
        style.configure("Header.TLabel", font=("TkDefaultFont", 20, "bold"))
        style.configure("Section.TLabelframe.Label", font=("TkDefaultFont", 11, "bold"))
        style.configure("Primary.TButton", font=("TkDefaultFont", 10, "bold"), padding=8)
        style.configure("Results.TLabel", font=("TkDefaultFont", 10))

    def _build_layout(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Smart Recruitment Ranker", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 8))
        subtitle = ttk.Label(
            container,
            text="Set job requirements, enter resumes, and rank candidates instantly.",
        )
        subtitle.pack(anchor="w", pady=(0, 14))

        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(body)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right_panel = ttk.Frame(body)
        right_panel.grid(row=0, column=1, sticky="nsew")

        self._build_job_requirements(left_panel)
        self._build_candidate_inputs(left_panel)
        self._build_results(right_panel)

    def _build_job_requirements(self, parent):
        frame = ttk.LabelFrame(parent, text="Job Requirements (0.0 to 1.0)", style="Section.TLabelframe")
        frame.pack(fill="x", padx=2, pady=(0, 10))

        key_features = [
            "Python",
            "Machine Learning",
            "Cloud Computing",
            "SQL",
            "Years of Experience",
        ]
        for index, feature in enumerate(key_features):
            ttk.Label(frame, text=feature).grid(row=index, column=0, sticky="w", padx=8, pady=6)
            entry = ttk.Entry(frame, width=12)
            entry.grid(row=index, column=1, sticky="w", padx=8, pady=6)
            self.job_inputs[feature] = entry

    def _build_candidate_inputs(self, parent):
        frame = ttk.LabelFrame(parent, text="Candidate Resumes", style="Section.TLabelframe")
        frame.pack(fill="both", expand=True, padx=2, pady=(0, 10))

        for i in range(self.CANDIDATE_SLOTS):
            row_base = i * 3
            ttk.Label(frame, text=f"Candidate {i + 1} Name").grid(
                row=row_base, column=0, sticky="w", padx=8, pady=(8, 2)
            )
            name_entry = ttk.Entry(frame)
            name_entry.grid(row=row_base, column=1, sticky="ew", padx=8, pady=(8, 2))
            self.candidate_name_entries.append(name_entry)

            ttk.Label(frame, text=f"Candidate {i + 1} Resume Text").grid(
                row=row_base + 1, column=0, sticky="nw", padx=8, pady=(2, 8)
            )
            resume_text = tk.Text(frame, height=4, wrap="word")
            resume_text.grid(row=row_base + 1, column=1, sticky="ew", padx=8, pady=(2, 8))
            self.candidate_text_entries.append(resume_text)

        frame.columnconfigure(1, weight=1)

        button_row = ttk.Frame(parent)
        button_row.pack(fill="x")
        ttk.Button(button_row, text="Rank Candidates", style="Primary.TButton", command=self.rank).pack(
            side="left", padx=(2, 8)
        )
        ttk.Button(button_row, text="Reset", command=self.reset_fields).pack(side="left")

    def _build_results(self, parent):
        frame = ttk.LabelFrame(parent, text="Ranking Results", style="Section.TLabelframe")
        frame.pack(fill="both", expand=True)

        self.top_candidate_var = tk.StringVar(value="Top Candidate: —")
        top_candidate = ttk.Label(
            frame,
            textvariable=self.top_candidate_var,
            font=("TkDefaultFont", 12, "bold"),
            foreground="#0b5ed7",
        )
        top_candidate.pack(anchor="w", padx=10, pady=(12, 8))

        columns = ("rank", "name", "score")
        self.result_tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        self.result_tree.heading("rank", text="Rank")
        self.result_tree.heading("name", text="Candidate")
        self.result_tree.heading("score", text="Score")
        self.result_tree.column("rank", width=60, anchor="center")
        self.result_tree.column("name", width=170, anchor="w")
        self.result_tree.column("score", width=90, anchor="center")
        self.result_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

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
            self.result_tree.insert("", "end", values=(i, name, f"{score:.3f}"))

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
