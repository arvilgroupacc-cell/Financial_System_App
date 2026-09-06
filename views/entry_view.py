import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from api_connector import get_chart_of_accounts, add_transaction, upload_file_attachment

def render_entry_view():
    st.header("📝 إدخال قيد محاسبي جديد")
    st.caption("إدخال والتأكد من توازن أطراف القيد قبل الترحيل")

    # جلب الحسابات
    res_acc = get_chart_of_accounts()
    if res_acc.get("status") != "success":
        st.error("فشل تحميل دليل الحسابات، يرجى التأكد من الاتصال.")
        return

    accounts = res_acc.get("accounts", [])
    account_dict = {f"{acc['code']} - {acc['name']}": (acc['code'], acc['name']) for acc in accounts}

    # تهيئة القيد المؤقت في Session State
    if "current_entries" not in st.session_state:
        st.session_state["current_entries"] = []

    # الجزء العلوى: بيانات القيد الأساسية
    col_date, col_attach = st.columns([1, 2])
    with col_date:
        trans_date = st.date_input("تاريخ الحركة", datetime.now())
    with col_attach:
        uploaded_file = st.file_uploader("مرفق القيد (اختياري - صورة أو PDF)", type=["pdf", "png", "jpg", "jpeg"])

    st.divider()

    # الجزء الأوسط: إضافة طرف القيد
    st.subheader("➕ إضافة طرف للقيد")
    col_acc, col_deb, col_crd = st.columns([3, 1.5, 1.5])

    with col_acc:
        selected_acc_label = st.selectbox("اختر الحساب", list(account_dict.keys()) if account_dict else ["لا يوجد حسابات"])
    with col_deb:
        debit_val = st.number_input("مبلغ مدين", min_value=0.0, value=0.0, step=100.0)
    with col_crd:
        credit_val = st.number_input("مبلغ دائن", min_value=0.0, value=0.0, step=100.0)

    col_desc, col_notes = st.columns([2, 2])
    with col_desc:
        entry_desc = st.text_input("البيان / الشرح التفصيلي")
    with col_notes:
        entry_notes = st.text_input("ملاحظات إضافية")

    if st.button("أضف الطرف للقيد", type="secondary"):
        if debit_val == 0 and credit_val == 0:
            st.warning("يجب إدخال قيمة في المدين أو الدائن.")
        elif debit_val > 0 and credit_val > 0:
            st.warning("لا يمكن إدخال مدين ودائن في نفس الطرف.")
        else:
            acc_code, acc_name = account_dict[selected_acc_label]
            st.session_state["current_entries"].append({
                "accountCode": acc_code,
                "accountName": acc_name,
                "debit": debit_val,
                "credit": credit_val,
                "description": entry_desc,
                "notes": entry_notes
            })
            st.success("تم إضافة الطرف للقيد.")
            st.rerun()

    # عرض جدول أطراف القيد الحالي وفحص التوازن
    if st.session_state["current_entries"]:
        st.divider()
        st.subheader("📋 أطراف القيد الحالي")
        df_entries = pd.DataFrame(st.session_state["current_entries"])
        
        # عرض الجدول
        st.dataframe(df_entries, use_container_width=True)

        total_debit = df_entries["debit"].sum()
        total_credit = df_entries["credit"].sum()
        balance_diff = total_debit - total_credit

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("إجمالي المدين", f"{total_debit:,.2f}")
        with col_t2:
            st.metric("إجمالي الدائن", f"{total_credit:,.2f}")
        with col_t3:
            if abs(balance_diff) < 0.001:
                st.success("⚖️ القيد متوازن")
            else:
                st.error(f"❌ غير متوازن (الفرق: {balance_diff:,.2f})")

        col_clear, col_save = st.columns([1, 2])
        with col_clear:
            if st.button("مسح القيد الحالي", type="secondary"):
                st.session_state["current_entries"] = []
                st.rerun()

        with col_save:
            if st.button("حفظ وترحيل القيد", type="primary", use_container_width=True):
                if abs(balance_diff) >= 0.001:
                    st.error("لا يمكن ترحيل قيد غير متوازن!")
                else:
                    attachment_url = ""
                    username = st.session_state.get("user", {}).get("username", "System")

                    with st.spinner("جاري رفع المرفق وترحيل القيد..."):
                        # رفع المرفق إن وجد
                        if uploaded_file is not None:
                            file_bytes = uploaded_file.read()
                            base64_file = base64.b64encode(file_bytes).decode("utf-8")
                            up_res = upload_file_attachment(uploaded_file.name, base64_file, uploaded_file.type)
                            if up_res.get("status") == "success":
                                attachment_url = up_res.get("fileUrl", "")

                        # تعيين رابط المرفق في كل الأطراف
                        for e in st.session_state["current_entries"]:
                            e["attachmentUrl"] = attachment_url

                        # إرسال القيد للـ API
                        res_trans = add_transaction(
                            trans_date.strftime("%Y-%m-%d"),
                            st.session_state["current_entries"],
                            username
                        )

                        if res_trans.get("status") == "success":
                            st.success(f"تم ترحيل القيد بنجاح! رقم القيد: {res_trans.get('journalID')}")
                            st.session_state["current_entries"] = []
                            st.rerun()
                        else:
                            st.error(f"فشل ترحيل القيد: {res_trans.get('message')}")