import streamlit as st
from api_connector import login_user

def check_authentication():
    """التحقق من حالة تسجيل الدخول في الجلسة"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

def render_login_page():
    """رسم شاشة تسجيل الدخول"""
    st.markdown(
        """
        <style>
        .login-box {
            max-width: 400px;
            margin: auto;
            padding: 30px;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔑 نظام المالية - الدخول")
        st.subheader("تسجيل الدخول إلى حسابك")

        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")

        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if not username or not password:
                st.error("يرجى إدخال اسم المستخدم وكلمة المرور.")
                return

            with st.spinner("جاري التحقق من البيانات..."):
                res = login_user(username, password)
                if res.get("status") == "success":
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = res.get("user")
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error(f"فشل الدخول: {res.get('message', 'بيانات غير صحيحة')}")

def logout():
    """تسجيل الخروج"""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()