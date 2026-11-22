"""TruthLens AI: simple three-page accessible news checker."""
import html
import sqlite3
import streamlit as st
import plotly.graph_objects as go
from src.predictor import load_model, predict_news
from src.database import add_prediction, get_history, clear_history
from src.analytics import summary, history_frame

st.set_page_config(page_title="TruthLens AI", page_icon="🔎", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');
:root{color-scheme:dark}html{scroll-behavior:smooth}
.stApp{background:#050505;color:#f1eee8;font-family:'DM Sans',sans-serif}
.block-container{max-width:1180px;padding-top:1.1rem;padding-bottom:5rem}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
h1,h2,h3,p,[data-testid="stMarkdownContainer"] p{color:#eeeae5}
h1,h2,h3{font-family:'Playfair Display',serif;letter-spacing:-.035em;font-weight:400!important}
h1{font-size:clamp(3rem,6vw,6rem)!important}h2{font-size:2.3rem!important}
[data-testid="stMarkdownContainer"] p{line-height:1.7}
[data-testid="stHorizontalBlock"]{gap:1rem}
hr{border-color:#292929!important}
.stButton>button{min-height:3.15rem;border-radius:2px;border:1px solid #6a6762;background:#101010;color:#f4f0e9;font-weight:500;letter-spacing:.035em;transition:background .35s,transform .35s,border-color .35s;box-shadow:none}
.stButton>button:hover{background:#eeeae5;color:#050505;border-color:#eeeae5;transform:translateY(-3px)}
.stButton>button[kind="primary"]{background:#f1eee8;color:#080808;border-color:#f1eee8}
.stButton>button[kind="primary"]:hover{background:#d6c3a3;color:#080808}
.stButton>button:focus-visible,.stTextArea textarea:focus-visible{outline:2px solid #d6c3a3;outline-offset:3px}
.stTextArea textarea{font-size:1.13rem!important;line-height:1.8!important;background:#101010!important;color:#f5f2ee!important;border:1px solid #555!important;border-radius:2px!important;padding:20px!important}
.stTextArea label{font-size:1.1rem!important;color:#f1eee8!important}
[data-testid="stMetric"]{background:#111;border:1px solid #3c3c3c;padding:24px;animation:rise .7s both}
[data-testid="stMetricValue"]{color:#f1eee8;font-family:'Playfair Display',serif;font-size:2.8rem}
[data-testid="stMetricLabel"]{color:#bcb7af}
[data-testid="stExpander"]{border:1px solid #4a4a4a;border-radius:2px;background:#101010}
[data-testid="stAlert"]{border-radius:2px}
.hero{min-height:660px;position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:95px 15px 80px;margin:10px 0 38px;background:radial-gradient(ellipse at 50% 48%,#1b1b1b 0%,#080808 46%,#050505 75%);isolation:isolate}
.hero:before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent 49.9%,#ffffff0c 50%,transparent 50.1%);pointer-events:none}
.hero .eyebrow{font-family:'DM Sans',sans-serif;font-size:.8rem!important;letter-spacing:.35em;text-transform:uppercase;color:#cbbda9!important;animation:rise 1s .2s both}
.hero h1{font-family:'Playfair Display',serif;font-weight:400!important;font-size:clamp(4.1rem,11vw,9rem)!important;letter-spacing:-.075em;line-height:.98;max-width:1000px;z-index:2;margin:15px 0 26px;animation:rise 1.2s .3s both}
.hero h1 em{font-weight:400;color:#c7b9a4}
.hero p:last-of-type{max-width:570px;font-size:1.06rem;color:#c8c5c0!important;z-index:2;animation:rise 1.2s .5s both}
.hero .floating{position:absolute;display:grid;place-items:center;background:linear-gradient(140deg,#ddd3c2,#5d564d 50%,#141414 51%,#8e887d);border:1px solid #8c867e;box-shadow:0 25px 80px #000c;opacity:.8;z-index:1;transform-style:preserve-3d;animation:orbit 9s ease-in-out infinite}
.hero .floating:after{content:'TRUTH / 01';font:10px 'DM Sans',sans-serif;letter-spacing:.25em;color:#eee;border:1px solid #eeeeee88;padding:8px}
.hero .one{width:130px;height:175px;top:8%;left:6%;transform:rotate(-20deg);animation-delay:-2s}
.hero .two{width:110px;height:155px;top:11%;right:7%;background:linear-gradient(135deg,#3c4047,#c2c6c7 42%,#0e0e0e 44%);animation-delay:-5s}
.hero .three{width:105px;height:140px;bottom:5%;left:12%;background:linear-gradient(155deg,#111,#a99b84 45%,#191919 47%);animation-delay:-3s}
.hero .four{width:145px;height:95px;bottom:9%;right:9%;background:linear-gradient(115deg,#c6b9a5,#1d1d1d 48%,#69645d 50%);animation-delay:-7s}
.hero .index{position:absolute;bottom:20px;left:20px;color:#aaa;font-size:.65rem;letter-spacing:.2em}
.glass{background:#101010;border:1px solid #383838;padding:28px;margin:12px 0 24px;min-height:140px;transition:transform .45s,border-color .45s;animation:rise .8s both}
.glass:hover{transform:translateY(-7px);border-color:#cbbda9}
.glass h3{font-size:1.55rem;margin:0 0 12px}.glass p{color:#bbb!important;margin:0;font-size:1rem}
.result{padding:36px;background:#121212;margin:24px 0;border:1px solid #666;animation:reveal .65s ease both}
.result.real{border-left:5px solid #a3b9a0}.result.fake{border-left:5px solid #d3a6a0}
.result strong{font:400 clamp(1.7rem,4vw,2.6rem) 'Playfair Display',serif;color:#f3f0ec}.result p{font-size:1.06rem;color:#c9c5c0!important}
.note{font-size:.93rem;line-height:1.8;margin-top:22px;color:#b9b3aa!important}
@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
@keyframes orbit{0%,100%{transform:translateY(0) rotate(-11deg) rotateY(-8deg)}50%{transform:translateY(-28px) rotate(6deg) rotateY(16deg)}}
@keyframes reveal{from{opacity:0;transform:scale(.96) translateY(16px)}to{opacity:1;transform:scale(1) translateY(0)}}
@media(max-width:720px){.hero{min-height:550px}.hero .floating{opacity:.25}.hero .one,.hero .two{width:80px;height:110px}.hero .three,.hero .four{width:80px;height:80px}.block-container{padding-top:.7rem}.hero h1{font-size:clamp(3.5rem,14vw,6rem)!important}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
/* Fix navigation button text contrast */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #f3f0ea !important;
    color: #111111 !important;
    border: 1px solid #f3f0ea !important;
}

div.stButton > button[kind="primary"] *,
div.stButton > button[data-testid="stBaseButton-primary"] * {
    color: #111111 !important;
}
</style>""",unsafe_allow_html=True)

@st.cache_resource(show_spinner="Preparing the news checker…")
def get_model():
    return load_model()

if 'page' not in st.session_state: st.session_state.page='Home'

nav=st.columns([1.7,1,1,1])
with nav[0]: st.markdown('### TRUTHLENS / AI')
for column, name in zip(nav[1:],('Home','Analyze News','Dashboard')):
    with column:
        if st.button(name,use_container_width=True,type='primary' if st.session_state.page==name else 'secondary',key='nav_'+name):
            st.session_state.page=name
            st.rerun()
st.divider()

if st.session_state.page=='Home':
    st.markdown('<div class="hero"><div class="floating one"></div><div class="floating two"></div><div class="floating three"></div><div class="floating four"></div><p class="eyebrow">The art of questioning</p><h1>BEYOND<br><em>THE</em> HEADLINE.</h1><p>In a world full of stories, find a moment of clarity. Explore the news through the lens of AI.</p><span class="index">TRUTHLENS AI — DIGITAL EXHIBITION / 2026</span></div>',unsafe_allow_html=True)
    if st.button('ENTER THE NEWS CHECKER  ↗',type='primary',use_container_width=True):
        st.session_state.page='Analyze News';st.rerun()
    left,right=st.columns(2)
    with left:st.markdown('<div class="glass"><h3>📋 1. Paste your news</h3><p>Copy a headline and a few sentences into the box.</p></div>',unsafe_allow_html=True)
    with right:st.markdown('<div class="glass"><h3>✨ 2. See a simple answer</h3><p>Find out whether it looks possibly real or possibly fake.</p></div>',unsafe_allow_html=True)
    st.info('A helpful clue, not a fact-check: always confirm important news with a trusted source.')

elif st.session_state.page=='Analyze News':
    st.title('The News Room')
    st.markdown('### Every headline tells a story. Question it.')
    examples={
        'Example 1':'The city council announced on Tuesday that the public library will extend its opening hours next month. Officials said the revised schedule follows a community survey and will be reviewed after six months.',
        'Example 2':'SHOCKING SECRET EXPOSED! Anonymous insiders claim an unbelievable discovery has been hidden from everyone for decades. Share this immediately before the powerful people erase all the evidence!'
    }
    with st.expander('Want to try an example?'):
        c1,c2=st.columns(2)
        for c,key in zip((c1,c2),examples):
            if c.button(key,use_container_width=True):
                st.session_state.news_input=examples[key]
                st.session_state.pop('last_result',None)
                st.rerun()
        st.caption('These are made-up examples for testing, not verified news.')
    article=st.text_area('Your news article',key='news_input',height=240,max_chars=100000,placeholder='Paste the news here…')
    if st.button('REVEAL THE ANALYSIS  ↗',type='primary',use_container_width=True):
        st.session_state.pop('last_result',None)
        try:
            with st.spinner('Checking the news…'):
                result=predict_news(get_model(),article)
            st.session_state.last_result=result
            try:
                add_prediction(article[:180],result['label'],result['score'])
            except (sqlite3.Error,OSError,ValueError):
                st.warning('Result is ready, but we could not save it to your dashboard.')
        except FileNotFoundError:
            st.error('The news checker needs its trained model. Please ask the project owner to set it up.')
        except ValueError as exc:
            st.warning('Please paste a longer news article before checking.')
        except Exception:
            st.error('Sorry, the news could not be checked right now. Please try again.')
    if st.session_state.get('last_result'):
        label=st.session_state.last_result['label']
        if label=='REAL':
            st.markdown('<div class="result real" role="status"><strong>✅ Possibly Real News</strong><p>This writing looks similar to real news in the training examples. Please still confirm important claims with a trusted source.</p></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="result fake" role="status"><strong>⚠️ Possibly Fake News</strong><p>This writing looks similar to misleading news in the training examples. Please check a trusted source before sharing.</p></div>',unsafe_allow_html=True)
    st.markdown('<p class="note">🔒 We only save a short preview for your dashboard, not the full article.<br>ℹ️ This tool looks at writing patterns. It cannot prove whether news is true or false.</p>',unsafe_allow_html=True)

else:
    st.title('The Archive')
    st.markdown('### A record of the stories you have explored.')
    try:
        records=get_history()
        counts=summary(records)
    except (sqlite3.Error,OSError,ValueError):
        records=[];counts={'total':0,'real':0,'fake':0}
        st.error('We could not load saved checks right now. Please try again.')
    a,b,c=st.columns(3)
    a.metric('News checked',counts['total'])
    b.metric('Possibly real',counts['real'])
    c.metric('Possibly fake',counts['fake'])
    if records:
        fig=go.Figure(data=[go.Bar(x=['Possibly real','Possibly fake'],y=[counts['real'],counts['fake']],marker_color=['#cbbda9','#76716c'],text=[counts['real'],counts['fake']],textposition='auto')])
        fig.update_layout(title='Your results at a glance',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#e8e3db',height=340,margin=dict(l=15,r=15,t=55,b=20),yaxis=dict(title='News articles',rangemode='tozero',dtick=1),xaxis=dict(title=''))
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.subheader('Recently checked news')
        for item in records[:8]:
            label='Possibly real' if item['label']=='REAL' else 'Possibly fake'
            preview=html.escape(item['preview'])
            st.markdown(f'<div class="glass"><h3>{"✅" if item["label"]=="REAL" else "⚠️"} {label}</h3><p>{preview}</p></div>',unsafe_allow_html=True)
        with st.expander('Remove saved history'):
            st.warning('This will permanently remove all saved checks from this device.')
            confirm=st.checkbox('Yes, remove all saved checks')
            if st.button('Clear history',disabled=not confirm):
                try:
                    clear_history();st.success('History cleared.');st.rerun()
                except (sqlite3.Error,OSError):st.error('Could not clear history. Please try again.')
    else:
        st.markdown('<div class="glass"><h3>Nothing here yet</h3><p>Check your first news article and your results will appear here.</p></div>',unsafe_allow_html=True)
        if st.button('Check news now',type='primary'):
            st.session_state.page='Analyze News';st.rerun()
    st.markdown('<p class="note">These counts show the AI’s past guesses, not confirmed facts. Only short news previews are saved on this device.</p>',unsafe_allow_html=True)
