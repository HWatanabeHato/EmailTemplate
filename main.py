import tkinter as tk
from tkinter import (
    ttk,
    messagebox,
    font,
    filedialog,
    colorchooser,
    simpledialog  # 确保包含此项
)
import sqlite3
from datetime import datetime
from tkinterweb import HtmlFrame
from PIL import Image, ImageTk
import base64
import json

class EnhancedEmailTemplateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高级邮件模板管理")
        self.conn = sqlite3.connect('templates.db')
        self.create_tables()
        
        # 初始化富文本编辑器
        self.init_editor()
        self.create_gui()
        self.load_all_data()
        
        # 绑定快捷键
        self.root.bind("<Control-f>", lambda e: self.search_box.focus())
        self.root.bind("<Control-s>", lambda e: self.save_template())

    def init_editor(self):
        """初始化富文本编辑系统"""
        self.html_mode = False  # 切换HTML编辑模式
        self.current_font = "Arial"
        self.current_color = "#000000"
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                content TEXT,
                html_content TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        self.conn.commit()

    def create_gui(self):
        # 主界面布局
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧导航面板
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        # 搜索框
        self.search_var = tk.StringVar()
        self.search_box = ttk.Entry(left_panel, textvariable=self.search_var)
        self.search_box.pack(fill=tk.X, padx=5, pady=5)
        self.search_var.trace_add("write", self.perform_search)

        # 分类树形视图
        self.category_tree = ttk.Treeview(left_panel, show="tree", selectmode="browse")
        self.category_tree.pack(fill=tk.BOTH, expand=True)
        self.category_tree.bind("<<TreeviewSelect>>", self.load_category_templates)
        
        # 分类管理按钮
        cat_btn_frame = ttk.Frame(left_panel)
        cat_btn_frame.pack(fill=tk.X)
        ttk.Button(cat_btn_frame, text="新建分类", command=self.create_category).pack(side=tk.LEFT)
        ttk.Button(cat_btn_frame, text="删除分类", command=self.delete_category).pack(side=tk.LEFT)

        # 右侧主内容区
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 模板信息头
        header_frame = ttk.Frame(right_panel)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="模板名称:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(header_frame, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text="分类:").pack(side=tk.LEFT)
        self.category_combo = ttk.Combobox(header_frame, state="readonly")
        self.category_combo.pack(side=tk.LEFT, padx=5)
        
        # 富文本工具栏
        toolbar = ttk.Frame(right_panel)
        toolbar.pack(fill=tk.X)
        self.init_toolbar(toolbar)

        # 编辑器区域
        self.editor_notebook = ttk.Notebook(right_panel)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 富文本编辑标签
        self.text_editor = tk.Text(self.editor_notebook, wrap=tk.WORD, undo=True)
        self.editor_notebook.add(self.text_editor, text="富文本")
        
        # HTML编辑标签
        self.html_editor = HtmlFrame(self.editor_notebook)
        self.editor_notebook.add(self.html_editor, text="HTML")
        self.editor_notebook.bind("<<NotebookTabChanged>>", self.handle_editor_tab_change)

        # 底部操作栏
        footer_frame = ttk.Frame(right_panel)
        footer_frame.pack(fill=tk.X)
        ttk.Button(footer_frame, text="新建", command=self.new_template).pack(side=tk.LEFT)
        ttk.Button(footer_frame, text="保存", command=self.save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(footer_frame, text="导出", command=self.export_template).pack(side=tk.LEFT)
        ttk.Button(footer_frame, text="导入", command=self.import_template).pack(side=tk.LEFT, padx=5)

        # 添加模板列表树形视图（新增代码）
        self.template_tree = ttk.Treeview(
            left_panel, 
            columns=("id", "name"), 
            show="headings", 
            selectmode="browse"
        )
        self.template_tree.pack(fill=tk.BOTH, expand=True)
        self.template_tree.heading("name", text="模板名称")
        self.template_tree.column("id", width=0, stretch=tk.NO)  # 隐藏ID列

        # 模板列表事件绑定（新增代码）
        self.template_tree.bind("<<TreeviewSelect>>", self.load_template_content)

    def init_toolbar(self, parent):
        """初始化富文本工具栏"""
        # 字体选择
        font_frame = ttk.Frame(parent)
        font_frame.pack(side=tk.LEFT)
        self.font_combo = ttk.Combobox(font_frame, values=list(font.families()), width=15)
        self.font_combo.pack(side=tk.LEFT)
        self.font_combo.set("Arial")
        self.font_combo.bind("<<ComboboxSelected>>", self.change_font)

        # 字号选择
        self.size_combo = ttk.Combobox(font_frame, values=[8,10,12,14,16,18,20], width=3)
        self.size_combo.pack(side=tk.LEFT, padx=5)
        self.size_combo.set(12)
        self.size_combo.bind("<<ComboboxSelected>>", self.change_font)

        # 颜色选择
        ttk.Button(parent, text="颜色", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # 格式按钮
        ttk.Button(parent, text="B", style="Bold.TButton", command=lambda: self.toggle_format("bold")).pack(side=tk.LEFT)
        ttk.Button(parent, text="I", style="Italic.TButton", command=lambda: self.toggle_format("italic")).pack(side=tk.LEFT)
        ttk.Button(parent, text="U", style="Underline.TButton", command=lambda: self.toggle_format("underline")).pack(side=tk.LEFT)

        # 插入图片按钮
        ttk.Button(parent, text="插入图片", command=self.insert_image).pack(side=tk.LEFT, padx=5)

    def toggle_format(self, tag):
        """切换文本格式"""
        current_tags = self.text_editor.tag_names("sel.first")
        if tag in current_tags:
            self.text_editor.tag_remove(tag, "sel.first", "sel.last")
        else:
            self.text_editor.tag_add(tag, "sel.first", "sel.last")
            self.text_editor.tag_config(tag, 
                font=(self.current_font, self.size_combo.get(), tag),
                foreground=self.current_color)

    def change_font(self, event=None):
        """更改字体设置"""
        self.current_font = self.font_combo.get()
        self.apply_current_style()

    def choose_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color
            self.apply_current_style()

    def apply_current_style(self):
        """应用当前字体样式到选中文本"""
        sel_range = self.text_editor.tag_ranges("sel")
        if sel_range:
            self.text_editor.tag_add("custom_style", sel_range[0], sel_range[1])
            self.text_editor.tag_config("custom_style", 
                font=(self.current_font, self.size_combo.get()),
                foreground=self.current_color)

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
        """将富文本内容转换为HTML的完整实现"""
        text_content = self.text_editor.get(1.0, tk.END)
        # 这里可以添加更复杂的格式转换逻辑
        return f"<html><body>{text_content}</body></html>"

    def convert_html_to_text(self, html=None):
        """将HTML转换为纯文本的完整实现"""
        if html is None:
            html = self.html_editor.get_content()
        # 简单的HTML到文本转换，可根据需要增强
        return html.replace("<", "&lt;").replace(">", "&gt;")

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
        """创建新分类"""
        category = simpledialog.askstring("新建分类", "输入分类名称:")
        if category:
            try:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
                self.conn.commit()
                self.load_categories()
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "该分类已存在")

    def delete_category(self):
        """删除选中分类"""
        selected = self.category_tree.selection()
        if selected:
            category = self.category_tree.item(selected)['text']
            if messagebox.askyesno("确认", f"确定要删除分类 '{category}' 及其所有模板吗？"):
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM categories WHERE name=?", (category,))
                cursor.execute("DELETE FROM templates WHERE category=?", (category,))
                self.conn.commit()
                self.load_all_data()

    # 导入导出功能
    def export_template(self):
        """导出当前模板"""
        # 实现JSON/HTML导出逻辑
        pass

    def import_template(self):
        """导入模板"""
        # 实现文件导入逻辑
        pass

    # 搜索功能
    def perform_search(self, *args):
        """执行实时搜索"""
        query = self.search_var.get().lower()
        # 实现搜索逻辑
        pass

    def load_category_templates(self, event):
        """加载选中分类的模板（修复版）"""
        selected = self.category_tree.selection()
        if selected:
            # 清空现有模板列表
            for item in self.template_tree.get_children():
                self.template_tree.delete(item)
        
            # 获取分类名称
            category = self.category_tree.item(selected)['text']
        
            # 查询数据库
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name FROM templates WHERE category=?", (category,))
        
            # 填充模板列表
            for template_id, name in cursor.fetchall():
                self.template_tree.insert(
                    "", 
                    tk.END, 
                    values=(template_id, name), 
                    text=name
                )
    
    def new_template(self):
        """新建模板的完整实现"""
        self.current_template_id = None
        self.name_entry.delete(0, tk.END)
        self.category_combo.set('')
        self.text_editor.delete(1.0, tk.END)
        self.html_editor.load_html("")
    
    def save_template(self):
        """保存模板的完整实现"""
        name = self.name_entry.get()
        category = self.category_combo.get()
        content = self.text_editor.get(1.0, tk.END)
        html_content = self.html_editor.get_content() if self.html_mode else ""

        if not name or not category:
            messagebox.showwarning("警告", "名称和分类不能为空")
            return

        try:
            cursor = self.conn.cursor()
            # 检查分类是否存在
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            
            if self.current_template_id:
                # 更新现有模板
                cursor.execute("""
                    UPDATE templates SET 
                    name=?, 
                    category=?, 
                    content=?, 
                    html_content=?, 
                    updated_at=?
                    WHERE id=?
                """, (name, category, content, html_content, datetime.now(), self.current_template_id))
            else:
                # 新建模板
                cursor.execute("""
                    INSERT INTO templates (
                        name, 
                        category, 
                        content, 
                        html_content, 
                        created_at, 
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (name, category, content, html_content, datetime.now(), datetime.now()))
            
            self.conn.commit()
            self.load_all_data()
            messagebox.showinfo("成功", "模板保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def load_all_data(self):
        """加载所有分类和模板数据"""
        self.load_categories()
        self.load_templates()

    def load_categories(self):
        """加载分类到树形视图"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        
        # 清空现有树节点
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        # 添加分类节点
        for cat in categories:
            self.category_tree.insert("", tk.END, text=cat)

    def load_templates(self, category=None):
        """加载模板到列表"""
        # 实现模板加载逻辑
        pass

    def load_template_content(self, event):
        """加载选中模板的内容（修复版）"""
        selection = self.template_tree.selection()
        if selection:
            # 获取模板ID
            template_id = self.template_tree.item(selection[0])['values'][0]
        
            # 查询数据库
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, category, content, html_content FROM templates WHERE id=?", (template_id,))
            result = cursor.fetchone()
        
            if result:
                # 更新界面控件
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, result[0])
                self.category_combo.set(result[1])
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, result[2])
                self.html_editor.load_html(result[3] if result[3] else "")
    


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Bold.TButton", font=('Arial', 10, 'bold'))
    style.configure("Italic.TButton", font=('Arial', 10, 'italic'))
    style.configure("Underline.TButton", font=('Arial', 10, 'underline'))
    app = EnhancedEmailTemplateApp(root)
    root.mainloop()