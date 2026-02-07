from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
import asyncio
from config import settings
import yfinance as yf


def analysttool(company:str):
    """Returns all critical metrics for analysis which can enable informed investment decisions
    It returns Context of the company, Profitability metrics, Growth metrics, Health metrics, Complete valuation, Risk etc.
    """
    stock = yf.Ticker(company)
    info = stock.info
    history = stock.history(period="1y")
    valuation = {
        "current_price": round(history['Close'].iloc[-1], 2) if len(history) > 0 else None,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        # "peg_ratio": info.get("pegRatio"),  # CRITICAL: PE adjusted for growth
        "price_to_book": info.get("priceToBook"),
    }
    profitability = {
        "profit_margin_pct": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
        "roe_pct": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
        "roa_pct": round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else None,
    }
    growth = {
        "revenue_growth_pct": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
        "earnings_growth_pct": round(info.get("earningsGrowth", 0) * 100, 2) if info.get("earningsGrowth") else None,
        "yearly_price_return_pct": round(
            ((history['Close'].iloc[-1] / history['Close'].iloc[0]) - 1) * 100, 2
        ) if len(history) > 0 else None,
    }
    health = {
        "current_ratio": info.get("currentRatio"),  # >1 is good
        "debt_to_equity": info.get("debtToEquity"),  # Lower is better
        "free_cash_flow": info.get("freeCashflow"),  # Cash after expenses
    }
    
    # ========== RISK (How volatile/risky?) ==========
    risk = {
        "beta": info.get("beta"),  # Market sensitivity
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "pct_off_high": round(
            ((history['Close'].iloc[-1] / info.get("fiftyTwoWeekHigh", 1)) - 1) * 100, 2
        ) if info.get("fiftyTwoWeekHigh") and len(history) > 0 else None,
    }
    try:
        financials = stock.financials
        if not financials.empty:
            latest = financials.iloc[:, 0]
            key_financials = {
                "revenue_billions": round(latest.get("Total Revenue", 0) / 1e9, 2),
                "net_income_billions": round(latest.get("Net Income", 0) / 1e9, 2),
                "operating_income_billions": round(latest.get("Operating Income", 0) / 1e9, 2),
            }
        else:
            key_financials = None
    except:
        key_financials = None
    
    # ========== CONTEXT ==========
    context = {
        "company_name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }
    return {
        "context": context,
        "valuation": valuation,
        "profitability": profitability,
        "growth": growth,
        "health": health,
        "risk": risk,
        "key_financials": key_financials,
    }





def newstool(company:str):
    """
    Fetches the latest market-moving news and press releases for a specific stock.
    Use this tool when you need to understand recent events, sentiment, or 
    catalysts affecting a company's stock price.

    Args:
        company (str): The official stock ticker symbol (e.g., 'AAPL', 'TSLA', 'NVDA').
        
    Returns:
        list: A list of dictionaries containing news metadata (title, summary, pubDate).
    """
    stock = yf.Ticker(company)
    news = stock.get_news(count=20,tab="all")
    news_list = []
    for i in range(len(news)):
        content_type = news[i]['content']['contentType']
        title = news[i]['content']['title']
        summary = news[i]['content']['summary']
        description = news[i]['content']['description']
        published_date = news[i]['content']['pubDate']
        dict = {'contentType':content_type,'title':title, 'summary':summary,'description':description,'pubDate':published_date}
        news_list.append(dict)
    return news_list


finance_tool = FunctionTool(analysttool, description=("Retrieves essential stock fundamentals and market metrics for a given ticker, including "
        "company context, valuation ratios, profitability, growth, financial health, risk indicators, "
        "and recent financial performance for efficient investment analysis."))
 

news_tool = FunctionTool(newstool,description=("Retrieves the most recent headlines and summaries for a stock ticker to analyze market sentiment and news catalysts."))

def buildteam():    
    # "AIzaSyDLVggZ-c_OmjPorzKM4s5W05aCFPpMXjI"
    model_client = OpenAIChatCompletionClient(model="gemini-2.5-flash", api_key=settings.gemini_api_key)
    # You are a precise Financial Data Scout. Your job is to call the analysttool for the requested ticker, Use a proper ticker name for company which is given in yahoo for example Tesla company's ticker name is 'TSLA'. Do not interpret the data; simply present the results clearly to the Analyst. "
    #   
    financeresearcher = AssistantAgent(name="finance_research_agent",description="Executes the finance_tool and return the output", system_message=("You are a Financial Data Retriever. Call analysttool with the correct ticker symbol (e.g., 'TSLA' for Tesla). Return ONLY the raw data output without any interpretation, analysis, or commentary. If any metric is None, simply include it as-is in your output. Don't answer the user's question just find the company's tiker name from the query and execute the analystool and return the output"),
    tools=[finance_tool],model_client=model_client, reflect_on_tool_use=True)
    
    # 
    newsresearcher = AssistantAgent(name="news_researcher_agent",description=("Executes the news_tool and returns the output"),system_message=("You are a dedicated News Retrieval Agent. Your sole responsibility is to execute the 'newstool' to fetch data for requested companies in the user query.You must use the correct Yahoo Finance ticker symbol. If a user provides a company name (e.g., 'Apple'), you must use its proper Ticker (eg. AAPL)"),tools=[news_tool],model_client=model_client,reflect_on_tool_use=True)
    analyst = AssistantAgent(name="investment_analyst", description="Interprets the data and looks for The Story.",system_message=("""You are a Senior Investment Strategist. Analyze the financial metrics and news provided by the research agents.

Your analysis must include:

**STRENGTHS:** Identify 3 key strengths (e.g., strong profitability, revenue growth, healthy balance sheet, positive news catalysts)

**RISKS:** Identify 3 key risks (e.g., high debt, declining margins, negative news, high volatility)

**VALUATION:** Assess if the stock is expensive or cheap using values sent by the finance_research_agent, and comparing current price to 52-week range.

**NEWS IMPACT:** Explain how recent news affects the investment case

**FINAL RATING:** Provide Buy/Hold/Sell with clear justification (2-3 sentences)

Structure your response with clear sections for each part above.Always give a disclaimer at the end to the user to do their own research before investing"""),model_client=model_client)
    # You are a Senior Investment Strategist. Analyze the financial metrics and recent news together. Identify strengths and  risks of the company, considering both fundamentals and news sentiment. Use the PEG Ratio to determine if the stock is overvalued relative to growth. Factor in how recent news impacts the investment thesis. Provide a Final Rating (Buy/Hold/Sell) with proper justification
    return RoundRobinGroupChat(participants=[financeresearcher,newsresearcher,analyst],max_turns=3)


    
    
# async def main():
#     team = buildteam()
#     team.reset()
#     task = ("Is Tesla a good buy right now?")
#     # async for msg in team.run_stream(task=task):
#     #     if isinstance(msg, TextMessage):
#     #         yield f"{msg.source}: {msg.content}"
#     result = await Console(team.run_stream(task=task))
#     print("result: ",result)

# # async def runner():
# #     async for out in main():
# #         print(out)

# asyncio.run(main())


