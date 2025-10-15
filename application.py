import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager  
load_dotenv()


def main():
    st.set_page_config(page_title="Study Buddy AI", page_icon="🎓")

    # Initialize session variables
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False

    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    st.title("🎓 Study Buddy AI")

    # Sidebar settings
    st.sidebar.header("⚙️ Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select Question Type",
        ["Multiple Choice", "Fill in the Blank"],
        index=0
    )

    topic = st.sidebar.text_input(
        "Enter Topic", placeholder="e.g., Indian History, Python, Machine Learning"
    )

    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1, max_value=10, value=5
    )

    # Generate Quiz Button
    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False

        generator = QuestionGenerator()
        success = st.session_state.quiz_manager.generate_questions(
            generator, topic, question_type, difficulty, num_questions
        )

        st.session_state.quiz_generated = success
        st.session_state.quiz_submitted = False
        st.rerun()

    # Display quiz
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("🧩 Quiz Time!")

        st.session_state.quiz_manager.attempt_quiz()

        if st.button("✅ Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            st.rerun()

    # Display Results
    if st.session_state.quiz_submitted:
        st.header("📊 Quiz Results")

        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100

            # Colored feedback
            if score_percentage >= 80:
                st.success(f"🎉 Excellent! Score: {score_percentage:.2f}%")
            elif score_percentage >= 50:
                st.warning(f"🙂 Good effort! Score: {score_percentage:.2f}%")
            else:
                st.error(f"😢 Score: {score_percentage:.2f}% — Keep practicing!")

            # Show detailed results
            for _, result in results_df.iterrows():
                question_num = result['question_number']
                if result['is_correct']:
                    st.success(f"✅ Q{question_num}: {result['question']}")
                else:
                    st.error(f"❌ Q{question_num}: {result['question']}")
                    st.write(f"**Your answer:** {result['user_answer']}")
                    st.write(f"**Correct answer:** {result['correct_answer']}")
                st.markdown("---")

            # Save results
            if st.button("💾 Save Results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file, 'rb') as f:
                        st.download_button(
                            label="📥 Download Results CSV",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime='text/csv'
                        )
                else:
                    st.warning("⚠️ No results available to save.")

        # Option to regenerate new quiz
        if st.button("🔁 Generate New Quiz"):
            st.session_state.quiz_generated = False
            st.session_state.quiz_submitted = False
            for key in list(st.session_state.keys()):
                if key.startswith("mcq_") or key.startswith("fill_blank_"):
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()




