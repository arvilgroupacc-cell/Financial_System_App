import streamlit as st
import pandas as pd
from api_connector import get_chart_of_accounts

def render_reports_view():
    st.header("📊 التقارير المالية والتصدير")
    st.caption("مراجعة كشوف الحسابات واستخراج التقارير بصيغة Excel")

    res_acc = get_chart_of_accounts()
    if res_acc.get("status") != "success":
        st.error("فشل جلب الحسابات لاستعراض التقارير.")
        return

    accounts = res_acc.get("accounts", [])
    df_acc = pd.DataFrame(accounts)

    st.subheader("دليل الحسابات والأرصدة الافتتاحية")
    st.dataframe(df_acc, use_container_width=True)

    # زر تصدير Excel
    if not df_acc.empty:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_acc.to_excel(writer, sheet_name='Chart_Of_Accounts', index=False)
        
        st.download_button(
            label="📥 تصدير دليل الحسابات كملف Excel",
            data=buffer.getvalue(),
            file_name="Chart_of_Accounts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )