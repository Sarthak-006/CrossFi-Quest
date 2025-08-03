import streamlit as st
import json
import time
import random
from groq import Groq
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

# App configuration
st.set_page_config(
    page_title="CrossFi Quest - Learn & Earn",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Groq client
@st.cache_resource
def init_groq():
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("Please set GROQ_API_KEY in Streamlit secrets")
        return None
    return Groq(api_key=api_key)

# Initialize session state
def init_session_state():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'level': 1,
            'xp': 0,
            'tokens': 0,
            'completed_lessons': [],
            'streak': 0,
            'last_login': datetime.now().isoformat(),
            'achievements': [],
            'wallet_connected': False,
            'wallet_address': '',
            'quiz_scores': []
        }
    
    if 'current_lesson' not in st.session_state:
        st.session_state.current_lesson = None
    
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'questions': [],
            'current_q': 0,
            'score': 0,
            'answered': []
        }

# CrossFi lesson content structure
LESSONS = {
    1: {
        'title': 'Introduction to Blockchain',
        'content': 'Learn the fundamentals of blockchain technology and how it revolutionizes digital transactions.',
        'xp_reward': 50,
        'token_reward': 10,
        'difficulty': 'Beginner'
    },
    2: {
        'title': 'What is CrossFi?',
        'content': 'Discover CrossFi\'s unique Layer 1 blockchain that bridges traditional finance with cryptocurrency.',
        'xp_reward': 75,
        'token_reward': 15,
        'difficulty': 'Beginner'
    },
    3: {
        'title': 'Cosmos & EVM Integration',
        'content': 'Understand how CrossFi combines Cosmos and Ethereum Virtual Machine for enhanced functionality.',
        'xp_reward': 100,
        'token_reward': 25,
        'difficulty': 'Intermediate'
    },
    4: {
        'title': 'DeFi on CrossFi',
        'content': 'Explore decentralized finance applications and opportunities on the CrossFi platform.',
        'xp_reward': 125,
        'token_reward': 35,
        'difficulty': 'Intermediate'
    },
    5: {
        'title': 'Smart Contracts & Development',
        'content': 'Learn to build and deploy smart contracts on CrossFi\'s dual-compatible platform.',
        'xp_reward': 150,
        'token_reward': 50,
        'difficulty': 'Advanced'
    }
}

# Achievement milestones
ACHIEVEMENTS = {
    'first_lesson': {'name': 'First Steps', 'tokens': 20, 'description': 'Complete your first lesson'},
    'level_5': {'name': 'Blockchain Explorer', 'tokens': 100, 'description': 'Reach level 5'},
    'perfect_quiz': {'name': 'Quiz Master', 'tokens': 50, 'description': 'Score 100% on a quiz'},
    'streak_7': {'name': 'Dedicated Learner', 'tokens': 75, 'description': '7-day learning streak'},
    'all_beginner': {'name': 'Beginner Graduate', 'tokens': 150, 'description': 'Complete all beginner lessons'}
}

def generate_quiz_with_groq(topic, difficulty="beginner"):
    """Generate quiz questions using Groq AI"""
    groq_client = init_groq()
    if not groq_client:
        return generate_fallback_quiz(topic)
    
    try:
        prompt = f"""Generate 3 multiple choice questions about {topic} in CrossFi blockchain.
        Difficulty: {difficulty}
        
        Format as JSON:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct": 0,
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        
        Focus on practical CrossFi knowledge including Layer 1 blockchain, Cosmos-EVM integration, and DeFi concepts."""
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        quiz_data = json.loads(response.choices[0].message.content)
        return quiz_data['questions']
    
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return generate_fallback_quiz(topic)

