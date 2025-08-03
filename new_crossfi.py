import streamlit as st
import json
import time
import random
from groq import Groq
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import hashlib
import base64

# Production-grade app configuration with latest Streamlit features
st.set_page_config(
    page_title="CrossFi Quest",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.crossfi.org',
        'Report a bug': None,
        'About': "CrossFi Quest - Learn blockchain, earn testnet tokens!"
    }
)

# CrossFi Testnet Configuration
CROSSFI_TESTNET_CONFIG = {
    "chainId": "0x103D",  # 4157 in hex
    "chainName": "CrossFi Testnet",
    "nativeCurrency": {
        "name": "CrossFi",
        "symbol": "XFI",
        "decimals": 18
    },
    "rpcUrls": ["https://rpc.testnet.ms"],
    "blockExplorerUrls": ["https://scan.testnet.ms"]
}

# Initialize Groq client with caching
@st.cache_resource(show_spinner="Initializing AI...")
def init_groq():
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("🔑 Please configure GROQ_API_KEY in Streamlit secrets to enable AI features")
        return None
    return Groq(api_key=api_key)

# Enhanced session state initialization
def init_session_state():
    defaults = {
        'user_data': {
            'username': '',
            'level': 1,
            'xp': 0,
            'tokens': 0,
            'completed_lessons': [],
            'streak': 0,
            'last_login': datetime.now().isoformat(),
            'achievements': [],
            'quiz_scores': [],
            'total_study_time': 0
        },
        'wallet': {
            'connected': False,
            'address': '',
            'network': '',
            'balance': 0
        },
        'quiz_state': {
            'active': False,
            'questions': [],
            'current_q': 0,
            'score': 0,
            'topic': ''
        },
        'ui_state': {
            'theme': 'light',
            'show_advanced': False
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Comprehensive lesson content
LESSON_CONTENT = {
    1: {
        'title': 'Blockchain Fundamentals',
        'description': 'Master the core concepts of blockchain technology',
        'content': """
        ## What is Blockchain?
        
        Blockchain is a **distributed ledger technology** that maintains a continuously growing list of records, called blocks, linked and secured using cryptography.
        
        ### Key Features:
        - **Decentralization**: No single point of control
        - **Immutability**: Records cannot be altered once confirmed
        - **Transparency**: All transactions are publicly verifiable
        - **Consensus**: Network agreement on transaction validity
        
        ### How It Works:
        1. **Transaction Initiation**: User initiates a transaction
        2. **Broadcasting**: Transaction is broadcast to the network
        3. **Validation**: Network nodes verify the transaction
        4. **Block Creation**: Valid transactions are grouped into blocks
        5. **Consensus**: Network agrees on the new block
        6. **Chain Addition**: Block is added to the existing chain
        """,
        'xp_reward': 100,
        'token_reward': 25,
        'difficulty': 'Beginner',
        'duration': 15
    },
    2: {
        'title': 'CrossFi Platform Deep Dive',
        'description': 'Explore CrossFi\'s unique Layer 1 blockchain architecture',
        'content': """
        ## CrossFi: Bridging Traditional Finance and Crypto
        
        CrossFi Chain is a **Layer 1 blockchain** that uniquely combines Cosmos SDK and Ethereum Virtual Machine (EVM) compatibility.
        
        ### Architecture Highlights:
        - **Dual Compatibility**: Both Cosmos and EVM ecosystems
        - **Modular Design**: Synchronized components working as one
        - **Financial Bridge**: Seamless fiat-to-crypto integration
        - **High Performance**: Optimized for financial applications
        
        ### Core Components:
        1. **Cosmos Integration**: IBC protocol for interoperability
        2. **EVM Compatibility**: Run Ethereum smart contracts
        3. **Native DeFi**: Built-in financial primitives
        4. **Cross-Chain Bridge**: Multi-chain asset support
        
        ### Use Cases:
        - Decentralized Finance (DeFi) applications
        - Cross-border payments
        - Digital asset management
        - Traditional finance integration
        """,
        'xp_reward': 150,
        'token_reward': 40,
        'difficulty': 'Intermediate',
        'duration': 20
    },
    3: {
        'title': 'Cosmos SDK & EVM Integration',
        'description': 'Understand the technical architecture of CrossFi',
        'content': """
        ## The Power of Dual Architecture
        
        CrossFi's innovative approach combines the best of both blockchain ecosystems.
        
        ### Cosmos SDK Benefits:
        - **Interoperability**: Connect with 50+ Cosmos chains
        - **Modularity**: Pluggable components and upgrades
        - **Sovereignty**: Independent governance and consensus
        - **Performance**: Tendermint BFT consensus
        
        ### EVM Compatibility:
        - **Developer Friendly**: Use existing Ethereum tools
        - **Smart Contracts**: Deploy Solidity contracts
        - **Ecosystem Access**: Leverage Ethereum DeFi protocols
        - **Migration Support**: Easy transition from Ethereum
        
        ### Integration Architecture:
        ```
        ┌─────────────────┐    ┌─────────────────┐
        │   Cosmos SDK    │◄──►│      EVM        │
        │   (Native)      │    │   (Ethereum)    │
        └─────────────────┘    └─────────────────┘
                 │                       │
                 └───────────┬───────────┘
                            │
                    ┌───────────────┐
                    │  CrossFi Core │
                    │   Consensus   │
                    └───────────────┘
        ```
        """,
        'xp_reward': 200,
        'token_reward': 60,
        'difficulty': 'Advanced',
        'duration': 25
    },
    4: {
        'title': 'DeFi on CrossFi',
        'description': 'Explore decentralized finance opportunities',
        'content': """
        ## DeFi Ecosystem on CrossFi
        
        CrossFi provides a comprehensive DeFi infrastructure with traditional finance integration.
        
        ### Native DeFi Features:
        - **Automated Market Makers (AMM)**: Decentralized exchanges
        - **Lending Protocols**: Borrow and lend digital assets
        - **Yield Farming**: Earn rewards for providing liquidity
        - **Synthetic Assets**: Exposure to traditional markets
        
        ### Unique Advantages:
        1. **Fiat Integration**: Direct fiat on/off ramps
        2. **Low Fees**: Efficient consensus mechanism
        3. **Fast Finality**: Sub-second transaction confirmation
        4. **Regulatory Compliance**: Built-in compliance features
        
        ### DeFi Protocols:
        - **CrossFi DEX**: Native decentralized exchange
        - **Lending Pools**: Multi-asset lending platform
        - **Staking Rewards**: Validator and delegator rewards
        - **Cross-Chain Bridges**: Multi-chain asset support
        
        ### Getting Started:
        1. Connect your wallet to CrossFi testnet
        2. Obtain testnet XFI tokens from faucet
        3. Interact with DeFi protocols
        4. Earn rewards and gain experience
        """,
        'xp_reward': 250,
        'token_reward': 80,
        'difficulty': 'Intermediate',
        'duration': 30
    },
    5: {
        'title': 'Building on CrossFi',
        'description': 'Learn to develop dApps on CrossFi platform',
        'content': """
        ## Developer Guide to CrossFi
        
        Build the next generation of financial applications on CrossFi.
        
        ### Development Environment:
        - **Solidity Support**: Use familiar Ethereum development tools
        - **Cosmos SDK**: Access native blockchain features
        - **Web3 Integration**: Standard Web3.js and Ethers.js
        - **Testing Tools**: Comprehensive testnet environment
        
        ### Smart Contract Deployment:
        ```solidity
        // Example CrossFi Smart Contract
        pragma solidity ^0.8.0;
        
        contract CrossFiDApp {
            mapping(address => uint256) public balances;
            
            function deposit() public payable {
                balances[msg.sender] += msg.value;
            }
            
            function withdraw(uint256 amount) public {
                require(balances[msg.sender] >= amount);
                balances[msg.sender] -= amount;
                payable(msg.sender).transfer(amount);
            }
        }
        ```
        
        ### Development Tools:
        - **Hardhat**: Smart contract development framework
        - **Remix IDE**: Browser-based development environment
        - **MetaMask**: Wallet integration and testing
        - **CrossFi Explorer**: Transaction and contract verification
        
        ### Best Practices:
        1. **Security First**: Audit your smart contracts
        2. **Gas Optimization**: Minimize transaction costs
        3. **User Experience**: Design intuitive interfaces
        4. **Testing**: Comprehensive testnet validation
        """,
        'xp_reward': 300,
        'token_reward': 100,
        'difficulty': 'Advanced',
        'duration': 45
    }
}

# Achievement system with detailed rewards
ACHIEVEMENTS = {
    'first_lesson': {
        'name': 'Blockchain Pioneer',
        'description': 'Complete your first lesson',
        'tokens': 50,
        'icon': '🎯'
    },
    'level_5': {
        'name': 'CrossFi Explorer',
        'description': 'Reach level 5',
        'tokens': 200,
        'icon': '🗺️'
    },
    'perfect_quiz': {
        'name': 'Quiz Master',
        'description': 'Score 100% on any quiz',
        'tokens': 100,
        'icon': '🧠'
    },
    'wallet_connected': {
        'name': 'DeFi Ready',
        'description': 'Connect your testnet wallet',
        'tokens': 75,
        'icon': '🔗'
    },
    'streak_7': {
        'name': 'Dedicated Learner',
        'description': 'Maintain 7-day learning streak',
        'tokens': 150,
        'icon': '🔥'
    },
    'all_lessons': {
        'name': 'CrossFi Expert',
        'description': 'Complete all lessons',
        'tokens': 500,
        'icon': '👑'
    }
}

def generate_quiz_questions(topic, difficulty="intermediate"):
    """Generate AI-powered quiz questions using Groq"""
    groq_client = init_groq()
    if not groq_client:
        return get_fallback_questions(topic)
    
    try:
        prompt = f"""Create 4 challenging multiple-choice questions about {topic} in CrossFi blockchain context.
        Difficulty: {difficulty}
        
        Return valid JSON only:
        {{
            "questions": [
                {{
                    "question": "Clear, specific question about {topic}?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct": 0,
                    "explanation": "Detailed explanation of why this answer is correct"
                }}
            ]
        }}
        
        Focus on practical CrossFi knowledge, DeFi concepts, and real-world applications."""
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        # Clean up the response to ensure valid JSON
        if content.startswith('```json'):
            content = content[7:-3]
        elif content.startswith('```'):
            content = content[3:-3]
        
        quiz_data = json.loads(content)
        return quiz_data.get('questions', get_fallback_questions(topic))
    
    except Exception as e:
        st.error(f"AI Quiz Generation Error: {str(e)}")
        return get_fallback_questions(topic)

def get_fallback_questions(topic):
    """Fallback quiz questions organized by topic"""
    question_bank = {
        'Blockchain Fundamentals': [
            {
                "question": "What is the primary benefit of blockchain's decentralized nature?",
                "options": ["A) Faster transactions", "B) No single point of failure", "C) Lower costs", "D) Better graphics"],
                "correct": 1,
                "explanation": "Decentralization eliminates single points of failure, making the system more resilient."
            },
            {
                "question": "What makes blockchain records immutable?",
                "options": ["A) Cryptographic hashing", "B) Government regulation", "C) High costs", "D) Slow processing"],
                "correct": 0,
                "explanation": "Cryptographic hashing creates unique fingerprints that make tampering detectable."
            }
        ],
        'CrossFi Platform': [
            {
                "question": "What makes CrossFi unique among blockchain platforms?",
                "options": ["A) Only supports Bitcoin", "B) Combines Cosmos and EVM", "C) Centralized system", "D) No smart contracts"],
                "correct": 1,
                "explanation": "CrossFi uniquely combines Cosmos SDK and EVM for maximum compatibility."
            },
            {
                "question": "CrossFi is primarily designed to bridge what two worlds?",
                "options": ["A) Gaming and NFTs", "B) Traditional finance and crypto", "C) Social media platforms", "D) Cloud computing"],
                "correct": 1,
                "explanation": "CrossFi focuses on bridging traditional financial systems with cryptocurrency."
            }
        ],
        'DeFi': [
            {
                "question": "What does AMM stand for in DeFi?",
                "options": ["A) Automatic Money Maker", "B) Automated Market Maker", "C) Advanced Monetary Method", "D) Asset Management Module"],
                "correct": 1,
                "explanation": "Automated Market Makers enable decentralized trading without traditional order books."
            }
        ]
    }
    
    return question_bank.get(topic, question_bank['CrossFi Platform'])

def calculate_level(xp):
    """Calculate user level with progressive XP requirements"""
    if xp < 200: return 1
    elif xp < 500: return 2
    elif xp < 1000: return 3
    elif xp < 1800: return 4
    elif xp < 3000: return 5
    else: return min(50, 5 + (xp - 3000) // 500)

def check_and_award_achievements():
    """Check for new achievements and award tokens"""
    user_data = st.session_state.user_data
    new_achievements = []
    
    # Achievement checks
    if len(user_data['completed_lessons']) >= 1 and 'first_lesson' not in user_data['achievements']:
        new_achievements.append('first_lesson')
    
    if calculate_level(user_data['xp']) >= 5 and 'level_5' not in user_data['achievements']:
        new_achievements.append('level_5')
    
    if user_data['quiz_scores'] and max(user_data['quiz_scores']) >= 100 and 'perfect_quiz' not in user_data['achievements']:
        new_achievements.append('perfect_quiz')
    
    if st.session_state.wallet['connected'] and 'wallet_connected' not in user_data['achievements']:
        new_achievements.append('wallet_connected')
    
    if len(user_data['completed_lessons']) >= len(LESSON_CONTENT) and 'all_lessons' not in user_data['achievements']:
        new_achievements.append('all_lessons')
    
    # Award new achievements
    for achievement_id in new_achievements:
        achievement = ACHIEVEMENTS[achievement_id]
        user_data['achievements'].append(achievement_id)
        user_data['tokens'] += achievement['tokens']
        
        # Show achievement notification with latest Streamlit features
        st.toast(f"{achievement['icon']} Achievement Unlocked: **{achievement['name']}**\n+{achievement['tokens']} XFI tokens!", icon="🏆")
        st.balloons()

def render_wallet_connection():
    """Enhanced wallet connection interface"""
    st.subheader("🔗 CrossFi Testnet Wallet")
    
    if not st.session_state.wallet['connected']:
        st.info("Connect your wallet to claim earned tokens and interact with CrossFi testnet.")
        
        # Display testnet configuration
        with st.expander("📋 CrossFi Testnet Configuration", expanded=False):
            config_col1, config_col2 = st.columns(2)
            with config_col1:
                st.code(f"""
Network Name: {CROSSFI_TESTNET_CONFIG['chainName']}
Chain ID: {CROSSFI_TESTNET_CONFIG['chainId']}
Symbol: {CROSSFI_TESTNET_CONFIG['nativeCurrency']['symbol']}
                """)
            with config_col2:
                st.code(f"""
RPC URL: {CROSSFI_TESTNET_CONFIG['rpcUrls'][0]}
Explorer: {CROSSFI_TESTNET_CONFIG['blockExplorerUrls'][0]}
                """)
        
        # Wallet connection buttons
        wallet_col1, wallet_col2, wallet_col3 = st.columns(3)
        
        with wallet_col1:
            if st.button("🦊 MetaMask", type="primary", use_container_width=True):
                # Simulate MetaMask connection
                st.session_state.wallet.update({
                    'connected': True,
                    'address': f"0x{random.randint(10**15, 10**16-1):016x}",
                    'network': 'CrossFi Testnet',
                    'balance': round(random.uniform(0.1, 10.0), 4)
                })
                st.success("🎉 MetaMask connected successfully!")
                check_and_award_achievements()
                st.rerun()
        
        with wallet_col2:
            if st.button("🔵 Keplr Wallet", use_container_width=True):
                st.session_state.wallet.update({
                    'connected': True,
                    'address': f"crossfi{random.randint(10**10, 10**11-1)}",
                    'network': 'Cosmos Hub',
                    'balance': round(random.uniform(0.1, 10.0), 4)
                })
                st.success("🎉 Keplr connected successfully!")
                check_and_award_achievements()
                st.rerun()
        
        with wallet_col3:
            if st.button("⚡ CrossFi Wallet", use_container_width=True):
                st.session_state.wallet.update({
                    'connected': True,
                    'address': f"xfi{random.randint(10**12, 10**13-1)}",
                    'network': 'CrossFi Native',
                    'balance': round(random.uniform(0.1, 10.0), 4)
                })
                st.success("🎉 CrossFi Wallet connected successfully!")
                check_and_award_achievements()
                st.rerun()
        
        # Instructions for manual setup
        st.markdown("### 📱 Manual Setup Instructions")
        st.markdown("""
        1. **Add CrossFi Testnet** to your wallet using the configuration above
        2. **Get testnet tokens** from the [CrossFi faucet](https://docs.crossfi.org)
        3. **Connect your wallet** using one of the buttons above
        4. **Start earning** tokens by completing lessons and quizzes!
        """)
    
    else:
        # Display connected wallet info
        wallet = st.session_state.wallet
        st.success(f"✅ Connected: {wallet['network']}")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.metric("💰 Wallet Balance", f"{wallet['balance']:.4f} XFI")
        with info_col2:
            st.metric("🏆 Earned Tokens", f"{st.session_state.user_data['tokens']} XFI")
        
        st.caption(f"Address: `{wallet['address']}`")
        
        # Token claiming interface
        available_tokens = st.session_state.user_data['tokens']
        if available_tokens > 0:
            st.success(f"💎 **{available_tokens} XFI** tokens ready to claim!")
            
            if st.button("🎯 Claim Tokens", type="primary", use_container_width=True):
                with st.spinner("Processing transaction..."):
                    time.sleep(2)  # Simulate transaction time
                
                # Update balances
                st.session_state.wallet['balance'] += available_tokens * 0.001  # Convert to actual XFI
                st.session_state.user_data['tokens'] = 0
                
                st.balloons()
                st.success(f"✅ Successfully claimed {available_tokens} XFI tokens!")
                st.info(f"📤 Sent to: {wallet['address']}")
                st.rerun()
        else:
            st.info("📚 Complete lessons and quizzes to earn more tokens!")
        
        # Disconnect option
        if st.button("🔌 Disconnect Wallet", type="secondary"):
            st.session_state.wallet = {
                'connected': False,
                'address': '',
                'network': '',
                'balance': 0
            }
            st.rerun()

def render_lesson(lesson_id):
    """Enhanced lesson rendering with better UX"""
    lesson = LESSON_CONTENT[lesson_id]
    completed = lesson_id in st.session_state.user_data['completed_lessons']
    
    # Lesson header
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.subheader(f"📚 Lesson {lesson_id}: {lesson['title']}")
        st.caption(f"⏱️ {lesson['duration']} minutes • {lesson['difficulty']} • +{lesson['xp_reward']} XP • +{lesson['token_reward']} XFI")
    
    with header_col2:
        if completed:
            st.success("✅ Completed")
        else:
            # Progress for current lesson
            current_level = calculate_level(st.session_state.user_data['xp'])
            if lesson_id <= current_level or lesson_id == 1:
                st.info("📖 Available")
            else:
                st.warning(f"🔒 Unlock at Level {lesson_id}")
    
    # Lesson content
    if lesson_id <= calculate_level(st.session_state.user_data['xp']) or lesson_id == 1 or completed:
        with st.container():
            st.markdown(lesson['content'])
        
        if not completed:
            st.markdown("---")
            
            complete_col1, complete_col2 = st.columns([2, 1])
            with complete_col1:
                if st.button(f"🎯 Complete Lesson {lesson_id}", type="primary", use_container_width=True):
                    # Mark lesson as completed
                    st.session_state.user_data['completed_lessons'].append(lesson_id)
                    st.session_state.user_data['xp'] += lesson['xp_reward']
                    st.session_state.user_data['tokens'] += lesson['token_reward']
                    st.session_state.user_data['total_study_time'] += lesson['duration']
                    
                    # Check for achievements
                    check_and_award_achievements()
                    
                    # Show completion message
                    st.toast(f"🎉 Lesson {lesson_id} completed!\n+{lesson['xp_reward']} XP, +{lesson['token_reward']} XFI tokens", icon="✅")
                    st.rerun()
            
            with complete_col2:
                st.metric("📊 Reward", f"+{lesson['xp_reward']} XP")
    else:
        st.warning(f"🔒 This lesson is locked. Reach level {lesson_id} to unlock it!")

def render_quiz_interface():
    """Enhanced quiz interface with better UX"""
    st.subheader("🧠 Knowledge Quiz")
    
    quiz_state = st.session_state.quiz_state
    
    if not quiz_state['active']:
        # Quiz setup
        setup_col1, setup_col2 = st.columns(2)
        
        with setup_col1:
            topic = st.selectbox(
                "📚 Select Topic:",
                ["Blockchain Fundamentals", "CrossFi Platform", "Cosmos SDK & EVM", "DeFi Concepts", "Smart Contract Development"],
                help="Choose a topic based on completed lessons"
            )
        
        with setup_col2:
            difficulty = st.selectbox(
                "⚙️ Difficulty Level:",
                ["beginner", "intermediate", "advanced"],
                index=1,
                help="Higher difficulty = more tokens!"
            )
        
        # Token rewards info
        token_rewards = {"beginner": "20-40", "intermediate": "30-60", "advanced": "50-100"}
        st.info(f"💰 Potential Rewards: {token_rewards[difficulty]} XFI tokens based on performance")
        
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating AI-powered quiz questions..."):
                questions = generate_quiz_questions(topic, difficulty)
                
                st.session_state.quiz_state.update({
                    'active': True,
                    'questions': questions,
                    'current_q': 0,
                    'score': 0,
                    'topic': topic,
                    'difficulty': difficulty,
                    'start_time': time.time()
                })
            st.rerun()
    
    else:
        # Active quiz
        questions = quiz_state['questions']
        current_q = quiz_state['current_q']
        
        if current_q < len(questions):
            question = questions[current_q]
            
            # Progress bar
            progress = (current_q + 1) / len(questions)
            st.progress(progress, text=f"Question {current_q + 1} of {len(questions)}")
            
            # Question display
            st.markdown(f"### {question['question']}")
            
            # Answer options
            answer = st.radio(
                "Select your answer:",
                question['options'],
                key=f"quiz_q_{current_q}",
                label_visibility="collapsed"
            )
            
            # Submit answer
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                    selected_index = question['options'].index(answer)
                    is_correct = selected_index == question['correct']
                    
                    if is_correct:
                        st.success("🎉 Correct!")
                        quiz_state['score'] += 1
                    else:
                        st.error("❌ Incorrect!")
                    
                    st.info(f"💡 **Explanation:** {question['explanation']}")
                    
                    quiz_state['current_q'] += 1
                    time.sleep(2)
                    st.rerun()
            
            with col2:
                if st.button("⏭️ Skip", help="Skip this question (no points)"):
                    quiz_state['current_q'] += 1
                    st.rerun()
        
        else:
            # Quiz completion
            final_score = (quiz_state['score'] / len(questions)) * 100
            time_taken = round(time.time() - quiz_state.get('start_time', time.time()))
            
            st.success("🎊 Quiz Completed!")
            
            # Results display
            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("📊 Final Score", f"{final_score:.0f}%")
            with result_col2:
                st.metric("⏱️ Time Taken", f"{time_taken}s")
            with result_col3:
                st.metric("✅ Correct", f"{quiz_state['score']}/{len(questions)}")
            
            # Token calculation
            base_tokens = {"beginner": 20, "intermediate": 30, "advanced": 50}[quiz_state['difficulty']]
            bonus_multiplier = 1.0
            
            if final_score >= 90:
                bonus_multiplier = 2.0
                st.success("🌟 Excellent! Perfect performance bonus!")
            elif final_score >= 75:
                bonus_multiplier = 1.5
                st.info("👍 Great job! Good performance bonus!")
            elif final_score >= 50:
                bonus_multiplier = 1.0
                st.info("📚 Good effort! Keep learning!")
            else:
                bonus_multiplier = 0.5
                st.warning("📖 Study more and try again!")
            
            tokens_earned = int(base_tokens * bonus_multiplier)
            
            # Award tokens and XP
            st.session_state.user_data['tokens'] += tokens_earned
            st.session_state.user_data['xp'] += tokens_earned // 2
            st.session_state.user_data['quiz_scores'].append(final_score)
            
            # Check for achievements
            check_and_award_achievements()
            
            st.success(f"🎁 Earned: {tokens_earned} XFI tokens + {tokens_earned//2} XP!")
            
            # Action buttons
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.button("🔄 Take Another Quiz", type="primary"):
                    st.session_state.quiz_state = {
                        'active': False,
                        'questions': [],
                        'current_q': 0,
                        'score': 0,
                        'topic': ''
                    }
                    st.rerun()
            
            with button_col2:
                if st.button("💰 View Wallet", type="secondary"):
                    st.info("💡 Navigate to the '💰 Wallet' tab to view your wallet and claim tokens!")

def render_user_profile():
    """Enhanced user profile with modern Streamlit features"""
    user_data = st.session_state.user_data
    current_level = calculate_level(user_data['xp'])
    
    # Profile header with better spacing
    st.markdown("### 👤 Your Learning Profile")
    st.markdown("---")
    
    # Key metrics with better alignment
    st.markdown("#### 📊 Key Metrics")
    
    # Use 2x2 grid for better mobile layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "🎯 Level", 
            current_level,
            delta=f"Level {current_level-1}" if current_level > 1 else None,
            help="Level increases with XP earned"
        )
        st.metric(
            "⚡ Total XP", 
            user_data['xp'],
            help="Experience Points from lessons and quizzes"
        )
    
    with col2:
        st.metric(
            "🏆 Available Tokens", 
            f"{user_data['tokens']} XFI",
            help="Testnet tokens ready to claim"
        )
        st.metric(
            "📚 Lessons Completed", 
            f"{len(user_data['completed_lessons'])}/{len(LESSON_CONTENT)}",
            help="Progress through the curriculum"
        )
    
    st.markdown("---")
    
    # Progress to next level with better formatting
    if current_level < 50:
        next_level_xp_req = [200, 500, 1000, 1800, 3000, 3500, 4000, 4500, 5000][min(current_level-1, 8)]
        if current_level > 5:
            next_level_xp_req = 3000 + (current_level - 5) * 500
        
        current_level_xp = user_data['xp']
        if current_level > 1:
            prev_level_req = [0, 200, 500, 1000, 1800, 3000][min(current_level-2, 5)]
            if current_level > 6:
                prev_level_req = 3000 + (current_level - 6) * 500
        else:
            prev_level_req = 0
        
        progress = (current_level_xp - prev_level_req) / (next_level_xp_req - prev_level_req)
        progress = max(0, min(1, progress))
        
        st.markdown("#### 📈 Progress to Level " + str(current_level + 1))
        st.progress(progress, text=f"{current_level_xp - prev_level_req}/{next_level_xp_req - prev_level_req} XP")
        st.caption(f"Next level requires {next_level_xp_req - current_level_xp} more XP")
    
    # Achievements section with better layout
    if user_data['achievements']:
        st.markdown("---")
        st.markdown("#### 🏆 Achievements Unlocked")
        
        # Display achievements in a cleaner format
        for i, achievement_id in enumerate(user_data['achievements']):
            achievement = ACHIEVEMENTS[achievement_id]
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"### {achievement['icon']}")
                with col2:
                    st.markdown(f"**{achievement['name']}**")
                    st.caption(achievement['description'])
                    st.caption(f"Reward: +{achievement['tokens']} XFI")
            if i < len(user_data['achievements']) - 1:
                st.markdown("---")
    
    # Learning statistics with better organization
    if user_data['quiz_scores']:
        st.markdown("---")
        st.markdown("#### 📊 Quiz Performance")
        
        # Performance metrics in a clean layout
        avg_score = sum(user_data['quiz_scores']) / len(user_data['quiz_scores'])
        best_score = max(user_data['quiz_scores'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Average", f"{avg_score:.1f}%")
        with col2:
            st.metric("🎯 Best", f"{best_score:.0f}%")
        with col3:
            st.metric("📝 Total", len(user_data['quiz_scores']))
        
        # Only show chart if there are multiple quiz scores
        if len(user_data['quiz_scores']) > 1:
            st.markdown("**Score Progression:**")
            quiz_df = pd.DataFrame({
                'Quiz': range(1, len(user_data['quiz_scores']) + 1),
                'Score': user_data['quiz_scores']
            })
            
            fig = px.line(
                quiz_df, 
                x='Quiz', 
                y='Score',
                markers=True,
                line_shape='spline'
            )
            fig.update_layout(
                yaxis_title="Score (%)",
                xaxis_title="Quiz Number",
                showlegend=False,
                height=200  # Smaller height for sidebar
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_leaderboard():
    """Simulated leaderboard for engagement"""
    st.subheader("🏆 Global Leaderboard")
    st.caption("See how you rank against other CrossFi learners!")
    
    # Generate simulated leaderboard data
    current_user_score = st.session_state.user_data['xp']
    
    # Create realistic leaderboard
    leaderboard_data = []
    names = ["CryptoMaster", "DeFiExplorer", "BlockchainPro", "CrossFiGuru", "TokenTrader", 
             "SmartContract", "CosmosExpert", "EVMDeveloper", "YieldFarmer", "LiquidityProvider"]
    
    for i, name in enumerate(names):
        if i < 3:
            score = random.randint(2000, 5000)
        elif i < 7:
            score = random.randint(1000, 2000)
        else:
            score = random.randint(500, 1000)
        
        leaderboard_data.append({
            'Rank': i + 1,
            'Username': name,
            'XP': score,
            'Level': calculate_level(score),
            'Tokens Earned': score // 10
        })
    
    # Add current user
    user_rank = len([x for x in leaderboard_data if x['XP'] > current_user_score]) + 1
    leaderboard_data.append({
        'Rank': user_rank,
        'Username': "You 👤",
        'XP': current_user_score,
        'Level': calculate_level(current_user_score),
        'Tokens Earned': current_user_score // 10
    })
    
    # Sort by XP
    leaderboard_data.sort(key=lambda x: x['XP'], reverse=True)
    
    # Update ranks
    for i, entry in enumerate(leaderboard_data):
        entry['Rank'] = i + 1
    
    # Display leaderboard
    df = pd.DataFrame(leaderboard_data)
    
    # Highlight current user
    def highlight_user(row):
        if "You 👤" in str(row['Username']):
            return ['background-color: #e1f5fe'] * len(row)
        return [''] * len(row)
    
    styled_df = df.style.apply(highlight_user, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # User's position
    user_entry = next(x for x in leaderboard_data if "You 👤" in x['Username'])
    st.info(f"🎯 Your Rank: #{user_entry['Rank']} with {current_user_score} XP")

def main():
    """Main application with modern Streamlit features"""
    init_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .lesson-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #fafafa;
    }
    .achievement-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: white;
        padding: 0.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App header with branding
    st.markdown("""
    <div class="main-header">
        <h1>🚀 CrossFi Quest: Learn & Earn</h1>
        <p>Master CrossFi blockchain technology • Earn real testnet tokens • Build your DeFi future</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with enhanced profile
    with st.sidebar:
        render_user_profile()
        
        # Quick actions with better spacing
        st.markdown("---")
        st.markdown("#### ⚡ Quick Actions")
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("🎯 Start Quiz", use_container_width=True):
                st.info("💡 Navigate to the '🧠 Quiz' tab to test your knowledge and earn tokens!")
        
        with action_col2:
            if st.button("💰 View Wallet", use_container_width=True):
                st.info("💡 Navigate to the '💰 Wallet' tab to connect your wallet and claim tokens!")
        
        # Wallet status with better formatting
        st.markdown("---")
        st.markdown("#### 🔗 Wallet Status")
        
        wallet_status = "🟢 Connected" if st.session_state.wallet['connected'] else "🔴 Not Connected"
        st.info(f"**Status:** {wallet_status}")
        
        if st.session_state.wallet['connected']:
            st.success(f"**Balance:** {st.session_state.wallet['balance']:.4f} XFI")
            st.caption(f"Address: {st.session_state.wallet['address'][:10]}...")
        else:
            st.warning("Connect your wallet to claim earned tokens!")
    
    # Main content with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Learn", 
        "🧠 Quiz", 
        "💰 Wallet", 
        "🏆 Leaderboard", 
        "📊 Progress"
    ])
    
    with tab1:
        st.header("📚 CrossFi Learning Path")
        st.markdown("Complete lessons in order to unlock advanced topics and earn XFI tokens!")
        
        # Learning progress overview
        completed = len(st.session_state.user_data['completed_lessons'])
        total = len(LESSON_CONTENT)
        progress = completed / total
        
        progress_col1, progress_col2 = st.columns([3, 1])
        with progress_col1:
            st.progress(progress, text=f"Course Progress: {completed}/{total} lessons completed")
        with progress_col2:
            st.metric("🎓 Completion", f"{progress*100:.0f}%")
        
        # Lesson list
        for lesson_id in sorted(LESSON_CONTENT.keys()):
            with st.expander(
                f"Lesson {lesson_id}: {LESSON_CONTENT[lesson_id]['title']} "
                f"({'✅ Completed' if lesson_id in st.session_state.user_data['completed_lessons'] else '📖 Available'})",
                expanded=lesson_id == 1 and lesson_id not in st.session_state.user_data['completed_lessons']
            ):
                render_lesson(lesson_id)
    
    with tab2:
        render_quiz_interface()
    
    with tab3:
        render_wallet_connection()
    
    with tab4:
        render_leaderboard()
    
    with tab5:
        st.header("📊 Learning Analytics")
        
        # Overall statistics
        user_data = st.session_state.user_data
        
        # Key performance indicators
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric("🎯 Current Level", calculate_level(user_data['xp']))
        
        with kpi_col2:
            completion_rate = len(user_data['completed_lessons']) / len(LESSON_CONTENT) * 100
            st.metric("📚 Course Progress", f"{completion_rate:.0f}%")
        
        with kpi_col3:
            if user_data['quiz_scores']:
                avg_score = sum(user_data['quiz_scores']) / len(user_data['quiz_scores'])
                st.metric("🧠 Avg Quiz Score", f"{avg_score:.0f}%")
            else:
                st.metric("🧠 Avg Quiz Score", "No data")
        
        with kpi_col4:
            total_tokens = sum(LESSON_CONTENT[lid]['token_reward'] for lid in user_data['completed_lessons'])
            total_tokens += sum(30 if score >= 80 else 20 if score >= 60 else 10 for score in user_data['quiz_scores'])
            st.metric("💎 Total Earned", f"{total_tokens} XFI")
        
        # Learning journey visualization
        if user_data['completed_lessons'] or user_data['quiz_scores']:
            st.subheader("📈 Your Learning Journey")
            
            # Create timeline data
            activity_data = []
            
            # Add lesson completions
            for lesson_id in user_data['completed_lessons']:
                activity_data.append({
                    'Activity': f"Lesson {lesson_id}",
                    'Type': 'Lesson',
                    'XP': LESSON_CONTENT[lesson_id]['xp_reward'],
                    'Tokens': LESSON_CONTENT[lesson_id]['token_reward']
                })
            
            # Add quiz scores
            for i, score in enumerate(user_data['quiz_scores']):
                tokens = 30 if score >= 80 else 20 if score >= 60 else 10
                activity_data.append({
                    'Activity': f"Quiz {i+1}",
                    'Type': 'Quiz',
                    'XP': tokens // 2,
                    'Tokens': tokens
                })
            
            if activity_data:
                activity_df = pd.DataFrame(activity_data)
                
                # XP progression chart
                fig = px.bar(
                    activity_df, 
                    x='Activity', 
                    y='XP', 
                    color='Type',
                    title="XP Earned by Activity",
                    color_discrete_map={'Lesson': '#1f77b4', 'Quiz': '#ff7f0e'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Achievement progress
        st.subheader("🏆 Achievement Progress")
        
        achievement_progress = []
        for achievement_id, achievement in ACHIEVEMENTS.items():
            is_earned = achievement_id in user_data['achievements']
            
            # Calculate progress for each achievement
            if achievement_id == 'first_lesson':
                progress = min(1.0, len(user_data['completed_lessons']))
            elif achievement_id == 'level_5':
                progress = min(1.0, calculate_level(user_data['xp']) / 5)
            elif achievement_id == 'perfect_quiz':
                progress = 1.0 if user_data['quiz_scores'] and max(user_data['quiz_scores']) >= 100 else 0.0
            elif achievement_id == 'wallet_connected':
                progress = 1.0 if st.session_state.wallet['connected'] else 0.0
            elif achievement_id == 'all_lessons':
                progress = len(user_data['completed_lessons']) / len(LESSON_CONTENT)
            else:
                progress = 1.0 if is_earned else 0.0
            
            achievement_progress.append({
                'Achievement': achievement['name'],
                'Progress': progress * 100,
                'Status': '✅ Earned' if is_earned else '🔒 Locked',
                'Reward': f"{achievement['tokens']} XFI"
            })
        
        achievement_df = pd.DataFrame(achievement_progress)
        st.dataframe(achievement_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🚀 <strong>CrossFi Quest</strong> - Gamified blockchain education platform</p>
        <p>Learn • Earn • Build the future of decentralized finance</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()