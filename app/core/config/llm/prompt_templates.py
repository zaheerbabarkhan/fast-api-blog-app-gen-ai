from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate

from app.models.comment import SentimentEnum

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

def comment_analysis_template():
    system_message = SystemMessage(
        content="You are a sentiment analysis AI that classifies user comments into three categories:"
                "positive: The comment expresses a favorable opinion about the post."
                "negative: The comment expresses an unfavorable opinion about the post."
                "inappropriate: The comment contains offensive, harmful, or inappropriate language."
                "Your task is to analyze the given comment and respond in **valid JSON format** "
                f"with a single key 'sentiment' and the value as one of the three categories: '{SentimentEnum.POSITIVE}', '{SentimentEnum.NEGATIVE}', or '{SentimentEnum.INAPPROPRIATE}'.")
    human_message = HumanMessage(content="<Comment>{comment}</Comment>")

    raw_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message.content),  
        ("user", human_message.content)      
        ])
    
    return raw_prompt