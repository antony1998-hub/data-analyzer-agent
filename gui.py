import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import threading
from src.core import analyze_all_files, generate_ai_report, auto_visualize

class DataAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 数据分析助手（增强版）")
        self.root.geometry("1000x700")
        self.chart_image_label = None  # 用于显示图表预览
        self.create_widgets()

    def create_widgets(self):
        # 顶部：选择路径
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10, fill=tk.X)

        tk.Label(frame1, text="数据文件夹：").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar()
        tk.Entry(frame1, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="📁 选择文件夹", command=self.select_folder).pack(side=tk.LEFT, padx=5)

        # 文件选择下拉框
        frame_file = tk.Frame(self.root)
        frame_file.pack(pady=5, fill=tk.X, padx=20)
        tk.Label(frame_file, text="选择文件：").pack(side=tk.LEFT)
        self.filename_combo = ttk.Combobox(frame_file, state="readonly", width=60)
        self.filename_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.filename_combo.bind("<<ComboboxSelected>>", self.on_file_selected)

        # 输入框（预测用）
        self.column_var = tk.StringVar(value="")
        self.steps_var = tk.IntVar(value=5)

        frame3 = tk.Frame(self.root)
        frame3.pack(pady=5)

        tk.Label(frame3, text="列名：").grid(row=0, column=0, padx=10)
        self.column_combo = ttk.Combobox(frame3, textvariable=self.column_var, width=13, state="readonly")
        self.column_combo.grid(row=0, column=1)

        tk.Label(frame3, text="步数：").grid(row=0, column=2, padx=10)
        tk.Entry(frame3, textvariable=self.steps_var, width=5).grid(row=0, column=3)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📊 自动可视化", command=self.on_visualize_click, bg="lightgreen", width=15).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🤖 AI 分析报告", command=self.on_ai_report_click, width=15).pack(side=tk.LEFT,
                                                                                              padx=5)
        tk.Button(btn_frame, text="📈 所有文件分析", command=self.on_analyze_all, width=15).pack(side=tk.LEFT, padx=5)

        # 图像预览区域
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.chart_image_label = tk.Label(self.image_frame)
        self.chart_image_label.pack()

        # 结果显示框
        self.result_text = scrolledtext.ScrolledText(self.root, height=10)
        self.result_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

    def select_folder(self):
        """选择文件夹"""
        global BASE_PATH
        path = filedialog.askdirectory()
        if path:
            BASE_PATH = path
            self.path_var.set(path)
            self.load_files()

    def load_files(self):
        """加载文件夹中的文件到下拉框"""
        global BASE_PATH
        files = [f for f in os.listdir(BASE_PATH) if f.endswith(('.csv', '.xlsx', '.txt'))]
        self.filename_combo['values'] = files
        if files:
            self.filename_combo.current(0)
            self.on_file_selected(None)

    def on_file_selected(self, event):
        """文件选择后更新列名下拉框"""
        filename = self.filename_combo.get()
        if not filename or not BASE_PATH:
            return

        file_path = os.path.join(BASE_PATH, filename)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            elif filename.endswith(".txt"):
                df = pd.read_csv(file_path, delimiter='\t')
            else:
                return

            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            self.column_combo['values'] = numeric_cols
            if numeric_cols:
                self.column_combo.current(0)
        except Exception as e:
            print(f"读取文件失败：{e}")

    def on_visualize_click(self):
        """可视化按钮点击事件"""
        filename = self.filename_combo.get()
        if not filename:
            messagebox.showwarning("警告", "请先选择一个文件")
            return

        # 清除旧图像
        if self.chart_image_label:
            self.chart_image_label.config(image=None)
            self.chart_image_label.image = None

        # 启动绘图（在子线程中避免卡顿）
        def task():
            result_msg, img_path = auto_visualize(filename, BASE_PATH)
            self.root.after(0, lambda: self.display_result(result_msg))
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((800, 400))  # 缩放适应窗口
                    photo = ImageTk.PhotoImage(img)
                    self.root.after(0, lambda: self.update_image_display(photo))
                except Exception as e:
                    print(f"图像加载失败：{e}")

        threading.Thread(target=task, daemon=True).start()

    def on_ai_report_click(self):
        """生成AI报告"""
        filename = self.filename_combo.get()
        if not filename:
            messagebox.showwarning("警告", "请先选择一个文件")
            return

        def task():
            result = generate_ai_report(filename, BASE_PATH)
            self.root.after(0, lambda: self.display_result(result))

        threading.Thread(target=task, daemon=True).start()

    def on_analyze_all(self):
        """分析所有文件"""
        def task():
            result = analyze_all_files(BASE_PATH)
            self.root.after(0, lambda: self.display_result(result))

        threading.Thread(target=task, daemon=True).start()

    def display_result(self, msg):
        """更新结果文本框"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, msg)

    def update_image_display(self, photo):
        """更新图像显示"""
        self.chart_image_label.config(image=photo)
        self.chart_image_label.image = photo  # 防止被垃圾回收