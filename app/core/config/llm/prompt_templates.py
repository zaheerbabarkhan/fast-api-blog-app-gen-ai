from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate

def summary_prompt_template():
    system_message = SystemMessage(
        content="You are an AI assistant that summarizes blog posts. "
                "You are given the post content in the format of <Content> and </Content>. "
                "Your task is to generate a summary of the content in 200 words or less. "
                "Respond **only** with a JSON object containing a single key 'summary'. "
                "Do not include any headings, additional information, or formatting in your response."
                "Do not include information from your own knowledge; only summarize the content from the blog post."
        )

    human_message = HumanMessage(
        content="<Content>{content}</Content>"
        )
    
    raw_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.content),  
        ("user", human_message.content)      
        ])
    
    return raw_prompt


def suggestion_prompt_template():
    system_message = SystemMessage(
        content="You are an AI assistant that generates title and tags suggestions for blog posts. "
                "You are given the post content in the format of <Content> and </Content>. "
                "Your task is to generate a title and a list of tags for the content. "
                "Respond with a JSON object containing two keys: 'title' and 'tags_list', in which the value of 'title' is a string and the value of 'tags_list' is a list of strings."
                "Do not include any headings, additional information, or formatting in your response."
                "Do not include information from your own knowledge; only generate a title and tags for the content from the blog post."
        )

    human_message = HumanMessage(
        content="<Content>{content}</Content>"
        )
    
    raw_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.content),  
        ("user", human_message.content)      
        ])
    
    return raw_prompt