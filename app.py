import streamlit as st
from auth import check_authentication, render_login_page, logout
from streamlit_option_menu import option_menu

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="النظام المالي الإلكتروني",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دعم الاتجاه واللغة العربية وتنسيق الواجهة
st.markdown(
    """
    <style>
    body, div, input, button, select {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        direction: rtl;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# فحص تسجيل الدخول
check_authentication()

if not st.session_state["authenticated"]:
    render_login_page()
else:
    # القائمة الجانبية والمعلومات الشخصية
    user_info = st.session_state["user"]
    
    with st.sidebar:
        st.title("💼 النظام المالي")
        st.write(f"مرحباً، **{user_info.get('username')}**")
        st.caption(f"الصلاحية: {user_info.get('role')}")
        st.divider()

        selected_menu = option_menu(
            menu_title="القائمة الرئيسية",
            options=["الداش بورد", "دليل الحسابات", "إدخال قيود", "التقارير المالية"],
            icons=["speedometer2", "diagram-3", "journal-plus", "file-earmark-bar-graph"],
            menu_icon="cast",
            default_index=0,
        )

        st.divider()
        if st.button("تسجيل الخروج", type="secondary", use_container_width=True):
            logout()

    # توجيه الشاشات حسب الاختيار
    if selected_menu == "الداش بورد":
        st.header("📌 لوحة التحكم الرئيسية (Dashboard)")
        st.info("أهلاً بك في النظام المالي الإلكتروني. يمكنك التنقل عبر القائمة الجانبية لإدارة الحسابات والقيود.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("حالة النظام", "متصل آونلاين", delta="Google Sheets API")
        with col2:
            st.metric("المستخدم الحالي", user_info.get('username'))
        with col3:
            st.metric("مستوى الصلاحية", user_info.get('role'))

    elif selected_menu == "دليل الحسابات":
        try:
            from views.chart_of_accounts import render_chart_of_accounts_view
            render_chart_of_accounts_view()
        except ImportError:
            st.warning("صفحة دليل الحسابات قيد الإنشاء (سيتم إضافتها في الخطوة التالية).")

    elif selected_menu == "إدخال قيود":
        try:
            from views.entry_view import render_entry_view
            render_entry_view()
        except ImportError:
            st.warning("صفحة إدخال القيود قيد الإنشاء (سيتم إضافتها في الخطوة التالية).")

    elif selected_menu == "التقارير المالية":
        try:
            from views.reports_view import render_reports_view
            render_reports_view()
        except ImportError:
            st.warning("صفحة التقارير المالية قيد الإنشاء (سيتم إضافتها في الخطوة التالية).")