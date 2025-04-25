import streamlit as st
import openai
import json

# خواندن متغیرهای محیطی
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📌 تعریف فانکشن
functions = [
    {
        "name": "comment_review",
        "description": "بررسی می‌کند که کامنت توهین‌آمیز هست یا نه",
        "parameters": {
            "type": "object",
            "properties": {
                "Offensive comment": {
                    "type": "boolean",
                    "description": "آیا کامنت توهین‌آمیز است یا نه"
                },
                "Reason for insult": {
                    "type": "string",
                    "description": "دلیل توهین‌آمیز بودن"
                },
                "The degree of offensiveness": {
                    "type": "integer",
                    "description": "درجه توهین بین ۰ تا ۱۰۰"
                }
            },
            "required": ["Offensive comment", "The degree of offensiveness"]
        }
    }
]

# 🎨 رابط کاربری
st.title("🛡️ بررسی توهین‌آمیز بودن کامنت")

rules_input = st.text_area("قوانین توهین را وارد کنید (هر خط یک قانون):")
rules = [rule.strip() for rule in rules_input.split('\n') if rule.strip()]

threshold = st.slider("حد آستانه شدت توهین:", 0, 100, 60)

user_input = st.text_area("کامنت مورد نظر را اینجا بنویسید:")

if st.button("تحلیل کن"):
    if not rules or not user_input.strip():
        st.warning("لطفاً قوانین و کامنت را وارد کنید.")
    else:
        with st.spinner("در حال بررسی..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""تو یک سیستم تحلیل‌گر کامنت هستی. کاربر قوانینی برای شناسایی توهین وارد کرده.
اگر کامنت به هر دلیلی یکی از این قوانین را نقض کرده باشد، میزان شدت توهین را عددی بین 0 تا 100 بده.
اگر از آستانه {threshold} بیشتر بود، مقدار 'Offensive comment' را True بگذار.

قوانین:
{chr(10).join(f"- {rule}" for rule in rules)}
"""
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    functions=functions,
                    function_call="auto"
                )

                func_call = response.choices[0].message.function_call
                if func_call is None:
                    st.error("❌ هیچ فانکشنی اجرا نشد.")
                else:
                    args = json.loads(func_call.arguments)
                    st.subheader("📊 نتیجه تحلیل")
                    st.json(args)

            except Exception as e:
                st.error(f"خطا در اجرای درخواست: {e}")
