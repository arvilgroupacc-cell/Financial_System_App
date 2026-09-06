import streamlit as st
import pandas as pd
from api_connector import get_chart_of_accounts, add_account

def render_chart_of_accounts_view():
    st.header("🌳 دليل الحسابات (Chart of Accounts)")
    st.caption("عرض وإدارة الهيكل الشجري للحسابات")

    # جلب الحسابات من API
    with st.spinner("جاري تحميل دليل الحسابات..."):
        res = get_chart_of_accounts()

    if res.get("status") != "success":
        st.error(f"حدث خطأ أثناء جلب دليل الحسابات: {res.get('message')}")
        return

    accounts = res.get("accounts", [])
    df_accounts = pd.DataFrame(accounts)

    # تبويب العرض وإضافة حساب
    tab1, tab2 = st.tabs(["📋 عرض دليل الحسابات", "➕ إضافة حساب جديد"])

    with tab1:
        if df_accounts.empty:
            st.info("لا توجد حسابات مسجلة بعد.")
        else:
            # إعادة ترتيب وتسمية الأعمدة للواجهة
            df_display = df_accounts.rename(columns={
                "code": "كود الحساب",
                "name": "اسم الحساب",
                "type": "نوع الحساب",
                "parentCode": "كود الحساب الأب",
                "level": "المستوى",
                "openingBalance": "الرصيد الافتتاحي"
            })
            
            # خيار البحث والفلترة
            search_query = st.text_input("🔍 بحث عن حساب (بالاسم أو الكود)", "")
            if search_query:
                df_display = df_display[
                    df_display["اسم الحساب"].astype(str).str.contains(search_query) | 
                    df_display["كود الحساب"].astype(str).str.contains(search_query)
                ]

            st.dataframe(df_display, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("إضافة حساب جديد في شجرة الحسابات")
        
        with st.form("add_account_form"):
            acc_name = st.text_input("اسم الحساب الجديد *")
            
            acc_type = st.selectbox("نوع الحساب *", [
                "أصول ثابتة", "أصول متداولة", "التزامات متداولة", 
                "التزامات طويلة الأجل", "حقوق ملكية", "إيرادات", "مصروفات"
            ])
            
            # قائمة اختيار الحساب الأب
            parent_options = {"بدون حساب أب (حساب رئيسي)": ""}
            for acc in accounts:
                parent_options[f"{acc['code']} - {acc['name']}"] = acc['code']
            
            selected_parent_label = st.selectbox("الحساب الأب (إن وجد)", list(parent_options.keys()))
            parent_code = parent_options[selected_parent_label]

            opening_bal = st.number_input("الرصيد الافتتاحي", value=0.0, step=100.0)

            submit_btn = st.form_submit_button("حفظ الحساب", type="primary")

            if submit_btn:
                if not acc_name:
                    st.error("يرجى كتابة اسم الحساب.")
                else:
                    username = st.session_state.get("user", {}).get("username", "System")
                    with st.spinner("جاري حفظ الحساب..."):
                        save_res = add_account(acc_name, acc_type, parent_code, opening_bal, username)
                        if save_res.get("status") == "success":
                            st.success(f"تم إضافة الحساب بنجاح! الكود المولد: {save_res.get('accountCode')}")
                            st.rerun()
                        else:
                            st.error(f"فشل الحفظ: {save_res.get('message')}")
