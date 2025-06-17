import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from scipy.stats import shapiro, ttest_ind, mannwhitneyu

st.set_page_config(page_title="Student Research Analyzer", layout="centered")
st.title("📊 Student Research Analyzer")

# ---- USER AUTHENTICATION ----
users = {
    "student1": {"name": "Student One", "password": stauth.Hasher(["pass123"])[0]},
    "student2": {"name": "Student Two", "password": stauth.Hasher(["abc456"])[0]}
}

authenticator = stauth.Authenticate(
    credentials=users,
    cookie_name="student_login",
    key="login",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("❌ Incorrect username or password.")
elif authentication_status is None:
    st.warning("🔐 Please enter your login details.")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name}!")

    st.markdown("Upload your research data (Excel) with two columns: **Group** and **Score**.")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.subheader("🔍 Preview of Uploaded Data")
            st.dataframe(df.head())

            if 'Group' not in df.columns or 'Score' not in df.columns:
                st.error("The file must contain 'Group' and 'Score' columns.")
            else:
                group_names = df['Group'].unique()

                if len(group_names) != 2:
                    st.error("Exactly two groups are required for analysis.")
                else:
                    group1 = df[df['Group'] == group_names[0]]['Score'].dropna()
                    group2 = df[df['Group'] == group_names[1]]['Score'].dropna()

                    st.subheader("📈 Normality Check (Shapiro-Wilk Test)")

                    def shapiro_result(data, label):
                        stat, p = shapiro(data)
                        is_normal = p > 0.05
                        st.write(f"**{label}** → W = {stat:.3f}, p = {p:.3f} " +
                                 ("✅ Normal" if is_normal else "❌ Not Normal"))
                        return is_normal

                    normal1 = shapiro_result(group1, group_names[0])
                    normal2 = shapiro_result(group2, group_names[1])

                    if normal1 and normal2:
                        st.subheader("✅ Performing Independent t-test")
                        stat, p = ttest_ind(group1, group2, equal_var=True)
                        test_used = "Independent t-test"
                    else:
                        st.subheader("⚠️ Performing Mann-Whitney U Test")
                        stat, p = mannwhitneyu(group1, group2, alternative='two-sided')
                        test_used = "Mann-Whitney U Test"

                    st.markdown("---")
                    st.subheader(f"📊 {test_used} Results")
                    st.write(f"**Test Statistic**: {stat:.3f}")
                    st.write(f"**P-value**: {p:.3f}")

                    if p < 0.05:
                        st.success("Result: Statistically significant difference between the two groups.")
                    else:
                        st.info("Result: No statistically significant difference between the groups.")

        except Exception as e:
            st.error("An error occurred while processing the file.")
            st.exception(e)

    else:
        st.info("Please upload an Excel file to begin.")
