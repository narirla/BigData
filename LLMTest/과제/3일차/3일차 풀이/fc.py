from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

gpt = ChatOpenAI( model="gpt-3.5-turbo", temperature=0 )

def chat(prompt, chat_history):
    chat_history.append( HumanMessage(content=prompt) )
    rst = gpt.stream( chat_history )
    return rst