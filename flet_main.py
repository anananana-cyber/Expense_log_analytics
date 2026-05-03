import flet as ft
import sqlite3
from datetime import date, datetime
import os
from pathlib import Path
from itertools import groupby

# --- PERSISTENT STORAGE SETUP ---
app_name = "AntigravityFinance"
app_data_path = Path(os.environ.get('APPDATA', Path.home())) / app_name
app_data_path.mkdir(parents=True, exist_ok=True)
DB_PATH = app_data_path / "wealth_manager.db"

CATEGORIES = ["Housing", "Food", "Transport", "Utilities", "Entertainment", "Healthcare", "Other"]

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT,
                description TEXT,
                category    TEXT,
                type        TEXT,
                amount      REAL
            )
        """)
        conn.commit()

def load_data():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def insert_transaction(txn_date, description, category, txn_type, amount):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO transactions (date, description, category, type, amount) VALUES (?,?,?,?,?)",
            (txn_date, description, category, txn_type, amount)
        )
        conn.commit()

def delete_transaction(txn_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        conn.commit()

init_db()

# Premium styling tokens
C_BG_START = "#0f0c29"
C_BG_MID = "#302b63"
C_BG_END = "#24243e"
C_CARD_BG = ft.colors.with_opacity(0.1, ft.colors.WHITE)
C_CARD_BORDER = ft.colors.with_opacity(0.15, ft.colors.WHITE)
C_ACCENT_PRIMARY = "#c084fc"
C_ACCENT_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=["#7c3aed", "#38bdf8"]
)
C_INCOME = "#34d399"
C_EXPENSE = "#f87171"
C_TEXT = "#f3eeff"
C_TEXT_MUTED = "#94a3b8"

def main(page: ft.Page):
    page.title = "Antigravity Finance"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 420
    page.window_height = 850
    page.fonts = {
        "Inter": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.woff2",
        "Inter-Bold": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Bold.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")

    dash_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=20, expand=True)
    logs_list = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
    
    # Form Widgets
    amount_input = ft.TextField(label="Amount (₹)", keyboard_type=ft.KeyboardType.NUMBER, border_color=C_CARD_BORDER, focused_border_color=C_ACCENT_PRIMARY)
    desc_input = ft.TextField(label="Description", hint_text="e.g. Zomato order", border_color=C_CARD_BORDER, focused_border_color=C_ACCENT_PRIMARY)
    cat_dropdown = ft.Dropdown(label="Category", options=[ft.dropdown.Option(c) for c in CATEGORIES], value="Housing", border_color=C_CARD_BORDER)
    type_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Income", label="Income", active_color=C_INCOME), ft.Radio(value="Expense", label="Expense", active_color=C_EXPENSE)]), value="Expense")

    # Date Picker Logic
    selected_date = date.today()
    selected_date_text = ft.Text(value=selected_date.strftime("%Y-%m-%d"), size=16, weight=ft.FontWeight.W_800, color=C_TEXT)

    def change_date(e):
        nonlocal selected_date
        selected_date = date_picker.value.date()
        selected_date_text.value = selected_date.strftime("%Y-%m-%d")
        page.update()

    date_picker = ft.DatePicker(
        on_change=change_date,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(date_picker)

    def glass_card(content_widget, padding=15):
        return ft.Container(
            content=content_widget,
            padding=padding,
            bgcolor=C_CARD_BG,
            border_radius=16,
            border=ft.border.all(1, C_CARD_BORDER),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.with_opacity(0.1, ft.colors.BLACK))
        )

    def refresh_app():
        df_all = load_data()
        
        # --- LOGS TAB WITH DATE GROUPING ---
        logs_list.controls.clear()
        if not df_all:
            logs_list.controls.append(ft.Text("No logs available.", color=C_TEXT_MUTED))
        else:
            grouped = groupby(df_all, key=lambda x: x['date'])
            for txn_date, items in grouped:
                try:
                    dt = datetime.strptime(txn_date, "%Y-%m-%d")
                    if dt.date() == date.today():
                        date_str = "Today"
                    else:
                        date_str = dt.strftime("%A, %d %b %Y")
                except:
                    date_str = txn_date
                
                logs_list.controls.append(
                    ft.Text(date_str, size=14, weight=ft.FontWeight.W_800, color=C_ACCENT_PRIMARY)
                )
                
                for row in items:
                    sign = "+" if row["type"] == "Income" else "-"
                    color = C_INCOME if row["type"] == "Income" else C_EXPENSE
                    
                    def make_del_click(txn_id):
                        def on_click(e):
                            delete_transaction(txn_id)
                            refresh_app()
                        return on_click
                    
                    row_ui = ft.Row([
                        ft.Column([
                            ft.Text(row['description'], size=15, weight=ft.FontWeight.W_600, color=C_TEXT),
                            ft.Text(row['category'], color=C_TEXT_MUTED, size=12)
                        ], expand=True),
                        ft.Text(f"{sign}₹{row['amount']:,.0f}", color=color, size=15, weight=ft.FontWeight.W_800),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_300, on_click=make_del_click(row['id']), tooltip="Delete")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    
                    logs_list.controls.append(glass_card(row_ui, padding=12))

        # --- DASHBOARD TAB ---
        dash_content.controls.clear()
        if not df_all:
            dash_content.controls.append(ft.Text("🌱 No transactions yet. Go to Add Entry.", color=C_TEXT_MUTED))
        else:
            total_income = sum(r['amount'] for r in df_all if r['type'] == 'Income')
            total_expenses = sum(r['amount'] for r in df_all if r['type'] == 'Expense')
            net_balance = total_income - total_expenses
            savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0.0
            
            def kpi_card(title, value, color=C_TEXT):
                return glass_card(
                    ft.Column([
                        ft.Text(title, size=11, color=C_TEXT_MUTED, weight=ft.FontWeight.W_800),
                        ft.Text(value, size=20, weight=ft.FontWeight.W_800, color=color)
                    ])
                )
            
            dash_content.controls.extend([
                ft.Row([
                    ft.Container(content=kpi_card("💰 INCOME", f"₹{total_income:,.0f}", C_INCOME), expand=True),
                    ft.Container(content=kpi_card("💸 EXPENSES", f"₹{total_expenses:,.0f}", C_EXPENSE), expand=True)
                ]),
                ft.Row([
                    ft.Container(content=kpi_card("🏦 BALANCE", f"₹{net_balance:,.0f}"), expand=True),
                    ft.Container(content=kpi_card("📈 SAVINGS", f"{savings_rate:.1f}%"), expand=True)
                ])
            ])
            
            cat_totals = {}
            for r in df_all:
                if r['type'] == 'Expense':
                    cat = r['category']
                    cat_totals[cat] = cat_totals.get(cat, 0) + r['amount']
                    
            if cat_totals:
                colors = ["#7c3aed", "#38bdf8", "#34d399", "#fbbf24", "#f87171", "#fb923c", "#f472b6"]
                pie_sections = []
                for i, (cat, amt) in enumerate(cat_totals.items()):
                    pie_sections.append(
                        ft.PieChartSection(
                            amt, 
                            title=f"{cat}\n₹{amt:,.0f}", 
                            color=colors[i % len(colors)], 
                            radius=65,
                            title_style=ft.TextStyle(size=11, color=ft.colors.WHITE, weight=ft.FontWeight.W_800)
                        )
                    )

                pie_chart = ft.PieChart(
                    sections=pie_sections, sections_space=2, center_space_radius=35, expand=True,
                )
                dash_content.controls.append(ft.Text("Expense Breakdown", size=18, weight=ft.FontWeight.W_800))
                dash_content.controls.append(glass_card(ft.Container(content=pie_chart, height=220)))

            # Advisor
            dash_content.controls.append(ft.Text("💡 AI Insights", size=18, weight=ft.FontWeight.W_800))
            if total_expenses > total_income:
                dash_content.controls.append(glass_card(ft.Text("🚨 Deficit warning: Your expenses exceed income this month.", color=ft.colors.RED_100)))
            elif total_income > 0 and savings_rate < 20:
                dash_content.controls.append(glass_card(ft.Text("⚠️ Savings rate below 20%. Consider reducing discretionary spending.", color=ft.colors.ORANGE_100)))
            elif total_income > 0:
                dash_content.controls.append(glass_card(ft.Text("✅ Great work! Your savings rate is above the 20% benchmark.", color=ft.colors.GREEN_100)))

        page.update()

    def submit_click(e):
        try:
            amt = float(amount_input.value)
            desc = desc_input.value.strip()
            if amt > 0 and desc:
                insert_transaction(selected_date.strftime("%Y-%m-%d"), desc, cat_dropdown.value, type_radio.value, amt)
                amount_input.value = ""
                desc_input.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("Transaction saved!"), bgcolor=ft.colors.GREEN_700)
                page.snack_bar.open = True
                refresh_app()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Enter a valid amount and description."), bgcolor=ft.colors.RED_700)
                page.snack_bar.open = True
                page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Invalid amount format."), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()

    submit_btn = ft.Container(
        content=ft.Text("✅ Submit Transaction", weight=ft.FontWeight.W_800, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER),
        gradient=C_ACCENT_GRADIENT,
        padding=15,
        border_radius=12,
        alignment=ft.alignment.center,
        on_click=submit_click,
        ink=True,
    )

    # Add Tab Assembly
    date_picker_row = glass_card(
        ft.Row([
            ft.Text("Date:", weight=ft.FontWeight.W_800, color=C_TEXT_MUTED),
            selected_date_text,
            ft.IconButton(
                icon=ft.icons.CALENDAR_MONTH,
                icon_color=C_ACCENT_PRIMARY,
                on_click=lambda e: date_picker.pick_date()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10
    )

    add_tab_content = ft.Column([
        date_picker_row,
        glass_card(ft.Column([
            amount_input,
            desc_input,
            cat_dropdown,
            ft.Text("Type:", weight=ft.FontWeight.W_800, color=C_TEXT_MUTED),
            type_radio,
        ], spacing=15)),
        submit_btn
    ], spacing=20, scroll=ft.ScrollMode.AUTO)
    
    manage_tab_content = ft.Column([
        logs_list
    ], expand=True)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        divider_color=C_CARD_BORDER,
        indicator_color=C_ACCENT_PRIMARY,
        label_color=C_ACCENT_PRIMARY,
        unselected_label_color=C_TEXT_MUTED,
        tabs=[
            ft.Tab(text="Dash", icon=ft.icons.DASHBOARD_ROUNDED, content=ft.Container(content=dash_content, padding=20)),
            ft.Tab(text="Add", icon=ft.icons.ADD_CIRCLE_ROUNDED, content=ft.Container(content=add_tab_content, padding=20)),
            ft.Tab(text="Logs", icon=ft.icons.LIST_ALT_ROUNDED, content=ft.Container(content=manage_tab_content, padding=20)),
        ],
        expand=1,
    )
    
    main_container = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
            colors=[C_BG_START, C_BG_MID, C_BG_END]
        ),
        expand=True,
        content=ft.SafeArea(ft.Column([
            ft.Container(
                content=ft.Text("Antigravity", size=28, weight=ft.FontWeight.W_800, color=ft.colors.WHITE),
                padding=ft.padding.only(left=20, top=20, bottom=5)
            ),
            tabs
        ], expand=True))
    )
    
    page.add(main_container)
    refresh_app()

ft.app(target=main)
