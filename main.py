import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime

class EmailTemplateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("邮件模板管理")
        self.conn = sqlite3.connect('templates.db')
        self.create_tables()
        
        # 初始化字体样式
        self.bold_font = font.Font(weight="bold")
        self.normal_font = font.Font(weight="normal")
        
        self.create_widgets()
        self.load_categories()
        self.load_templates()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                content TEXT,
                created_at DATETIME
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # 左侧面板
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 分类筛选
        ttk.Label(left_frame, text="分类:").pack(anchor=tk.W)
        self.category_combo = ttk.Combobox(left_frame, state='readonly')
        self.category_combo.pack(fill=tk.X)
        self.category_combo.bind('<<ComboboxSelected>>', self.filter_by_category)

        # 模板列表
        self.template_list = tk.Listbox(left_frame, width=25)
        self.template_list.pack(fill=tk.BOTH, expand=True)
        self.template_list.bind('<<ListboxSelect>>', self.load_template_content)

        # 右侧编辑区
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 模板名称
        ttk.Label(right_frame, text="模板名称:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(right_frame)
        self.name_entry.pack(fill=tk.X)

        # 富文本编辑
        ttk.Label(right_frame, text="内容:").pack(anchor=tk.W)
        self.content_text = tk.Text(right_frame, wrap=tk.WORD, height=15)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # 格式工具栏
        #toolbar = ttk.Frame(right_frame)
        #toolbar.pack(fill=tk.X)
        #self.bold_btn = ttk.Button(toolbar, text="B", command=lambda: self.toggle_font_weight())
        #self.bold_btn.pack(side=tk.LEFT)

        # 分类输入
        ttk.Label(right_frame, text="分类:").pack(anchor=tk.W)
        self.category_entry = ttk.Entry(right_frame)
        self.category_entry.pack(fill=tk.X)

        # 操作按钮
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="新建", command=self.new_template).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="保存", command=self.save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_template).pack(side=tk.LEFT)

    def toggle_font_weight(self):
        current_tags = self.content_text.tag_names("sel.first")
        if "bold" in current_tags:
            self.content_text.tag_remove("bold", "sel.first", "sel.last")
        else:
            self.content_text.tag_add("bold", "sel.first", "sel.last")
            self.content_text.tag_configure("bold", font=self.bold_font)

    def load_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM templates")
        categories = [row[0] for row in cursor.fetchall()]
        self.category_combo['values'] = categories

    def load_templates(self):
        self.template_list.delete(0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM templates")
        for row in cursor.fetchall():
            self.template_list.insert(tk.END, row[1], row[0])

    def filter_by_category(self, event):
        category = self.category_combo.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM templates WHERE category=?", (category,))
        self.template_list.delete(0, tk.END)
        for row in cursor.fetchall():
            self.template_list.insert(tk.END, row[1], row[0])

<<<<<<< Updated upstream
    def load_template_content(self, event):
        selection = self.template_list.curselection()
        if selection:
            template_id = self.template_list.get(selection[0], tk.END)[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, category, content FROM templates WHERE id=?", (template_id,))
            result = cursor.fetchone()
            if result:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, result[0])
                self.category_entry.delete(0, tk.END)
                self.category_entry.insert(0, result[1])
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, result[2])
=======
    # 后续数据库操作和功能方法与之前类似，但需要增加对HTML内容的支持
    # 此处省略部分数据库操作方法，保持代码长度合理

    def handle_editor_tab_change(self, event):
        """处理编辑器标签切换"""
        current_tab = self.editor_notebook.index(self.editor_notebook.select())
        self.html_mode = (current_tab == 1)
        
        if self.html_mode:
            # 同步文本到HTML编辑器
            html_content = self.convert_text_to_html()
            self.html_editor.load_html(html_content)
        else:
            # 同步HTML到文本编辑器
            text_content = self.convert_html_to_text()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, text_content)

    def convert_text_to_html(self):
        """将富文本内容转换为HTML"""
        # 此处实现格式转换逻辑
        return "<html><body>" + self.text_editor.get(1.0, tk.END) + "</body></html>"

    def convert_html_to_text(self):
        """将HTML内容转换为纯文本"""
        return self.html_editor.get_content().strip()

    def insert_image(self):
        """插入图片到编辑器"""
        filepath = filedialog.askopenfilename(filetypes=[
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp")
        ])
        if filepath:
            try:
                # 将图片转为base64嵌入
                with open(filepath, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                img_tag = f'<img src="data:image/png;base64,{img_data}">'
                self.text_editor.insert(tk.END, "\n" + img_tag + "\n")
            except Exception as e:
                messagebox.showerror("错误", f"无法插入图片: {str(e)}")

    # 分类管理功能
    
    def create_category(self):
        """创建新分类（修复后的版本）"""
        # 使用 tkinter.simpledialog 的正确调用方式
        category = simpledialog.askstring(
            "新建分类", 
            "输入分类名称:",
            parent=self.root  # 添加 parent 参数确保对话框正确显示
        )
    
        if category:
            try:
                cursor = self.conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
                self.conn.commit()
                self.load_categories()
                # 自动选中新建分类
                self.category_combo.set(category)
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "该分类已存在")
            except Exception as e:
                messagebox.showerror("错误", f"创建失败: {str(e)}")
>>>>>>> Stashed changes

    def new_template(self):
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)

    def save_template(self):
        name = self.name_entry.get()
        category = self.category_entry.get()
        content = self.content_text.get(1.0, tk.END)
        
        if not name or not category:
            messagebox.showwarning("警告", "名称和分类不能为空")
            return

        cursor = self.conn.cursor()
        if self.template_list.curselection():
            # 更新现有模板
            template_id = self.template_list.get(self.template_list.curselection()[0], tk.END)[0]
            cursor.execute("UPDATE templates SET name=?, category=?, content=? WHERE id=?",
                          (name, category, content, template_id))
        else:
            # 新建模板
            cursor.execute("INSERT INTO templates (name, category, content, created_at) VALUES (?, ?, ?, ?)",
                          (name, category, content, datetime.now()))
        
        self.conn.commit()
        self.load_categories()
        self.load_templates()

    def delete_template(self):
        if self.template_list.curselection():
            template_id = self.template_list.get(self.template_list.curselection()[0], tk.END)[0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM templates WHERE id=?", (template_id,))
            self.conn.commit()
            self.load_categories()
            self.load_templates()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailTemplateApp(root)
    root.mainloop()