def generate_fallback_quiz(topic):
    """Fallback quiz questions if Groq fails"""
    questions = [
        {
            "question": "What makes CrossFi unique as a blockchain platform?",
            "options": ["A) Only supports Bitcoin", "B) Combines Cosmos and EVM", "C) Centralized system", "D) No smart contracts"],
            "correct": 1,
            "explanation": "CrossFi uniquely combines Cosmos and EVM architectures for enhanced functionality."
        },
        {
            "question": "CrossFi is primarily designed to bridge what?",
            "options": ["A) Gaming and NFTs", "B) Traditional finance and crypto", "C) Social media platforms", "D) Cloud computing"],
            "correct": 1,
            "explanation": "CrossFi focuses on bridging traditional financial systems with cryptocurrency."
        },
        {
            "question": "What type of blockchain is CrossFi?",
            "options": ["A) Layer 2", "B) Sidechain", "C) Layer 1", "D) Private blockchain"],
            "correct": 2,
            "explanation": "CrossFi is a Layer 1 blockchain with its own consensus mechanism."
        }
    ]
    return questions

def calculate_level(xp):
    """Calculate user level based on XP"""
    return min(50, max(1, int(xp / 200) + 1))

def check_achievements(user_data):
    """Check and award new achievements"""
    new_achievements = []
    
    # First lesson achievement
    if len(user_data['completed_lessons']) >= 1 and 'first_lesson' not in user_data['achievements']:
        new_achievements.append('first_lesson')
    
    # Level achievements
    current_level = calculate_level(user_data['xp'])
    if current_level >= 5 and 'level_5' not in user_data['achievements']:
        new_achievements.append('level_5')
    
    # Perfect quiz achievement
    if user_data['quiz_scores'] and max(user_data['quiz_scores']) == 100 and 'perfect_quiz' not in user_data['achievements']:
        new_achievements.append('perfect_quiz')
    
    # Award achievements
    for achievement in new_achievements:
        user_data['achievements'].append(achievement)
        user_data['tokens'] += ACHIEVEMENTS[achievement]['tokens']
        st.success(f"🏆 Achievement Unlocked: {ACHIEVEMENTS[achievement]['name']} (+{ACHIEVEMENTS[achievement]['tokens']} XFI tokens)")
    
    return new_achievements

def wallet_connection_simulation():
    """Simulate wallet connection for demo purposes"""
    st.subheader("🔗 Connect Your Testnet Wallet")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🦊 MetaMask", use_container_width=True):
            st.session_state.user_data['wallet_connected'] = True
            st.session_state.user_data['wallet_address'] = f"0x{random.randint(10**15, 10**16-1):016x}"
            st.success("MetaMask connected successfully!")
            st.rerun()
    
    with col2:
        if st.button("🔵 Keplr", use_container_width=True):
            st.session_state.user_data['wallet_connected'] = True
            st.session_state.user_data['wallet_address'] = f"crossfi{random.randint(10**10, 10**11-1)}"
            st.success("Keplr connected successfully!")
            st.rerun()
    
    with col3:
        if st.button("⚡ CrossFi Wallet", use_container_width=True):
            st.session_state.user_data['wallet_connected'] = True
            st.session_state.user_data['wallet_address'] = f"xfi{random.randint(10**12, 10**13-1)}"
            st.success("CrossFi Wallet connected successfully!")
            st.rerun()

def claim_tokens_interface():
    """Interface for claiming earned tokens"""
    if not st.session_state.user_data['wallet_connected']:
        st.warning("Please connect your wallet to claim tokens!")
        return
    
    available_tokens = st.session_state.user_data['tokens']
    if available_tokens > 0:
        st.success(f"💰 Available to claim: {available_tokens} XFI testnet tokens")
        
        if st.button("🎯 Claim Tokens", type="primary", use_container_width=True):
            # Simulate transaction
            with st.spinner("Processing transaction..."):
                time.sleep(2)
            
            st.balloons()
            st.success(f"✅ Successfully claimed {available_tokens} XFI tokens!")
            st.info(f"Transaction sent to: {st.session_state.user_data['wallet_address']}")
            
            # Reset claimable tokens
            st.session_state.user_data['tokens'] = 0
            st.rerun()
    else:
        st.info("No tokens available to claim. Complete more lessons to earn rewards!")

