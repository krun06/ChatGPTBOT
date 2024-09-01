import streamlit as st
import PyPDF2
import docx
import openai


openai.api_key = st.secrets["openai"]["openkey"]
def limit_words(text, word_limit=1000):
    words = text.split()
    return " ".join(words[:word_limit]) if len(words) > word_limit else text

def extract_text_from_pdf(file, word_limit=1000):
    reader = PyPDF2.PdfReader(file)
    full_text = "".join([page.extract_text() for page in reader.pages])
    return limit_words(full_text, word_limit)

def extract_text_from_docx(file, word_limit=1000):
    doc = docx.Document(file)
    full_text = "".join([para.text for para in doc.paragraphs])
    return limit_words(full_text, word_limit)


def get_answer_from_gpt(question,type, document_text, max_response_tokens=1000):
    prompt = f"The document contains the following information:\n\n{document_text}\n\nUser's question: {question}\nAnswer:"

    chat_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-3.5-turbo" for cost efficiency
        messages=[
            {"role": "system",
             "content": f"You are an {type} assistant who helps with answering questions based on documents. Please provide only relevant facts and figures, if you do not know just let me know."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_response_tokens  # Limit the response tokens
    )
    response=chat_response.choices[0].message.content
    return response

st.title("📄 Document Q&A AI Chatbot")
st.image("images.png")
st.write("""
    Upload a PDF or DOCX file and ask questions about its content.
    The chatbot will help you find answers based on the document. (Try to keep the document under 1000 words, else will be trimmed)
""")

uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file:
    # Determine file type and extract text accordingly
    if uploaded_file.name.endswith('.pdf'):
        document_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        document_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format")
        document_text = None

    if document_text:
        st.success("File successfully uploaded and processed. You can now ask questions.")

        # Allow the user to ask questions
        doc_type = st.text_input("What type of document did you upload (financial, health report, etc.)")
        user_question = st.text_input("Ask a question about the document:")

        passcode= st.text_input("Please enter the passcode:")

        with st.spinner("Validating passcode.."):
            if passcode == st.secrets["passcode"]["key"]:
                if st.button("Get Answer"):
                    if user_question:
                        with st.spinner("Generating answer..."):
                            answer = get_answer_from_gpt(user_question,doc_type, document_text)
                            st.write("### Answer:")
                            st.write(answer)
                    else:
                        st.error("Please enter a question.")
                else:
                    st.info("Please upload a PDF or DOCX file to get started.")
            else:
                st.error("Please enter correct passcode.")
st.markdown("""
    ---
    **Note:** This application is designed for small documents (under 1,000 words) and generates concise answers using OpenAI's GPT API.
""")