def main():
    init_session_state()
    
    # Header
    st.title("🚀 CrossFi Quest: Learn & Earn Blockchain Academy")
    st.markdown("*Master CrossFi blockchain technology through gamified learning and earn testnet tokens!*")
    
    # Sidebar - User Profile
    with st.sidebar:
        st.header("👤 Your Profile")
        
        user_data = st.session_state.user_data
        current_level = calculate_level(user_data['xp'])
        
        # Progress metrics
        st.metric("Level", current_level)
        st.metric("Total XP", user_data['xp'])
        st.metric("Lessons Completed", len(user_data['completed_lessons']))
        st.metric("Available Tokens", f"{user_data['tokens']} XFI")
        
        # Progress bar for next level
        next_level_xp = current_level * 200
        current_progress = user_data['xp'] % 200
        progress = current_progress / 200
        st.progress(progress)
        st.caption(f"Progress to Level {current_level + 1}: {current_progress}/200 XP")
        
        # Wallet status
        if user_data['wallet_connected']:
            st.success("🔗 Wallet Connected")
            st.caption(f"Address: {user_data['wallet_address'][:10]}...")
        else:
            st.warning("⚠️ Wallet Not Connected")
        
        # Achievements
        if user_data['achievements']:
            st.subheader("🏆 Achievements")
            for achievement in user_data['achievements']:
                st.write(f"🎖️ {ACHIEVEMENTS[achievement]['name']}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Learn", "🧠 Quiz", "💰 Wallet", "📊 Progress"])
    
    with tab1:
        st.header("📚 Learning Modules")
        
        # Lesson selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Available Lessons")
            
            for lesson_id, lesson in LESSONS.items():
                with st.expander(f"Lesson {lesson_id}: {lesson['title']} ({lesson['difficulty']})"):
                    st.write(lesson['content'])
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**XP Reward:** {lesson['xp_reward']}")
                    with col_b:
                        st.write(f"**Token Reward:** {lesson['token_reward']}")
                    with col_c:
                        completed = lesson_id in user_data['completed_lessons']
                        if completed:
                            st.success("✅ Completed")
                        else:
                            if st.button(f"Start Lesson {lesson_id}", key=f"lesson_{lesson_id}"):
                                # Complete lesson (simplified)
                                user_data['completed_lessons'].append(lesson_id)
                                user_data['xp'] += lesson['xp_reward']
                                user_data['tokens'] += lesson['token_reward']
                                
                                # Check for achievements
                                check_achievements(user_data)
                                
                                st.success(f"🎉 Lesson completed! +{lesson['xp_reward']} XP, +{lesson['token_reward']} tokens")
                                st.rerun()
        
        with col2:
            st.subheader("📈 Learning Path")
            
            # Create learning progress visualization
            lesson_status = []
            for lesson_id in LESSONS.keys():
                status = "Completed" if lesson_id in user_data['completed_lessons'] else "Available"
                lesson_status.append({
                    'Lesson': f"Lesson {lesson_id}",
                    'Status': status,
                    'Difficulty': LESSONS[lesson_id]['difficulty']
                })
            
            df = pd.DataFrame(lesson_status)
            fig = px.bar(df, x='Lesson', color='Status', 
                        title="Learning Progress",
                        color_discrete_map={'Completed': '#00ff00', 'Available': '#cccccc'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("🧠 Knowledge Quiz")
        
        if not st.session_state.quiz_state['questions']:
            st.subheader("Select Quiz Topic")
            
            col1, col2 = st.columns(2)
            with col1:
                topic = st.selectbox("Choose Topic:", [
                    "Blockchain Basics",
                    "CrossFi Platform",
                    "Cosmos & EVM",
                    "DeFi Concepts",
                    "Smart Contracts"
                ])
            
            with col2:
                difficulty = st.selectbox("Difficulty:", ["beginner", "intermediate", "advanced"])
            
            if st.button("🎯 Start Quiz", type="primary"):
                with st.spinner("Generating quiz questions..."):
                    questions = generate_quiz_with_groq(topic, difficulty)
                    st.session_state.quiz_state = {
                        'questions': questions,
                        'current_q': 0,
                        'score': 0,
                        'answered': []
                    }
                st.rerun()
        
        else:
            # Display quiz
            quiz = st.session_state.quiz_state
            if quiz['current_q'] < len(quiz['questions']):
                current_question = quiz['questions'][quiz['current_q']]
                
                st.subheader(f"Question {quiz['current_q'] + 1}/{len(quiz['questions'])}")
                st.write(current_question['question'])
                
                # Answer options
                answer = st.radio("Select your answer:", current_question['options'], key=f"q_{quiz['current_q']}")
                
                if st.button("Submit Answer"):
                    selected_index = current_question['options'].index(answer)
                    is_correct = selected_index == current_question['correct']
                    
                    if is_correct:
                        st.success("✅ Correct!")
                        quiz['score'] += 1
                    else:
                        st.error("❌ Incorrect!")
                    
                    st.info(f"**Explanation:** {current_question['explanation']}")
                    quiz['answered'].append(is_correct)
                    quiz['current_q'] += 1
                    
                    time.sleep(1)
                    st.rerun()
            
            else:
                # Quiz completed
                final_score = (quiz['score'] / len(quiz['questions'])) * 100
                st.subheader("🎉 Quiz Completed!")
                
                st.metric("Final Score", f"{final_score:.0f}%")
                
                # Award tokens based on performance
                if final_score >= 80:
                    tokens_earned = 30
                    st.success("🌟 Excellent performance!")
                elif final_score >= 60:
                    tokens_earned = 20
                    st.info("👍 Good job!")
                else:
                    tokens_earned = 10
                    st.warning("📚 Keep studying!")
                
                user_data['tokens'] += tokens_earned
                user_data['quiz_scores'].append(final_score)
                
                # Check achievements
                check_achievements(user_data)
                
                st.success(f"Earned {tokens_earned} XFI tokens!")
                
                if st.button("Take Another Quiz"):
                    st.session_state.quiz_state = {'questions': [], 'current_q': 0, 'score': 0, 'answered': []}
                    st.rerun()
    
    with tab3:
        st.header("💰 Wallet & Tokens")
        
        if not st.session_state.user_data['wallet_connected']:
            wallet_connection_simulation()
        else:
            st.success(f"🔗 Connected: {st.session_state.user_data['wallet_address']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💎 Token Balance")
                claim_tokens_interface()
            
            with col2:
                st.subheader("📊 Earning History")
                if st.session_state.user_data['quiz_scores']:
                    df_scores = pd.DataFrame({
                        'Quiz': range(1, len(st.session_state.user_data['quiz_scores']) + 1),
                        'Score': st.session_state.user_data['quiz_scores']
                    })
                    fig = px.line(df_scores, x='Quiz', y='Score', title="Quiz Performance")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No quiz history yet. Take a quiz to see your progress!")
    
    with tab4:
        st.header("📊 Learning Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Achievement Progress")
            for achievement_id, achievement in ACHIEVEMENTS.items():
                earned = achievement_id in user_data['achievements']
                status = "✅ Earned" if earned else "🔒 Locked"
                st.write(f"{status} **{achievement['name']}** - {achievement['description']}")
        
        with col2:
            st.subheader("📈 Learning Stats")
            
            # Calculate completion rate
            completion_rate = (len(user_data['completed_lessons']) / len(LESSONS)) * 100
            
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
            st.metric("Total Tokens Earned", sum([lesson['token_reward'] for lesson_id, lesson in LESSONS.items() if lesson_id in user_data['completed_lessons']]) + sum([30 if score >= 80 else 20 if score >= 60 else 10 for score in user_data['quiz_scores']]))
            
            if user_data['quiz_scores']:
                avg_score = sum(user_data['quiz_scores']) / len(user_data['quiz_scores'])
                st.metric("Average Quiz Score", f"{avg_score:.1f}%")

if __name__ == "__main__":
    main()